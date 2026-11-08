# Final verification package (Addendum 9)

Double resampling B1=1000 (default_rng(1)); key bootstrap B2=2000 (default_rng(0)). Every new interval is shown NEXT TO the original fixed-calibration interval; nothing replaces a pre-registered estimate.


## ALLaM-7B-Instruct-preview: test 1420, calibration 808

### 9.1 Calibration sensitivity (r*=0.2, α=0.3); τ_MSA across resamples: median 0.786 [0.707,0.883]; q̂_MSA median 0.752 [0.709,0.784]

| variety | S4 Δanswered: original [CI] → double-resampled [CI] (width ratio) | realised risk @τ: orig → resampled [CI] | D4 residual gap: orig [CI] → resampled [CI] | D4 realised risk @τ_v resampled [CI] | P2 Δcov: orig [CI] → resampled [CI] | P2 size ratio: orig [CI] → resampled [CI] | verdict |
|---|---|---|---|---|---|---|---|
| EGY | -0.039 [-0.063,-0.015] → -0.031 [-0.061,-0.004] (×1.21) | 0.248 → 0.256 [0.179,0.320] | -0.120 [-0.144,-0.096] → -0.123 [-0.218,-0.029] | 0.199 [0.132,0.262] | -0.037 [-0.058,-0.015] → -0.036 [-0.061,-0.013] (×1.13) | 1.107 [1.082,1.133] → 1.117 [1.045,1.197] (×2.99) | S4 robust; D4 robust; Δcov robust; size robust |
| KSA | -0.054 [-0.076,-0.030] → -0.047 [-0.072,-0.021] (×1.09) | 0.238 → 0.246 [0.184,0.309] | -0.146 [-0.170,-0.123] → -0.138 [-0.231,-0.051] | 0.197 [0.130,0.259] | -0.047 [-0.068,-0.027] → -0.045 [-0.066,-0.023] (×1.07) | 1.116 [1.093,1.141] → 1.139 [1.033,1.242] (×4.30) | S4 robust; D4 robust; Δcov robust; size robust |
| MAG | -0.113 [-0.140,-0.087] → -0.109 [-0.142,-0.075] (×1.28) | 0.280 → 0.288 [0.212,0.357] | -0.280 [-0.306,-0.254] → -0.269 [-0.358,-0.175] | 0.202 [0.144,0.257] | -0.075 [-0.098,-0.051] → -0.075 [-0.103,-0.047] (×1.20) | 1.170 [1.139,1.199] → 1.188 [1.100,1.294] (×3.26) | S4 robust; D4 robust; Δcov robust; size robust |
| SYR | -0.053 [-0.080,-0.026] → -0.050 [-0.088,-0.011] (×1.42) | 0.306 → 0.311 [0.228,0.372] | -0.162 [-0.189,-0.136] → -0.176 [-0.284,-0.082] | 0.233 [0.148,0.296] | -0.063 [-0.087,-0.039] → -0.064 [-0.089,-0.039] (×1.03) | 1.204 [1.173,1.235] → 1.204 [1.110,1.303] (×3.12) | S4 robust; D4 robust; Δcov robust; size robust |
| UAE | -0.014 [-0.037,+0.009] → -0.014 [-0.044,+0.014] (×1.24) | 0.258 → 0.255 [0.176,0.312] | -0.139 [-0.163,-0.116] → -0.138 [-0.227,-0.051] | 0.179 [0.114,0.256] | -0.043 [-0.063,-0.023] → -0.046 [-0.066,-0.025] (×1.02) | 1.076 [1.052,1.102] → 1.081 [1.002,1.173] (×3.44) | S4 sensitive; D4 robust; Δcov robust; size robust |
| ENG | +0.067 [+0.041,+0.094] → +0.074 [+0.045,+0.101] (×1.05) | 0.182 → 0.187 [0.124,0.238] | +0.140 [+0.113,+0.166] → +0.149 [+0.052,+0.256] | 0.227 [0.180,0.280] | +0.045 [+0.022,+0.069] → +0.043 [+0.021,+0.068] (×1.00) | 0.861 [0.840,0.881] → 0.862 [0.789,0.935] (×3.54) | S4 robust; D4 robust; Δcov robust; size robust |

### 9.1b Rotation subset (500 keys): S4 Δanswered order-averaged — original (τ fixed) [CI] → double-resampled [CI]

| variety | original | double-resampled | verdict |
|---|---|---|---|
| EGY | -0.039 [-0.068,-0.012] | -0.034 [-0.064,-0.005] | robust |
| KSA | -0.066 [-0.092,-0.038] | -0.058 [-0.086,-0.030] | robust |
| MAG | -0.099 [-0.131,-0.067] | -0.095 [-0.127,-0.063] | robust |
| SYR | -0.045 [-0.076,-0.015] | -0.049 [-0.085,-0.013] | robust |
| UAE | -0.027 [-0.053,-0.001] | -0.025 [-0.059,+0.007] | sensitive |
| ENG | +0.093 [+0.064,+0.125] | +0.093 [+0.063,+0.126] | robust |

### 9.2 Re-run reproducibility (subset 500×7 cells): different prediction in 0.857%; top-2 margin median all 1.750 nats vs disagreeing 0.125; share margin<0.05: all 0.027 vs disagreeing 0.433; max |Δ(gap estimate)| across Δacc/ΔP1/S4 and dialects = 0.016

| variety | Δacc confirm → rerun | ΔP1 confirm → rerun | S4 Δanswered confirm → rerun |
|---|---|---|---|
| EGY | -0.036 → -0.034 | -0.102 → -0.100 | -0.016 → -0.012 |
| KSA | -0.068 → -0.066 | -0.104 → -0.100 | -0.070 → -0.064 |
| MAG | -0.110 → -0.108 | -0.178 → -0.184 | -0.102 → -0.100 |
| SYR | -0.082 → -0.078 | -0.180 → -0.188 | -0.030 → -0.022 |
| UAE | -0.070 → -0.072 | -0.086 → -0.080 | -0.038 → -0.028 |
| ENG | +0.024 → +0.024 | +0.144 → +0.156 | +0.072 → +0.088 |

### 9.3 R4 paired comparison: D = [dialect≠MSA at k=0] − [same variety k=0≠k=1]; D′ uses MSA's own rotation change

| variety | P3 (dialect vs MSA) | within-variety rotation change | mean D [CI] | mean D′ [CI] | reading |
|---|---|---|---|---|---|
| EGY | 0.246 | 0.262 | -0.016 [-0.060,+0.030] | -0.020 [-0.062,+0.024] | not larger than one-rotation change |
| KSA | 0.228 | 0.304 | -0.076 [-0.124,-0.028] | -0.038 [-0.084,+0.008] | not larger than one-rotation change |
| MAG | 0.324 | 0.312 | +0.012 [-0.038,+0.060] | +0.058 [+0.008,+0.106] | not larger than one-rotation change |
| SYR | 0.314 | 0.286 | +0.028 [-0.020,+0.076] | +0.048 [+0.002,+0.098] | not larger than one-rotation change |
| UAE | 0.234 | 0.240 | -0.006 [-0.052,+0.040] | -0.032 [-0.078,+0.012] | not larger than one-rotation change |
| ENG | 0.264 | 0.246 | +0.018 [-0.030,+0.066] | -0.002 [-0.048,+0.044] | not larger than one-rotation change |

### 9.4 D4 distance to target (post hoc): closer in 5/5 cells; cells with risk>0.24 under τ_MSA 4 → under τ_v 0; mean distance 0.066 → 0.016

| variety | risk @τ_MSA → @τ_v | distance → | closer | answered @τ_MSA → @τ_v |
|---|---|---|---|---|
| EGY | 0.248 → 0.199 | 0.048 → 0.001 | yes | 0.477 → 0.396 |
| KSA | 0.238 → 0.187 | 0.038 → 0.013 | yes | 0.462 → 0.369 |
| MAG | 0.280 → 0.195 | 0.080 → 0.005 | yes | 0.403 → 0.235 |
| SYR | 0.306 → 0.237 | 0.106 → 0.037 | yes | 0.463 → 0.354 |
| UAE | 0.258 → 0.176 | 0.058 → 0.024 | yes | 0.501 → 0.376 |

## Fanar-1-9B: test 1420, calibration 808

### 9.1 Calibration sensitivity (r*=0.2, α=0.3); τ_MSA across resamples: median 0.499 [0.446,0.568]; q̂_MSA median 0.708 [0.688,0.722]

| variety | S4 Δanswered: original [CI] → double-resampled [CI] (width ratio) | realised risk @τ: orig → resampled [CI] | D4 residual gap: orig [CI] → resampled [CI] | D4 realised risk @τ_v resampled [CI] | P2 Δcov: orig [CI] → resampled [CI] | P2 size ratio: orig [CI] → resampled [CI] | verdict |
|---|---|---|---|---|---|---|---|
| EGY | -0.083 [-0.106,-0.061] → -0.078 [-0.101,-0.056] (×1.00) | 0.208 → 0.208 [0.153,0.268] | -0.039 [-0.061,-0.017] → -0.038 [-0.118,+0.044] | 0.229 [0.179,0.281] | -0.034 [-0.054,-0.015] → -0.035 [-0.055,-0.013] (×1.07) | 1.132 [1.107,1.158] → 1.135 [1.058,1.220] (×3.19) | S4 robust; D4 sensitive; Δcov robust; size robust |
| KSA | -0.073 [-0.096,-0.051] → -0.070 [-0.092,-0.050] (×0.95) | 0.217 → 0.213 [0.150,0.276] | -0.101 [-0.123,-0.080] → -0.092 [-0.175,-0.022] | 0.202 [0.147,0.252] | -0.054 [-0.075,-0.035] → -0.053 [-0.073,-0.032] (×1.00) | 1.163 [1.137,1.191] → 1.174 [1.102,1.264] (×2.97) | S4 robust; D4 robust; Δcov robust; size robust |
| MAG | -0.153 [-0.177,-0.130] → -0.148 [-0.175,-0.120] (×1.15) | 0.208 → 0.211 [0.154,0.272] | -0.192 [-0.217,-0.167] → -0.197 [-0.290,-0.108] | 0.182 [0.125,0.236] | -0.105 [-0.127,-0.081] → -0.104 [-0.130,-0.071] (×1.27) | 1.253 [1.224,1.284] → 1.264 [1.158,1.385] (×3.75) | S4 robust; D4 robust; Δcov robust; size robust |
| SYR | -0.125 [-0.150,-0.101] → -0.119 [-0.144,-0.092] (×1.07) | 0.228 → 0.229 [0.156,0.298] | -0.198 [-0.222,-0.174] → -0.179 [-0.269,-0.088] | 0.186 [0.132,0.257] | -0.080 [-0.101,-0.059] → -0.082 [-0.107,-0.057] (×1.18) | 1.180 [1.152,1.207] → 1.195 [1.101,1.307] (×3.76) | S4 robust; D4 robust; Δcov robust; size robust |
| UAE | -0.052 [-0.073,-0.031] → -0.047 [-0.069,-0.024] (×1.07) | 0.205 → 0.204 [0.137,0.266] | -0.059 [-0.080,-0.039] → -0.064 [-0.140,+0.013] | 0.197 [0.137,0.250] | -0.033 [-0.051,-0.014] → -0.032 [-0.052,-0.011] (×1.13) | 1.124 [1.099,1.151] → 1.130 [1.064,1.214] (×2.87) | S4 robust; D4 sensitive; Δcov robust; size robust |
| ENG | +0.152 [+0.127,+0.177] → +0.154 [+0.114,+0.192] (×1.55) | 0.159 → 0.156 [0.116,0.195] | +0.315 [+0.291,+0.340] → +0.319 [+0.221,+0.420] | 0.235 [0.197,0.277] | +0.066 [+0.045,+0.087] → +0.069 [+0.046,+0.093] (×1.12) | 0.748 [0.727,0.769] → 0.758 [0.696,0.824] (×3.01) | S4 robust; D4 robust; Δcov robust; size robust |

### 9.1b Rotation subset (500 keys): S4 Δanswered order-averaged — original (τ fixed) [CI] → double-resampled [CI]

| variety | original | double-resampled | verdict |
|---|---|---|---|
| EGY | -0.074 [-0.098,-0.051] | -0.078 [-0.104,-0.052] | robust |
| KSA | -0.069 [-0.091,-0.046] | -0.068 [-0.091,-0.045] | robust |
| MAG | -0.164 [-0.194,-0.133] | -0.164 [-0.195,-0.133] | robust |
| SYR | -0.119 [-0.146,-0.091] | -0.119 [-0.145,-0.089] | robust |
| UAE | -0.054 [-0.077,-0.030] | -0.053 [-0.078,-0.030] | robust |
| ENG | +0.178 [+0.150,+0.206] | +0.178 [+0.144,+0.211] | robust |

### 9.2 Re-run reproducibility (subset 500×7 cells): different prediction in 1.343%; top-2 margin median all 0.749 nats vs disagreeing 0.002; share margin<0.05: all 0.074 vs disagreeing 0.511; max |Δ(gap estimate)| across Δacc/ΔP1/S4 and dialects = 0.030

| variety | Δacc confirm → rerun | ΔP1 confirm → rerun | S4 Δanswered confirm → rerun |
|---|---|---|---|
| EGY | -0.050 → -0.062 | -0.138 → -0.162 | -0.074 → -0.068 |
| KSA | -0.012 → -0.018 | -0.082 → -0.112 | -0.070 → -0.062 |
| MAG | -0.104 → -0.112 | -0.194 → -0.222 | -0.164 → -0.160 |
| SYR | -0.086 → -0.096 | -0.160 → -0.168 | -0.120 → -0.120 |
| UAE | -0.038 → -0.044 | -0.076 → -0.080 | -0.048 → -0.046 |
| ENG | +0.120 → +0.112 | +0.268 → +0.252 | +0.188 → +0.188 |

### 9.3 R4 paired comparison: D = [dialect≠MSA at k=0] − [same variety k=0≠k=1]; D′ uses MSA's own rotation change

| variety | P3 (dialect vs MSA) | within-variety rotation change | mean D [CI] | mean D′ [CI] | reading |
|---|---|---|---|---|---|
| EGY | 0.252 | 0.356 | -0.104 [-0.150,-0.056] | -0.032 [-0.084,+0.020] | not larger than one-rotation change |
| KSA | 0.210 | 0.352 | -0.142 [-0.188,-0.096] | -0.074 [-0.122,-0.026] | not larger than one-rotation change |
| MAG | 0.306 | 0.392 | -0.086 [-0.140,-0.038] | +0.022 [-0.034,+0.072] | not larger than one-rotation change |
| SYR | 0.286 | 0.388 | -0.102 [-0.158,-0.048] | +0.002 [-0.048,+0.054] | not larger than one-rotation change |
| UAE | 0.256 | 0.316 | -0.060 [-0.108,-0.012] | -0.028 [-0.078,+0.020] | not larger than one-rotation change |
| ENG | 0.286 | 0.192 | +0.094 [+0.046,+0.140] | +0.002 [-0.044,+0.050] | larger than one-rotation change |

### 9.4 D4 distance to target (post hoc): closer in 3/5 cells; cells with risk>0.24 under τ_MSA 0 → under τ_v 0; mean distance 0.013 → 0.014

| variety | risk @τ_MSA → @τ_v | distance → | closer | answered @τ_MSA → @τ_v |
|---|---|---|---|---|
| EGY | 0.208 → 0.231 | 0.008 → 0.031 | no | 0.475 → 0.519 |
| KSA | 0.217 → 0.202 | 0.017 → 0.002 | yes | 0.485 → 0.457 |
| MAG | 0.208 → 0.188 | 0.008 → 0.012 | no | 0.406 → 0.366 |
| SYR | 0.228 → 0.174 | 0.028 → 0.026 | yes | 0.432 → 0.360 |
| UAE | 0.205 → 0.202 | 0.005 → 0.002 | yes | 0.506 → 0.499 |

## Qwen3-8B-Base: test 1420, calibration 808

### 9.1 Calibration sensitivity (r*=0.2, α=0.3); τ_MSA across resamples: median 0.523 [0.469,0.597]; q̂_MSA median 0.693 [0.666,0.710]

| variety | S4 Δanswered: original [CI] → double-resampled [CI] (width ratio) | realised risk @τ: orig → resampled [CI] | D4 residual gap: orig [CI] → resampled [CI] | D4 realised risk @τ_v resampled [CI] | P2 Δcov: orig [CI] → resampled [CI] | P2 size ratio: orig [CI] → resampled [CI] | verdict |
|---|---|---|---|---|---|---|---|
| EGY | -0.060 [-0.084,-0.037] → -0.058 [-0.086,-0.032] (×1.15) | 0.219 → 0.217 [0.153,0.278] | -0.170 [-0.194,-0.146] → -0.155 [-0.254,-0.066] | 0.173 [0.127,0.229] | -0.037 [-0.058,-0.017] → -0.038 [-0.061,-0.018] (×1.07) | 1.183 [1.153,1.213] → 1.179 [1.098,1.258] (×2.71) | S4 robust; D4 robust; Δcov robust; size robust |
| KSA | -0.067 [-0.089,-0.044] → -0.063 [-0.089,-0.039] (×1.13) | 0.200 → 0.203 [0.143,0.272] | -0.075 [-0.098,-0.054] → -0.075 [-0.154,+0.012] | 0.194 [0.140,0.248] | -0.030 [-0.049,-0.011] → -0.029 [-0.051,-0.008] (×1.11) | 1.171 [1.145,1.200] → 1.164 [1.090,1.241] (×2.76) | S4 robust; D4 sensitive; Δcov robust; size robust |
| MAG | -0.208 [-0.235,-0.182] → -0.204 [-0.232,-0.173] (×1.12) | 0.236 → 0.235 [0.181,0.293] | -0.340 [-0.368,-0.314] → -0.306 [-0.424,-0.177] | 0.184 [0.092,0.259] | -0.130 [-0.155,-0.106] → -0.132 [-0.162,-0.104] (×1.20) | 1.321 [1.289,1.356] → 1.329 [1.227,1.456] (×3.40) | S4 robust; D4 robust; Δcov robust; size robust |
| SYR | -0.122 [-0.147,-0.096] → -0.119 [-0.146,-0.094] (×1.03) | 0.231 → 0.232 [0.173,0.288] | -0.196 [-0.223,-0.169] → -0.176 [-0.275,-0.076] | 0.205 [0.156,0.260] | -0.064 [-0.088,-0.042] → -0.066 [-0.097,-0.037] (×1.30) | 1.222 [1.192,1.253] → 1.228 [1.135,1.339] (×3.35) | S4 robust; D4 robust; Δcov robust; size robust |
| UAE | -0.055 [-0.077,-0.032] → -0.055 [-0.078,-0.030] (×1.06) | 0.208 → 0.203 [0.147,0.255] | -0.087 [-0.109,-0.064] → -0.075 [-0.168,+0.024] | 0.194 [0.155,0.239] | -0.032 [-0.051,-0.014] → -0.032 [-0.052,-0.012] (×1.08) | 1.120 [1.094,1.146] → 1.122 [1.044,1.202] (×3.02) | S4 robust; D4 sensitive; Δcov robust; size robust |
| ENG | +0.159 [+0.133,+0.185] → +0.161 [+0.121,+0.205] (×1.61) | 0.119 → 0.120 [0.084,0.159] | +0.387 [+0.362,+0.412] → +0.383 [+0.280,+0.486] | 0.214 [0.181,0.242] | +0.114 [+0.092,+0.137] → +0.113 [+0.089,+0.137] (×1.08) | 0.706 [0.685,0.728] → 0.703 [0.645,0.772] (×2.92) | S4 robust; D4 robust; Δcov robust; size robust |

### 9.1b Rotation subset (500 keys): S4 Δanswered order-averaged — original (τ fixed) [CI] → double-resampled [CI]

| variety | original | double-resampled | verdict |
|---|---|---|---|
| EGY | -0.058 [-0.084,-0.034] | -0.056 [-0.084,-0.029] | robust |
| KSA | -0.053 [-0.080,-0.027] | -0.054 [-0.083,-0.028] | robust |
| MAG | -0.193 [-0.226,-0.161] | -0.194 [-0.229,-0.160] | robust |
| SYR | -0.106 [-0.137,-0.076] | -0.107 [-0.138,-0.077] | robust |
| UAE | -0.044 [-0.070,-0.016] | -0.045 [-0.072,-0.018] | robust |
| ENG | +0.176 [+0.140,+0.208] | +0.173 [+0.122,+0.220] | robust |

### 9.2 Re-run reproducibility (subset 500×7 cells): different prediction in 1.371%; top-2 margin median all 0.750 nats vs disagreeing 0.000; share margin<0.05: all 0.061 vs disagreeing 0.521; max |Δ(gap estimate)| across Δacc/ΔP1/S4 and dialects = 0.030

| variety | Δacc confirm → rerun | ΔP1 confirm → rerun | S4 Δanswered confirm → rerun |
|---|---|---|---|
| EGY | -0.032 → -0.038 | -0.196 → -0.166 | -0.068 → -0.060 |
| KSA | -0.032 → -0.036 | -0.072 → -0.050 | -0.048 → -0.048 |
| MAG | -0.134 → -0.134 | -0.262 → -0.254 | -0.212 → -0.204 |
| SYR | -0.064 → -0.068 | -0.184 → -0.192 | -0.114 → -0.102 |
| UAE | -0.038 → -0.044 | -0.064 → -0.052 | -0.046 → -0.040 |
| ENG | +0.140 → +0.138 | +0.354 → +0.366 | +0.170 → +0.172 |

### 9.3 R4 paired comparison: D = [dialect≠MSA at k=0] − [same variety k=0≠k=1]; D′ uses MSA's own rotation change

| variety | P3 (dialect vs MSA) | within-variety rotation change | mean D [CI] | mean D′ [CI] | reading |
|---|---|---|---|---|---|
| EGY | 0.198 | 0.306 | -0.108 [-0.156,-0.060] | -0.090 [-0.142,-0.038] | not larger than one-rotation change |
| KSA | 0.208 | 0.290 | -0.082 [-0.132,-0.032] | -0.080 [-0.132,-0.030] | not larger than one-rotation change |
| MAG | 0.290 | 0.368 | -0.078 [-0.130,-0.024] | +0.002 [-0.054,+0.056] | not larger than one-rotation change |
| SYR | 0.288 | 0.322 | -0.034 [-0.086,+0.018] | +0.000 [-0.050,+0.052] | not larger than one-rotation change |
| UAE | 0.214 | 0.312 | -0.098 [-0.150,-0.048] | -0.074 [-0.124,-0.024] | not larger than one-rotation change |
| ENG | 0.282 | 0.134 | +0.148 [+0.100,+0.196] | -0.006 [-0.054,+0.042] | larger than one-rotation change |

### 9.4 D4 distance to target (post hoc): closer in 2/5 cells; cells with risk>0.24 under τ_MSA 0 → under τ_v 0; mean distance 0.019 → 0.016

| variety | risk @τ_MSA → @τ_v | distance → | closer | answered @τ_MSA → @τ_v |
|---|---|---|---|---|
| EGY | 0.219 → 0.166 | 0.019 → 0.034 | no | 0.527 → 0.417 |
| KSA | 0.200 → 0.194 | 0.000 → 0.006 | no | 0.520 → 0.512 |
| MAG | 0.236 → 0.171 | 0.036 → 0.029 | yes | 0.380 → 0.247 |
| SYR | 0.231 → 0.198 | 0.031 → 0.002 | yes | 0.465 → 0.391 |
| UAE | 0.208 → 0.191 | 0.008 → 0.009 | no | 0.532 → 0.501 |

## gemma-2-9b: test 1420, calibration 808

### 9.1 Calibration sensitivity (r*=0.2, α=0.3); τ_MSA across resamples: median 0.498 [0.455,0.527]; q̂_MSA median 0.733 [0.717,0.748]

| variety | S4 Δanswered: original [CI] → double-resampled [CI] (width ratio) | realised risk @τ: orig → resampled [CI] | D4 residual gap: orig [CI] → resampled [CI] | D4 realised risk @τ_v resampled [CI] | P2 Δcov: orig [CI] → resampled [CI] | P2 size ratio: orig [CI] → resampled [CI] | verdict |
|---|---|---|---|---|---|---|---|
| EGY | -0.070 [-0.091,-0.048] → -0.071 [-0.095,-0.046] (×1.15) | 0.222 → 0.225 [0.174,0.274] | -0.079 [-0.100,-0.058] → -0.070 [-0.139,+0.006] | 0.222 [0.166,0.283] | -0.046 [-0.065,-0.026] → -0.046 [-0.067,-0.023] (×1.11) | 1.108 [1.084,1.134] → 1.111 [1.043,1.188] (×2.91) | S4 robust; D4 sensitive; Δcov robust; size robust |
| KSA | -0.074 [-0.095,-0.053] → -0.076 [-0.106,-0.049] (×1.35) | 0.212 → 0.211 [0.156,0.269] | -0.072 [-0.092,-0.051] → -0.080 [-0.143,-0.020] | 0.209 [0.152,0.267] | -0.035 [-0.055,-0.015] → -0.039 [-0.060,-0.019] (×1.02) | 1.096 [1.071,1.118] → 1.112 [1.043,1.196] (×3.25) | S4 robust; D4 robust; Δcov robust; size robust |
| MAG | -0.181 [-0.205,-0.158] → -0.179 [-0.202,-0.156] (×1.00) | 0.174 → 0.175 [0.131,0.229] | -0.190 [-0.214,-0.168] → -0.199 [-0.258,-0.154] | 0.162 [0.120,0.207] | -0.081 [-0.105,-0.058] → -0.080 [-0.104,-0.050] (×1.15) | 1.211 [1.184,1.238] → 1.219 [1.135,1.322] (×3.42) | S4 robust; D4 robust; Δcov robust; size robust |
| SYR | -0.123 [-0.146,-0.099] → -0.124 [-0.149,-0.099] (×1.07) | 0.218 → 0.221 [0.165,0.286] | -0.202 [-0.227,-0.180] → -0.191 [-0.279,-0.111] | 0.174 [0.112,0.242] | -0.088 [-0.110,-0.065] → -0.085 [-0.111,-0.058] (×1.19) | 1.233 [1.204,1.262] → 1.230 [1.132,1.337] (×3.55) | S4 robust; D4 robust; Δcov robust; size robust |
| UAE | -0.034 [-0.055,-0.012] → -0.034 [-0.060,-0.010] (×1.16) | 0.193 → 0.199 [0.160,0.244] | -0.010 [-0.031,+0.011] → -0.014 [-0.092,+0.049] | 0.208 [0.158,0.255] | -0.030 [-0.049,-0.010] → -0.031 [-0.052,-0.011] (×1.05) | 1.105 [1.080,1.130] → 1.110 [1.027,1.197] (×3.37) | S4 robust; D4 sensitive; Δcov robust; size robust |
| ENG | +0.229 [+0.204,+0.254] → +0.229 [+0.200,+0.254] (×1.10) | 0.155 → 0.155 [0.128,0.184] | +0.394 [+0.370,+0.420] → +0.383 [+0.300,+0.456] | 0.229 [0.180,0.267] | +0.091 [+0.070,+0.113] → +0.092 [+0.068,+0.117] (×1.15) | 0.680 [0.660,0.701] → 0.686 [0.625,0.748] (×3.03) | S4 robust; D4 robust; Δcov robust; size robust |

### 9.1b Rotation subset (500 keys): S4 Δanswered order-averaged — original (τ fixed) [CI] → double-resampled [CI]

| variety | original | double-resampled | verdict |
|---|---|---|---|
| EGY | -0.056 [-0.077,-0.033] | -0.059 [-0.083,-0.034] | robust |
| KSA | -0.067 [-0.090,-0.044] | -0.066 [-0.090,-0.043] | robust |
| MAG | -0.160 [-0.186,-0.134] | -0.160 [-0.189,-0.133] | robust |
| SYR | -0.119 [-0.145,-0.093] | -0.121 [-0.149,-0.095] | robust |
| UAE | -0.035 [-0.054,-0.015] | -0.034 [-0.056,-0.012] | robust |
| ENG | +0.263 [+0.231,+0.294] | +0.261 [+0.229,+0.293] | robust |

### 9.2 Re-run reproducibility (subset 500×7 cells): different prediction in 2.029%; top-2 margin median all 0.502 nats vs disagreeing 0.118; share margin<0.05: all 0.087 vs disagreeing 0.437; max |Δ(gap estimate)| across Δacc/ΔP1/S4 and dialects = 0.026

| variety | Δacc confirm → rerun | ΔP1 confirm → rerun | S4 Δanswered confirm → rerun |
|---|---|---|---|
| EGY | -0.058 → -0.074 | -0.160 → -0.172 | -0.024 → -0.026 |
| KSA | -0.036 → -0.046 | -0.156 → -0.168 | -0.048 → -0.056 |
| MAG | -0.108 → -0.108 | -0.238 → -0.258 | -0.170 → -0.172 |
| SYR | -0.102 → -0.120 | -0.200 → -0.222 | -0.118 → -0.122 |
| UAE | -0.040 → -0.040 | -0.134 → -0.154 | +0.000 → -0.026 |
| ENG | +0.148 → +0.146 | +0.300 → +0.308 | +0.262 → +0.256 |

### 9.3 R4 paired comparison: D = [dialect≠MSA at k=0] − [same variety k=0≠k=1]; D′ uses MSA's own rotation change

| variety | P3 (dialect vs MSA) | within-variety rotation change | mean D [CI] | mean D′ [CI] | reading |
|---|---|---|---|---|---|
| EGY | 0.244 | 0.412 | -0.168 [-0.218,-0.120] | -0.136 [-0.188,-0.082] | not larger than one-rotation change |
| KSA | 0.230 | 0.424 | -0.194 [-0.246,-0.138] | -0.150 [-0.204,-0.096] | not larger than one-rotation change |
| MAG | 0.314 | 0.484 | -0.170 [-0.224,-0.116] | -0.066 [-0.122,-0.010] | not larger than one-rotation change |
| SYR | 0.332 | 0.458 | -0.126 [-0.178,-0.072] | -0.048 [-0.106,+0.012] | not larger than one-rotation change |
| UAE | 0.230 | 0.418 | -0.188 [-0.240,-0.138] | -0.150 [-0.202,-0.096] | not larger than one-rotation change |
| ENG | 0.318 | 0.198 | +0.120 [+0.072,+0.172] | -0.062 [-0.110,-0.014] | larger than one-rotation change |

### 9.4 D4 distance to target (post hoc): closer in 1/5 cells; cells with risk>0.24 under τ_MSA 0 → under τ_v 0; mean distance 0.017 → 0.023

| variety | risk @τ_MSA → @τ_v | distance → | closer | answered @τ_MSA → @τ_v |
|---|---|---|---|---|
| EGY | 0.222 → 0.222 | 0.022 → 0.022 | yes | 0.399 → 0.390 |
| KSA | 0.212 → 0.215 | 0.012 → 0.015 | no | 0.395 → 0.397 |
| MAG | 0.174 → 0.164 | 0.026 → 0.036 | no | 0.287 → 0.279 |
| SYR | 0.218 → 0.164 | 0.018 → 0.036 | no | 0.346 → 0.267 |
| UAE | 0.193 → 0.209 | 0.007 → 0.009 | no | 0.435 → 0.459 |
