# AGENTS.md — nvfan-simple

## 项目概述

NVIDIA GPU 风扇控制器 + 硬件平台调优（2× RTX 3090）。Python 多模块 + systemd 服务 + shell 脚本。

## 开发命令

```bash
# 设置/更新 Python 环境（无需 sudo，依赖 uv）
bash update.sh

# 手动运行（前台，占用终端，含 GPU 优化 nvidia-smi 命令）
bash gpu-fan.sh

# 安装/更新 systemd 服务（需 sudo）
sudo bash service_setup.sh

# 服务管理
sudo systemctl status|start|stop|restart nvfan-simple

# 卸载
sudo bash uninstall.sh
```

## 关键约束

- **必须 root 权限运行** — `nvmlDeviceSetFanSpeed_v2` 和 sysfs hwmon PWM 写入都需要 root
- **依赖 `uv`** 管理虚拟环境，不是 venv/pip/poetry。Python 3.12（`update.sh` 硬编码）
- **最低 Python 3.11** — `tomllib` 是 3.11+ 内置模块
- **唯一第三方 Python 依赖**: `nvidia-ml-py`（pynvml）
- **pynvml 导入风格**: 显式导入（`from pynvml import nvmlInit, ...`），不是 `from pynvml import *`
- **无测试、无 linter、无 typechecker** — 修改后手动运行 `bash gpu-fan.sh` 验证
- **systemd 服务名**: `nvfan-simple`

## 架构

| 文件 | 作用 |
|------|------|
| `nvidia_fan_control.py` | 主入口 `main()`，控制循环，~140 行 |
| `Curve.py` | 风扇曲线：断点定义 + 归一化 + 线性插值（可调用对象） |
| `GPU.py` | 单 GPU 风扇管理（pynvml 封装） |
| `SysFan.py` | 系统风扇管理（sysfs hwmon3/pwm8，0-255 PWM 占空比） |
| `config.toml` | 风扇曲线配置；启动时读取一次，修改后重启服务生效 |
| `gpu-fan.sh` | 手动启动；先执行 GPU 优化命令（persistence/功耗墙/目标温度），再激活 venv 运行 Python |
| `service_setup.sh` | sed 替换 `service.template` 中的 `%SCRIPT_DIR%` → 实际路径，写入 `/etc/systemd/system/` |
| `service.template` | systemd unit 模板；修改后必须重新运行 `service_setup.sh` |
| `update.sh` | git pull + uv venv + uv pip install；不依赖 sudo |
| `uninstall.sh` | 停止、禁用、删除 systemd 服务 |

## 控制流程

1. `config.toml` → `Curve.normalize()` 构建 GPU 风扇曲线 + 系统风扇曲线
2. 枚举 GPU，跳过无风扇设备
3. 主循环（每 `sleep` 秒）：
   - 读取所有 GPU 温度 → 插值算转速 → 迟滞防抖 → 写入风扇
   - 读取 GPU 0 温度 → 插值算 PWM 占空比 → 写 `hwmon3/pwm8`
4. 退出（信号/异常）：恢复所有 GPU 风扇为自动模式 + `nvmlShutdown()`

## 硬件平台相关

- `SysFan.py` 硬编码 `hwmon3/pwm8` — 路径随硬件变化
- `gpu-fan.sh` 中的 GPU 优化命令硬编码 `-i 0,1`（2 块 3090）
- `gddr6/` — GDDR6 显存温度读取（[olealgoritme/gddr6](https://github.com/olealgoritme/gddr6)），需 `iomem=relaxed` + 关 Secure Boot
- `nct6687d/` — 主板 NCT6687D 传感器驱动（[Fred78290/nct6687d](https://github.com/Fred78290/nct6687d)），加载后才能暴露 hwmon 接口

## Shell 脚本约定

- 所有脚本 `set -e` 严格模式
- `SCRIPT_DIR` 统一用 `cd "$(dirname "${BASH_SOURCE[0]}")" && pwd` 模式

## 外部参考

- 想法源于: [nvidia_fan_control_linux](https://github.com/RoversX/nvidia_fan_control_linux)
- pynvml 风扇 API 参考: `docs/fan_speed_api.md`
- pynvml 温度 API 参考: `docs/temperature_api.md`
- GPU 功耗/温度/时钟调参: `POWER_TEMP_WALLS.md`
- Python 兼容性: `docs/COMPATIBILITY.md`
