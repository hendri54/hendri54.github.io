function class_schedule_520
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

year1 = 2021;

topicListV = cell(10, 1);
iTopic = 0;


%% Class dates

startDate = datetime(year1, 1, 19);
endDate = datetime(year1, 5, 5);
weekDayV = {'Monday', 'Wednesday'};
cdS = markdownLH.ClassDates(startDate, endDate, weekDayV);
classDateV = cdS.date_list;



%% Special dates

topicV = cell(5,1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Midterm: Material covered: TBA'}, datetime(year1, 3, 10));

for wday = [datetime(year1, 2, 15), datetime(year1, 4, 5)]
   i1 = i1 + 1;
   topicV{i1} = markdownLH.SubTopic({'Wellness day'},  wday);
end

% i1 = i1 + 1;
% topicV{i1} = markdownLH.SubTopic({'Spring break'},  datetime(year1, 3, 14));
% i1 = i1 + 1;
% topicV{i1} = markdownLH.SubTopic({'Spring break'},  datetime(year1, 3, 16));

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Special dates', topicV(1 : i1), classDateV);



%% Growth

topicV = cell(20, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Growth facts](growth/GrowthFacts_SL.pdf)', ...
   'In case you need a refresher: [Growth rates and logarithms](growth/growth_algebra_sl.pdf)', ...
   '[PP](growth/growth_algebra_rq.pdf) (practice problems; previous exams are at the bottom of the page)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Methods for identifying causes and effects](growth/causes_SL.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[The Role of Capital](growth/Capital_SL.pdf)',  '[PP](growth/Capital_RQ.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[The Role of Capital, part 2](growth/Capital2_SL.pdf)'});

% Solow
i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Solow model](growth/Solow_SL.pdf)'});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Solow diagram](growth/solow_diagram_SL.pdf)',  ...
   '[PP](growth/Solow_RQ.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Solow Applications](growth/Solow_Applications_SL.pdf)', ...
   '[Applications, part 2](growth/Solow_Applications2_SL.pdf)'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({...
   'Discussion: [How to prevent the end of economic growth](https://www.scientificamerican.com/article/how-to-prevent-the-end-of-economic-growth/)'});

% Institutions
i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Institutions](growth/Institutions_SL.pdf), [PP](growth/Institutions_RQ.pdf)'});

% R&D
i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Growth and ideas](growth/Ideas_SL.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Romer model](growth/RandD_SL.pdf)', '[PP](growth/RandD_RQ.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Policy implications](growth/romer_implications_SL.pdf)'}, [], 'sameDate');

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Economic Growth', topicV(1 : i1), classDateV);


%% Inequality


topicV = cell(5, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Inequality facts](inequality/basic_facts_sl.pdf)'});
i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Earnings inequality](inequality/earnings_inequality_sl.pdf)'}, [], ...
   'sameDate');
i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[The top 1 percent](inequality/top_incomes_sl.pdf)'});


iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Inequality', topicV(1 : i1), classDateV);


%% Short run

topicV = cell(20, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[IS-LM model](islm/islm_sl.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Equilibrium](islm/islm_equil_sl.pdf)',  '[PP](islm/islm_rq.pdf)'});

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Short Run', topicV(1 : i1), classDateV);


%% Medium Run

topicV = cell(20, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Labor market](asad/labor_mk_sl.pdf)',  '[PP](asad/Labor_RQ.pdf)'});

% <!--- 
% [Rising wage inequality](asad/labor_inequality_sl.pdf)
% enable next time; take material out of inequality_sl
% --->

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[AS-AD model](asad/asad_model_sl.pdf)',  ...
   '[PP](asad/as_ad_rq.pdf) (covers Phillips Curve)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Inflation and unemployment](asad/infl_unempl_sl.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Inflation expectations and monetary policy](expectations/expectations_sl.pdf)', ...
   '[PP](expectations/expectations_rq.pdf)'});


% <!---
% * European Unemployment: [SL](asad/EuropeUnemployment_SL.pdf), [PP](asad/EuropeUnemployment_RQ.pdf)
% * The Financial Crisis: [SL](crisis/crisis_sl.pdf), [PP](crisis/Crisis_RQ.pdf))
% --->

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Medium Run', topicV(1 : i1), classDateV);


%% Open Economy

topicV = cell(20, 1);
i1 = 0;

% <!---
% Mar-22: Exchange rates: [SL](open/basics_open_sl.pdf)
% --->

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Trade deficits](open/TradeDeficit_SL.pdf)', '[PP](open/TradeDeficit_RQ.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'Trade deficits (continued)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[IS-LM model](open/islm_open_sl.pdf)', '[PP](open/is_lm_open_rq.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[IS-LM floating exchange rate](open/islm_floating_sl.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[IS-LM fixed exchange rate](open/islm_fixed_sl.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[AS-AD model](open/asad_open_sl.pdf)', ...
   '[Policy analysis](open/asad_policy_sl.pdf)',  '[PP](open/as_ad_open_rq.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Costs and benefits of international trade](open/trade_sl.pdf)'});

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Open Economy', topicV(1 : i1), classDateV);


%% Expectations

topicV = cell(20, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Asset prices](expectations/asset_prices_sl.pdf)', ...
   '[PP](expectations/asset_prices_rq.pdf)'});

% i1 = i1 + 1;
% topicV{i1} =  markdownLH.SubTopic({'[Consumption](expectations/consumption_sl.pdf)', ...
%    '[PP](expectations/consumption_rq.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Expectations and policy](expectations/policy_sl.pdf)', ...
   '[PP](expectations/policy_rq.pdf)'});

% i1 = i1 + 1;
% topicV{i1} =  markdownLH.SubTopic({'[Budget deficits](policy/fiscal_sl.pdf)',  '[PP](policy/fiscal_rq.pdf)'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'Model synthesis: [SL](expectations/model_summary_sl.pdf)'});

% <!---
% The recovery post 2008
% 
% * [Secular stagnation?](crisis/secular_stagnation_sl.pdf)
% * [Slow wage growth][inactive]
% --->

% Apr-26: Last class: Review. All questions answered.

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Last class'});

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Expectations', topicV(1 : i1), classDateV);




%% Write

cS = markdownLH.ClassSchedule(classDateV, topicListV(1 : iTopic));

cS.write('schedule520.md');



end
