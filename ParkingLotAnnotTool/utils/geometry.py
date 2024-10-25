from typing import Self
from math import acos
from math import sqrt
from ParkingLotAnnotTool.utils.math import *


class Vector2d:
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Triangle2d:

    def __init__(self,
                 x1: float, y1: float,
                 x2: float, y2: float,
                 x3: float, y3: float):
        self.empty: bool = False
        self.x1: float = x1
        self.y1: float = y1
        self.x2: float = x2
        self.y2: float = y2
        self.x3: float = x3
        self.y3: float = y3

    def p1(self) -> tuple[float, float]:
        return (self.x1, self.y1)
    
    def p2(self) -> tuple[float, float]:
        return (self.x2, self.y2)

    def p3(self) -> tuple[float, float]:
        return (self.x3, self.y3)


def is_polygon_convex(
        xs: list[float],
        ys: list[float]
        ) -> bool:
    def cross_product_length(ax, ay, bx, by, cx, cy):
        bax = ax - bx
        bay = ay - by
        bcx = cx - bx
        bcy = cy - by
        return bax * bcy - bay * bcx
    got_negative = False
    got_positive = False
    num_points = len(xs)
    for a in range(num_points):
        b = (a + 1) % num_points
        c = (b + 1) % num_points
        cross_product = cross_product_length(xs[a], ys[a], xs[b], ys[b], xs[c], ys[c])
        if cross_product < 0:
            got_negative = True
        if cross_product > 0:
            got_positive = True
        if got_negative and got_positive:
            return False
    return True