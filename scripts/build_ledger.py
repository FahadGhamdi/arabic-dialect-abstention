#!/usr/bin/env python3
"""Authoring source of docs/CLAIMS_LEDGER.csv — every numeric or countable claim in the manuscript, with its
comparison, denominator, unit, interval type, analysis tier, allowed wording and the exact source cell(s).
Run:  python3 scripts/build_ledger.py && python3 scripts/check_ledger.py

Tier codes
  T1   endpoint/rule fixed in ANALYSIS_PLAN.md before confirmatory scoring; analysis code frozen before any confirmatory file was opened
  T1b  S4: added during score collection, before any confirmatory score file was opened for analysis
  T2   addendum specified AFTER the main confirmatory results had been seen and BEFORE its own computation (Add. 2, 4, 7, 8, 9, 10)
  T3   exploratory / post hoc (specified after the relevant results were seen)
  W    claim withdrawn; the negative test result remains documented
  DEV  development phase (500-key pilot)
  EXT  external fact (resource documentation, independent-implementation report)
  DSN  design parameter (counts, seeds) checked against data files
Interval codes
  FIX  paired key bootstrap over test keys, thresholds fixed (B = 2000, 95% percentile)
  RS   double resampling of calibration and test keys with threshold re-selection (B = 1000, 95% percentile)
  KC   key-clustered 95% CI (model-assisted screen)
  PT   point estimate only
"""
import csv, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S4 = 'results/confirm/S4_operational_selective.csv'
P1 = 'results/confirm/P1_selective.csv'
P2 = 'results/confirm/P2_conformal.csv'
P3 = 'results/confirm/P3_churn.csv'
S2 = 'results/confirm/S2_variety_aware.csv'
D12 = 'results/diag/D1_D2_discrimination.csv'
D4 = 'results/diag/D4_variety_threshold.csv'
R1 = 'results/robust/R1_order_sensitivity.csv'
R2 = 'results/robust/R2_gap_stability.csv'
R3 = 'results/robust/R3_s4_by_order.csv'
R4 = 'results/robust/R4_p3_decomposition.csv'
R5 = 'results/robust/R5_generation.csv'
S91 = 'results/sens/S91_calibration_sensitivity.csv'
S91R = 'results/sens/S91_rotation_sensitivity.csv'
S92 = 'results/sens/S92_reproducibility.csv'
S93 = 'results/sens/S93_R4_paired.csv'
S94 = 'results/sens/S94_D4_distance.csv'
S101 = 'results/supp/S101_risk_diff.csv'
S102 = 'results/supp/S102_gen_selective_risk.csv'
L1 = 'results/validity/L1_ifm_filter.csv'
L2 = 'results/validity/L2_fidelity.csv'
L4 = 'results/validity/L4_aradice.csv'
AUD = 'results/audit/AUDIT_RESULTS.md'
IND = 'results/indep_check/INDEP_COMPARISON.md'
CONF = 'results/confirm/CONFIRM_SUMMARY.md'

DI = 'variety in EGY|KSA|MAG|SYR|UAE'
W_S4 = 'answered fraction / realised risk under the MSA-calibrated threshold; "fewer answers" and "higher risk than MSA" are separate statements; "exceeds the target" only where the interval lower bound is above 0.20'
W_P1 = 'descriptive: answerable fraction at the risk MSA reaches at 50% coverage (test labels used); not a deployable policy'
W_P2 = 'coverage lost under the MSA quantile; set size under the own quantile at the same nominal target (the target was not met empirically in every cell)'
W_D4 = 'per-dialect re-selection brings the empirical risk toward/under the 0.20 ceiling where transfer failed badly, at a cost in coverage; a gap remains at the targets studied'

rows = []


def add(id, section, claim, quantity, comparison, denominator, unit, interval, tier, wording, file, filter, expr, claimed, tol=0.0, note=''):
    rows.append(dict(id=id, section=section, claim=claim, quantity=quantity, comparison=comparison, denominator=denominator,
                     unit=unit, interval=interval, tier=tier, wording=wording, file=file, filter=filter, expr=expr,
                     claimed=json.dumps(claimed), tol=tol, note=note))


# ---------------- design parameters ----------------
add('D01', '§2 Methods', '3,135 DAMM questions (keys)', 'count of keys', '-', 'DAMM', 'keys', 'PT', 'DSN', '-', 'data/damm.csv', '', "D['key'].nunique()", 3135)
add('D02', '§2 Methods', 'development sample 500 keys', 'count', '-', 'DAMM keys', 'keys', 'PT', 'DSN', 'reported as development only', 'data/pilot_keys.json', '', "len(J['keys']) if 'keys' in J else len([v for v in J.values() if isinstance(v,list)][0])", 500)
add('D03', '§2 Methods', 'router 404 / calibration 808 / test 1,420 keys; seed 20261105', 'counts', '-', 'remaining 2,632 keys', 'keys', 'PT', 'DSN', '-', 'data/confirmatory_splits.json', '', "[len(J['router_train']), len(J['calibration']), len(J['test']), J['seed']]", [404, 808, 1420, 20261105])
add('D04', '§2 Methods', 'AraDiCE 600 calibration / 1,400 test parallel items', 'counts', '-', 'AraDiCE parallel pool', 'items', 'PT', 'DSN', '-', 'data/aradice_splits.json', '', "[len(J['calibration']), len(J['test'])]", [600, 1400])
add('D05', '§2 Methods', 'IFM filter: 935 flagged dialect rows in the resource, of which 387 fall on test keys (5–6% of test keys per dialect)', 'count; share', '-', '5 × 1,420 test rows', 'rows; %', 'PT', 'T2', 'external filter (three LLM judges, unanimous)', L1, "model=ALLaM-7B-Instruct-preview", "[int((df.n_orig-df.n_kept).sum()), rng(df.assign(s=100*(df.n_orig-df.n_kept)/df.n_orig),'s',0)]", [387, [5.0, 6.0]], 0.6, 'v0.2 wrote "dropping the 935 dialect rows"; 935 is the resource-wide count (data/ifm_excluded.json n_excluded), 387 rows are on test keys (v0.3 corrected)')

# ---------------- S4 (T1b) ----------------
add('S4-01', 'Abstract/§3.1', 'MSA answered fraction 0.52/0.56/0.59/0.47 at r*=0.20', 'answered fraction', 'MSA', '1,420 test keys', 'fraction', 'PT', 'T1b', W_S4, S4, 'target_risk=0.2; variety=MSA', "rd(pick(df,'answered'),2)", [0.52, 0.56, 0.59, 0.47], 0.005)
add('S4-02', '§3.1', 'MSA realised risk 0.21/0.19/0.20/0.18', 'realised risk among answered', 'MSA', 'answered MSA items', 'fraction', 'PT', 'T1b', W_S4, S4, 'target_risk=0.2; variety=MSA', "rd(pick(df,'realised_risk'),2)", [0.21, 0.19, 0.2, 0.18], 0.005)
for v, vals in {'MAG': [-0.11, -0.15, -0.21, -0.18], 'SYR': [-0.05, -0.13, -0.12, -0.12], 'EGY': [-0.04, -0.08, -0.06, -0.07], 'KSA': [-0.05, -0.07, -0.07, -0.07], 'UAE': [-0.01, -0.05, -0.05, -0.03]}.items():
    add(f'S4-03-{v}', '§3.1 table', f'Δ answered vs MSA, {v}: {vals}', 'answered(v) − answered(MSA)', 'dialect − MSA, same test keys', '1,420', 'fraction', 'FIX', 'T1b', W_S4, S4, f'target_risk=0.2; variety={v}', "rd(pick(df,'d_answered'),2)", vals, 0.005)
for v, vals in {'MAG': [0.28, 0.21, 0.24, 0.17], 'SYR': [0.31, 0.23, 0.23, 0.22], 'EGY': [0.25, 0.21, 0.22, 0.22], 'KSA': [0.24, 0.22, 0.2, 0.21], 'UAE': [0.26, 0.2, 0.21, 0.19]}.items():
    add(f'S4-04-{v}', '§3.1 table', f'realised risk for the dialect user, {v}: {vals}', 'realised risk at τ_MSA', 'dialect alone (vs 0.20 ceiling and vs MSA separately)', 'answered dialect items', 'fraction', 'PT', 'T1b', W_S4, S4, f'target_risk=0.2; variety={v}', "rd(pick(df,'realised_risk'),2)", vals, 0.005)
add('S4-05', 'Abstract/§3.1', 'answers fewer dialect questions in every model (point estimates <0 in 20/20)', 'sign of Δanswered', 'dialect − MSA', '20 dialect×model cells', 'count', 'PT', 'T1b', '"fewer answers in every model" (point estimates); significance stated separately', S4, f'target_risk=0.2; {DI}', "cnt(df.d_answered<0)", 20)
add('S4-06', '§3.1', 'Δanswered CI excludes 0 in 19/20 cells; exception ALLaM–UAE', 'Δanswered interval', 'dialect − MSA', '20 cells', 'count', 'FIX', 'T1b', W_S4, S4, f'target_risk=0.2; {DI}', "[cnt(df.d_hi<0), list(df[df.d_hi>=0].apply(lambda r: r.model[:5]+'-'+r.variety,axis=1))]", [19, ['ALLaM-UAE']])
add('S4-07', '§3.1', 'Δanswered calibration-robust in 19/20 under double resampling (same cell)', 'Δanswered interval', 'dialect − MSA', '20 cells', 'count', 'RS', 'T2', 'Addendum 9 §9.1', S91, DI, "[cnt(df.s4_hi_rs<0), list(df[df.s4_hi_rs>=0].apply(lambda r: r.model[:5]+'-'+r.variety,axis=1))]", [19, ['ALLaM-UAE']])
add('S4-08', '§3.1', 'Δrisk vs MSA: MAG ALLaM +6.7 [+3.3,+10.3], Qwen3 +3.5 [+0.2,+6.8] (pp)', 'realised risk(v) − risk(MSA)', 'dialect − MSA', 'answered items', 'pp', 'FIX', 'T2', 'higher risk than MSA only where the interval excludes 0 (Addendum 10 §10.1)', S101, 'variety=MAG; model in ALLaM-7B-Instruct-preview|Qwen3-8B-Base', "rd(pp([df.d_risk.iloc[0],df.d_risk_lo.iloc[0],df.d_risk_hi.iloc[0],df.d_risk.iloc[1],df.d_risk_lo.iloc[1],df.d_risk_hi.iloc[1]]),1)", [6.7, 3.1, 10.1, 3.5, 0.3, 7.0], 0.06, 'SOURCE CHANGE: v0.2 quoted the post-hoc bootstrap in CONFIRM_SUMMARY ([+3.3,+10.3]; [+0.2,+6.8]); v0.3 uses the frozen Addendum 10 run (S101, default_rng(0), B=2000)')
add('S4-09', '§3.1', 'Δrisk vs MSA, SYR: +9.3/+3.7/+3.1/+4.2 pp, all CIs exclude 0', 'realised risk(v) − risk(MSA)', 'dialect − MSA', 'answered items', 'pp', 'FIX', 'T2', 'Addendum 10 §10.1', S101, 'variety=SYR', "[rd(pp(pick(df,'d_risk')),1), cnt(df.d_risk_lo>0)]", [[9.3, 3.7, 3.1, 4.2], 4], 0.06)
add('S4-10', 'Abstract/§1/§3.1', 'risk higher than MSA (fixed-cal CI excludes 0): SYR 4/4, MAG 2/4 (ALLaM, Qwen3), EGY 2/4, KSA 1/4, UAE 1/4', 'count of cells with d_risk_lo>0', 'dialect − MSA', '4 models per dialect', 'count', 'FIX', 'T2', 'Addendum 10 §10.1', S101, DI, "[cnt(df[df.variety==v].higher_than_msa_fixed) for v in ['SYR','MAG','EGY','KSA','UAE']]", [4, 2, 2, 1, 1])
add('S4-11', '§1/§3.1', 'under double resampling: SYR 3/4 (Gemma drops), MAG 2/4', 'count of cells with d_risk_rs_lo>0', 'dialect − MSA', '4 models per dialect', 'count', 'RS', 'T2', 'Addendum 10 §10.1', S101, DI, "[cnt(df[df.variety=='SYR'].higher_than_msa_rs), cnt(df[df.variety=='MAG'].higher_than_msa_rs), list(df[(df.variety=='SYR')&(~df.higher_than_msa_rs)].model.str[:5])]", [3, 2, ['gemma']])
add('S4-12', '§3.1', 'point estimates above 0.20 in 18/20 dialect cells; Qwen3–KSA by 0.0003', 'realised risk vs 0.20', 'dialect vs ceiling', '20 cells', 'count; fraction', 'PT', 'T2', 'point estimates reported as such, separately from exceedance with confidence', S101, DI, "[cnt(df.exceeds_target_point), round(float(df[(df.model=='Qwen3-8B-Base')&(df.variety=='KSA')].risk.iloc[0]-0.20),4)]", [18, 0.0003], 0.00005)
add('S4-13', 'Abstract/§1/§3.1', 'exceeds 0.20 with confidence (fixed-cal lower bound >0.20): ALLaM’s five dialects only; range 0.24–0.31', 'realised risk interval vs 0.20', 'dialect vs ceiling', '20 cells', 'count; fraction', 'FIX', 'T2', 'Addendum 10 §10.1', S101, DI, "[cnt(df.exceeds_target_fixed), cnt(df[df.model=='ALLaM-7B-Instruct-preview'].exceeds_target_fixed), rng(df[df.model=='ALLaM-7B-Instruct-preview'],'risk',2)]", [5, 5, [0.24, 0.31]], 0.005)
add('S4-14', '§3.1', 'under double resampling only ALLaM–MAG and ALLaM–SYR exceed 0.20 with confidence', 'realised risk RS interval vs 0.20', 'dialect vs ceiling', '20 cells', 'count', 'RS', 'T2', 'Addendum 10 §10.1', S101, DI, "sorted(list(df[df.exceeds_target_rs].apply(lambda r: r.model[:5]+'-'+r.variety,axis=1)))", ['ALLaM-MAG', 'ALLaM-SYR'])
add('S4-15', '§3.1', 'MSA realised risk is itself above 0.20 for ALLaM (0.21) and at 0.20 for Qwen3 — point estimates', 'MSA realised risk', 'MSA vs ceiling', 'answered MSA items', 'fraction', 'PT', 'T1b', 'the calibration-set rule targets an empirical risk; the test realisation can be above the target', S4, 'target_risk=0.2; variety=MSA', "rd(pick(df,'realised_risk'),3)", [0.213, 0.191, 0.2, 0.176], 0.0006)

# ---------------- P1 (T1) ----------------
add('P1-01', '§3.1', 'MSA matched risk t50 per model', 'MSA risk at 50% coverage', '-', '710 most confident MSA test items', 'fraction', 'PT', 'T1', W_P1, P1, 'variety=MSA', "rd(pick(df,'msa_matched_risk'),3)", [0.203, 0.149, 0.156, 0.194], 0.0006)
add('P1-02', 'Abstract/§3.1', 'MAG answerable 0.26/0.29/0.23/0.32', 'answerable fraction at t50', 'dialect vs MSA (=0.50 by construction)', '1,420', 'fraction', 'PT', 'T1', W_P1, P1, 'variety=MAG', "rd(pick(df,'answerable'),2)", [0.26, 0.29, 0.23, 0.32], 0.005)
add('P1-03', '§3.1', 'MAG Δ −0.24 [−.31,−.17] / −0.20 [−.28,−.14] / −0.27 [−.32,−.21] / −0.18 [−.24,−.13]', 'answerable(v) − 0.50', 'dialect − MSA', '1,420', 'fraction', 'FIX', 'T1', W_P1, P1, 'variety=MAG', "rd([x for m in range(4) for x in (pick(df,'d_answerable')[m],pick(df,'d_lo')[m],pick(df,'d_hi')[m])],2)", [-0.24, -0.31, -0.17, -0.2, -0.28, -0.14, -0.27, -0.32, -0.21, -0.18, -0.24, -0.13], 0.005)
add('P1-04', 'Abstract/§3.1', 'MAG and SYR answerable on a quarter to a third (0.23–0.34)', 'answerable fraction', 'dialect vs MSA 0.50', '1,420', 'fraction', 'PT', 'T1', W_P1, P1, 'variety in MAG|SYR', "rng(df,'answerable',2)", [0.23, 0.34], 0.005)
add('P1-05', '§3.1', 'SYR answerable 0.31–0.34; Δ −0.17 to −0.19', 'answerable; Δ', 'dialect − MSA', '1,420', 'fraction', 'FIX', 'T1', W_P1, P1, 'variety=SYR', "[rng(df,'answerable',2), rng(df,'d_answerable',2)]", [[0.31, 0.34], [-0.19, -0.17]], 0.005)
add('P1-06', '§3.1', 'EGY 0.35–0.41 (Δ −0.10 to −0.15); KSA 0.37–0.44 (−0.06 to −0.13); UAE 0.42–0.44 (−0.07 to −0.08)', 'answerable; Δ', 'dialect − MSA', '1,420', 'fraction', 'FIX', 'T1', W_P1, P1, 'variety in EGY|KSA|UAE', "[rng(df[df.variety=='EGY'],'answerable',2), rng(df[df.variety=='EGY'],'d_answerable',2), rng(df[df.variety=='KSA'],'answerable',2), rng(df[df.variety=='KSA'],'d_answerable',2), rng(df[df.variety=='UAE'],'answerable',2), rng(df[df.variety=='UAE'],'d_answerable',2)]", [[0.35, 0.41], [-0.15, -0.1], [0.37, 0.44], [-0.13, -0.06], [0.42, 0.44], [-0.08, -0.07]], 0.005)
add('P1-07', '§3.1', 'all 20 P1 intervals exclude 0', 'Δ interval', 'dialect − MSA', '20 cells', 'count', 'FIX', 'T1', W_P1, P1, DI, "cnt(df.d_hi<0)", 20)

# ---------------- P2 (T1) ----------------
add('P2-01', 'Abstract/§3.1', 'coverage under MSA q̂ falls 8/11/13/8 pp (MAG) at α=0.30', 'cov(v) − cov(MSA) under q̂_MSA', 'dialect − MSA', '1,420', 'pp', 'FIX', 'T1', W_P2, P2, 'alpha=0.3; variety=MAG', "rd(pp(pick(df,'d_cov')),0)", [-8, -10, -13, -8], 0.5, 'v0.2 said 8/11/13/8; Fanar–MAG Δcov is −10.4 → −10 (v0.3 corrected)')
add('P2-02', '§3.1', 'coverage falls 6/8/6/9 pp (SYR); other dialects 3–5 pp', 'Δcov', 'dialect − MSA', '1,420', 'pp', 'FIX', 'T1', W_P2, P2, 'alpha=0.3; variety in EGY|KSA|SYR|UAE', "[rd(pp(pick(df[df.variety=='SYR'],'d_cov')),0), rng(df[df.variety!='SYR'].assign(p=100*df[df.variety!='SYR'].d_cov),'p',0)]", [[-6, -8, -6, -9], [-5, -3]], 0.5)
add('P2-03', 'Abstract/§3.1', 'MAG+SYR coverage loss range 6–13 pp', 'Δcov', 'dialect − MSA', '1,420', 'pp', 'FIX', 'T1', W_P2, P2, 'alpha=0.3; variety in MAG|SYR', "rng(df.assign(p=-100*df.d_cov),'p',0)", [6, 13], 0.5)
add('P2-04', 'Abstract/§3.1', 'own-q̂ set-size ratio MAG ×1.17/1.25/1.32/1.21; SYR ×1.18–1.23; Gulf ×1.08–1.17', 'mean set size(v, q̂_v) / mean set size(MSA, q̂_MSA)', 'dialect / MSA at same nominal target', '1,420', 'ratio', 'FIX', 'T1', W_P2, P2, 'alpha=0.3', "[rd(pick(df[df.variety=='MAG'],'size_ratio'),2), rng(df[df.variety=='SYR'],'size_ratio',2), rng(df[df.variety.isin(['KSA','UAE'])],'size_ratio',2)]", [[1.17, 1.25, 1.32, 1.21], [1.18, 1.23], [1.08, 1.17]], 0.005)
add('P2-05', 'Abstract', 'sets 17–32% larger (MAG and SYR, α=0.30)', 'size ratio − 1', 'dialect / MSA', '1,420', '%', 'FIX', 'T1', '"produced sets 17–32% larger at the same nominal target" (not "needs")', P2, 'alpha=0.3; variety in MAG|SYR', "rng(df.assign(p=100*(df.size_ratio-1)),'p',0)", [17, 32], 0.5)
add('P2-06', '§3.1/§3.4', 'size-ratio RS intervals 2.7–4.3× wider; all 20 still exclude 1', 'size ratio interval width ratio; lower bound', 'dialect / MSA', '20 cells', 'ratio; count', 'RS', 'T2', 'Addendum 9 §9.1', S91, DI, "[rng(df,'p2_szr_width_ratio',1), cnt(df.p2_szr_lo_rs>1)]", [[2.7, 4.3], 20], 0.05)
add('P2-07', '§3.1', 'Δcov RS intervals 20/20 exclude 0; widths 1.00–1.30×', 'Δcov RS', 'dialect − MSA', '20 cells', 'count; ratio', 'RS', 'T2', 'Addendum 9 §9.1', S91, DI, "[cnt(df.p2_dcov_hi_rs<0), rng(df,'p2_dcov_width_ratio',2)]", [20, [1.0, 1.3]], 0.01)
add('P2-08', '§3.1', 'at α=0.10 coverage differences are ≤1.7 pp and 19 of 20 intervals include 0', 'Δcov at α=0.10', 'dialect − MSA', '20 cells', 'count with CI excluding 0; max |Δcov| pp', 'FIX', 'T1', 'property of the operating range studied, not of every target', P2, f'alpha=0.1; {DI}', "[cnt(df.d_cov_hi<0), rd(pp(df.d_cov.abs().max()),1)]", [1, 1.7], 0.06, 'v0.2 said the α=0.10 intervals include 0: 19 of 20 do (one excludes 0); largest |Δcov| 1.7 pp — v0.3 wording corrected')
add('P2-09', '§3.1', 'own-threshold coverage ALLaM–MAG 0.657 (lowest), target 0.70', 'coverage under own q̂ (= Mondrian with true label)', 'dialect vs nominal target', '1,420', 'fraction', 'PT', 'T1', 'target not met empirically in every cell', P2, 'alpha=0.3; variety=MAG; model=ALLaM-7B-Instruct-preview', "rd(df.cov_ownthr.iloc[0],3)", 0.657, 0.0006)

# ---------------- S2 (T1) ----------------
add('S2-01', '§3.1', 'MAG coverage msa_only 0.61/0.59/0.57/0.62 → pooled 0.64/0.64/0.62/0.66 → text 0.63/0.66/0.66/0.68 → oracle 0.66/0.69/0.69/0.69 (α=0.30)', 'achieved coverage on MAG test items', 'method vs method, same keys', '1,420', 'fraction', 'PT', 'T1', 'what a known remedy buys and costs here; not a new method', S2, 'alpha=0.3; variety=MAG', "[rd(pick(df[df.method==m],'coverage'),2) for m in ['msa_only','pooled','text_router','oracle']]", [[0.61, 0.59, 0.57, 0.62], [0.64, 0.64, 0.62, 0.65], [0.63, 0.66, 0.66, 0.68], [0.66, 0.69, 0.69, 0.69]], 0.005, 'Gemma pooled 0.6549 → 0.65 (v0.2 said 0.66)')
add('S2-02', '§3.1', 'MAG mean set size 1.36/1.17/1.14/1.44 (msa_only) → 1.53/1.54/1.56/1.72 (oracle)', 'mean set size', 'method vs method', '1,420', 'options', 'PT', 'T1', '-', S2, 'alpha=0.3; variety=MAG', "[rd(pick(df[df.method=='msa_only'],'set_size'),2), rd(pick(df[df.method=='oracle'],'set_size'),2)]", [[1.36, 1.17, 1.14, 1.44], [1.53, 1.54, 1.56, 1.72]], 0.005)
add('S2-03', '§3.1', 'text classifier recovers 51/69/81/88% of the oracle gain (MAG)', '(cov_text − cov_msa)/(cov_oracle − cov_msa)', 'practical vs oracle', 'MAG test items', '%', 'PT', 'T1', 'recovering most of the gain is not matching the oracle', S2, 'alpha=0.3; variety=MAG', "rd(pp([(pick(df[df.method=='text_router'],'coverage')[i]-pick(df[df.method=='msa_only'],'coverage')[i])/(pick(df[df.method=='oracle'],'coverage')[i]-pick(df[df.method=='msa_only'],'coverage')[i]) for i in range(4)]),0)", [51, 69, 81, 88], 1.0)
add('S2-04', '§3.1', 'ALLaM–MAG stays below target with the true label (0.657)', 'oracle Mondrian coverage', 'vs nominal 0.70', '1,420', 'fraction', 'PT', 'T1', 'calibration-sample variability is a possible explanation, not an established one', S2, 'alpha=0.3; variety=MAG; model=ALLaM-7B-Instruct-preview; method=oracle', "rd(df.coverage.iloc[0],3)", 0.657, 0.0006)
add('S2-05', '§3.1', 'ALLaM–MAG own-threshold coverage resampling range 0.63–0.70 (exploratory)', 'calibration-resampling range', '-', 'calibration items', 'fraction', 'PT', 'T3', 'possible explanation only; nothing is built on it', CONF, '', '', [0.63, 0.7], 0, 'report-sourced: CONFIRM_SUMMARY.md P2 note ("Exploratory check (not pre-registered)")')

# ---------------- independent computational check (EXT) ----------------
add('IC-01', '§3.1/App. C', 'independent implementation reproduces P1 exactly; S4 (r*≤0.25) and P2 to one boundary item; per-key 39,759/39,760 (S4) and 39,755/39,760 (coverage); Fanar r*=0.30 τ 0.3757 vs 0.3790', 'max abs differences; per-key mismatches', 'frozen vs independent implementation', '4 × 9,940 per-key cells', 'items', 'PT', 'EXT', '"computational check by an independent implementation", never "audit"', IND, '', '', 'see INDEP_COMPARISON.md', 0, 'report-sourced; the independent implementation read docs/METRIC_DEFINITIONS.md and the raw score files only')

# ---------------- accuracy (T2, Addendum 7) ----------------
add('AC-01', '§3.1/§3.3', 'MSA accuracy 0.59/0.61/0.63/0.59', 'accuracy', 'MSA', '1,420', 'fraction', 'PT', 'T1', '-', D12, 'variety=MSA', "rd(pick(df,'acc'),2)", [0.59, 0.61, 0.63, 0.59], 0.005)
add('AC-02', '§3.3', 'MAG accuracy 0.49/0.53/0.52/0.50; SYR 0.53/0.53/0.58/0.50', 'accuracy', 'dialect', '1,420', 'fraction', 'PT', 'T1', 'lower in every cell', D12, 'variety in MAG|SYR', "[rd(pick(df[df.variety=='MAG'],'acc'),2), rd(pick(df[df.variety=='SYR'],'acc'),2)]", [[0.49, 0.53, 0.52, 0.5], [0.53, 0.53, 0.58, 0.5]], 0.005)
add('AC-03', '§3.3', 'dialect accuracy lower than MSA in every cell (20/20)', 'acc(v) < acc(MSA)', 'dialect − MSA', '20 cells', 'count', 'PT', 'T1', '-', D12, '', "cnt([df[(df.model==m)&(df.variety==v)].acc.iloc[0] < df[(df.model==m)&(df.variety=='MSA')].acc.iloc[0] for m in M for v in DIAL])", 20)

# ---------------- D4 (T2, Addendum 7) ----------------
add('D4-01', '§3.3', 'realised risk under τ_v: 0.16–0.24 over 20 cells (r*=0.20)', 'realised risk at the variety-selected threshold', 'dialect vs ceiling 0.20', 'answered dialect items', 'fraction', 'PT', 'T2', W_D4, D4, f'target_risk=0.2; {DI}', "rng(df,'realised_risk_v_thr',2)", [0.16, 0.24], 0.005)
add('D4-02', '§3.3', 'realised risk under τ_MSA: 0.17–0.31 over 20 cells', 'realised risk at the transferred threshold', 'dialect vs ceiling', 'answered items', 'fraction', 'PT', 'T2', W_D4, D4, f'target_risk=0.2; {DI}', "rng(df,'realised_risk_msa_thr',2)", [0.17, 0.31], 0.005)
add('D4-03', '§3.3', 'answered(τ_v) − answered(τ_MSA) negative with CI<0 in 17/20', '"recoverable" contrast', 'own threshold − transferred threshold', '20 cells', 'count', 'FIX', 'T2', 'per-dialect re-selection answers FEWER dialect questions here', D4, f'target_risk=0.2; {DI}', "cnt(df.rec_hi<0)", 17)
add('D4-04', '§3.3', 'residual gap −0.04 to −0.34; CI<0 in 19/20 (fixed)', 'answered_v(τ_v) − answered_MSA(τ_MSA)', 'dialect at own threshold − MSA at its threshold', '20 cells', 'fraction; count', 'FIX', 'T2', W_D4, D4, f'target_risk=0.2; {DI}', "[rng(df,'residual_gap',2), cnt(df.res_hi<0)]", [[-0.34, -0.01], 19], 0.005, 'v0.2 said −0.04 to −0.34; the smallest residual gap is Gemma–UAE −0.010 (v0.3 corrected)')
add('D4-05', '§3.3/§3.4', 'residual gap calibration-robust in 14/20 (not Fanar EGY/UAE, Qwen3 KSA/UAE, Gemma EGY/UAE); RS widths 2.2–4.5×', 'residual gap RS interval', 'dialect − MSA', '20 cells', 'count; ratio', 'RS', 'T2', 'not resolved for the Egyptian and Gulf varieties in three of four models', S91, DI, "[cnt(df.d4_res_hi_rs<0), sorted(list(df[df.d4_res_hi_rs>=0].apply(lambda r: r.model[:5]+'-'+r.variety,axis=1))), rng(df.assign(w=(df.d4_res_hi_rs-df.d4_res_lo_rs)/(df.d4_res_hi_orig-df.d4_res_lo_orig)),'w',1)]", [14, ['Fanar-EGY', 'Fanar-UAE', 'Qwen3-KSA', 'Qwen3-UAE', 'gemma-EGY', 'gemma-UAE'], [2.2, 4.5]], 0.05)
add('D4-06', '§3.3', 'cells with realised risk above 0.24 under τ_MSA: 4 (all ALLaM) → 0 under τ_v', 'count of cells above 0.24', 'transferred vs re-selected threshold', '20 cells', 'count', 'PT', 'T3', 'ceiling framing: cells above the ceiling brought under it', S94, '', "[cnt(df.risk_msa_thr>0.24), cnt(df[df.risk_msa_thr>0.24].model=='ALLaM-7B-Instruct-preview'), cnt(df.risk_v_thr>0.24)]", [4, 4, 0])
add('D4-07', '§3.3', 'cells with realised risk above 0.20 under τ_MSA vs under τ_v (ceiling framing; point estimates)', 'count of cells above 0.20', 'transferred vs re-selected', '20 cells', 'count', 'PT', 'T3', 'presentation change (review #12): count above the ceiling, not distance to it', S94, '', "[cnt(df.risk_msa_thr>0.20), cnt(df.risk_v_thr>0.20)]", [18, 7], 0, 'ceiling framing for v0.3: 18 of 20 dialect cells above 0.20 under τ_MSA (point estimates), 7 under τ_v')
add('D4-08', '§3.3', 'Qwen3–EGY: risk 0.22 → 0.17, answered 0.53 → 0.42', 'risk and answered under τ_MSA vs τ_v', 'transferred vs re-selected', 'Qwen3 EGY', 'fraction', 'PT', 'T2', 'where the transferred threshold was near target, re-selection mostly traded answers for small changes in risk', S94, 'model=Qwen3-8B-Base; variety=EGY', "rd([df.risk_msa_thr.iloc[0], df.risk_v_thr.iloc[0], df.answered_msa_thr.iloc[0], df.answered_v_thr.iloc[0]],2)", [0.22, 0.17, 0.53, 0.42], 0.005)
add('D4-09', '§3.3', 'post-hoc observed range of realised risk under τ_v: within ±0.04 of 0.20', 'max |risk_v − 0.20|', '-', '20 cells', 'fraction', 'PT', 'T3', 'observed range, not a tolerance or guarantee', S94, '', "rd((df.risk_v_thr-0.20).abs().max(),2)", 0.04, 0.005)
add('D4-10', '§3.3 (dropped in v0.3)', 'closer to 0.20 in 11/20 cells (distance framing; superseded by D4-06/07)', 'count closer', '-', '20', 'count', 'PT', 'T3', 'superseded: 0.20 is a ceiling', S94, '', "cnt(df.closer)", 11)

# ---------------- discrimination (T2, Addendum 7) ----------------
auroc_tbl = {'MAG': [-0.045, -0.072, -0.015, -0.040, -0.063, -0.014, -0.059, -0.087, -0.032, -0.029, -0.057, -0.001],
             'SYR': [-0.056, -0.084, -0.028, -0.038, -0.063, -0.012, -0.065, -0.091, -0.039, -0.036, -0.063, -0.009],
             'EGY': [-0.023, -0.050, 0.002, -0.037, -0.060, -0.015, -0.031, -0.055, -0.008, -0.020, -0.044, 0.005],
             'KSA': [-0.012, -0.037, 0.011, -0.033, -0.057, -0.010, -0.015, -0.037, 0.006, -0.027, -0.050, -0.004],
             'UAE': [0.002, -0.022, 0.026, -0.013, -0.035, 0.010, -0.014, -0.039, 0.009, -0.005, -0.028, 0.018]}
for v, vals in auroc_tbl.items():
    add(f'AU-01-{v}', '§3.3 table', f'ΔAUROC {v} with CIs (ALLaM/Fanar/Qwen3/Gemma)', 'AUROC(v) − AUROC(MSA), p_max as score', 'dialect − MSA, paired by key', '1,420', 'AUROC', 'FIX', 'T2', 'confidence score ranks correct above incorrect less well', D12, f'variety={v}', "rd([x for m in range(4) for x in (pick(df,'d_auroc')[m],pick(df,'d_auroc_lo')[m],pick(df,'d_auroc_hi')[m])],3)", vals, 0.0006)
add('AU-02', '§3.3', 'ΔAUROC CIs excluding 0: MAG 4/4, SYR 4/4, EGY 2/4, KSA 2/4, UAE 0/4', 'count d_auroc_hi<0', 'dialect − MSA', '4 per dialect', 'count', 'FIX', 'T2', '-', D12, DI, "[cnt(df[df.variety==v].d_auroc_hi<0) for v in ['MAG','SYR','EGY','KSA','UAE']]", [4, 4, 2, 2, 0])
add('AU-03', 'Abstract/§1', 'ΔAUROC −0.03 to −0.07 for MAG and SYR in all four models', 'ΔAUROC range', 'dialect − MSA', '8 cells', 'AUROC', 'FIX', 'T2', '-', D12, 'variety in MAG|SYR', "[rng(df,'d_auroc',2), cnt(df.d_auroc_hi<0)]", [[-0.06, -0.03], 8], 0.005, 'v0.2 said −0.03 to −0.07; the minimum is −0.065 → −0.06 at two decimals (v0.3 corrected)')
add('AU-04', '§3.3', 'MSA AUROC 0.77–0.80', 'AUROC', 'MSA', '1,420', 'AUROC', 'PT', 'T2', '-', D12, 'variety=MSA', "rng(df,'auroc',2)", [0.77, 0.8], 0.005)
add('AU-05', '§3.3', 'AUGRC worse than MSA in all 20 cells (CI excludes 0)', 'ΔAUGRC', 'dialect − MSA', '20 cells', 'count', 'FIX', 'T2', 'AUGRC combines accuracy and ranking (Traub et al. 2024)', D12, DI, "cnt(df.d_augrc_lo>0)", 20)

# ---------------- validity layers ----------------
add('L1-01', '§3.2', 'IFM filter changes every endpoint by at most 1.5 pp (1.45, ALLaM–SYR ΔP1) in all 20 cells', 'max |kept − full| over Δacc, ΔP1, Δcov, Δanswered', 'filtered vs full sample', '20 cells', 'pp', 'PT', 'T2', 'Addendum 4 L1', L1, '', "rd(pp(max((df.kept_dacc-df.dacc).abs().max(), (df.kept_dp1-df.dp1).abs().max(), (df.kept_dcov-df.dcov).abs().max(), (df.kept_dans-df.dans).abs().max())),2)", 1.45, 0.006, 'CORRECTION: VALIDITY_SUMMARY/v0.2 said ≤1.1 pp; the largest change is 1.45 pp (ALLaM–SYR ΔP1 −18.7 → −17.2); v0.3 says "at most 1.5 points"')
add('L2-01', '§3.2', 'most-similar tercile retains ≥2/3 of the full-sample ΔP1 for MAG, SYR, EGY in 3/4 models; KSA/UAE in ≤1/4', 'ΔP1(high tercile)/ΔP1(full)', 'tercile vs full sample', '≈473 keys per tercile', 'ratio', 'PT', 'T2', 'descriptive: similarity also tracks dialectal distance and item difficulty', L2, 'tercile=high', "[cnt([ (df[(df.model==m)&(df.dialect==v)].dp1.iloc[0]/pd.read_csv('results/confirm/P1_selective.csv').set_index(['model','variety']).loc[(m,v),'d_answerable'])>=2/3 for m in M]) for v in ['MAG','SYR','EGY','KSA','UAE']]", [3, 3, 3, 1, 1])
add('L4-01', '§3.2', 'AraDiCE: accuracy drops 3.6–7.0 pp', 'acc(v) − acc(MSA)', 'variety − MSA (AraDiCE)', '1,400', 'pp', 'FIX', 'T2', 'replication for EGY/LEV only; not for MAG', L4, '', "rng(df.assign(p=-100*df.dacc),'p',1)", [3.6, 7.0], 0.06)
add('L4-02', '§3.2', 'AraDiCE ΔP1: EGY −11 to −17 pp; LEV −6 to −14 pp', 'ΔP1', 'variety − MSA', '1,400', 'pp', 'FIX', 'T2', '-', L4, '', "[rng(df[df.variety=='EGY'].assign(p=pp(df[df.variety=='EGY'].dp1)),'p',0), rng(df[df.variety=='LEV'].assign(p=pp(df[df.variety=='LEV'].dp1)),'p',0)]", [[-17, -11], [-14, -6]], 0.5)
add('L4-03', '§3.2', 'AraDiCE Δcov under MSA q̂: −3 to −7 pp; set size ×1.02–1.28', 'Δcov; size ratio', 'variety − MSA', '1,400', 'pp; ratio', 'FIX/PT', 'T2', '-', L4, '', "[rng(df.assign(p=pp(df.dcov)),'p',0), rng(df,'size_ratio',2)]", [[-7, -3], [1.02, 1.28]], 0.5)
add('L4-04', '§3.2', 'AraDiCE: all intervals (Δacc, ΔP1, Δcov, Δanswered) exclude 0', 'upper bounds <0', '-', '8 cells × 4', 'count', 'FIX', 'T2', '-', L4, '', "cnt(df.dacc_hi<0)+cnt(df.dp1_hi<0)+cnt(df.dcov_hi<0)+cnt(df.dans_hi<0)", 32)
for k, (claim, val) in {'AUD-01': ('400 pairs = 80 keys × 5 dialects; 150 double-rated', '400/80/150'),
                        'AUD-02': ('basic defect rate 0.37 [0.31, 0.44]; UAE 0.44, EGY 0.33', '0.37 [0.31,0.44]'),
                        'AUD-03': ('invalidating the gold answer 0.08 overall (MAG 0.16); hint/ambiguity 0.34', '0.08; 0.16; 0.34'),
                        'AUD-04': ('κ: 0.86 meaning, 0.36 answer validity, 0.90 clarity (within-model consistency)', '0.86/0.36/0.90'),
                        'AUD-05': ('1,600 pair×model observations; Δacc −4.5 (unflagged) vs −6.2 (flagged); difference −1.8 [−8.6, +4.6]; answer change 26.9% vs 27.7%', '−1.8 [−8.6,+4.6]'),
                        'AUD-06': ('after excluding flagged pairs (80 keys) operational answered fraction −6 to −20 pp; MAG per-model ΔP1 CIs ≈ ±40 pp', '−6.7…−20.2'),
                        'AUD-07': ('resource documentation reports ≈5% error from a 32-item/dialect check', '5%')}.items():
    add(k, '§3.2 / App. E', claim, 'model-assisted screen (GPT-6 sessions)', 'flagged vs unflagged; rates under the screen’s criteria', '400 pairs / 80 keys', 'fraction', 'KC', 'T2' if k != 'AUD-07' else 'EXT', 'rates under that screen’s criteria, not an established estimate of the resource’s error rate', AUD, '', '', val, 0, 'report-sourced: AUDIT_RESULTS.md §1–§4')

# ---------------- robustness (T2, Addendum 8) ----------------
add('RB-01', '§3.4', 're-scoring the original order reproduces the confirmatory prediction in 98–99% of cells; 0.9–2.0% differ', 'share of cells with a different prediction', 're-run vs confirmatory', '500 × 7 cells per model', '%', 'PT', 'T2', '"observed choice differences of 0.9–2.0% in the specified re-scoring"; cause not isolated', S92, '', "rng(df.assign(p=pp(df.share_disagree)),'p',1)", [0.9, 2.0], 0.06)
add('RB-02', '§3.4', 'median top-two margin among disagreeing cells ≤0.13 nats vs 0.5–1.75 overall; 43–52% of them below 0.05 nats', 'log-prob margin', 'disagreeing vs all cells', 'per model', 'nats; %', 'PT', 'T2', 'disagreements sit at near-ties', S92, '', "[rd(df.margin_median_disagree.max(),2), rng(df,'margin_median_all',2), rng(df.assign(p=pp(df.share_margin_lt005_disagree)),'p',0)]", [0.13, [0.5, 1.75], [43, 52]], 0.5)
add('RB-03', '§3.4', 'gap estimates from the two runs differ by ≤0.03 (Δacc, ΔP1, S4 Δanswered)', 'max |confirm − rerun|', 'two scoring runs', '500 keys', 'fraction', 'PT', 'T2', '-', S92, '', "rd(max((df.d_acc_confirm-df.d_acc_rerun).abs().max(), (df.d_p1_confirm-df.d_p1_rerun).abs().max(), (df.s4_d_ans_confirm-df.s4_d_ans_rerun).abs().max()),2)", 0.03, 0.005)
add('RB-04', '§3.4', 'Δacc and ΔP1 order-robust (sign in all 4 orderings; averaged CI excludes 0) in 20/20 cells each', 'verdict counts', 'dialect − MSA, averaged over 4 rotations', '500 keys × 4 orders', 'count', 'FIX', 'T2', 'balances option positions; does not test all 24 permutations', R2, DI, "[cnt(df.d_acc_verdict=='order-robust'), cnt(df.d_p1_verdict=='order-robust')]", [20, 20])
add('RB-05', '§3.4', 'order-averaged ΔP1 (ALLaM/Fanar/Qwen3/Gemma): MAG −0.21/−0.22/−0.25/−0.24; SYR −0.19/−0.20/−0.20/−0.25', 'ΔP1 averaged over orderings', 'dialect − MSA', '500 × 4', 'fraction', 'FIX', 'T2', 'STANDARD model order (v0.2 used ALLaM/Qwen3/Fanar/Gemma — corrected in v0.3)', R2, 'variety in MAG|SYR', "[rd(pick(df[df.variety=='MAG'],'d_p1_avg'),2), rd(pick(df[df.variety=='SYR'],'d_p1_avg'),2)]", [[-0.21, -0.22, -0.25, -0.24], [-0.19, -0.2, -0.19, -0.25]], 0.005, 'Qwen3–SYR −0.1945 → −0.19')
add('RB-06', '§3.4', 'order-averaged ΔP1 ranges: EGY −0.13 to −0.15; KSA −0.10 to −0.15; UAE −0.08 to −0.13', 'ΔP1 averaged', 'dialect − MSA', '500 × 4', 'fraction', 'FIX', 'T2', '-', R2, 'variety in EGY|KSA|UAE', "[rng(df[df.variety=='EGY'],'d_p1_avg',2), rng(df[df.variety=='KSA'],'d_p1_avg',2), rng(df[df.variety=='UAE'],'d_p1_avg',2)]", [[-0.15, -0.13], [-0.15, -0.1], [-0.13, -0.08]], 0.005)
add('RB-07', '§3.4', 'S4 Δanswered at the original τ_MSA, order-averaged, excludes 0 in 20/20', 'S4 Δanswered averaged over orderings', 'dialect − MSA', '500 × 4', 'count', 'FIX', 'T2', '-', R3, DI, "cnt(df.d_ans_hi<0)", 20)
add('RB-08', '§3.4', 'order-averaged S4 Δanswered calibration-robust in 19/20 (ALLaM–UAE borderline)', 'RS interval', 'dialect − MSA', '20 cells', 'count', 'RS', 'T2', 'Addendum 9 §9.1b', S91R, DI, "[cnt(df.hi_rs<0), list(df[df.hi_rs>=0].apply(lambda r: r.model[:5]+'-'+r.variety,axis=1))]", [19, ['ALLaM-UAE']])
add('RB-09', '§3.4', 'OSR MSA 0.43/0.45/0.45/0.58; MAG 0.51/0.61/0.57/0.72; SYR 0.52/0.58/0.52/0.70 (ALLaM/Fanar/Qwen3/Gemma)', 'order-sensitivity rate', 'variety', '500 keys', 'fraction', 'PT', 'T2', 'STANDARD model order (v0.2 listed ALLaM/Qwen3/Fanar/Gemma — corrected in v0.3); secondary correlational observation', R1, 'variety in MSA|MAG|SYR', "[rd(pick(df[df.variety=='MSA'],'osr'),2), rd(pick(df[df.variety=='MAG'],'osr'),2), rd(pick(df[df.variety=='SYR'],'osr'),2)]", [[0.43, 0.45, 0.45, 0.58], [0.51, 0.61, 0.57, 0.72], [0.52, 0.58, 0.52, 0.7]], 0.005)
add('RB-10', '§3.4', 'ΔOSR vs MSA excludes 0: MAG, SYR, EGY 4/4; KSA 3/4; UAE 1/4; ENG lower than MSA in 4/4', 'ΔOSR interval', 'variety − MSA', '4 per variety', 'count', 'FIX', 'T2', '-', R1, '', "[cnt(df[df.variety==v].d_osr_lo>0) for v in ['MAG','SYR','EGY','KSA','UAE']]+[cnt(df[df.variety=='ENG'].d_osr<0)]", [4, 4, 4, 3, 1, 4])
add('RB-11', 'App. D', 'P3 answer change vs MSA 20–34% (dialects, test); within-variety one-rotation change 24–48%; MSA alone 27–38%', 'answer-change rates', 'dialect vs MSA; k0 vs k1', '1,420 / 500', '%', 'PT', 'W', 'the CLAIM is withdrawn; the negative result is documented: answer change alone does not identify a dialect-specific instability', P3, DI, "rng(df.assign(p=pp(df.answer_change)),'p',0)", [20, 34], 0.5)
add('RB-12', 'App. D', 'within-variety one-rotation change 24–48%; MSA 27–38%', 'floor k0 vs k1', 'same question, same variety', '500', '%', 'PT', 'W', '-', R4, '', "[rng(df[df.variety.isin(DIAL)].assign(p=pp(df[df.variety.isin(DIAL)].floor_k0_vs_k1)),'p',0), rng(df[df.variety=='MSA'].assign(p=pp(df[df.variety=='MSA'].floor_k0_vs_k1)),'p',0)]", [[24, 48], [27, 38]], 0.5)
add('RB-13', 'App. D', 'paired D = (dialect-vs-MSA change) − (within-variety rotation change): CI<0 in 15/20, includes 0 in 5, >0 in 0', 'D interval', 'paired by key', '20 cells', 'count', 'FIX', 'T2', 'no positive difference reached significance (does not show that none could)', S93, DI, "[cnt(df.D_hi<0), cnt((df.D_lo<0)&(df.D_hi>0)), cnt(df.D_lo>0)]", [15, 5, 0])
add('RB-14', 'App. D', 'against MSA’s own rotation change (D′) larger only for ALLaM MAG +0.06 [+0.01,+0.11] and SYR +0.05 [+0.00,+0.10]', 'D′ interval', 'dialect change − MSA rotation change', '20 cells', 'count; fraction', 'FIX', 'T2', '-', S93, DI, "[sorted(list(df[df.Dp_lo>0].apply(lambda r: r.model[:5]+'-'+r.variety,axis=1))), rd([df[(df.model=='ALLaM-7B-Instruct-preview')&(df.variety=='MAG')].mean_Dprime.iloc[0], df[(df.model=='ALLaM-7B-Instruct-preview')&(df.variety=='SYR')].mean_Dprime.iloc[0]],2)]", [['ALLaM-MAG', 'ALLaM-SYR'], [0.06, 0.05]], 0.005)
add('RB-15', '§3.4', 'G1 agreement with letter-logit choice: ALLaM 97–100%, Fanar 94–97%, Qwen3 94–96%, Gemma 90–97%; unextractable ≤0.8%', 'agreement; unextractable', 'generated vs logit, same prompt', '500 per variety', '%', 'PT', 'T2', 'near-tautological for base models; does not characterise free-form dialectal behaviour', R5, 'cond=G1', "[rng(df[df.model==m].assign(p=pp(df[df.model==m].agreement)),'p',0) for m in M]+[rd(pp(df.unextractable.max()),1)]", [[97, 100], [94, 97], [94, 96], [90, 97], 0.8], 0.5)
add('RB-16', '§3.4', 'G1 generated accuracy within 0.012 of letter-logit accuracy in every cell', 'max |gen_acc − logit_acc|', 'generated vs logit', '28 cells', 'fraction', 'PT', 'T2', '-', R5, 'cond=G1', "rd((df.gen_acc-df.logit_acc).abs().max(),3)", 0.014, 0.0006, 'v0.2 said 0.012 (Gemma only); across all cells the maximum is 0.014 (v0.3 corrected)')
add('RB-17', '§3.4', 'G2 (ALLaM chat template): unextractable ≤0.4%; generated = first-token argmax 99–100%; agreement with raw-prompt choice 82–92%; generated accuracy 0.53–0.66', 'G2 statistics', 'chat-template generation vs raw-prompt logits', '500 per variety', '%; fraction', 'PT', 'T2', 'usage-validity check, not a decoding isolation', R5, 'cond=G2', "[rd(pp(df.unextractable.max()),1), rng(df.assign(p=pp(df.gen_vs_chat_logit)),'p',0), rng(df.assign(p=pp(df.agreement)),'p',0), rng(df,'gen_acc',2)]", [0.4, [99, 100], [82, 92], [0.53, 0.66]], 0.5)
add('RB-18', '§3.4', 'on items accepted by τ_MSA the generated letter equals the logit choice in 27/28 cells; exception Fanar–ENG −0.003 [−0.008, +0.000]', 'selective risk gen − logit on accepted items', 'generated vs logit, accepted set', '500-key subset', 'fraction', 'FIX', 'T2', 'Addendum 10 §10.2: S4 statements hold for the generated answers on this prompt', S102, '', "[cnt(df['diff']==0), list(df[df['diff']!=0].apply(lambda r: r.model[:5]+'-'+r.variety,axis=1)), rd([df[df['diff']!=0]['diff'].iloc[0], df[df['diff']!=0].diff_lo.iloc[0], df[df['diff']!=0].diff_hi.iloc[0]],3)]", [27, ['Fanar-ENG'], [-0.003, -0.008, 0.0]], 0.0006)
add('RB-19', '§3.4', 'S4 and Δcov RS interval widths 0.95–1.4× the fixed-calibration widths', 'width ratio', 'RS vs FIX', '20 cells', 'ratio', 'RS', 'T2', '-', S91, DI, "rng(pd.concat([df.s4_width_ratio, df.p2_dcov_width_ratio]).to_frame('w'),'w',2)", [0.95, 1.42], 0.01)

rows.sort(key=lambda r: r['id'])
os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
with open(os.path.join(ROOT, 'docs', 'CLAIMS_LEDGER.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f'{len(rows)} ledger rows written')
