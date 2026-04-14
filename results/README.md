# 结果索引

这个目录保存的是仓库内的“可复现实验证据包”，不是权重仓库。

这里应该保留：

- 运行命令
- `train_results.json`
- `predict_results.json`
- `toolcall_eval.json`
- 必要的 `trainer_log.jsonl`
- 如果体量仍然很小，也可以保留 `generated_predictions.jsonl`
- 一组 run 的人工总结和机器可读 `manifest.json`

这里不应该保留：

- checkpoint / adapter 权重
- 大体积模型缓存
- editable 第三方源码 checkout
- 其它明显属于重产物的中间文件

当前已收录：

- `local_2080ti/pilot_v1`

刷新一组结果证据包的示例命令：

```bash
/root/miniconda3/envs/tooluse-llf/bin/python scripts/summarize_run_results.py \
  --run-root /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1 \
  --output-dir results/local_2080ti/pilot_v1 \
  --machine local_2080ti \
  --experiment-group pilot_v1 \
  --dataset pilot_v1 \
  --include-generated-predictions
```

约束：

- 权重和其它重产物继续放在 `/root/autodl-fs/tooluse-artifacts`。
- 仓库内的 `results/` 负责保存“证明实验确实跑过”的轻量证据。
