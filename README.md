# nvfan-simple

在 Ubuntu (headless) 中运行的简单 NVIDIA GPU 风扇控制器 

## 支持

* 多 GPU

* 自定义温控曲线（不想折腾保持默认配置即可）

## 需求

* 已有 Nvidia GPU 且已安装驱动
* 已安装 uv（Python 环境管理工具）

## 安装

**步骤 1：设置 Python 环境**

```bash
bash update.sh
```

**步骤 2：安装 systemd 服务**

```bash
sudo bash service_setup.sh
```

## 卸载

```bash
sudo bash uninstall.sh
```

## 配置

编辑 `config.toml`：

```toml
# 风扇曲线：[温度点] -> [风扇转速%]
# 温度范围：0-90°C，转速范围：0-100%
temp_points = [30, 40, 50, 65, 70]
fan_points = [0, 10, 40, 100, 100]

# 迟滞：温度下降多少度才允许降低风扇转速（防止震荡）
hysteresis = 5

# 控制循环间隔（秒）
sleep = 3
```

曲线会在相邻温度点之间线性插值。高温端会自动强制到 (90°C, 100%)。

## 服务管理

```bash
sudo systemctl status|start|stop|restart nvfan-simple
```

## 手动运行
不推荐，因为这种方式要占用一个终端窗口
```bash
bash gpu-fan.sh
```

## 关于本项目

* Nvidia GPU的默认曲线功率不够，而大多数GPU风扇软件要么只支持Windows，要么支持Ubuntu但需要GUI，索性自己找方案DIY了一个，主要是给自己的服务器用

* 基于这个项目 [nvidia_fan_control_linux](https://github.com/RoversX/nvidia_fan_control_linux)，修复了它在多GPU情况下的bug，增加了将该工具注册为ubuntu的service的功能
