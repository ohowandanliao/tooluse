# local_2080ti / xlam_fc_single_call

这组内容对应本机 `RTX 2080 Ti 22GB` 上的 `xLAM function-calling-60k` single-call clean slice baseline bring-up。

定位：

- 这是当前最接近真实 baseline 数据源的一组 direct baseline 证据；
- 仍然只是 `pilot1000` 预算；
- 还不能直接拿来当最终论文结论。

仓库内保留的证明材料：

- `manifest.json`
- 每个 run 子目录里的：
  - `train_results.json`
  - `predict_results.json`
  - `toolcall_eval.json`
  - `trainer_log.jsonl`
  - `generated_predictions.jsonl`

仓库外完整产物根目录：

- `$ARTIFACT_ROOT/runs/local_2080ti/xlam_fc_single_call`

## 当前结论

- `pilot1000` 预算下，本机最好的 direct baseline 是 `vanilla`。
- `hammer_like` 的总 exact match 基本和外部机器回传的 `schema_augmented` 持平。
- 同口径看 `A` 侧，`schema_augmented` 和 `hammer_like` 目前都没有超过 `vanilla`。
- 但这轮预算不完全公平，因为 `vanilla` 的 epoch 覆盖更高。

## Run 摘要

| run | mode | config | exact match | A split | B split | train loss |
| --- | --- | --- | --- | --- | --- | --- |
| `qwen25_05b_vanilla_qlora_pilot1000` | `vanilla` | `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml` | `2083/2570 = 0.8105` | `0.8105` | `-` | `0.05200534148514271` |
| `qwen25_05b_hammer_like_qlora_pilot1000` | `hammer_like` | `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_hammer_like_qlora_pilot1000.yaml` | `3983/5140 = 0.7749` | `0.8070` | `0.7428` | `0.05071068285405636` |

## 维护方式

- 外部 run 有新增后，先刷新 `manifest.json` 和各 run 子目录证据文件。
- 如果阶段性判断改变，再更新这一页。
