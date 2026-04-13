# 环境复现与新机恢复

这份文档是给“新机器上自己手动恢复环境并开始跑实验”的。

默认前提现在改成两层：

1. 平台侧系统盘/镜像默认保留，作为快速恢复手段；
2. 仓库内维护一条**不依赖 Codex** 的裸 Linux 恢复路径。

也就是说：

- 平台镜像负责“快”
- 仓库文档和脚本负责“稳”和“可复现”

当前默认**不单独维护 Docker 方案**，因为你已经明确说了平台侧镜像会保留。

## 当前已验证环境

### 机器指纹

- GPU：`NVIDIA GeForce RTX 2080 Ti 22GB`
- Driver：`550.120`
- Python：`3.11.15`

### 当前路径约定

- conda 环境：`/root/miniconda3/envs/tooluse-llf`
- 仓库：`/autodl-fs/data/tooluse`
- 重产物根目录：`/root/autodl-fs/tooluse-artifacts`
- 外置 `LLaMA-Factory` checkout：
  - `/root/autodl-fs/tooluse-artifacts/external/LLaMA-Factory`

### 当前已验证关键版本

- `torch==2.6.0+cu124`
- `transformers==5.2.0`
- `datasets==4.0.0`
- `accelerate==1.11.0`
- `peft==0.18.1`
- `trl==0.24.0`
- `bitsandbytes==0.49.2`
- `modelscope==1.35.4`

### 当前已验证的 LLaMA-Factory 版本

- repo：`https://github.com/hiyouga/LlamaFactory.git`
- commit：`436d26bc28b7c6422c89b63064c5a87e258ed73e`

## 推荐恢复方式

### 路径 A：先尝试平台镜像恢复

如果平台支持保留系统盘/镜像/快照，优先用它恢复。

这条路径的优点：

- 最快；
- 不用重新装一遍环境；
- 最接近当前这台机器的工作状态。

但即使镜像默认保留，repo 内的恢复路径仍然必须维护，因为：

- 换机器不一定能直接用同一个镜像；
- 以后开源 release 不能只剩镜像；
- 你自己也需要一条可审计、可重复的安装路径。

### 路径 B：裸 Linux 从零恢复

这条路径是当前 repo 内的主维护对象。

核心脚本：

- `scripts/bootstrap_train_env.sh`

它会做这些事：

- 创建 conda 环境
- 安装 repo 侧依赖
- clone 并 checkout 外置 `LLaMA-Factory`
- 安装 editable `LLaMA-Factory`
- 安装本仓库
- 如果 torch 已装好，就自动跑 `pytest` 和环境探针

## 为什么现在不把 CUDA 写死

因为你已经明确说了，这件事在不同机器上很难完全提前控制。

所以现在的策略是：

- repo 记录“当前这台机器验证过什么版本”；
- 裸机恢复脚本不强行绑定某个 CUDA；
- `torch` 安装命令由你在新机器上自己传进去，或者复用机器已有环境；
- 其余 repo 依赖、路径和 runtime commit 由脚本负责收敛。

这比“把所有机器都假设成同一套 CUDA”更稳。

## 裸机恢复：推荐命令

### 最短用法

如果你已经自己装好了 `torch`：

```bash
bash scripts/bootstrap_train_env.sh
```

如果你想让脚本顺手也装 `torch`，可以自己传安装命令：

```bash
bash scripts/bootstrap_train_env.sh \
  --torch-install-cmd "pip install torch torchvision torchaudio"
```

如果你知道当前机器就适合某个官方 wheel 源，也可以自己指定：

```bash
bash scripts/bootstrap_train_env.sh \
  --torch-install-cmd 'pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124'
```

### 国内源

脚本默认已经用：

- `https://pypi.tuna.tsinghua.edu.cn/simple`

如果你想改成别的源：

```bash
bash scripts/bootstrap_train_env.sh \
  --pip-index-url https://pypi.mirrors.ustc.edu.cn/simple
```

### 只装范围版本，不装精确版本

默认脚本会用：

- `requirements/train-server-validated.txt`

如果你想更宽松一些，用范围版本：

```bash
bash scripts/bootstrap_train_env.sh \
  --requirements requirements/train-server.txt
```

## 裸机恢复：脚本参数

查看帮助：

```bash
bash scripts/bootstrap_train_env.sh --help
```

常用参数：

- `--conda-root`
- `--env-name`
- `--python-version`
- `--artifact-root`
- `--pip-index-url`
- `--requirements`
- `--torch-install-cmd`
- `--skip-llamafactory`
- `--skip-checks`

## 不用脚本时的手动恢复顺序

如果你不想跑脚本，也可以手动按下面顺序走：

### 1. 创建 conda 环境

```bash
/root/miniconda3/bin/conda create -n tooluse-llf python=3.11 -y
```

### 2. 安装 torch

这里不写死，由当前机器自己决定。

例如：

```bash
/root/miniconda3/envs/tooluse-llf/bin/pip install torch torchvision torchaudio
```

### 3. 安装 repo 依赖

```bash
/root/miniconda3/envs/tooluse-llf/bin/pip install \
  -r requirements/train-server-validated.txt \
  -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 安装外置 LLaMA-Factory

```bash
git clone https://github.com/hiyouga/LlamaFactory.git /root/autodl-fs/tooluse-artifacts/external/LLaMA-Factory
git -C /root/autodl-fs/tooluse-artifacts/external/LLaMA-Factory checkout 436d26bc28b7c6422c89b63064c5a87e258ed73e
/root/miniconda3/envs/tooluse-llf/bin/pip install -e /root/autodl-fs/tooluse-artifacts/external/LLaMA-Factory
```

### 5. 安装本仓库

```bash
/root/miniconda3/envs/tooluse-llf/bin/pip install -e .
```

### 6. 运行验证

```bash
/root/miniconda3/envs/tooluse-llf/bin/python -m pytest -q
/root/miniconda3/envs/tooluse-llf/bin/python scripts/check_train_env.py
```

当前预期：

- `pytest`: `23 passed`
- `check_train_env.py`: `ready_for_real_training = true`

## 当前依赖文件

### 范围版本

- `requirements/train-server.txt`

用途：

- 新机器上更灵活地恢复环境；
- 不强行复制当前机器的每一个小版本。

### 精确版本

- `requirements/train-server-validated.txt`

用途：

- 尽可能靠近当前已验证环境；
- 当你想复刻这台机器的行为时优先用它。

## 推荐缓存路径

为了减轻系统盘压力，建议在新机器上也继续外置缓存：

```bash
export HF_HOME=/root/autodl-fs/tooluse-artifacts/cache/huggingface
export MODELSCOPE_CACHE=/root/autodl-fs/tooluse-artifacts/cache/modelscope
export PIP_CACHE_DIR=/root/autodl-fs/tooluse-artifacts/cache/pip
export USE_MODELSCOPE_HUB=1
```

## 当前结论

对这个项目最合适的策略是：

1. 平台镜像默认保留；
2. repo 内维护裸 Linux 恢复脚本和文档；
3. 不假设新机器上一定有 Codex；
4. 不把 CUDA 版本硬编码成唯一前提；
5. 关键依赖、commit、验证命令和路径约定都保留在仓库里。
