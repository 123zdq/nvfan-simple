from pynvml import (
    NVML_TEMPERATURE_GPU,
    nvmlDeviceGetFanSpeed,
    nvmlDeviceGetTemperature,
    nvmlDeviceSetDefaultFanSpeed_v2,
    nvmlDeviceSetFanSpeed_v2,
)
from Curve import Curve


class GPU:
    """单块 GPU 的风扇管理。"""

    def __init__(self, idx: int, handle, fan_count: int, name: str, curve: Curve):
        """idx: GPU 索引; handle: NVML 句柄; fan_count: 风扇数; name: GPU 名称; curve: 风扇曲线。"""
        self.idx = idx
        self.handle = handle
        self.fan_count = fan_count
        self.name = name
        self.curve = curve
        self.prev_temp = 0
        self.step_down_temp = 0
        self.current_fan = nvmlDeviceGetFanSpeed(handle)
        self.set_fan(self.current_fan)

    def get_temp(self) -> int:
        """读取 GPU 核心温度。"""
        return nvmlDeviceGetTemperature(self.handle, NVML_TEMPERATURE_GPU)

    def set_fan(self, speed: int) -> None:
        """设置所有风扇转速百分比。"""
        for i in range(self.fan_count):
            nvmlDeviceSetFanSpeed_v2(self.handle, i, speed)

    def set_default_fan(self) -> None:
        """恢复所有风扇为默认自动模式。"""
        for i in range(self.fan_count):
            nvmlDeviceSetDefaultFanSpeed_v2(self.handle, i)
