function class_schedule_920

year1 = 2017;

startDate = datetime(year1, 1, 11);
endDate = datetime(year1, 4, 28);
weekDayV = {'Thursday'};
cdS = markdownLH.ClassDates(startDate, endDate, weekDayV);
classDateV = cdS.date_list


%% Special dates

topicV = cell(5,1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Spring break'},  datetime(year1, 3, 16));

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Special dates', topicV(1 : i1), classDateV);


end