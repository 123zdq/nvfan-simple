"""GDDR6/GDDR6X 显存温度读取，通过 mmap /dev/mem 直接读取 GPU 内存传感器寄存器。"""

import os
import struct
import mmap

# 支持的 GPU 设备 ID → (offset, 名称) 映射
_DEV_TABLE = {
    0x2204: (0xE2A8, "RTX 3090 GDDR6X"),
    0x2203: (0xE2A8, "RTX 3090 Ti GDDR6X"),
    0x2208: (0xE2A8, "RTX 3080 Ti GDDR6X"),
    0x2206: (0xE2A8, "RTX 3080 GDDR6X"),
    0x2216: (0xE2A8, "RTX 3080 LHR GDDR6X"),
    0x2484: (0xEE50, "RTX 3070 GDDR6"),
    0x2488: (0xEE50, "RTX 3070 LHR GDDR6"),
    0x2531: (0xE2A8, "RTX A2000 GDDR6"),
    0x2571: (0xE2A8, "RTX A2000 GDDR6"),
    0x2232: (0xE2A8, "RTX A4500 GDDR6"),
    0x2231: (0xE2A8, "RTX A5000 GDDR6"),
    0x2236: (0xE2A8, "A10 GDDR6"),
    0x2684: (0xE2A8, "RTX 4090 GDDR6X"),
    0x2685: (0xE2A8, "RTX 4090 D GDDR6X"),
    0x2702: (0xE2A8, "RTX 4080 Super GDDR6X"),
    0x2704: (0xE2A8, "RTX 4080 GDDR6X"),
    0x2705: (0xE2A8, "RTX 4070 Ti Super GDDR6X"),
    0x2782: (0xE2A8, "RTX 4070 Ti GDDR6X"),
    0x2783: (0xE2A8, "RTX 4070 Super GDDR6X"),
    0x2786: (0xE2A8, "RTX 4070 GDDR6X"),
    0x2860: (0xE2A8, "RTX 4070 Max-Q GDDR6"),
    0x26B1: (0xE2A8, "RTX A6000 GDDR6"),
    0x27b8: (0xE2A8, "L4 GDDR6"),
    0x26b9: (0xE2A8, "L40S GDDR6"),
}

PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")


class VRAM:
    """单块 GPU 的显存温度读取。"""

    def __init__(self, bar0: int, offset: int, name: str) -> None:
        """bar0: PCI BAR0 基地址; offset: 温度寄存器偏移; name: GPU 名称。"""
        self._name = name
        self._phys = bar0 + offset
        self._base = self._phys & ~(PAGE_SIZE - 1)
        self._disp = self._phys - self._base
        self._fd = -1
        self._mm = None

    def __enter__(self) -> "VRAM":
        self.open()
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def open(self) -> None:
        """打开 /dev/mem 并 mmap 目标页。"""
        self._fd = os.open("/dev/mem", os.O_RDONLY)
        self._mm = mmap.mmap(self._fd, PAGE_SIZE, access=mmap.ACCESS_READ, offset=self._base)

    def close(self) -> None:
        """关闭 mmap 和文件描述符。"""
        if self._mm is not None:
            self._mm.close()
            self._mm = None
        if self._fd != -1:
            os.close(self._fd)
            self._fd = -1

    def get_temp(self) -> int:
        """读取显存温度（摄氏度）。"""
        raw = struct.unpack_from("I", self._mm, self._disp)[0]
        return (raw & 0xFFF) // 0x20

    @classmethod
    def detect_all(cls) -> list["VRAM"]:
        """扫描系统，返回所有支持的 GPU 的 VRAM 实例（未 mmap，需调用 open()）。"""
        result: list[VRAM] = []
        pci_sys = "/sys/bus/pci/devices"

        for dev_name in sorted(os.listdir(pci_sys)):
            dev_dir = os.path.join(pci_sys, dev_name)

            vendor_path = os.path.join(dev_dir, "vendor")
            with open(vendor_path, "r") as f:
                vendor = int(f.read().strip(), 16)

            if vendor != 0x10DE:
                continue

            device_path = os.path.join(dev_dir, "device")
            with open(device_path, "r") as f:
                device_id = int(f.read().strip(), 16)

            if device_id not in _DEV_TABLE:
                continue

            offset, name = _DEV_TABLE[device_id]

            resource_path = os.path.join(dev_dir, "resource")
            with open(resource_path, "r") as f:
                bar0 = int(f.readline().split()[0], 16)

            result.append(VRAM(bar0, offset, name))

        return result
