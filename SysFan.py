"""主板风扇控制，通过 sysfs hwmon 接口调节 PWM。"""

import os
import atexit

from Curve import Curve


def default_sysfan_curve() -> Curve:
    """默认系统风扇曲线：0°C 停转，60°C 全速。"""
    return Curve.normalize([0, 40, 50, 60], [0, 63, 128, 255], y_max=255)


class SysFan:
    """主板风扇管理（hwmon3 pwm8）。"""

    BASE = "/sys/class/hwmon/hwmon3"
    FAN_IDX = 8

    def __init__(self):
        self.pwm_path = os.path.join(self.BASE, f"pwm{self.FAN_IDX}")
        self.enable_path = os.path.join(self.BASE, f"pwm{self.FAN_IDX}_enable")
        self.current_duty = 0

        self._set_manual()
        atexit.register(self._set_auto)

    def _write_sysfs(self, path: str, value: str) -> None:
        """写入 sysfs 节点。"""
        with open(path, 'w') as f:
            f.write(value)

    def _set_manual(self) -> None:
        """切换到手动模式。"""
        self._write_sysfs(self.enable_path, "1")

    def _set_auto(self) -> None:
        """恢复自动模式。"""
        self._write_sysfs(self.enable_path, "99")

    def set_duty(self, duty: int) -> None:
        """设置 PWM 占空比（0-255）。"""
        duty = max(0, min(255, duty))
        self._write_sysfs(self.pwm_path, str(duty))
        self.current_duty = duty
