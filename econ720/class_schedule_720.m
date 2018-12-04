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

year1 = 2018;

topicListV = cell(10, 1);
iTopic = 0;


%% Which problem sets have answers?

answerOlg = true;
dueOlg = 'Sep-10';
answerOlgMoney = true;
dueOlgMoney = 'Oct-1';
answerIh1 = true;
dueIh1 = 'Oct-15';
answerCia = true;
dueCia = 'Oct-22';
answerIh2 = true;
dueIh2 = 'Nov-19';
answerRandD = true;
dueRandD = 'Dec-3';
answerAsset = false;
dueAsset = 'never';


%% Class dates

startDate = datetime(year1, 8, 21);
endDate = datetime(year1, 12, 5);
weekDayV = {'Monday', 'Wednesday'};
cdS = markdownLH.ClassDates(startDate, endDate, weekDayV);
classDateV = cdS.date_list;


%% Special dates

topicV = cell(5,1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Midterm: Material covered: TBA.'}, ...
   datetime(year1, 10, 15));
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Labor day'}, datetime(year1, 9, 3));
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Hurricane'}, datetime(year1, 9, 12));
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Hurricane'}, datetime(year1, 9, 17));
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Make-up class will be scheduled.'}, datetime(year1, 10, 17));
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Thanksgiving'}, datetime(year1, 11, 21));

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Special dates', topicV(1 : i1), classDateV);



%% Modern macro

i1 = 0;
topicV = cell(5, 1);

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'[Modern macro](GenEquil_SL.pdf)', ...
   'Here we talk about methods: how to set up a general equilibrium model and characterize its equilibrium.'});

i1 = i1 + 1;
topicV{i1} =  markdownLH.SubTopic({'Modern macro, part 2'});

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Modern Macro', topicV(1 : i1), classDateV);


%% OLG


topicV = cell(10, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Model](olg/OLG_SL.pdf)'});

i1 = i1 + 1;
if answerOlg
   answerStr = '[answers](olg/OLG_PS-answers.pdf)';
else
   answerStr = ['due ', dueOlg];
end
if false
   % Final example with government bonds
   exampleStr = '[solution for example](OLG_example.pdf)';
else
   exampleStr = 'example (not yet active)';
end
topicV{i1} = markdownLH.SubTopic({'[Dynamics and steady state](olg/olg_analysis_sl.pdf)', ...
   exampleStr,    '[PS1](olg/OLG_PS.pdf)', answerStr});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Dynamics and steady state, part 2'});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Efficiency and Social Security](olg/OLG_SS_SL.pdf)', ...
   '[RQ](olg/OLG_RQ.pdf) (review questions, not to be handed in)'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Bequests](olg/OLG_Bequest_SL.pdf)'});

i1 = i1 + 1;
if answerOlgMoney
   answerStr = '[answers](olg/OLG_Money_PS-answers.pdf)';
else
   answerStr = ['due ', dueOlgMoney];
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
if answerIh1
   answerStr = '[answers](ih1/IH1_PS-answers.pdf)';
else
   answerStr = ['due ', dueIh1];
end
topicV{i1} = markdownLH.SubTopic({'[Competitive equilibrium](ih1/ih1_equil_sl.pdf)', ...
	'[RQ](ih1/IH1_RQ.pdf)', '[PS3](ih1/IH1_PS.pdf)',  answerStr});
% * Sep-23 (Fri): Recitation - dynamic programming and growth model examples

i1 = i1 + 1;
if answerCia
   answerStr = '[answers](ih1/CIA_PS-answers.pdf)';
else
   answerStr = ['due ', dueCia];
end
topicV{i1} = markdownLH.SubTopic({'[Cash in advance models](ih1/CIA_SL.pdf)', ...
   '[RQ](ih1/CIA_RQ.pdf)',    '[PS4](ih1/CIA_PS.pdf)',   answerStr});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Two sector models](ih1/TwoSec_SL.pdf)', ...
   '[RQ](ih1/TwoSec_RQ.pdf)'});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Example: Asset pricing](ih1/IH1_Asset_SL.pdf)', ...
   '[RQ](ih1/ih1_asset_rq.pdf)'});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Dynamic programming theorems](ih1/DP_SL.pdf)', ...
   '[Notes on Dynamic Programming](ih1/Dp_ln.pdf)'}, [], 'sameDate');

% i1 = i1 + 1;
% topicV{i1} = markdownLH.SubTopic({'[Final example](ih1/ih1_final_example_sl.pdf)'},  [],  'sameDate');


iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Infinite Horizon, Discrete Time Models [IH1]', topicV(1 : i1), classDateV);


%% IH continuous time

topicV = cell(10, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Solow model](ih2/solow_SL.pdf)'});
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Optimal control](ih2/OptControl_SL.pdf)'});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[The growth model](ih2/Ramsey_SL.pdf)'});
   
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Competitive equilibrium](ih2/ih2_equil_sl.pdf)'});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Dynamics and phase diagrams](ih2/PhaseDiagrams_SL.pdf) (skipped this year)', ...
   '[RQ](ih2/IH2_RQ.pdf)'},  [],  'sameDate');

if answerIh2
   answerStr = '[answers](ih2/IH2_PS-answers.pdf)';
else
   answerStr = ['due ', dueIh2];
end

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Money in the utility function](ih2/miu_sl.pdf)', ...
   '[PS5](ih2/IH2_PS.pdf)',   answerStr});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Perpetual youth](ih2/PerpetualYouth_SL.pdf)'});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Aggregation issues](ih2/Aggregation_SL.pdf) (skipped this year)'}, ...
   [],  'sameDate');

% [ih2psa]: ih2/IH2_PS-answers.pdf

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Infinite Horizon, Continuous Time Models [IH2]', topicV(1 : i1), classDateV);


%% Growth

topicV = cell(10, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Endogenous growth: AK model](growth/AK_SL.pdf)', ...
   '[RQ](growth/AK_RQ.pdf)',  '[Phase diagram](growth/phase_diagram_sl.pdf) (skipped this year)'});
% * : Recitation: Midterm + examples

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[R&D driven growth](growth/RandD_SL.pdf)'}, [], 'sameDate');

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Increasing varieties](growth/Varieties_SL.pdf)', ...
   '[RQ](growth/RandD_RQ.pdf)'}, [], 'sameDate');

i1 = i1 + 1;
if answerRandD
   answerStr = '[answers](growth/RandD_PS-answers.pdf)';
else
   answerStr = ['due ', dueRandD];
end
topicV{i1} = markdownLH.SubTopic({'[Knowledge spillovers and scale effects](growth/ScaleEffects_SL.pdf)', ...
   '[PS6](growth/RandD_PS.pdf)',    answerStr});
% * : Recitation (examples)
i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Quality ladders](growth/Schumpeter_SL.pdf)'},  [],  'sameDate');

% i1 = i1 + 1;
% topicV{i1} = markdownLH.SubTopic({'[Quality ladders with firm dynamics](growth/Schumpeter2_SL.pdf)'});

%[randpsa]: growth/RandD_PS-answers.pdf

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

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Asset pricing](stochastic/AssetTheory_SL.pdf)'});

i1 = i1 + 1;
if answerAsset
   answerStr = '[answers](stochastic/Asset_PS-answers.pdf)';
else
   answerStr = ['due ', dueAsset];
end

topicV{i1} = markdownLH.SubTopic({'[Extensions](stochastic/asset_extensions_sl.pdf)', ...
   '[RQ](stochastic/Asset_RQ.pdf)', ...
   '[PS7](stochastic/Asset_PS.pdf)',   answerStr});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Stochastic growth model](stochastic/Stoch_Growth_SL.pdf)', ...
   '[RQ](stochastic/Stoch_Growth_RQ.pdf)'});

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Stochastic Growth', topicV(1 : i1), classDateV);



%% Heterogeneous agent models

topicV = cell(10, 1);
i1 = 0;

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Bewley model](hetero/Bewley_SL.pdf)'});

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Wealth distribution: ', ...
   '[Motivation and baseline model](hetero/huggett1996_sl.pdf)'},  [],  'sameDate');

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'[Stochastic aging](hetero/castaneda_sl.pdf)'}, [], 'sameDate');
   
   % '[Self-employment](hetero/wealth_selfempl_sl.pdf)'},  [],  'sameDate');

i1 = i1 + 1;
topicV{i1} = markdownLH.SubTopic({'Aggregate uncertainty: [Krusell and Smith](hetero/Krusell_Smith_SL.pdf)'});

iTopic = iTopic + 1;
topicListV{iTopic} = markdownLH.Topic('Heterogeneous Agents', topicV(1 : i1), classDateV);



%% Search / matching
if false
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
end


%% Contracts
if false
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
end



%% Write

cS = markdownLH.ClassSchedule(classDateV, topicListV);

cS.write('schedule720.mmd');



end
