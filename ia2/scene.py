"""Scene/transformation system: point wrappers, z-ordering, 3D view ordering."""

import math
from statistics import mean

import cairo
import numpy as np
from scipy.spatial.transform import Rotation


class ScaledPoint:
    """A point wrapper that applies scaling transformations."""

    def __init__(self, p, origin, scalefactor, rotation):
        self.origin = origin
        self.p = p
        self.scalefactor = scalefactor
        self.rotation = rotation

    def __getitem__(self, index):
        if self.p[index] is None:
            return None
        return (self.p[index] - self.origin[index]) / self.scalefactor

    def __setitem__(self, index, value):
        self.p[index] = value * self.scalefactor + self.origin[index]

    def __repr__(self):
        return str(list(self))


class DeltaPoint:
    """A point wrapper that applies an offset transformation."""

    def __init__(self, p, offset):
        self.p = p
        self.offset = offset

    def __getitem__(self, i):
        if self.p[i] is None:
            return None
        if self.offset[i] is None:
            return None
        return self.p[i] + self.offset[i]

    def __setitem__(self, i, value):
        if value is None:
            self.offset[i] = None
        else:
            self.offset[i] = value - self.p[i]

    def __repr__(self):
        return repr(list(self))

    def __json__(self):
        return list(self)

    def __eq__(self, o):
        if o is None:
            return False
        return list(self) == list(o)


ComputedPoint = DeltaPoint


class PointWrapper:
    """A wrapper for point objects that handles None values gracefully."""

    def __init__(self, p):
        self.p = p

    def __getitem__(self, i):
        if self.p is None:
            return None
        if self.p[i] is None:
            return None
        return self.p[i]

    def __setitem__(self, i, value):
        if value is None:
            self.p = None
        else:
            self.p[i] = value

    def __repr__(self):
        return repr(list(self))

    def __json__(self):
        return list(self)

    def __eq__(self, o):
        if o is None:
            return False
        return list(self) == list(o)


def transformation(p, scalefactor, rotation):
    """Create a Cairo transformation matrix for scaling and rotation."""
    m = cairo.Matrix()
    m.translate(*p)
    m.scale(scalefactor[0], scalefactor[0])
    m.rotate(rotation)
    return m


class Ref:
    """A reference wrapper for generators; use +ref to get next value."""

    def __init__(self, gen):
        self.gen = gen

    def __pos__(self):
        return next(self.gen)


class Value:
    """A simple value wrapper with +value access and indexing."""

    def __init__(self, value):
        self.value = value

    def __pos__(self):
        return self.value

    def __getitem__(self, key):
        if key == 0:
            return self.value
        raise IndexError()

    def __setitem__(self, key, value):
        if key == 0:
            self.value = value
        else:
            raise IndexError()

    def __len__(self):
        return 1


class ZOrderList:
    """A list wrapper that sorts elements by z-coordinate for depth ordering."""

    def __init__(self, elements):
        self.elements = elements

    def __iter__(self):
        sorted_elements = sorted(self.elements, key=lambda x: x[0][2])
        for e in sorted_elements:
            yield e[1]


class ThreeDMidPoint:
    """Dynamic midpoint between two 3D points."""

    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1

    def __getitem__(self, i):
        if self.p0[i] is None or self.p1[i] is None:
            return None
        return (self.p0[i] + self.p1[i]) / 2


class TwoDMidPoint:
    """Dynamic midpoint between two 2D points."""

    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1

    def __getitem__(self, i):
        if self.p0[i] is None or self.p1[i] is None:
            return None
        return (self.p0[i] + self.p1[i]) / 2


class JoinedLists:
    """Combines multiple lists into a single iterable/indexable interface."""

    def __init__(self, *lists):
        self.lists = lists

    def __iter__(self):
        for item in self.lists:
            for e in item:
                yield e

    def __len__(self):
        return sum(len(item) for item in self.lists)

    def __getitem__(self, key):
        if key < 0:
            key += len(self)
        if key < 0 or key >= len(self):
            raise IndexError("list index out of range")
        for item in self.lists:
            if key < len(item):
                return item[key]
            key -= len(item)

    def __setitem__(self, key, value):
        if key < 0:
            key += len(self)
        if key < 0 or key >= len(self):
            raise IndexError("list index out of range")
        for item in self.lists:
            if key < len(item):
                item[key] = value
                return
            key -= len(item)

    def pop(self, key):
        if key < 0:
            key += len(self)
        if key < 0 or key >= len(self):
            raise IndexError("list index out of range")
        for item in self.lists:
            if key < len(item):
                return item.pop(key)
            key -= len(item)

    def insert(self, key, value):
        if key < 0:
            key += len(self)
        if key < 0:
            key = 0
        if key > len(self):
            key = len(self)

        for item in self.lists:
            if key < len(item):
                item.insert(key, value)
                return
            elif key == len(item):
                if item is self.lists[-1]:
                    item.append(value)
                    return
                else:
                    key -= len(item)
            else:
                key -= len(item)

        if self.lists:
            self.lists[-1].append(value)

    def remove(self, value):
        for item in self.lists:
            if value in item:
                item.remove(value)
                return
        raise ValueError("x not in list")


class ViewOrderList:
    """Orders elements by projected x-position."""

    def __init__(self, elements, start=0, end=None):
        self.elements = elements
        self.start = start
        self.end = end

    def __iter__(self):
        v_e = []
        for e in self.elements:
            v_e.append([mean([x[0] for x in e[0]]), e[1]])
        v_e = sorted(v_e, key=lambda x: x[0])
        for e in v_e[self.start : self.end]:
            yield e[1]


class ViewOrderList2:
    """Orders elements by projected z-distance using 3D rotation."""

    def __init__(self, elements, scene, start=0, end=None, fn=mean):
        self.elements = elements
        self.scene = scene
        self.start = start
        self.end = end
        self.fn = fn

    def __iter__(self):
        angle_x = self.scene["x_angle"]
        angle_y = self.scene["y_angle"]
        angle_z = self.scene["z_angle"]

        order = self.scene.get("rotation_order", "xyz")
        if order == "yxz":
            rotation_m = Rotation.from_euler("yxz", [angle_y, angle_x, angle_z])
        elif order == "zxy":
            rotation_m = Rotation.from_euler("zxy", [angle_z, angle_x, angle_y])
        else:
            rotation_m = Rotation.from_euler("xyz", [angle_x, angle_y, angle_z])

        inv_m = rotation_m.inv()
        Y = inv_m.apply(np.array([[0, 0, -1]], np.float32))[0]

        def project(X):
            return np.dot(X, Y)

        v_e = []
        for e in self.elements:
            if e.points3d is None:
                v_e.append([math.inf, e])
            elif len(e.points3d) == 0:
                v_e.append([-math.inf, e])
            else:
                v_e.append([self.fn([project(x) for x in e.points3d]), e])

        v_e = sorted(v_e, key=lambda x: x[0])
        for e in v_e[self.start : self.end]:
            yield e[1]


class ViewOrderList3:
    """Orders elements by projected z-distance from points and a function fn."""

    def __init__(self, elements, scene, start=0, end=None, fn=mean):
        self.elements = elements
        self.scene = scene
        self.start = start
        self.end = end
        self.fn = fn

    def __iter__(self):
        angle_x = self.scene["x_angle"]
        angle_y = self.scene["y_angle"]
        angle_z = self.scene["z_angle"]

        order = self.scene.get("rotation_order", "xyz")
        if order == "yxz":
            rotation_m = Rotation.from_euler("yxz", [angle_y, angle_x, angle_z])
        elif order == "zxy":
            rotation_m = Rotation.from_euler("zxy", [angle_z, angle_x, angle_y])
        else:
            rotation_m = Rotation.from_euler("xyz", [angle_x, angle_y, angle_z])

        inv_m = rotation_m.inv()
        Y = inv_m.apply(np.array([[0, 0, -1]], np.float32))[0]

        def project(X):
            return np.dot(X, Y)

        v_e = []
        for e in self.elements:
            if len(e[0]) == 0:
                v_e.append([-math.inf, e[1]])
            else:
                v_e.append([self.fn([project(x) for x in e[0]]), e[1]])

        v_e = sorted(v_e, key=lambda x: x[0])
        for e in v_e[self.start : self.end]:
            yield e[1]


class ViewOrderList4:
    """Filters and orders elements by face normal dot product with view vector."""

    def __init__(self, anim, elements, scene, start=0, end=None):
        self.anim = anim
        self.elements = elements
        self.scene = scene
        self.start = start
        self.end = end

    def __iter__(self):
        angle_x = self.scene["x_angle"]
        angle_y = self.scene["y_angle"]
        angle_z = self.scene["z_angle"]

        order = self.scene.get("rotation_order", "xyz")
        if order == "yxz":
            rotation_m = Rotation.from_euler("yxz", [angle_y, angle_x, angle_z])
        elif order == "zxy":
            rotation_m = Rotation.from_euler("zxy", [angle_z, angle_x, angle_y])
        else:
            rotation_m = Rotation.from_euler("xyz", [angle_x, angle_y, angle_z])

        inv_m = rotation_m.inv()
        Y = inv_m.apply(np.array([[0, 0, -1]], np.float32))[0]

        def project(X):
            return np.dot(X, Y) / np.linalg.norm(Y)

        v_e = []
        for e in self.elements:
            points = e[0]
            v1 = points[1] - points[0]
            v2 = points[2] - points[0]
            normal = np.cross(v1, v2)
            normal = normal / np.linalg.norm(normal)
            v_e.append([project(normal), e[1]])

        v_e = sorted(v_e, key=lambda x: x[0])
        for e in v_e[self.start : self.end]:
            yield e[1]
