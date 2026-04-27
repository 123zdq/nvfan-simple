"""GPU 风扇曲线控制器，带迟滞防抖。

在用户定义的温度-转速点之间线性插值，降温时应用迟滞防止风扇频繁波动。退出时恢复风扇自动模式。
"""

from pynvml import (
    nvmlDeviceGetCount,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetName,
    nvmlDeviceGetNumFans,
    nvmlInit,
    nvmlShutdown,
    nvmlSystemGetDriverVersion,
)
import signal
import time
import tomllib
import os

from Curve import Curve
from GPU import GPU
from SysFan import SysFan, default_sysfan_curve
from VRAM import VRAM


def load_config() -> dict:
    """读取同目录下的 config.toml 配置。"""
    config_path = os.path.join(os.path.dirname(__file__), "config.toml")
    with open(config_path, "rb") as f:
        return tomllib.load(f)


# 加载全局配置
config = load_config()
HYSTERESIS = config["hysteresis"]
SLEEP = config["sleep"]

# 系统风扇曲线（若配置了则使用配置值，否则用默认曲线）
sysfan_cfg = config.get("sysfan")
if sysfan_cfg:
    sysfan_curve = Curve.normalize(sysfan_cfg["temp_points"], sysfan_cfg["duty_points"], y_max=255)
else:
    sysfan_curve = default_sysfan_curve()

SYSFAN_HYSTERESIS = 20

# 主循环运行标志
running = True


def signal_handler(signum: int, frame) -> None:
    """收到退出信号时终止主循环。"""
    global running
    running = False


def main() -> None:
    """主入口：初始化 NVML → 检测带风扇的 GPU → 进入控制循环。

    收到 SIGTERM/SIGINT/SIGHUP 时优雅退出，恢复风扇自动模式。

    Raises:
        RuntimeError: 未检测到 GPU 或没有带风扇的 GPU。
    """
    global running

    # 注册信号处理器，支持优雅退出
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    # 构建风扇曲线并初始化 NVML
    fan_curve = Curve.normalize(config["temp_points"], config["fan_points"])
    nvmlInit()
    gpus = []
    vrams = []

    try:
        # 枚举 GPU 设备，只保留带风扇的
        print("Finding...")
        dev_count = nvmlDeviceGetCount()

        if dev_count == 0:
            raise RuntimeError("No GPUs detected on this system")

        for idx in range(dev_count):
            handle = nvmlDeviceGetHandleByIndex(idx)
            fan_count = nvmlDeviceGetNumFans(handle)
            name = nvmlDeviceGetName(handle)
            if fan_count == 0:
                print(f"GPU {idx}: {name} (no fans, skipping)")
            else:
                print(f"GPU {idx}: {name} ({fan_count} fans)")
                gpus.append(GPU(idx, handle, fan_count, name, fan_curve))

        print(f"Driver: {nvmlSystemGetDriverVersion()}")

        if not gpus:
            raise RuntimeError("No GPUs with fans detected")

        # 初始化系统风扇
        sysfan = SysFan()
        sysfan_prev_temp = 0
        sysfan_step_down_temp = 0

        # 初始化显存温度读取（失败则跳过，只影响 sysfan）
        vrams_raw = VRAM.detect_all()
        for v in vrams_raw:
            try:
                v.open()
                vrams.append(v)
            except Exception:
                pass

        # 主控制循环
        print("Running... (Ctrl+C to stop)")
        while running:
            # 读取所有 GPU 温度
            temps = [gpu.get_temp() for gpu in gpus]

            # 根据曲线和迟滞调整每块 GPU 的风扇转速
            for gpu, temp in zip(gpus, temps):
                if temp < gpu.step_down_temp or temp > gpu.prev_temp:
                    fan = gpu.curve(temp)
                    gpu.prev_temp = temp
                    gpu.step_down_temp = temp - HYSTERESIS

                    if fan != gpu.current_fan:
                        gpu.set_fan(fan)
                        gpu.current_fan = fan
                        print(f"GPU{gpu.idx}: {temp}°C -> {fan}%")

            # 根据 GPU0 显存温度调节系统风扇 PWM（迟滞 SYSFAN_HYSTERESIS）
            if vrams:
                sysfan_temp = vrams[0].get_temp()
                if sysfan_temp < sysfan_step_down_temp or sysfan_temp > sysfan_prev_temp:
                    duty = sysfan_curve(sysfan_temp)
                    sysfan_prev_temp = sysfan_temp
                    sysfan_step_down_temp = sysfan_temp - SYSFAN_HYSTERESIS
                    sysfan.set_duty(duty)

            time.sleep(SLEEP)

    # 退出时恢复所有风扇为自动模式
    finally:
        if gpus:
            for gpu in gpus:
                gpu.set_default_fan()
        for v in vrams:
            v.close()
        print("\nStopped, fans reset to auto mode")
        nvmlShutdown()


if __name__ == "__main__":
    main()
