import cv2
import numpy as np
import pytesseract
import csv
import time
from dataclasses import dataclass
from threading import Thread
import sys
from queue import Queue

VideoPath = "/Users/akshar/Downloads/Humans in Autonomy/DroneFootageAnalysis/SampleVid.mp4"
REFERENCE_INSPECTION_FRAME = cv2.imread("/Users/akshar/Downloads/Humans in Autonomy/DroneFootageAnalysis/blankFrame.jpg")
CROPPED_REFERENCE = cv2.imread("/Users/akshar/Downloads/Humans in Autonomy/DroneFootageAnalysis/ReferenceUnderJoystick.jpg")
LEFT_JOYSTICK = cv2.imread("/Users/akshar/Downloads/Humans in Autonomy/DroneFootageAnalysis/leftJoystick.jpg")
RIGHT_JOYSTICK = cv2.imread("/Users/akshar/Downloads/Humans in Autonomy/DroneFootageAnalysis/rightJoystick.jpg")
TESSERACT_PATH = "/Users/akshar/Downloads/Humans in Autonomy/DroneFootageAnalysis/tesseractPattern.txt"

LEFT_JOYSTICK_DIFFERENCE_THRESHOLD = 280000
RIGHT_JOYSTICK_DIFFERENCE_THRESHOLD = 260000
INSPECTION_MODE_THRESHOLD = 450000

start_frame_number = 0
#cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_number)
cv2.startWindowThread()

times = []
all_times = []
ocr_error = []

@dataclass
class ClickEvent:
    side: float
    time: float

class FileVideoStream:
    def __init__(self, path, queueSize=512):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.stream = cv2.VideoCapture(path)
        self.stream.set(cv2.CAP_PROP_POS_FRAMES, start_frame_number)
        self.stopped = False

        # initialize the queue used to store frames read from
        # the video file
        self.Q = Queue(maxsize=queueSize)

    def start(self):
        # start a thread to read frames from the file video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                return
            if not self.Q.full():
                # read the next frame from the file
                (grabbed, frame) = self.stream.read()
                # if the `grabbed` boolean is `False`, then we have
                # reached the end of the video file
                if not grabbed:
                    self.stop()
                    return
                # add the frame to the queue
                self.Q.put(frame)

    def more(self):
        # return True if there are still frames in the queue
        return self.Q.qsize() > 0

    def size(self):
        # return the number of frames stored in queue
        return self.Q.qsize()

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


def isInspectionMode(left, right):
    left_diff = cv2.subtract(left, LEFT_JOYSTICK)
    right_diff = cv2.subtract(right, RIGHT_JOYSTICK)

    if (left_diff.sum() + right_diff.sum())/2 < INSPECTION_MODE_THRESHOLD:
        return True
    else:
        return False

def isLeftClick(frame, reference):
    difference = cv2.subtract(frame, reference)
    # print ("l ", difference.sum())
    if difference.sum() > LEFT_JOYSTICK_DIFFERENCE_THRESHOLD:
        # print ("returning left click")
        # cv2.imshow("left difference", difference)
        return True
    else:
        return False

def isRightClick(frame, reference):
    difference = cv2.subtract(frame, reference)
    # print ("r ", difference.sum())
    if difference.sum() > RIGHT_JOYSTICK_DIFFERENCE_THRESHOLD:
        # print ("returning right click")
        # cv2.imshow("right difference", difference)
        return True
    else:
        return False

def flightTime(frame):
    time_frame = frame[10:75, 600:700]
    # cv2.imshow("time", time_frame)
    time_str = pytesseract.image_to_string(time_frame, config='--psm 6 -c tessedit_char_whitelist=0123456789:')
    try:
        seconds = (time.strptime(time_str, '%M:%S')[4]*60) + time.strptime(time_str, '%M:%S')[5]
        return seconds
    except:
        # print ("BAD OCR. READ {}".format(time_str))
        if time_str not in ocr_error and all_times:
            seconds = all_times[-1]+1
            ocr_error.append(time_str)
        elif all_times:
            seconds = all_times[-1]
        else:
            seconds = 0
        # print ("returning %d" % seconds)
        return seconds

def checkJoysticks(frame):
    #frame - cv2.medianBlur(frame, 5)
    #LEFT_JOYSTICK = cv2.medianBlur(LEFT_JOYSTICK, 5)
    #RIGHT_JOYSTICK = cv2.medianBlur(RIGHT_JOYSTICK, 5)
    leftJoystick = frame[160:420, 20:280]
    rightJoystick = frame[160:420:, 1000:1260]
    if isInspectionMode(leftJoystick, rightJoystick):
        time = flightTime(frame)
        if time not in all_times:
            all_times.append(time)
        if isLeftClick(leftJoystick, LEFT_JOYSTICK) and not isRightClick(rightJoystick, RIGHT_JOYSTICK):
            if time not in times or not time:
                with open('/Users/akshar/Downloads/Humans in Autonomy/DroneFootageAnalysis/times.csv', 'a') as csvfile:
                    filewriter = csv.writer(csvfile)
                    filewriter.writerow(['1', str(time)])
                times.append(time)
        if isRightClick(rightJoystick, RIGHT_JOYSTICK):
            if time not in times or not time:
                with open('/Users/akshar/Downloads/Humans in Autonomy/DroneFootageAnalysis/times.csv', 'a') as csvfile:
                    filewriter = csv.writer(csvfile)
                    filewriter.writerow(['2', str(time)])
                times.append(time)

stream = FileVideoStream(VideoPath).start()
time.sleep(1.0)
print ("Checking if buffer exists...", stream.more())
while stream.more():
    frame = stream.read()
    #cv2.imshow("frame", frame)
    checkJoysticks(frame)
    # print ("Checking buffer size...", stream.size())
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
print ("Video Complete")
