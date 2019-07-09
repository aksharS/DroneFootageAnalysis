value = xlsread('46_Group_3_Experiment_3_Cleaned_Trimmed.xlsx','46_Group_3_Experiment_3','F2:F999999');

takeoff=0; land=0; exfp=0; pause=0; inspl=0; inspc=0; inspcmdst=0; inspcmdend=0; wpcr=0; wpdel=0; wpmov=0; alt=0; no=0;

takeoff = sum(value==0)
land = sum(value==1)
exfp = sum(value==2)
pause = sum(value==3)
inspl = sum(value==4)
inspc = sum(value==5)
inspcmdst = sum(value==6)
inspcmdend = sum(value==7)
wpcr = sum(value==8)
wpdel = sum(value==9)
wpmov = sum(value==10)
alt = sum(value==11)
no = sum(value==12)

A={'46_Group_3_Experiment_3', takeoff, land, exfp, pause, inspl, inspc, inspcmdst, inspcmdend, wpcr, wpdel, wpmov, alt, no};

xlsread('Data Frequency.xlsx');
xlsappend('Data Frequency.xlsx',A);