function class_schedule_720
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
topicV{i1} = markdownLH.SubTopic({'Midterm: Material covered: TBA'}, datetime(year1, 10, 10));
% i1 = i1 + 1;
% topicV{i1} = markdownLH.SubTopic({'Labor day'},  datetime(year1, 9, 5));
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Fall break'}, datetime(year1, 10, 19));
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Thanksgiving'}, datetime(year1, 11, 23));

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Special dates', topicV(1 : i1), classDateV);



%% Modern macro

topicV = cell(1, 1);
topicV{1} =  markdownLH.SubTopic({'[Modern macro](GenEquil_SL.pdf)', ...
   'Here we talk about methods: how to set up a general equilibrium model and characterize its equilibrium.'});

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Modern Macro', topicV, classDateV);


%% OLG

topicV = cell(10, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Model](olg/OLG_SL.pdf)'});

i1 = i1 + 1;
if false
   answerStr = '[answers](olg/OLG_PSA.pdf)';
else
   answerStr = 'due Sep-5';
end
if false
   exampleStr = '[solution for example](OLG_example.pdf)';
else
   exampleStr = '';
end
topicV{i1} = markdownLH.SubTopic({'[Dynamics and steady state](olg/olg_analysis_sl.pdf)', ...
   exampleStr,    '[PS1](olg/OLG_PS.pdf)', answerStr});

% * Sep-2 (Fri): Recitation, OLG examples
% i1 = i1 + 1;
% topicV{i1} = markdownLH.SubTopic({'Labor day'}, datetime(year1,9,5));
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Efficiency and Social Security](olg/OLG_SS_SL.pdf)', ...
   '[RQ](olg/OLG_RQ.pdf) (review questions, not to be handed in)'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Bequests](olg/OLG_Bequest_SL.pdf)'},  [],  'sameDate');

i1 = i1 + 1;
if 0
   answerStr = '[answers](olg/OLG_Money_PSA.pdf)';
else
   answerStr = 'due TBA';
end
topicV{i1} = markdownLH.SubTopic({'[Money in OLG models](olg/OLG_Money_SL.pdf)', ...
   '[PS2](olg/OLG_Money_PS.pdf)', answerStr});

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Overlapping Generations [OLG Models]', topicV(1 : i1), classDateV);


%% IH discrete time


topicV = cell(10, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[The growth model](ih1/IH1_SL.pdf)'});

% * Sep-16 (Fri): Recitation: PS 2
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Dynamic programming](ih1/ih1_dp_sl.pdf)'});

i1 = i1 + 1;
if 0
   answerStr = '[answers](ih1/IH1_PSA.pdf)';
else
   answerStr = 'due TBA';
end
topicV{i1} = markdownLH.SubTopic({'[Competitive equilibrium](ih1/ih1_equil_sl.pdf)', ...
	'[RQ](ih1/IH1_RQ.pdf)', '[PS3](ih1/IH1_PS.pdf)',  answerStr}, [], 'sameDate');
% * Sep-23 (Fri): Recitation - dynamic programming and growth model examples

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Dynamic programming theorems](ih1/DP_SL.pdf)', ...
   '[Notes on Dynamic Programming](ih1/Dp_ln.pdf)'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Example: Asset pricing](ih1/IH1_Asset_SL.pdf)', ...
   '[RQ](ih1/ih1_asset_rq.pdf)'},  [],  'sameDate');

i1 = i1 + 1;
if 0
   answerStr = '[answers](ih1/CIA_PSA.pdf)';
else
   answerStr = 'due TBA';
end
topicV{i1} = markdownLH.SubTopic({'[Cash in advance models](ih1/CIA_SL.pdf)', ...
   '[RQ](ih1/CIA_RQ.pdf)',    '[PS4](ih1/CIA_PS.pdf)',   answerStr});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Two sector models](ih1/TwoSec_SL.pdf)', ...
   '[RQ](ih1/TwoSec_RQ.pdf)'});
% * : Recitation: PS3
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Final example](ih1/ih1_final_example_sl.pdf)'},  [],  'sameDate');

%[ciapsa]: ih1/CIA_PSA.pdf
%[ih1psa]: ih1/IH1_PSA.pdf

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Infinite Horizon, Discrete Time Models [IH1]', topicV(1 : i1), classDateV);


%% IH continuous time

topicV = cell(10, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Solow model](ih2/solow_SL.pdf)'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Optimal control](ih2/OptControl_SL.pdf)'},  [],  'sameDate');

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[The growth model](ih2/Ramsey_SL.pdf)'});

i1 = i1 + 1;
if 0
   answerStr = '[answers](ih2/IH2_PSA.pdf)';
else
   answerStr = 'due TBA';
end
topicV{i1} = markdownLH.SubTopic({'[Dynamics and phase diagrams](ih2/PhaseDiagrams_SL.pdf)', ...
   '[RQ](ih2/IH2_RQ.pdf)',    '[PS5](ih2/IH2_PS.pdf)',   answerStr},  [],  'sameDate');
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Money in the utility function](ih2/miu_sl.pdf)'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Perpetual youth](ih2/PerpetualYouth_SL.pdf)'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Aggregation issues](ih2/Aggregation_SL.pdf)'});

% [ih2psa]: ih2/IH2_PSA.pdf

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Infinite Horizon, Continuous Time Models [IH2]', topicV(1 : i1), classDateV);


%% Growth

topicV = cell(10, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Endogenous growth: AK model](growth/AK_SL.pdf)', ...
   '[RQ](growth/AK_RQ.pdf)',  '[Phase diagram](growth/phase_diagram_sl.pdf)'});
% * : Recitation: Midterm + examples
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[R&D driven growth](growth/RandD_SL.pdf)'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Increasing varieties](growth/Varieties_SL.pdf)', ...
   '[RQ](growth/RandD_RQ.pdf)'});

i1 = i1 + 1;
if 0
   answerStr = '[answers](growth/RandD_PSA.pdf)';
else
   answerStr = 'due TBA';
end
topicV{i1} = markdownLH.SubTopic({'[Knowledge spillovers and scale effects](growth/ScaleEffects_SL.pdf)', ...
   '[PS6](growth/RandD_PS.pdf)',    answerStr});
% * : Recitation (examples)
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Quality ladders](growth/Schumpeter_SL.pdf)'},  [],  'sameDate');

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Quality ladders with firm dynamics](growth/Schumpeter2_SL.pdf)'});

%[randpsa]: growth/RandD_PSA.pdf

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Endogenous Growth [Growth]', topicV(1 : i1), classDateV);


%% Stochastic growth

topicV = cell(10, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Stochastic optimization](stochastic/Stochastic_SL.pdf)'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Dynamic programming](stochastic/theorems_sl.pdf) -- we will not talk about this in class. Think of it as a simple user guide to the results that are out there.'}, ...
   [],  'sameDate');
% iTopic = iTopic + 1; topicListV{iTopic} = markdownLH.Topic('Recitation: '});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Asset pricing](stochastic/AssetTheory_SL.pdf)'},  [],  'sameDate');

i1 = i1 + 1;
dueStr = 'TBA';
if isempty(dueStr)  &&  ~strcmpi(dueStr, 'TBA')
   answerStr = '[answers](stochastic/Asset_PSA.pdf)';
else
   answerStr = ['due ', dueStr];
end
topicV{i1} = markdownLH.SubTopic({'[Extensions](stochastic/asset_extensions_sl.pdf)', ...
   '[RQ](stochastic/Asset_RQ.pdf)', ...
   '[PS7](stochastic/Asset_PS.pdf)',   answerStr});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Stochastic growth model](stochastic/Stoch_Growth_SL.pdf)', ...
   '[RQ](stochastic/Stoch_Growth_RQ.pdf)'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Bewley model](stochastic/Bewley_SL.pdf)'});
% 'Recitation'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Incomplete markets: ', ...
   '[Huggett 1996](stochastic/huggett1996_sl.pdf)', ...
   '[Krusell and Smith](stochastic/Krusell_Smith_SL.pdf)'},  [],  'sameDate');
% * : Recitation


iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Stochastic Growth', topicV(1 : i1), classDateV);


%% Search / matching



topicV = cell(10, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[McCall model](search/McCall_SL.pdf)'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Mortenson-Pissarides](search/MortensonPissarides_SL.pdf)', ...
	'[RQ](search/Search_RQ.pdf)'});


% Dec-2 (M): [Search models of money](search/Search_Money_SL.pdf)

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Search and Matching [Search]', topicV(1 : i1), classDateV);


%% Contracts

topicV = cell(10, 1);
i1 = 0;

%* : Recitation
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Limited commitment](contracts/Contract1_SL.pdf)'});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Last class',  '[Asymmetric information](contracts/Contract2_SL.pdf)', ...
   '[Incentives](contracts/Contract3_SL.pdf)',  ...
   '[RQ](contracts/Contracts_RQ.pdf)' });

%i1 = i1 + 1;
%topicV{i1} = markdownLH.SubTopic({'Last class -- examples and Q&A'}, datetime(year1, 12, 7));

%* Unemployment insurance

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Contracts', topicV(1 : i1), classDateV);




%% Write

cS = markdownLH.ClassSchedule(classDateV, topicListV);

cS.write('schedule720.mmd');



end
