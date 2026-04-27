# AGENTS.md — nvfan-simple

## 项目概述

NVIDIA GPU 风扇控制器，运行在 Ubuntu (headless) 服务器。单文件 Python 应用 + systemd 服务。

## 架构速览

| 文件 | 作用 |
|------|------|
| `nvidia_fan_control.py` | 核心逻辑，入口 `main()`，~191 行 |
| `config.toml` | 风扇曲线配置（修改后重启服务即生效） |
| `gpu-fan.sh` | 手动运行脚本（激活 venv + 启动 Python） |
| `service_setup.sh` | 安装/更新 systemd 服务（需要 sudo） |
| `service.template` | systemd unit 模板，`%SCRIPT_DIR%` 占位符被 sed 替换 |
| `update.sh` | 拉取代码 + 创建/更新 Python 虚拟环境 |
| `uninstall.sh` | 停止并删除 systemd 服务 |

## 关键约束

- **依赖 `uv`** 管理 Python 虚拟环境，不是 venv/pipenv/poetry
- **唯一 Python 依赖**: `nvidia-ml-py` (pynvml)，通过 `uv pip install` 安装
- **Python 3.12**（hardcoded 在 `update.sh`），最低支持 3.9+
- **`from pynvml import *`** — 代码通篇 `from pynvml import *` 风格，修改时保持一致
- **`tomllib`** — Python 3.11+ 内置，用于读取 `config.toml`
- **systemd 服务名**: `nvfan-simple`
- **必须 root 权限运行** — NVML 的 `nvmlDeviceSetFanSpeed_v2` 需要 root，手动运行也要 `sudo`

## 开发命令

```bash
# 设置/更新环境（无需 sudo）
bash update.sh

# 手动运行（前台，占用终端）
bash gpu-fan.sh

# 安装/更新 systemd 服务（需 sudo）
sudo bash service_setup.sh

# 服务管理
sudo systemctl status|start|stop|restart nvfan-simple

# 卸载
sudo bash uninstall.sh
```

## 修改注意事项

1. **Python 代码** — 单文件 `nvidia_fan_control.py`，无测试、无 linter，修改后手动运行 `bash gpu-fan.sh` 验证
2. **config.toml 修改** — 重启服务即可生效（`sudo systemctl restart nvfan-simple`），配置在程序启动时读取一次
3. **service.template 修改** — 必须重新运行 `sudo bash service_setup.sh` 才能生效
4. **Shell 脚本修改** — 所有脚本用 `set -e` 严格模式，注意 `SCRIPT_DIR` 的 cd 模式

## 外部参考

- 上游: [nvidia_fan_control_linux](https://github.com/RoversX/nvidia_fan_control_linux)
- pynvml 温度 API 参考: `docs/temperature_api.md`
- Python 兼容性: `docs/COMPATIBILITY.md`
