#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

CONDA_ROOT="/root/miniconda3"
ENV_NAME="tooluse-llf"
PYTHON_VERSION="3.11"
ARTIFACT_ROOT="/root/autodl-fs/tooluse-artifacts"
LLAMAFACTORY_DIR="${ARTIFACT_ROOT}/external/LLaMA-Factory"
LLAMAFACTORY_REPO="https://github.com/hiyouga/LlamaFactory.git"
LLAMAFACTORY_COMMIT="436d26bc28b7c6422c89b63064c5a87e258ed73e"
PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
REQUIREMENTS_FILE="requirements/train-server-validated.txt"
TORCH_INSTALL_CMD=""
INSTALL_LLAMAFACTORY="1"
RUN_CHECKS="1"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/bootstrap_train_env.sh [options]

Options:
  --conda-root PATH           Conda root directory. Default: /root/miniconda3
  --env-name NAME            Conda env name. Default: tooluse-llf
  --python-version VERSION   Python version. Default: 3.11
  --artifact-root PATH       Artifact root. Default: /root/autodl-fs/tooluse-artifacts
  --pip-index-url URL        pip index url. Default: https://pypi.tuna.tsinghua.edu.cn/simple
  --requirements FILE        Requirements file relative to repo root.
                             Default: requirements/train-server-validated.txt
  --torch-install-cmd CMD    Command executed inside the conda env before installing
                             repo dependencies. Example:
                             --torch-install-cmd "pip install torch torchvision torchaudio"
  --skip-llamafactory        Do not clone/install external LLaMA-Factory.
  --skip-checks              Do not run pytest or scripts/check_train_env.py.
  --help                     Show this message.

Notes:
  1. This script does not hard-code a CUDA choice.
  2. If torch is already installed in the target env, --torch-install-cmd can be omitted.
  3. If torch is missing and --torch-install-cmd is omitted, the script will install
     the rest of the environment but skip final validation.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --conda-root)
      CONDA_ROOT="$2"
      shift 2
      ;;
    --env-name)
      ENV_NAME="$2"
      shift 2
      ;;
    --python-version)
      PYTHON_VERSION="$2"
      shift 2
      ;;
    --artifact-root)
      ARTIFACT_ROOT="$2"
      LLAMAFACTORY_DIR="${ARTIFACT_ROOT}/external/LLaMA-Factory"
      shift 2
      ;;
    --pip-index-url)
      PIP_INDEX_URL="$2"
      shift 2
      ;;
    --requirements)
      REQUIREMENTS_FILE="$2"
      shift 2
      ;;
    --torch-install-cmd)
      TORCH_INSTALL_CMD="$2"
      shift 2
      ;;
    --skip-llamafactory)
      INSTALL_LLAMAFACTORY="0"
      shift
      ;;
    --skip-checks)
      RUN_CHECKS="0"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

CONDA_BIN="${CONDA_ROOT}/bin/conda"
REQUIREMENTS_PATH="${REPO_ROOT}/${REQUIREMENTS_FILE}"

if [[ ! -x "${CONDA_BIN}" ]]; then
  echo "conda not found at ${CONDA_BIN}" >&2
  exit 1
fi

if [[ ! -f "${REQUIREMENTS_PATH}" ]]; then
  echo "requirements file not found: ${REQUIREMENTS_PATH}" >&2
  exit 1
fi

echo "[bootstrap] repo_root=${REPO_ROOT}"
echo "[bootstrap] conda_root=${CONDA_ROOT}"
echo "[bootstrap] env_name=${ENV_NAME}"
echo "[bootstrap] python_version=${PYTHON_VERSION}"
echo "[bootstrap] artifact_root=${ARTIFACT_ROOT}"
echo "[bootstrap] requirements=${REQUIREMENTS_FILE}"

if ! "${CONDA_BIN}" env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
  echo "[bootstrap] creating conda env ${ENV_NAME}"
  "${CONDA_BIN}" create -y -n "${ENV_NAME}" "python=${PYTHON_VERSION}"
else
  echo "[bootstrap] conda env ${ENV_NAME} already exists"
fi

mkdir -p "${ARTIFACT_ROOT}/external"
mkdir -p "${ARTIFACT_ROOT}/cache/huggingface"
mkdir -p "${ARTIFACT_ROOT}/cache/modelscope"
mkdir -p "${ARTIFACT_ROOT}/cache/pip"

if [[ -n "${TORCH_INSTALL_CMD}" ]]; then
  echo "[bootstrap] running torch install command"
  "${CONDA_BIN}" run -n "${ENV_NAME}" bash -lc "${TORCH_INSTALL_CMD}"
else
  echo "[bootstrap] no --torch-install-cmd provided; will reuse existing torch if present"
fi

echo "[bootstrap] installing repo dependencies"
"${CONDA_BIN}" run -n "${ENV_NAME}" pip install -r "${REQUIREMENTS_PATH}" -i "${PIP_INDEX_URL}"

if [[ "${INSTALL_LLAMAFACTORY}" == "1" ]]; then
  if [[ ! -d "${LLAMAFACTORY_DIR}/.git" ]]; then
    echo "[bootstrap] cloning LLaMA-Factory"
    git clone "${LLAMAFACTORY_REPO}" "${LLAMAFACTORY_DIR}"
  fi
  echo "[bootstrap] checking out LLaMA-Factory commit ${LLAMAFACTORY_COMMIT}"
  git -C "${LLAMAFACTORY_DIR}" fetch --depth 1 origin "${LLAMAFACTORY_COMMIT}" || true
  git -C "${LLAMAFACTORY_DIR}" checkout "${LLAMAFACTORY_COMMIT}"
  "${CONDA_BIN}" run -n "${ENV_NAME}" pip install -e "${LLAMAFACTORY_DIR}"
else
  echo "[bootstrap] skipping external LLaMA-Factory install"
fi

echo "[bootstrap] installing repo editable package"
"${CONDA_BIN}" run -n "${ENV_NAME}" pip install -e "${REPO_ROOT}"

echo "[bootstrap] recommended cache exports:"
echo "  export HF_HOME=${ARTIFACT_ROOT}/cache/huggingface"
echo "  export MODELSCOPE_CACHE=${ARTIFACT_ROOT}/cache/modelscope"
echo "  export PIP_CACHE_DIR=${ARTIFACT_ROOT}/cache/pip"
echo "  export USE_MODELSCOPE_HUB=1"

TORCH_PRESENT="1"
if ! "${CONDA_BIN}" run -n "${ENV_NAME}" python -c "import torch" >/dev/null 2>&1; then
  TORCH_PRESENT="0"
fi

if [[ "${RUN_CHECKS}" == "1" ]]; then
  if [[ "${TORCH_PRESENT}" == "0" ]]; then
    echo "[bootstrap] torch is not installed in ${ENV_NAME}; skipping validation" >&2
    echo "[bootstrap] install torch manually, then rerun with --skip-llamafactory if needed" >&2
    exit 0
  fi
  echo "[bootstrap] running pytest"
  "${CONDA_BIN}" run -n "${ENV_NAME}" bash -lc "cd '${REPO_ROOT}' && python -m pytest -q"
  echo "[bootstrap] running environment probe"
  "${CONDA_BIN}" run -n "${ENV_NAME}" bash -lc "cd '${REPO_ROOT}' && python scripts/check_train_env.py"
fi

echo "[bootstrap] done"
