"""GPU fan curve controller with hysteresis.

Interpolates fan speed linearly between user-defined (temp, speed) points,
and applies hysteresis to prevent rapid oscillation when temperature drops.
Resets fans to auto mode on exit.
"""

from pynvml import *
import signal
import time
import tomllib
import os


def load_config() -> dict:
    """Load configuration from config.toml.
    
    Returns:
        dict: Configuration dictionary containing temp_points, fan_points,
              hysteresis, and sleep settings.
    
    Raises:
        FileNotFoundError: If config.toml doesn't exist.
        tomllib.TOMLDecodeError: If config.toml is malformed.
    """
    config_path = os.path.join(os.path.dirname(__file__), "config.toml")
    with open(config_path, "rb") as f:
        return tomllib.load(f)


config = load_config()
TEMP_POINTS = config["temp_points"]
FAN_POINTS = config["fan_points"]
HYSTERESIS = config["hysteresis"]
SLEEP = config["sleep"]

running = True


def signal_handler(signum: int, frame) -> None:
    """Handle shutdown signals gracefully.
    
    Args:
        signum: Signal number received.
        frame: Current stack frame (unused).
    """
    global running
    running = False


def normalize_fan_curve():
    """Clamp, deduplicate, and enforce monotonicity on the fan curve.

    Clamps temps to [0, 90] and fan speeds to [0, 100]. Ensures (90, 100)
    endpoint exists. Deduplicates by temperature, at same temp keep higher fan
    speed. Enforces fan speed monotonically non-decreasing with temperature.
    """
    global TEMP_POINTS, FAN_POINTS
    TEMP_POINTS += [0, 90]
    FAN_POINTS += [0, 100]
    curve = {}
    for t, f in zip(TEMP_POINTS, FAN_POINTS):
        t, f = max(0, min(90, t)), max(0, min(100, f))
        curve[t] = max(curve.get(t, 0), f)
    TEMP_POINTS = []
    FAN_POINTS = []
    prev_fan = 0
    for t in sorted(curve.keys()):
        fan = max(curve[t], prev_fan)
        prev_fan = fan
        TEMP_POINTS.append(t)
        FAN_POINTS.append(fan)


class GPU:
    """Manages fan control for a single GPU.

    Attributes:
        idx: GPU index.
        handle: NVML device handle.
        fan_count: Number of fans on the GPU.
        name: GPU name.
        prev_temp: Previous temperature reading.
        step_down_temp: Temperature threshold for allowing fan speed decrease.
        current_fan: Current fan speed percentage.
    """

    def __init__(self, idx, handle, fan_count, name):
        self.idx = idx
        self.handle = handle
        self.fan_count = fan_count
        self.name = name
        self.prev_temp = 0
        self.step_down_temp = 0
        self.current_fan = nvmlDeviceGetFanSpeed(self.handle)
        self.set_fan(self.current_fan)

    def get_temp(self):
        return nvmlDeviceGetTemperature(self.handle, NVML_TEMPERATURE_GPU)

    def set_fan(self, speed):
        for i in range(self.fan_count):
            nvmlDeviceSetFanSpeed_v2(self.handle, i, speed)

    def set_default_fan(self):
        for i in range(self.fan_count):
            nvmlDeviceSetDefaultFanSpeed_v2(self.handle, i)

    def calc_fan_speed(self, temp):
        """Linearly interpolate fan speed between curve breakpoints."""
        point = 0
        while point < len(TEMP_POINTS) - 1 and temp >= TEMP_POINTS[point + 1]:
            point += 1
        if point == len(TEMP_POINTS) - 1:
            return 100

        temp_delta = TEMP_POINTS[point + 1] - TEMP_POINTS[point]
        fan_delta = FAN_POINTS[point + 1] - FAN_POINTS[point]
        temp_inc = temp - TEMP_POINTS[point]

        return max(FAN_POINTS[0], min(100, round(FAN_POINTS[point] + fan_delta * temp_inc / temp_delta)))


def main() -> None:
    """Main entry point for the GPU fan controller.
    
    Initializes the NVML library, detects available GPUs with fans,
    and enters the main control loop. Handles graceful shutdown on
    SIGTERM, SIGINT, and SIGHUP signals, restoring fans to auto mode.
    
    Raises:
        RuntimeError: If no GPUs or no GPUs with fans are detected.
    """
    global running
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    normalize_fan_curve()
    nvmlInit()
    gpus = []

    try:
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
                gpus.append(GPU(idx, handle, fan_count, name))

        print(f"Driver: {nvmlSystemGetDriverVersion()}")

        if not gpus:
            raise RuntimeError("No GPUs with fans detected")
        
        print("Running... (Ctrl+C to stop)")
        while running:
            for gpu in gpus:
                temp = gpu.get_temp()

                if temp < gpu.step_down_temp or temp > gpu.prev_temp:
                    fan = gpu.calc_fan_speed(temp)
                    gpu.prev_temp = temp
                    gpu.step_down_temp = temp - HYSTERESIS

                    if fan != gpu.current_fan:
                        gpu.set_fan(fan)
                        gpu.current_fan = fan
                        print(f"GPU{gpu.idx}: {temp}°C -> {fan}%")

            time.sleep(SLEEP)

    finally:
        if gpus:
            for gpu in gpus:
                gpu.set_default_fan()
            print("\nStopped, fans reset to auto mode")
        nvmlShutdown()


if __name__ == "__main__":
    main()
