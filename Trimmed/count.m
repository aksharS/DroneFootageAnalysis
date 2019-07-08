    data = xlsread('1_Group_1_Experiment_1.xlsx'); %import data
    columnData1 = data(:,6); %pull out column
    columnData2 = data(:,7);
    syms i;
    i = 0;
    l = length(data);
    [rows columns] = size(data);
    A = int16.empty(l, 0);
    B = int16.empty(l,0);
    for k=1:rows
        cd1 = data(k,6);
        cd2 = data(k,7);
        ActionNum = cd1;
            if ((cd1 == 6) && (cd2 == 2)) % changing up (2) to 12
            AddAction = 12;
        elseif ((cd1 == 6) && (cd2 == 4)) % changing down (4) to 13
            AddAction = 13;
        elseif ((cd1 == 6) && (cd2 == 1)) % changing right (1) to 14
            AddAction = 14;
        elseif ((cd1 == 6) && (cd2 == 3)) % changing left (3) to 15
            AddAction = 15;
        else
            AddAction = 17;
            end
        A(k,1) = ActionNum;
        B(k,1) = AddAction;

    end

    B(B == 17) = [];

    newcol = horzcat(A',B');

    % newDataSet = data(inRangeIndexes,:); % contains only desired rows
    % 
    filename = '1_1.xlsx';
    xlswrite(filename,newcol')