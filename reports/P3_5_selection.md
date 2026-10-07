# P3-5: the pre-stated rules applied to the sealed run's outputs

Built by `/tmp/p3_5_rules.py` from `reports/P3_4_sealed_run.json` (SHA-256 `65e68c8cf9a76afda05869e8772b345e49f30fa24bcad6790de28d6bcab58942`) and `docs/P3_RUN_CONFIG.json` (SHA-256 `ca989095436c97da723d233267af9a8b454d4dee0e5b528835a6bb88323e574e`) alone. The rules are the Decision-log lines D3.4, D2.6 and D4.3b, applied as written. Bands are tested on the point estimate k/n in exact integer arithmetic: in [3.5%, 6.5%] is 35·n ≤ 1000·k ≤ 65·n; at least 0.80 is 5·k ≥ 4·n; at most 6.5% is 1000·k ≤ 65·n. The bootstrap's own rate at b = 0 is cell 0's `bootstrap` rejection rate.

## Results

| Rule | Test | Result |
|---|---|---|
| D3.4, H1: cell 0 `dk_normal` rejection in band | 35·5000 = 175000 <= 1000·291 = 291000 <= 65·5000 = 325000: True | True |
| D3.4, H1 | the selected method M | **dk_normal** |
| D3.4, Clark–West: cell 9 `normal` rate in band | 35·2000 = 70000 <= 1000·66 = 66000 <= 65·2000 = 130000: False | False |
| D3.4, Clark–West | the selected reference CW | **calibrated** |
| D2.6 (i): cell 0 TOST at the primary SESOI under dk_normal ≥ 0.80 | 5·5000 = 25000 >= 4·5000 = 20000: True | True |
| D2.6 (ii): cell 1 TOST at the primary SESOI under dk_normal ≤ 6.5% | 1000·296 = 296000 <= 65·5000 = 325000: True | True |
| D2.6 | viable | **True** |
| D4.3b: cell 7 `ols_dk` centred rejection in band | 35·1000 = 35000 <= 1000·55 = 55000 <= 65·1000 = 65000: True | flagged: **False** |
| D4.3b: cell 7 `huber_dk` centred rejection in band | 35·1000 = 35000 <= 1000·57 = 57000 <= 65·1000 = 65000: True | flagged: **False** |
| D4.3b: cell 7 `winsorised_ols_dk` centred rejection in band | 35·1000 = 35000 <= 1000·52 = 52000 <= 65·1000 = 65000: True | flagged: **False** |

## The binding numbers

Under M = `dk_normal`, and CW = `calibrated` for Clark–West.

| Cell | b | k | n | Rejection rate |
|---|---|---|---|---|
| 0 | 0.0 | 291 | 5000 | 0.0582 |
| 2 | 0.1 | 212 | 1000 | 0.212 |
| 3 | 0.25 | 809 | 1000 | 0.809 |
| 4 | 0.4 | 995 | 1000 | 0.995 |

| MDE80 | Value |
|---|---|
| probit interpolated | 0.24707872570018363 |
| normal approximation, sd(b̂) | 0.2425411037781687 |
| normal approximation, mean se | 0.23995965196729913 |

| T3 cell | h1_method | cw_method | both | h1_only | cw_only | neither |
|---|---|---|---|---|---|---|
| 9 | dk_normal | calibrated | 62 | 56 | 38 | 1844 |
| 10 | dk_normal | calibrated | 108 | 7 | 47 | 338 |
| 11 | dk_normal | calibrated | 417 | 0 | 35 | 48 |

## The switch's branch and placeholder values

| Amendment | Use |
|---|---|
| AM-07 | variant "viable" |
| AM-08 | unused (M is dk_normal) |
| AM-09 | used |
| AM-10 | always |

| Placeholder | Value | Needed by the used amendments |
|---|---|---|
| `<S>` | `0.8652` | yes |
| `<SL>` | `0.07152` | yes |
| `<SH>` | `2.719` | yes |
| `<M>` | `dk_normal` | yes |
| `<P0>` | `1.0000` | yes |
| `<PB>` | `0.0592` | yes |
| `<MDE>` | `0.2471` | no |
| `<R_dk>` | `0.0582` | no |
| `<R_boot>` | `0.0492` | no |
| `<R_cw>` | `0.0330` | yes |
| `<C95>` | `2.004103434596224` | no |
| `<C90>` | `1.6735080187686666` | no |
| `<CCW>` | `1.411608406163672` | yes |
| `<date>` | the switch's date (set at P3-6) | yes |

## The inputs

### Cell 0 (T1, b = 0) and cell 9 (T3, b = 0)

| Quantity | k | n | Rate | Wilson 95% |
|---|---|---|---|---|
| cell 0 rejection, dk_normal | 291 | 5000 | 0.0582 | [0.052043410621939824, 0.06503493081671266] |
| cell 0 rejection, bootstrap | 246 | 5000 | 0.0492 | [0.04354338255549715, 0.05554877751816637] |
| cell 0 rejection, calibrated | 253 | 5000 | 0.0506 | [0.044862312290198145, 0.0570276982180192] |
| cell 9 Clark–West, normal | 66 | 2000 | 0.033 | [0.026022752700289677, 0.041767769460400554] |
| cell 9 Clark–West, calibrated | 100 | 2000 | 0.05 | [0.04128123361873174, 0.0604441089343959] |

### Critical values

| Critical value | Value | 95% interval | Rank | Rank interval | n |
|---|---|---|---|---|---|
| c_cal_q95 | 2.004103434596224 | [1.9698396058131495, 2.0320964672762334] | 12350 | [12301, 12399] | 13000 |
| c_cal_q90 | 1.6735080187686666 | [1.6442807581465901, 1.7004491869119305] | 11700 | [11632, 11768] | 13000 |
| c_boot_q95 | 2.022569888520032 | [1.9820577181451606, 2.0594603250401056] | 12350 | [12301, 12399] | 13000 |
| c_boot_q90 | 1.6799577365175238 | [1.6526050040282763, 1.7084563399082786] | 11700 | [11632, 11768] | 13000 |
| c_boot_h3_q95 | 2.042922605074861 | [2.01350072583419, 2.075983445449829] | 12350 | [12301, 12399] | 13000 |
| c_cw_cal | 1.411608406163672 | [1.3296005543310443, 1.5279886332165615] | 1900 | [1880, 1920] | 2000 |

### TOST (cells 0 and 1)

| Method | Cell | SESOI | k | n | Rate |
|---|---|---|---|---|---|
| dk_normal | 0 | primary | 5000 | 5000 | 1.0 |
| dk_normal | 0 | low | 0 | 5000 | 0.0 |
| dk_normal | 0 | high | 5000 | 5000 | 1.0 |
| dk_normal | 1 | primary | 296 | 5000 | 0.0592 |
| dk_normal | 1 | low | 0 | 5000 | 0.0 |
| dk_normal | 1 | high | 5000 | 5000 | 1.0 |
| bootstrap | 0 | primary | 5000 | 5000 | 1.0 |
| bootstrap | 0 | low | 0 | 5000 | 0.0 |
| bootstrap | 0 | high | 5000 | 5000 | 1.0 |
| bootstrap | 1 | primary | 286 | 5000 | 0.0572 |
| bootstrap | 1 | low | 0 | 5000 | 0.0 |
| bootstrap | 1 | high | 5000 | 5000 | 1.0 |
| calibrated | 0 | primary | 5000 | 5000 | 1.0 |
| calibrated | 0 | low | 0 | 5000 | 0.0 |
| calibrated | 0 | high | 5000 | 5000 | 1.0 |
| calibrated | 1 | primary | 288 | 5000 | 0.0576 |
| calibrated | 1 | low | 0 | 5000 | 0.0 |
| calibrated | 1 | high | 5000 | 5000 | 1.0 |

### Rejection rates (cells 0, 2, 3, 4) and MDE80, per method

| Method | Cell 0 | Cell 2 | Cell 3 | Cell 4 | MDE80 probit | MDE80 normal, sd | MDE80 normal, mean se |
|---|---|---|---|---|---|---|---|
| dk_normal | 291/5000 = 0.0582 | 212/1000 = 0.212 | 809/1000 = 0.809 | 995/1000 = 0.995 | 0.24707872570018363 | 0.2425411037781687 | 0.23995965196729913 |
| bootstrap | 246/5000 = 0.0492 | 194/1000 = 0.194 | 788/1000 = 0.788 | 994/1000 = 0.994 | 0.2536890596268369 | 0.2425411037781687 | 0.23995965196729913 |
| calibrated | 253/5000 = 0.0506 | 203/1000 = 0.203 | 793/1000 = 0.793 | 995/1000 = 0.995 | 0.2521103275443551 | 0.2425411037781687 | 0.23995965196729913 |

### T3 (cells 9 to 11)

| Cell | b | Reps | H1 dk_normal | H1 bootstrap | H1 calibrated | CW normal | CW calibrated |
|---|---|---|---|---|---|---|---|
| 9 | 0.0 | 2000 | 118/2000 = 0.059 | 99/2000 = 0.0495 | 105/2000 = 0.0525 | 66/2000 = 0.033 | 100/2000 = 0.05 |
| 10 | 0.1 | 500 | 115/500 = 0.23 | 107/500 = 0.214 | 109/500 = 0.218 | 122/500 = 0.244 | 155/500 = 0.31 |
| 11 | 0.25 | 500 | 417/500 = 0.834 | 402/500 = 0.804 | 405/500 = 0.81 | 428/500 = 0.856 | 452/500 = 0.904 |

| Cell | h1_method | cw_method | both | h1_only | cw_only | neither |
|---|---|---|---|---|---|---|
| 9 | dk_normal | normal | 54 | 64 | 12 | 1870 |
| 9 | dk_normal | calibrated | 62 | 56 | 38 | 1844 |
| 9 | bootstrap | normal | 48 | 51 | 18 | 1883 |
| 9 | bootstrap | calibrated | 54 | 45 | 46 | 1855 |
| 9 | calibrated | normal | 51 | 54 | 15 | 1880 |
| 9 | calibrated | calibrated | 57 | 48 | 43 | 1852 |
| 10 | dk_normal | normal | 101 | 14 | 21 | 364 |
| 10 | dk_normal | calibrated | 108 | 7 | 47 | 338 |
| 10 | bootstrap | normal | 98 | 9 | 24 | 369 |
| 10 | bootstrap | calibrated | 102 | 5 | 53 | 340 |
| 10 | calibrated | normal | 99 | 10 | 23 | 368 |
| 10 | calibrated | calibrated | 104 | 5 | 51 | 340 |
| 11 | dk_normal | normal | 415 | 2 | 13 | 70 |
| 11 | dk_normal | calibrated | 417 | 0 | 35 | 48 |
| 11 | bootstrap | normal | 401 | 1 | 27 | 71 |
| 11 | bootstrap | calibrated | 402 | 0 | 50 | 48 |
| 11 | calibrated | normal | 403 | 2 | 25 | 70 |
| 11 | calibrated | calibrated | 405 | 0 | 47 | 48 |

### T6 (cells 5 to 8; D4.3a centred outputs)

| Cell | Window | b | Estimator | Centred k/n | Rate | Wilson 95% | sd | mean se | se/sd | Share downweighted |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | full | 0.0 | ols_dk | 56/1000 | 0.056 | [0.043374813385442, 0.07202334814973096] | 0.08674332270422938 | 0.08599488263494814 | 0.991371784640609 | — |
| 5 | full | 0.0 | huber_dk | 57/1000 | 0.057 | [0.04425344035871594, 0.07313706765948591] | 0.08364015429426375 | 0.0835448628814702 | 0.9988606977880709 | 0.20546046248062827 |
| 5 | full | 0.0 | winsorised_ols_dk | 53/1000 | 0.053 | [0.04074650524859452, 0.06867461683749176] | 0.08655803046222124 | 0.08629331538239607 | 0.9969417617474474 | — |
| 6 | full | 0.25 | ols_dk | 55/1000 | 0.055 | [0.04249742737476844, 0.07090838767737563] | 0.08534188080436858 | 0.08592455451640223 | 1.0068275236793682 | — |
| 6 | full | 0.25 | huber_dk | 46/1000 | 0.046 | [0.03466249276326498, 0.06081220394161907] | 0.08304858971075 | 0.08338157358621241 | 1.0040095066830412 | 0.20533560951966848 |
| 6 | full | 0.25 | winsorised_ols_dk | 50/1000 | 0.05 | [0.03813026239274882, 0.06531382024425081] | 0.0858114503921344 | 0.08655380928928813 | 1.0086510470777659 | — |
| 7 | early | 0.0 | ols_dk | 55/1000 | 0.055 | [0.04249742737476844, 0.07090838767737563] | 0.06797936534321417 | 0.0683947112613717 | 1.0061098822570722 | — |
| 7 | early | 0.0 | huber_dk | 57/1000 | 0.057 | [0.04425344035871594, 0.07313706765948591] | 0.06600790956741807 | 0.0660882579692269 | 1.0012172541493192 | 0.19168792453546735 |
| 7 | early | 0.0 | winsorised_ols_dk | 52/1000 | 0.052 | [0.03987303628377742, 0.06755573931927998] | 0.06765052181017138 | 0.06800651629661178 | 1.0052622578054804 | — |
| 8 | early | 0.25 | ols_dk | 50/1000 | 0.05 | [0.03813026239274882, 0.06531382024425081] | 0.06641314257707664 | 0.06819609773704602 | 1.026846420614717 | — |
| 8 | early | 0.25 | huber_dk | 51/1000 | 0.051 | [0.03900094277526684, 0.06643548634476165] | 0.06483181058304209 | 0.06597866934362688 | 1.0176897536914504 | 0.19099755736127408 |
| 8 | early | 0.25 | winsorised_ols_dk | 44/1000 | 0.044 | [0.0329382145884185, 0.058551789150407776] | 0.06624989896925858 | 0.06796117742254322 | 1.0258306575543414 | — |
