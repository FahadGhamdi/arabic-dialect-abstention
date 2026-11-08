# Stage B — variety-aware conformal calibration under the correct protocol (all models)

Grouped 3-way split per seed (router-train / calibration / test, 150/175/175 question keys); routers trained on router-train only; thresholds per PREDICTED group on calibration; evaluated per TRUE variety on test. Original scoring-run scores. Same calibration budget for every method.

## ALLaM-7B-Instruct-preview (layer 31; 30 splits)

Router accuracy on test (7-way): internal 0.590 ± 0.039; text 0.636 ± 0.020

- internal router: per-variety recall MSA 0.65, EGY 0.52, KSA 0.42, MAG 0.77, SYR 0.48, UAE 0.32, ENG 0.97; main confusions: MSA→UAE 0.16, KSA→UAE 0.18, SYR→UAE 0.16, UAE→MSA 0.18, UAE→KSA 0.20, UAE→SYR 0.16
- text router: per-variety recall MSA 0.72, EGY 0.52, KSA 0.44, MAG 0.79, SYR 0.71, UAE 0.27, ENG 1.00; main confusions: EGY→SYR 0.17, KSA→MSA 0.20, UAE→MSA 0.28, UAE→SYR 0.18

### α=0.2 (target coverage 0.80); mean over splits (split SD in brackets)

| method | MSA | UAE | EGY | KSA | SYR | MAG | ENG | worst dialect | mean size (dialects) | size MAG |
|---|---|---|---|---|---|---|---|---|---|---|
| msa_only | 0.808 [0.038] | 0.810 [0.036] | 0.807 [0.042] | 0.803 [0.034] | 0.793 [0.045] | 0.808 [0.042] | 0.852 [0.026] | 0.780 | 2.09 | 2.24 |
| pooled | 0.797 [0.038] | 0.801 [0.037] | 0.794 [0.041] | 0.787 [0.034] | 0.777 [0.045] | 0.793 [0.040] | 0.842 [0.029] | 0.765 | 2.03 | 2.17 |
| oracle | 0.808 [0.038] | 0.794 [0.045] | 0.802 [0.049] | 0.804 [0.031] | 0.801 [0.049] | 0.796 [0.052] | 0.805 [0.032] | 0.761 | 2.07 | 2.18 |
| text_router | 0.800 [0.040] | 0.811 [0.042] | 0.811 [0.048] | 0.789 [0.038] | 0.798 [0.040] | 0.782 [0.053] | 0.819 [0.037] | 0.762 | 2.06 | 2.11 |
| internal_router | 0.801 [0.037] | 0.811 [0.035] | 0.807 [0.042] | 0.795 [0.036] | 0.794 [0.038] | 0.796 [0.046] | 0.808 [0.035] | 0.770 | 2.07 | 2.19 |
| plausible_set | 0.803 [0.036] | 0.816 [0.035] | 0.808 [0.042] | 0.799 [0.036] | 0.800 [0.037] | 0.797 [0.046] | 0.808 [0.035] | 0.775 | 2.09 | 2.20 |

Paired differences vs msa_only over splits (mean, ±1.96·SE): pooled: ΔMAG -0.015 (±0.005), Δworst -0.016 (±0.004); oracle: ΔMAG -0.012 (±0.010), Δworst -0.020 (±0.008); text_router: ΔMAG -0.026 (±0.011), Δworst -0.018 (±0.008); internal_router: ΔMAG -0.012 (±0.008), Δworst -0.010 (±0.007); plausible_set: ΔMAG -0.010 (±0.008), Δworst -0.005 (±0.007)

### α=0.3 (target coverage 0.70); mean over splits (split SD in brackets)

| method | MSA | UAE | EGY | KSA | SYR | MAG | ENG | worst dialect | mean size (dialects) | size MAG |
|---|---|---|---|---|---|---|---|---|---|---|
| msa_only | 0.710 [0.048] | 0.715 [0.050] | 0.690 [0.062] | 0.677 [0.052] | 0.683 [0.054] | 0.671 [0.062] | 0.765 [0.042] | 0.658 | 1.57 | 1.64 |
| pooled | 0.709 [0.037] | 0.710 [0.037] | 0.688 [0.048] | 0.674 [0.039] | 0.685 [0.046] | 0.669 [0.048] | 0.761 [0.032] | 0.656 | 1.55 | 1.62 |
| oracle | 0.710 [0.048] | 0.698 [0.048] | 0.707 [0.043] | 0.709 [0.042] | 0.699 [0.057] | 0.691 [0.055] | 0.711 [0.042] | 0.659 | 1.62 | 1.72 |
| text_router | 0.712 [0.047] | 0.723 [0.046] | 0.708 [0.054] | 0.690 [0.037] | 0.706 [0.039] | 0.662 [0.051] | 0.719 [0.043] | 0.655 | 1.61 | 1.61 |
| internal_router | 0.704 [0.054] | 0.713 [0.040] | 0.706 [0.054] | 0.679 [0.052] | 0.694 [0.052] | 0.691 [0.048] | 0.710 [0.041] | 0.661 | 1.62 | 1.72 |
| plausible_set | 0.709 [0.051] | 0.719 [0.040] | 0.712 [0.052] | 0.688 [0.048] | 0.699 [0.051] | 0.694 [0.048] | 0.711 [0.041] | 0.670 | 1.64 | 1.73 |

Paired differences vs msa_only over splits (mean, ±1.96·SE): pooled: ΔMAG -0.002 (±0.010), Δworst -0.002 (±0.009); oracle: ΔMAG +0.020 (±0.014), Δworst +0.001 (±0.012); text_router: ΔMAG -0.009 (±0.012), Δworst -0.003 (±0.011); internal_router: ΔMAG +0.020 (±0.013), Δworst +0.003 (±0.012); plausible_set: ΔMAG +0.022 (±0.014), Δworst +0.012 (±0.012)


## Fanar-1-9B (layer 40; 10 splits)

Router accuracy on test (7-way): internal 0.571 ± 0.013; text 0.628 ± 0.015

- internal router: per-variety recall MSA 0.66, EGY 0.49, KSA 0.41, MAG 0.72, SYR 0.43, UAE 0.32, ENG 0.98; main confusions: MSA→UAE 0.18, EGY→UAE 0.16, KSA→UAE 0.17, SYR→EGY 0.16, SYR→UAE 0.16, UAE→MSA 0.20, UAE→EGY 0.18, UAE→KSA 0.16
- text router: per-variety recall MSA 0.72, EGY 0.52, KSA 0.41, MAG 0.80, SYR 0.68, UAE 0.27, ENG 1.00; main confusions: EGY→SYR 0.16, KSA→MSA 0.22, UAE→MSA 0.29, UAE→SYR 0.18

### α=0.2 (target coverage 0.80); mean over splits (split SD in brackets)

| method | MSA | UAE | EGY | KSA | SYR | MAG | ENG | worst dialect | mean size (dialects) | size MAG |
|---|---|---|---|---|---|---|---|---|---|---|
| msa_only | 0.811 [0.045] | 0.786 [0.048] | 0.766 [0.056] | 0.772 [0.058] | 0.771 [0.059] | 0.773 [0.061] | 0.861 [0.031] | 0.749 | 1.91 | 2.03 |
| pooled | 0.815 [0.025] | 0.805 [0.034] | 0.781 [0.033] | 0.791 [0.031] | 0.785 [0.029] | 0.807 [0.034] | 0.866 [0.025] | 0.772 | 1.99 | 2.14 |
| oracle | 0.811 [0.045] | 0.801 [0.037] | 0.811 [0.038] | 0.803 [0.037] | 0.809 [0.027] | 0.819 [0.028] | 0.795 [0.047] | 0.781 | 2.07 | 2.21 |
| text_router | 0.795 [0.028] | 0.810 [0.033] | 0.799 [0.043] | 0.796 [0.034] | 0.796 [0.031] | 0.827 [0.029] | 0.807 [0.045] | 0.776 | 2.06 | 2.25 |
| internal_router | 0.815 [0.041] | 0.819 [0.022] | 0.801 [0.046] | 0.797 [0.037] | 0.797 [0.033] | 0.825 [0.042] | 0.800 [0.046] | 0.766 | 2.07 | 2.24 |
| plausible_set | 0.818 [0.043] | 0.824 [0.021] | 0.805 [0.045] | 0.803 [0.035] | 0.803 [0.031] | 0.828 [0.041] | 0.800 [0.046] | 0.773 | 2.10 | 2.25 |

Paired differences vs msa_only over splits (mean, ±1.96·SE): pooled: ΔMAG +0.035 (±0.022), Δworst +0.023 (±0.022); oracle: ΔMAG +0.047 (±0.029), Δworst +0.032 (±0.020); text_router: ΔMAG +0.054 (±0.033), Δworst +0.027 (±0.022); internal_router: ΔMAG +0.053 (±0.033), Δworst +0.017 (±0.024); plausible_set: ΔMAG +0.055 (±0.033), Δworst +0.024 (±0.025)

### α=0.3 (target coverage 0.70); mean over splits (split SD in brackets)

| method | MSA | UAE | EGY | KSA | SYR | MAG | ENG | worst dialect | mean size (dialects) | size MAG |
|---|---|---|---|---|---|---|---|---|---|---|
| msa_only | 0.692 [0.060] | 0.681 [0.061] | 0.653 [0.049] | 0.634 [0.062] | 0.626 [0.065] | 0.604 [0.061] | 0.795 [0.041] | 0.603 | 1.37 | 1.38 |
| pooled | 0.723 [0.039] | 0.702 [0.049] | 0.681 [0.042] | 0.661 [0.047] | 0.658 [0.049] | 0.643 [0.047] | 0.815 [0.038] | 0.641 | 1.49 | 1.52 |
| oracle | 0.692 [0.060] | 0.692 [0.058] | 0.702 [0.049] | 0.703 [0.049] | 0.709 [0.051] | 0.699 [0.024] | 0.686 [0.059] | 0.666 | 1.62 | 1.72 |
| text_router | 0.702 [0.051] | 0.706 [0.044] | 0.693 [0.052] | 0.694 [0.041] | 0.699 [0.049] | 0.702 [0.043] | 0.690 [0.061] | 0.669 | 1.60 | 1.74 |
| internal_router | 0.712 [0.060] | 0.722 [0.043] | 0.694 [0.054] | 0.699 [0.046] | 0.693 [0.042] | 0.709 [0.052] | 0.688 [0.059] | 0.645 | 1.64 | 1.74 |
| plausible_set | 0.718 [0.057] | 0.733 [0.039] | 0.700 [0.052] | 0.707 [0.043] | 0.705 [0.037] | 0.714 [0.052] | 0.689 [0.058] | 0.658 | 1.67 | 1.76 |

Paired differences vs msa_only over splits (mean, ±1.96·SE): pooled: ΔMAG +0.039 (±0.016), Δworst +0.038 (±0.017); oracle: ΔMAG +0.095 (±0.032), Δworst +0.063 (±0.018); text_router: ΔMAG +0.098 (±0.032), Δworst +0.066 (±0.023); internal_router: ΔMAG +0.105 (±0.048), Δworst +0.042 (±0.031); plausible_set: ΔMAG +0.110 (±0.049), Δworst +0.055 (±0.032)


## Qwen3-8B-Base (layer 34; 10 splits)

Router accuracy on test (7-way): internal 0.524 ± 0.034; text 0.628 ± 0.015

- internal router: per-variety recall MSA 0.60, EGY 0.47, KSA 0.40, MAG 0.59, SYR 0.39, UAE 0.22, ENG 1.00; main confusions: KSA→EGY 0.19, SYR→EGY 0.18, SYR→KSA 0.17, SYR→MAG 0.15, UAE→MSA 0.16, UAE→EGY 0.21, UAE→KSA 0.16
- text router: per-variety recall MSA 0.72, EGY 0.52, KSA 0.41, MAG 0.80, SYR 0.68, UAE 0.27, ENG 1.00; main confusions: EGY→SYR 0.16, KSA→MSA 0.22, UAE→MSA 0.29, UAE→SYR 0.18

### α=0.2 (target coverage 0.80); mean over splits (split SD in brackets)

| method | MSA | UAE | EGY | KSA | SYR | MAG | ENG | worst dialect | mean size (dialects) | size MAG |
|---|---|---|---|---|---|---|---|---|---|---|
| msa_only | 0.787 [0.065] | 0.754 [0.058] | 0.750 [0.068] | 0.747 [0.053] | 0.745 [0.046] | 0.693 [0.068] | 0.861 [0.036] | 0.693 | 1.73 | 1.81 |
| pooled | 0.811 [0.050] | 0.776 [0.045] | 0.774 [0.057] | 0.765 [0.045] | 0.767 [0.042] | 0.731 [0.046] | 0.872 [0.027] | 0.730 | 1.84 | 1.95 |
| oracle | 0.787 [0.065] | 0.770 [0.068] | 0.786 [0.048] | 0.788 [0.046] | 0.801 [0.039] | 0.782 [0.041] | 0.786 [0.045] | 0.743 | 1.95 | 2.21 |
| text_router | 0.794 [0.060] | 0.773 [0.048] | 0.783 [0.054] | 0.759 [0.057] | 0.796 [0.051] | 0.783 [0.043] | 0.785 [0.043] | 0.745 | 1.93 | 2.20 |
| internal_router | 0.798 [0.048] | 0.790 [0.049] | 0.778 [0.050] | 0.789 [0.040] | 0.795 [0.040] | 0.781 [0.045] | 0.785 [0.044] | 0.756 | 1.95 | 2.19 |
| plausible_set | 0.802 [0.051] | 0.796 [0.047] | 0.788 [0.047] | 0.796 [0.043] | 0.802 [0.041] | 0.787 [0.042] | 0.786 [0.045] | 0.765 | 1.99 | 2.22 |

Paired differences vs msa_only over splits (mean, ±1.96·SE): pooled: ΔMAG +0.038 (±0.015), Δworst +0.037 (±0.016); oracle: ΔMAG +0.089 (±0.034), Δworst +0.050 (±0.018); text_router: ΔMAG +0.091 (±0.036), Δworst +0.052 (±0.021); internal_router: ΔMAG +0.088 (±0.027), Δworst +0.063 (±0.023); plausible_set: ΔMAG +0.094 (±0.027), Δworst +0.072 (±0.023)

### α=0.3 (target coverage 0.70); mean over splits (split SD in brackets)

| method | MSA | UAE | EGY | KSA | SYR | MAG | ENG | worst dialect | mean size (dialects) | size MAG |
|---|---|---|---|---|---|---|---|---|---|---|
| msa_only | 0.682 [0.058] | 0.671 [0.065] | 0.633 [0.061] | 0.645 [0.062] | 0.641 [0.054] | 0.537 [0.064] | 0.789 [0.027] | 0.537 | 1.25 | 1.20 |
| pooled | 0.711 [0.061] | 0.690 [0.061] | 0.661 [0.056] | 0.667 [0.058] | 0.667 [0.045] | 0.574 [0.067] | 0.802 [0.031] | 0.574 | 1.35 | 1.33 |
| oracle | 0.682 [0.058] | 0.683 [0.069] | 0.695 [0.062] | 0.678 [0.061] | 0.698 [0.042] | 0.679 [0.050] | 0.703 [0.056] | 0.651 | 1.49 | 1.74 |
| text_router | 0.683 [0.081] | 0.694 [0.056] | 0.674 [0.060] | 0.672 [0.065] | 0.700 [0.050] | 0.670 [0.052] | 0.702 [0.055] | 0.651 | 1.48 | 1.69 |
| internal_router | 0.689 [0.064] | 0.696 [0.065] | 0.674 [0.067] | 0.696 [0.055] | 0.690 [0.056] | 0.655 [0.066] | 0.701 [0.056] | 0.642 | 1.48 | 1.65 |
| plausible_set | 0.698 [0.057] | 0.706 [0.060] | 0.686 [0.065] | 0.707 [0.053] | 0.699 [0.052] | 0.663 [0.065] | 0.702 [0.057] | 0.653 | 1.52 | 1.68 |

Paired differences vs msa_only over splits (mean, ±1.96·SE): pooled: ΔMAG +0.038 (±0.019), Δworst +0.038 (±0.019); oracle: ΔMAG +0.143 (±0.032), Δworst +0.115 (±0.021); text_router: ΔMAG +0.134 (±0.033), Δworst +0.115 (±0.024); internal_router: ΔMAG +0.118 (±0.028), Δworst +0.106 (±0.023); plausible_set: ΔMAG +0.126 (±0.028), Δworst +0.117 (±0.025)


## Reading

A method is useful only if it raises worst-dialect / MAG coverage toward target by more than the split noise, at equal calibration budget, without inflating set size, and the internal router must beat the text router (which costs no model access). Oracle Mondrian uses true labels and is a reference, not a guaranteed ceiling.

## Verdict (2026-11-04 20:15 local, all three models, correct protocol)

1. **Variety-aware calibration is needed and effective where the gap is large.** With the MSA threshold at α=0.30, MAG coverage is 0.604 (Fanar) and 0.537 (Qwen3) against a 0.70 target (ALLaM 0.671). Calibrating per variety restores it: oracle Mondrian +9.5 / +14.3 pp (MAG), +6.3 / +11.5 pp (worst dialect), all far outside split noise. Pooled calibration recovers only ≈ +4 pp. The price is the set size predicted by Stage A (MAG 1.38→1.72 Fanar; 1.20→1.74 Qwen3).
2. **A label-free router recovers almost all of the oracle gain — but the cheap text router does it as well as the internal one.** Text char-n-gram router: +9.8 / +13.4 pp MAG at α=0.30 (Fanar / Qwen3), within ≈1 pp of oracle. Internal hidden-state router: +10.5 / +11.8 pp. Router accuracies: text 0.63 for all models; internal 0.57 (Fanar), 0.52 (Qwen3), 0.59 (ALLaM). Predicted-group calibration works despite ~60% 7-way accuracy because confusions are between varieties with similar thresholds (MSA↔UAE/KSA, SYR↔EGY) while MAG recall is 0.72–0.80.
3. **The internal (representation-based) router is therefore not a contribution**: it is less accurate than a text router that needs no model access, and gives no coverage or set-size advantage. "Plausible-set conservative" routing gives the best worst-dialect coverage (e.g. Qwen3 α=0.2: 0.765 vs oracle 0.743) at +0.02–0.04 set size — a modest, legitimate variant, not a headline.
4. On ALLaM (small gaps) all methods are within ±2 pp; with 30 splits the internal router and oracle both show +2.0 pp on MAG at α=0.30 (±1.3–1.4) — real but small.

Decision for the paper (wording revised after external review #4): keep (a) the equal-reliability cost measurement (Stage A), (b) the demonstration that per-variety calibration — with true labels, or with the simple text classifier we tested — SUBSTANTIALLY NARROWS the coverage gap where it is large (to ≈ target on Fanar, to 0.67–0.68 on Qwen3 even with true labels; nothing to recover on ALLaM) at the set-size cost measured in Stage A, and (c) the internal router as a controlled comparison: no consistent practical advantage over the text router that would justify its cost (where its coverage is higher, e.g. ALLaM 0.691 vs 0.662, its sets are larger, 1.72 vs 1.61). Drop "self-routed from internal representations" from the title and claims.

Caveats (from review #4): the intervals above are split-repetition variability on the same 500 keys, not generalisation uncertainty — that is what the pre-registered held-out test (ANALYSIS_PLAN.md) is for; "equal budget" means equal question keys, not equal numbers of scored items or labels (MSA-only: 175 items; pooled: 175×7; Mondrian/routers: 175 per variety + router training data); the 7 variants of a key are not independent, so standard split-conformal guarantees apply to per-variety calibration with true labels, while pooled/routed results are empirical (predicted-group-conditional coverage is not a per-true-variety guarantee; see Dunn et al. on hierarchical exchangeability).
