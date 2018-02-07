function mpc = case33bw_dcs
%CASE33BW  Power flow data for 33 bus distribution system from Baran & Wu
%    Please see CASEFORMAT for details on the case file format.
%
%    Data from ...
%       M. E. Baran and F. F. Wu, "Network reconfiguration in distribution
%       systems for loss reduction and load balancing," in IEEE Transactions
%       on Power Delivery, vol. 4, no. 2, pp. 1401-1407, Apr 1989.
%       doi: 10.1109/61.25627
%       URL: http://doi.org/10.1109/61.25627

%    Modifications (16.10.17):
% • the long branches are cut short, so the number of nodes – the main 
% branch is from node 1 to 7, and additional single branches, to nodes 8,9,
% 10, from nodes 2,3,6, respectively.
% •	rescaling of the loads since the majority is cut off
% •	significantly heavier load at the end of the feeder (node 7), so that 
% voltage drops a bit
% •	additional generators at nodes 5,7,9 (5 with medium ratings, say a WPP,
% and 7&9 with small ratings, spay PVs)
% •	partially flexible load at node 8
% •	fully flexible load at node 9
% •	separate costs for P and Q, for both generators and flexible loads (all
% linear, costs of RES production are small, costs of manipulating loads 
% are higher)


%% MATPOWER Case Format : Version 2
mpc.version = '2';

%%-----  Power Flow Data  -----%%
%% system MVA base
mpc.baseMVA = 100;

%% bus data
%	bus_i	type	Pd	Qd	Gs	Bs	area	Vm	Va	baseKV	zone	Vmax	Vmin
mpc.bus = [  %% (Pd and Qd are specified in kW & kVAr here, converted to MW & MVAr below)
	1	3	0       0       0	0	1	1	0	12.66	1	1	1;
	2	1	1000    600     0	0	1	1	0	12.66	1	1.1	0.9;
	3	1	900     400     0	0	1	1	0	12.66	1	1.1	0.9;
	4	1	590     300     0	0	1	1	0	12.66	1	1.1	0.9;
	5	1	570     290     0	0	1	1	0	12.66	1	1.1	0.9;
	6	1	520     170     0	0	1	1	0	12.66	1	1.1	0.9;
	7	1	170     87     0	0	1	1	0	12.66	1	1.1	0.9;
	8	1	400     200     0	0	1	1	0	12.66	1	1.1	0.9; % partially flexible load
	9	1	0     	0       0	0	1	1	0	12.66	1	1.1	0.9; % fully flexible load
	10	1	4265    2132    0	0	1	1	0	12.66	1	1.1	0.9;
];

%% generator data
%	bus	Pg	Qg	Qmax	Qmin	Vg	mBase	status	Pmax	Pmin	Pc1	Pc2	Qc1min	Qc1max	Qc2min	Qc2max	ramp_agc	ramp_10	ramp_30	ramp_q	apf
mpc.gen = [
	1	0	0	10      -10     1	100     1       10      0       0	0	0	0	0	0	0	0	0	0	0;
    5	0	0	1.5     -1.5    1	100     1       3       0       0	0	0	0	0	0	0	0	0	0	0;
    7	0	0	2       -2      1	100     1       5       0       0	0	0	0	0	0	0	0	0	0	0;
    9	0	0	0.1     -0.1    1	100     1       0.5     0       0	0	0	0	0	0	0	0	0	0	0;
    % flexible loads
    8	0	0	0       -0.1     1	100     1       0       -0.5	0	0	0	0	0	0	0	0	0	0	0;
    %9	0	0	0       -0.2     1	100     1       0       -0.7	0	0	0	0	0	0	0	0	0	0	0;
];

%% branch data
%	fbus	tbus	r	x	b	rateA	rateB	rateC	ratio	angle	status	angmin	angmax
mpc.branch = [  %% (r and x specified in ohms here, converted to p.u. below)
	1	2	0.0922	0.0470	0	0	0	0	0	0	1	-360	360;
	2	3	0.4930	0.2511	0	0	0	0	0	0	1	-360	360;
	3	4	0.3660	0.1864	0	0	0	0	0	0	1	-360	360;
	4	5	0.3811	0.1941	0	0	0	0	0	0	1	-360	360;
	5	6	0.8190	0.7070	0	0	0	0	0	0	1	-360	360;
	6	7	0.1872	0.6188	0	0	0	0	0	0	1	-360	360;
	2	8	0.1640	0.1565	0	0	0	0	0	0	1	-360	360;
	3	9	0.4512	0.3083	0	0	0	0	0	0	1	-360	360;
	6	10	0.2030	0.1034	0	0	0	0	0	0	1	-360	360;
];

%%-----  OPF Data  -----%%
%% generator cost data
%	1	startup	shutdown	n	x1	y1	...	xn	yn
%	2	startup	shutdown	n	c(n-1)	...	c0
mpc.gencost = [
    % gen costs (P)
	2	0	0	2	20	0;
    2   0   0   2   2   0;
    2   0   0   2   25  0;
    2   0   0   2   1   0;
    % flexible loads costs (P)
    2   0   0   2   50  0;
    %2   0   0   2   50  0;
%     % gen costs (Q)
    2	0	0	2   25	0;
    2   0   0   2   3   0;
    2   0   0   2   2   0;
    2   0   0   2   2   0;
    % flexible loads costs (Q)
    2   0   0   2   80  0;
%     2   0   0   2   80  0;
];


%% convert branch impedances from Ohms to p.u.
[PQ, PV, REF, NONE, BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, VM, ...
    VA, BASE_KV, ZONE, VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN] = idx_bus;
[F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, ...
    TAP, SHIFT, BR_STATUS, PF, QF, PT, QT, MU_SF, MU_ST, ...
    ANGMIN, ANGMAX, MU_ANGMIN, MU_ANGMAX] = idx_brch;
Vbase = mpc.bus(1, BASE_KV) * 1e3;      %% in Volts
Sbase = mpc.baseMVA * 1e6;              %% in VA
mpc.branch(:, [BR_R BR_X]) = mpc.branch(:, [BR_R BR_X]) / (Vbase^2 / Sbase);

%% convert loads from kW to MW
mpc.bus(:, [PD, QD]) = mpc.bus(:, [PD, QD]) / 1e3;
