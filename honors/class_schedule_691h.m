function class_schedule_691h
%{
Change
   avoid topics; they are unnecessary
   simply have entries that can be
      - headings
      - SubTopics
      - exams
   each item should have a duration, possibly a fixed date
   the other items are squeezed in between
   should be possible to mark all dates up to a fixed date as taken (easier to handle ex post)
%}

year1 = 2017;

topicListV = cell(10, 1);
iTopic = 0;


%% Class dates

startDate = datetime(year1, 8, 22);
endDate = datetime(year1, 12, 6);
weekDayV = {'Tuesday', 'Thursday'};
cdS = markdownLH.ClassDates(startDate, endDate, weekDayV);
classDateV = cdS.date_list;



%% Special dates

topicV = cell(5,1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Fall break'}, datetime(year1, 10, 19));

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Thanksgiving'},  datetime(year1, 11, 23));

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Special dates', topicV(1 : i1), classDateV);



%% Part 1

topicV = cell(20, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Syllabus](syllabus691h.html)',  '[Finding a topic](finding_topic.html)',  ...
   '[Finding an advisor](finding_advisor.html)',   '[Useful links](links.html)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Writing a literature review](lit_review.html)',  ...
   '[Reading papers](how_to_read.html)'});
   
for ix = 1 : 27
   i1 = i1 + 1;
   topicV{i1} =  markdownLH.SubTopic({'TBD'});
end

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Part I', topicV(1 : i1), classDateV);



%% Wrap up

topicV = cell(20, 1);
i1 = 0;


i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Last class'});

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Wrap up', topicV(1 : i1), classDateV);




%% Write

cS = markdownLH.ClassSchedule(classDateV, topicListV(1 : iTopic));

% For this class, it is best to hand edit schedule (b/c of class presentations)
cS.write('schedule691h_auto.mmd');



end
