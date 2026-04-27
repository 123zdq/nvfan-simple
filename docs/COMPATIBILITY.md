# 兼容性说明

## Python 版本

| 版本 | 状态 |
|------|------|
| Python 3.11 | 最低要求（`tomllib` 内置模块） |
| Python 3.12 | 当前使用（`update.sh` 硬编码） |

**`tomllib` 是 Python 3.11 引入的内置模块，无法降级到 3.10 及以下。**

## 操作系统

- **Ubuntu LTS** (headless 服务器)
- 需要 systemd
- 需要 NVIDIA 专有驱动（提供 NVML 库）

| Ubuntu | 系统 Python | 兼容性 |
|--------|------------|--------|
| 22.04 | 3.10 | ⚠️ 需额外安装 Python 3.11+ 或使用项目 `.venv` |
| 24.04 | 3.12 | ✅ 推荐 |

> `update.sh` 会通过 `uv venv --python 3.12` 创建独立环境，不依赖系统 Python 版本。

## 依赖

### Python

| 包 | 用途 | 约束 |
|----|------|------|
| `nvidia-ml-py` | pynvml，NVIDIA NVML 的 Python 绑定 | 唯一第三方依赖；无硬版本要求 |

### 系统

| 依赖 | 用途 |
|------|------|
| `uv` | Python 包/environment 管理器（`update.sh` 必需） |
| `git` | 代码拉取（`update.sh`） |
| `nvidia-smi` | GPU 优化命令（`gpu-fan.sh`） |
| `nvml` (libnvidia-ml) | NVML C 库，由 NVIDIA 驱动提供 |
| root 权限 | `nvmlDeviceSetFanSpeed_v2` 及 sysfs hwmon 写入需要 root |

## 硬件

| 组件 | 说明 |
|------|------|
| NVIDIA GPU | Maxwell 架构或更新（手动风扇控制 API 的硬件要求），如 GTX 980 (GM204)、RTX 2080 (TU104)、RTX 3090 (GA102)、RTX 4090 (AD102) 等 |
| 主板风扇控制器 | 当前硬编码 `hwmon3/pwm8`，芯片参考 NCT6687D（可通过 `sensors-detect` 检测） |

## Python 特性使用

| 特性 | 最低版本 | 使用位置 |
|------|---------|---------|
| `tomllib` | 3.11 | `nvidia_fan_control.py` |
| f-string | 3.6 | 全项目 |
| 类型注解 (`->`, `List[T]`) | 3.6 | 全项目 |
| `typing.List` | 3.5 | `Curve.py` |
