# local_2080ti / pilot_v1

这组内容对应本机 `RTX 2080 Ti 22GB` 上的 `pilot_v1` QLoRA bring-up。

定位：

- 这是工程打通证据；
- 不是论文主结论；
- 也不是正式 paper baseline。

仓库内保留的证明材料：

- `commands.md`
- `manifest.json`
- 每个 run 子目录里的：
  - `train_results.json`
  - `predict_results.json`
  - `toolcall_eval.json`
  - `trainer_log.jsonl`
  - 当前这组还额外保留了轻量 `generated_predictions.jsonl`

仓库外完整产物根目录：

- `$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1`

## 当前结论

- 三个 held-out toy baseline run 都没有拿到 exact tool-call match。
- 三个 baseline 的失败模式一致：
  - tool name 对
  - argument keys 对
  - argument values 错
- `vanilla_overfit_trainbook` 的 exact match 是 `1/1`，说明训练链路本身是通的。
- 所以这里更像是 toy slice 泛化失败，而不是训练/导出/预测/eval 栈损坏。

## Run 摘要

| run | mode | config | exact match | arg value exact | train loss |
| --- | --- | --- | --- | --- | --- |
| `qwen25_05b_vanilla_qlora` | `vanilla` | `configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml` | `0/1` | `0.0` | `0.001416889084794093` |
| `qwen25_05b_schema_augmented_qlora` | `schema_augmented` | `configs/llamafactory/local_qwen25_05b_schema_augmented_qlora.yaml` | `0/2` | `0.0` | `0.009449722981177426` |
| `qwen25_05b_hammer_like_qlora` | `hammer_like` | `configs/llamafactory/local_qwen25_05b_hammer_like_qlora.yaml` | `0/2` | `0.0` | `0.004456632679405933` |
| `qwen25_05b_vanilla_overfit_trainbook_qlora` | `vanilla` | `configs/llamafactory/local_qwen25_05b_vanilla_overfit_trainbook_qlora.yaml` | `1/1` | `1.0` | `0.019234412994410376` |

## 维护方式

- 外部 run 有新增后，先刷新 `manifest.json` 和各 run 子目录证据文件。
- 如果人工解释变了，再更新这一页。
- 命令入口统一写在 `commands.md`。
