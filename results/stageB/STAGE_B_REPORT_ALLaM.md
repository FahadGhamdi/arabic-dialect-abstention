# Stage B — routers under the correct protocol (ALLaM-7B, layer 31, 10 grouped 3-way splits: 150 router-train / 175 calibration / 175 test keys)

Thresholds computed on the calibration split per PREDICTED group; scores are the original scoring-run scores (no lens). Same calibration budget for all methods; routers see only the router-train split.

## Router accuracy on test (7-way)

| router   |   mean |   std |
|:---------|-------:|------:|
| internal |  0.591 | 0.036 |
| text     |  0.628 | 0.016 |

## α=0.2: coverage per TRUE variety (target 0.80; mean over splits, split SD ≈ 0.040)

| method          |   EGY |   ENG |   KSA |   MAG |   MSA |   SYR |   UAE |
|:----------------|------:|------:|------:|------:|------:|------:|------:|
| msa_only        | 0.789 | 0.841 | 0.784 | 0.786 | 0.793 | 0.778 | 0.803 |
| pooled          | 0.775 | 0.831 | 0.77  | 0.766 | 0.783 | 0.761 | 0.793 |
| oracle          | 0.79  | 0.799 | 0.789 | 0.763 | 0.793 | 0.788 | 0.78  |
| text_router     | 0.795 | 0.807 | 0.769 | 0.763 | 0.791 | 0.78  | 0.797 |
| internal_router | 0.793 | 0.799 | 0.775 | 0.768 | 0.789 | 0.786 | 0.805 |
| plausible_set   | 0.794 | 0.799 | 0.78  | 0.771 | 0.79  | 0.791 | 0.808 |

Set size per true variety (α=0.2)

| method          |   EGY |   ENG |   KSA |   MAG |   MSA |   SYR |   UAE |
|:----------------|------:|------:|------:|------:|------:|------:|------:|
| msa_only        |  2.03 |  1.79 |  2.01 |  2.2  |  1.96 |  2.04 |  2.01 |
| pooled          |  1.96 |  1.74 |  1.94 |  2.11 |  1.89 |  1.97 |  1.95 |
| oracle          |  2.03 |  1.6  |  2    |  2.09 |  1.96 |  2.08 |  1.89 |
| text_router     |  2.04 |  1.63 |  1.93 |  2.07 |  1.94 |  2.03 |  2.01 |
| internal_router |  2.05 |  1.6  |  1.95 |  2.12 |  1.94 |  2.06 |  2    |
| plausible_set   |  2.06 |  1.6  |  1.98 |  2.13 |  1.95 |  2.09 |  2.03 |

Worst-dialect coverage and mean |coverage−target| over the 5 dialects (α=0.2)

| method          |   worst |   mad |
|:----------------|--------:|------:|
| msa_only        |   0.764 | 0.037 |
| pooled          |   0.745 | 0.038 |
| oracle          |   0.741 | 0.038 |
| text_router     |   0.747 | 0.035 |
| internal_router |   0.753 | 0.034 |
| plausible_set   |   0.759 | 0.031 |

## α=0.3: coverage per TRUE variety (target 0.70; mean over splits, split SD ≈ 0.048)

| method          |   EGY |   ENG |   KSA |   MAG |   MSA |   SYR |   UAE |
|:----------------|------:|------:|------:|------:|------:|------:|------:|
| msa_only        | 0.669 | 0.751 | 0.659 | 0.646 | 0.699 | 0.665 | 0.705 |
| pooled          | 0.671 | 0.749 | 0.661 | 0.651 | 0.7   | 0.67  | 0.705 |
| oracle          | 0.694 | 0.71  | 0.69  | 0.667 | 0.699 | 0.692 | 0.684 |
| text_router     | 0.695 | 0.714 | 0.675 | 0.649 | 0.706 | 0.695 | 0.715 |
| internal_router | 0.694 | 0.7   | 0.651 | 0.673 | 0.692 | 0.679 | 0.702 |
| plausible_set   | 0.699 | 0.702 | 0.662 | 0.674 | 0.698 | 0.686 | 0.709 |

Set size per true variety (α=0.3)

| method          |   EGY |   ENG |   KSA |   MAG |   MSA |   SYR |   UAE |
|:----------------|------:|------:|------:|------:|------:|------:|------:|
| msa_only        |  1.49 |  1.42 |  1.51 |  1.58 |  1.49 |  1.52 |  1.53 |
| pooled          |  1.48 |  1.43 |  1.5  |  1.59 |  1.49 |  1.54 |  1.54 |
| oracle          |  1.56 |  1.24 |  1.62 |  1.67 |  1.49 |  1.65 |  1.46 |
| text_router     |  1.56 |  1.26 |  1.56 |  1.6  |  1.51 |  1.64 |  1.58 |
| internal_router |  1.6  |  1.21 |  1.5  |  1.68 |  1.49 |  1.61 |  1.56 |
| plausible_set   |  1.62 |  1.22 |  1.53 |  1.69 |  1.51 |  1.64 |  1.58 |

Worst-dialect coverage and mean |coverage−target| over the 5 dialects (α=0.3)

| method          |   worst |   mad |
|:----------------|--------:|------:|
| msa_only        |   0.641 | 0.054 |
| pooled          |   0.639 | 0.041 |
| oracle          |   0.65  | 0.039 |
| text_router     |   0.647 | 0.038 |
| internal_router |   0.638 | 0.042 |
| plausible_set   |   0.65  | 0.039 |

## Internal-router confusion (rows = true, cols = predicted; summed over splits)

|     |   MSA |   EGY |   KSA |   MAG |   SYR |   UAE |   ENG |
|:----|------:|------:|------:|------:|------:|------:|------:|
| MSA |  1184 |    12 |   198 |    97 |    71 |   180 |     8 |
| EGY |   109 |   902 |   222 |   150 |   199 |   163 |     5 |
| KSA |   227 |   110 |   764 |   155 |   274 |   213 |     7 |
| MAG |    57 |    33 |   107 |  1360 |   129 |    59 |     5 |
| SYR |   103 |   134 |   290 |   185 |   825 |   208 |     5 |
| UAE |   284 |   183 |   340 |   159 |   295 |   482 |     7 |
| ENG |     0 |     0 |     8 |     6 |     3 |    10 |  1723 |

## Reading
- Under the correct protocol, no variety-aware method separates from the others or from the MSA-only threshold beyond split-to-split noise (≈3pp) on ALLaM; ALLaM's own gaps are small (MSA-only MAG −5pp at α=.30).
- The internal probe (0.59) does NOT beat a same-budget char n-gram text router (0.63); its confusions are MSA↔Gulf and SYR↔EGY/KSA. The earlier 'self-routed' table (lens scores, true-label calibration) overstated the method.
- Verdict for ALLaM: the router adds nothing demonstrable at this scale. The informative test is Fanar/Qwen3 (coverage gaps 10–13pp), which needs their hidden states (queued, batch 2). Stage A3 already shows ~50 own-dialect items restore coverage, so the practical fix is cheap with labels.
