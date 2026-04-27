# nvfan-simple

Ubuntu 服务器上的 NVIDIA GPU 风扇控制器 + 硬件平台调优工具。

## 项目分层

| 层级 | 功能 | 通用性 |
|------|------|--------|
| **GPU 风扇控制** | GPU 核心温度 → GPU 内部风扇转速 | ✅ 通用（pynvml + nvidia-smi 即可） |
| **平台调优** | 系统风扇控制、GPU 参数调整、显存温度读取、主板传感器驱动 | 🔧 针对作者硬件（2× RTX 3090） |

---

## GPU 风扇控制（通用）

基于 [nvidia_fan_control_linux](https://github.com/RoversX/nvidia_fan_control_linux) 改造：修复了多 GPU bug，拆分模块，增加 systemd 服务支持。

**功能：**
- 多 GPU 支持
- 自定义温度-转速曲线（线性插值）
- 迟滞防抖（防止温度临界时风扇频繁波动）
- 退出时自动恢复风扇自动模式

### 需求

- 已有 NVIDIA GPU 且已安装驱动
- 已安装 `uv`（Python 包管理工具）

### 安装

```bash
# 设置 Python 环境
bash update.sh

# 安装 systemd 服务
sudo bash service_setup.sh
```

### 卸载

```bash
sudo bash uninstall.sh
```

### 配置

编辑 `config.toml`：

```toml
# 风扇曲线：[温度点] -> [风扇转速%]
# 温度范围：0-90°C，转速范围：0-100%
temp_points = [30, 40, 55, 65, 70]
fan_points = [0, 10, 40, 100, 100]

# 迟滞：温度下降多少度才允许降低风扇转速（防止震荡）
hysteresis = 5

# 控制循环间隔（秒）
sleep = 3
```

曲线在相邻温度点之间线性插值，(90°C, 100%) 会自动添加为终点。

### 服务管理

```bash
sudo systemctl status|start|stop|restart nvfan-simple
```

### 手动运行（调试用）

```bash
bash gpu-fan.sh
```

---

## 平台调优

以下功能针对作者特定硬件平台，不一定适用于其他机器。

### 系统风扇控制

一块接在主板 SYSFAN 接口的风扇用于给 GPU 背板散热。因为它的温度源来自 GPU（而非主板传感器），无法使用 `fancontrol` 等通用工具——`sensors` 仅识别主板和 CPU 的传感器，甚至主板支持也是靠找到 NCT6687D 的驱动才实现的。

程序读取 GPU 0 的核心温度，通过 `hwmon3/pwm8` 接口（0-255 占空比）PWM 调节系统风扇。配置在 `config.toml` 的 `[sysfan]` 段：

```toml
[sysfan]
temp_points = [0, 40, 50, 60]
duty_points = [0, 63, 128, 255]
```

### GPU 参数调整

`gpu-fan.sh` 启动前会自动执行以下优化命令（`nvidia-smi`）：

```bash
# Persistence mode — 驱动常驻，减少降频
sudo nvidia-smi -pm 1 -i 0,1
# 功耗墙
sudo nvidia-smi -pl 380 -i 0,1
# 目标温度
sudo nvidia-smi -gtt 88 -i 0,1
```

更多功耗/温度/时钟调节命令参考 `POWER_TEMP_WALLS.md`。

### 显存温度（GDDR6）

RTX 3090 的显存温度无法通过 `nvidia-smi` 直接读取。使用 [olealgoritme/gddr6](https://github.com/olealgoritme/gddr6)——通过逆向 NVIDIA 驱动找出了 GDDR6/GDDR6X 显存温度在 GPU 内存映射寄存器中的偏移，直接读取硬件传感器值。

```bash
# 需内核启动参数 iomem=relaxed，关闭 Secure Boot
sudo gddr6
```

### 主板传感器驱动

主板 Super I/O 芯片 Nuvoton NCT6687D 的内核驱动 [Fred78290/nct6687d](https://github.com/Fred78290/nct6687d)，通过逆向 LibreHardwareMonitor 的 Windows 源实现。驱动加载后 `lm-sensors` 可识别主板电压、温度、风扇 RPM，并暴露 sysfs hwmon 接口（`hwmon3/pwm8`）供程序控制系统风扇。

---

## 项目结构

| 文件/目录 | 说明 |
|-----------|------|
| `nvidia_fan_control.py` | 主入口，控制循环 |
| `Curve.py` | 风扇曲线：断点定义 + 线性插值 |
| `GPU.py` | 单 GPU 风扇管理（pynvml） |
| `SysFan.py` | 系统风扇管理（sysfs hwmon PWM） |
| `config.toml` | 风扇曲线配置 |
| `gpu-fan.sh` | 手动启动脚本（含 GPU 优化命令） |
| `service_setup.sh` | 安装/更新 systemd 服务 |
| `update.sh` | 拉取代码 + 更新 Python 环境 |
| `gddr6/` | GDDR6 显存温度读取工具 |
| `nct6687d/` | 主板传感器芯片内核驱动 |
| `POWER_TEMP_WALLS.md` | GPU 功耗/温度/时钟调参参考 |
| `docs/` | pynvml API 参考文档 |

## 关于

NVIDIA GPU 默认风扇曲线不够激进，而大多数 GPU 风扇控制工具要么只支持 Windows，要么在 Linux 下需要 GUI。本项目最初为自己的服务器打造，通用部分（GPU 风扇控制）可直接用于任何 NVIDIA GPU，平台调优部分供同型号硬件参考。
