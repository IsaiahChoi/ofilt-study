# P3-2b synthetic smoke run (`tools/p3_sealed_run.py --synthetic --smoke 20`, twice)

Synthetic only: the stand-in calibrator (no data file read), `OFILT_DATA_DIR` an empty folder, `TMPDIR` the item's own folder. Timings only; the fingerprint registry was empty in both runs.

- Configuration: `docs/P3_RUN_CONFIG.json`, SHA-256 `645ef80ee91c91e81ac4a880ff34b0fc19906bbb3c36f5300575d727dc1d7eaa`.
- Gate 1, both runs complete with every assertion passing, no exception recorded and no abort: **True**
- Gate 2, the two JSON outputs identical apart from `runtime`: **True**
- Total runtime: run 1 90.8 s, run 2 85.6 s; calibrator 0.01 s and 0.01 s.

## Seconds per replication and the projected full run

| Task | Replications (run 1 / run 2) | s per replication (run 1 / run 2) | Mean | Full replications | Projected |
|---|---|---|---|---|---|
| T1 | 20 / 20 | 0.1465 / 0.1330 | 0.1398 | 5000 | 699 s (11.6 min) |
| T5_boundary | 20 / 20 | 0.1506 / 0.1394 | 0.1450 | 5000 | 725 s (12.1 min) |
| T2 | 60 / 60 | 0.1404 / 0.1353 | 0.1379 | 3000 | 414 s (6.9 min) |
| T6 | 80 / 80 | 0.1467 / 0.1371 | 0.1419 | 4000 | 568 s (9.5 min) |
| T3 | 60 / 60 | 1.0781 / 1.0179 | 1.0480 | 3000 | 3144 s (52.4 min) |

Projected full configuration at these rates, including the calibrator (0.01 s) and the pooled step (0.00 s): **5549 s (1.54 h)**.

Note: these rates exclude the guard's cost with a populated fingerprint registry. In real mode the registry holds the real targets (loaded with `io.load_dev` and `targets.add_targets`), and every guard call on a synthetic frame then does set-membership work (PASS1_STATUS, B7b: about 2/3 of each fit's time). That cost is measured at P3-3, by the rehearsal (`--rehearsal`), which populates the registry the same way.
