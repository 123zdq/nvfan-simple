"""系统风扇测试脚本，调试 hwmon3 pwm8 接口。"""


def write_sysfs(path, value):
    """写入 sysfs 节点，失败时打印错误。"""
    try:
        with open(path, 'w') as f:
            f.write(str(value))
    except PermissionError:
        print("需要 root 权限，请用 sudo 运行")
    except OSError as e:
        print(f"写入失败: {e}")

# 切换风扇模式
write_sysfs("/sys/class/hwmon/hwmon3/pwm8_enable", 99)  # 自动模式
write_sysfs("/sys/class/hwmon/hwmon3/pwm8_enable", 1)   # 手动模式

# 只读参考（取消注释即可读取）
# fan8_input  — RPM 转速
# fan8_label  — 主板接口名称
# fan8_max    — 转速上限（校准时用）
# fan8_min    — 转速下限（校准时用）

# 设置 PWM 占空比（0-255）
write_sysfs("/sys/class/hwmon/hwmon3/pwm8", 255)


"""
参考: https://github.com/Fred78290/nct6687d

sensor 检测命令:
  sudo sensors-detect
  sensors
"""