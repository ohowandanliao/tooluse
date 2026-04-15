# repro_4090d / xlam_fc_single_call

这组内容是外部机器 `repro_4090d` 回传的 `schema_augmented` bring-up 结果包。

定位：

- 这是新机器环境和训练链路打通证据；
- 预测是在 `test` 上跑的；
- 用户已明确备注：`this run predicted on test; use as bring-up only`；
- 因此这里不应被直接包装成最终论文主结果。

当前已知配置：

- `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot1000.yaml`

当前保留文件：

- `train_results.json`
- `predict_results.json`
- `toolcall_eval.json`
- `trainer_log.jsonl`
- `generated_predictions.jsonl`

## 当前结论

- `schema_augmented` 在当前 `pilot1000` bring-up 预算下没有超过本机 `vanilla`。
- 同口径看 `A` 侧，`0.8066` 也略低于 `vanilla(A)=0.8105`。
- 这说明它至少还不是“明显更强”的 direct baseline。

## 指标摘要

| run | mode | config | exact match | A split | B split | train loss |
| --- | --- | --- | --- | --- | --- | --- |
| `qwen25_05b_schema_augmented_qlora_pilot1000` | `schema_augmented` | `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot1000.yaml` | `3984/5140 = 0.7751` | `0.8066` | `0.7436` | `0.04809650798141956` |

## 缺口

- 这份回传包没有带标准化 `manifest.json`。
- 训练命令本身没有单独回收；当前只保留了配置名和结果文件。
