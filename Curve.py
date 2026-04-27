"""风扇曲线：断点定义 + 线性插值。"""

from typing import List


class Curve:
    x: List[int]
    y: List[int]

    @classmethod
    def normalize(cls, x_points: List[int], y_points: List[int], x_max: int = 90, y_max: int = 100) -> "Curve":
        """规范化曲线：补充边界点、裁剪越界值、去重合并、确保单调不降。
        
        Args:
            x_points: 温度断点列表
            y_points: 转速断点列表
            x_max: x 轴最大值（温度上限，默认 90°C）
            y_max: y 轴最大值（转速上限，默认 100%）
        """
        if len(x_points) != len(y_points):
            raise ValueError(f"x_points and y_points must have the same length: " f"{len(x_points)} != {len(y_points)}")
        x_points = list(x_points) + [0, x_max]
        y_points = list(y_points) + [0, y_max]
        curve: dict[int, int] = {}
        for xt, yt in zip(x_points, y_points):
            xt, yt = max(0, min(x_max, xt)), max(0, min(y_max, yt))
            curve[xt] = max(curve.get(xt, 0), yt)
        x: List[int] = []
        y: List[int] = []
        prev = 0
        for xt in sorted(curve):
            yt = max(curve[xt], prev)
            prev = yt
            x.append(xt)
            y.append(yt)
        return cls(x, y)

    def __init__(self, x: List[int], y: List[int]) -> None:
        self.x = x
        self.y = y

    def __call__(self, x_value: int) -> int:
        """根据温度值线性插值，返回对应转速。"""
        point = 0
        while point < len(self.x) - 1 and x_value >= self.x[point + 1]:
            point += 1
        if point == len(self.x) - 1:
            return self.y[-1]
        delta = self.x[point + 1] - self.x[point]
        return max(0, min(self.y[-1], round(self.y[point] + (self.y[point + 1] - self.y[point]) * (x_value - self.x[point]) / delta)))
