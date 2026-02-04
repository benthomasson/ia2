"""Tests for ia2.scene: point wrappers, JoinedLists, Value, Ref, ZOrderList, etc."""

import cairo
import pytest

from ia2.scene import (
    DeltaPoint,
    JoinedLists,
    PointWrapper,
    Ref,
    ScaledPoint,
    ThreeDMidPoint,
    TwoDMidPoint,
    Value,
    ZOrderList,
    transformation,
)


class TestDeltaPoint:
    def test_getitem(self):
        p = [10, 20]
        offset = [5, 5]
        dp = DeltaPoint(p, offset)
        assert dp[0] == 15
        assert dp[1] == 25

    def test_setitem(self):
        p = [10, 20]
        offset = [0, 0]
        dp = DeltaPoint(p, offset)
        dp[0] = 30
        # offset should now be 30 - 10 = 20
        assert offset[0] == 20
        assert dp[0] == 30

    def test_repr(self):
        p = [10, 20]
        offset = [5, 5]
        dp = DeltaPoint(p, offset)
        assert repr(dp) == repr([15, 25])

    def test_eq_with_list(self):
        p = [10, 20]
        offset = [5, 5]
        dp = DeltaPoint(p, offset)
        assert dp == [15, 25]

    def test_eq_with_none(self):
        p = [10, 20]
        offset = [5, 5]
        dp = DeltaPoint(p, offset)
        assert dp != None  # noqa: E711

    def test_none_in_p(self):
        p = [None, 20]
        offset = [5, 5]
        dp = DeltaPoint(p, offset)
        assert dp[0] is None

    def test_none_in_offset(self):
        p = [10, 20]
        offset = [None, 5]
        dp = DeltaPoint(p, offset)
        assert dp[0] is None

    def test_setitem_none(self):
        p = [10, 20]
        offset = [5, 5]
        dp = DeltaPoint(p, offset)
        dp[0] = None
        assert offset[0] is None


class TestScaledPoint:
    def test_getitem(self):
        p = [100, 200]
        origin = [0, 0]
        sp = ScaledPoint(p, origin, 2, 0)
        assert sp[0] == 50
        assert sp[1] == 100

    def test_setitem(self):
        p = [0, 0]
        origin = [0, 0]
        sp = ScaledPoint(p, origin, 2, 0)
        sp[0] = 50
        assert p[0] == 100

    def test_with_origin_offset(self):
        p = [110, 220]
        origin = [10, 20]
        sp = ScaledPoint(p, origin, 2, 0)
        assert sp[0] == 50
        assert sp[1] == 100

    def test_none_value(self):
        p = [None, 200]
        origin = [0, 0]
        sp = ScaledPoint(p, origin, 2, 0)
        assert sp[0] is None


class TestPointWrapper:
    def test_normal_access(self):
        pw = PointWrapper([10, 20])
        assert pw[0] == 10
        assert pw[1] == 20

    def test_none_point(self):
        pw = PointWrapper(None)
        assert pw[0] is None
        assert pw[1] is None

    def test_none_element(self):
        pw = PointWrapper([None, 20])
        assert pw[0] is None
        assert pw[1] == 20

    def test_setitem(self):
        pw = PointWrapper([10, 20])
        pw[0] = 30
        assert pw[0] == 30

    def test_setitem_none_nullifies(self):
        pw = PointWrapper([10, 20])
        pw[0] = None
        assert pw.p is None

    def test_eq(self):
        pw = PointWrapper([10, 20])
        assert pw == [10, 20]

    def test_eq_none(self):
        pw = PointWrapper([10, 20])
        assert pw != None  # noqa: E711


class TestValue:
    def test_pos(self):
        v = Value(42)
        assert +v == 42

    def test_getitem_0(self):
        v = Value(42)
        assert v[0] == 42

    def test_getitem_out_of_range(self):
        v = Value(42)
        with pytest.raises(IndexError):
            v[1]

    def test_setitem_0(self):
        v = Value(42)
        v[0] = 99
        assert +v == 99

    def test_setitem_out_of_range(self):
        v = Value(42)
        with pytest.raises(IndexError):
            v[1] = 99

    def test_len(self):
        v = Value(42)
        assert len(v) == 1


class TestRef:
    def test_pos_advances_generator(self):
        def gen():
            yield 1
            yield 2
            yield 3

        r = Ref(gen())
        assert +r == 1
        assert +r == 2
        assert +r == 3

    def test_pos_exhausted(self):
        def gen():
            yield 1

        r = Ref(gen())
        assert +r == 1
        with pytest.raises(StopIteration):
            +r


class TestJoinedLists:
    def test_len(self):
        jl = JoinedLists([1, 2], [3, 4, 5])
        assert len(jl) == 5

    def test_iter(self):
        jl = JoinedLists([1, 2], [3, 4])
        assert list(jl) == [1, 2, 3, 4]

    def test_getitem(self):
        jl = JoinedLists([1, 2], [3, 4])
        assert jl[0] == 1
        assert jl[2] == 3
        assert jl[3] == 4

    def test_getitem_negative(self):
        jl = JoinedLists([1, 2], [3, 4])
        assert jl[-1] == 4
        assert jl[-2] == 3

    def test_getitem_out_of_range(self):
        jl = JoinedLists([1, 2], [3])
        with pytest.raises(IndexError):
            jl[3]

    def test_setitem(self):
        a = [1, 2]
        b = [3, 4]
        jl = JoinedLists(a, b)
        jl[2] = 99
        assert b[0] == 99

    def test_pop(self):
        a = [1, 2]
        b = [3, 4]
        jl = JoinedLists(a, b)
        val = jl.pop(2)
        assert val == 3
        assert len(jl) == 3

    def test_insert(self):
        a = [1, 2]
        b = [3, 4]
        jl = JoinedLists(a, b)
        jl.insert(1, 99)
        assert a == [1, 99, 2]

    def test_remove(self):
        a = [1, 2]
        b = [3, 4]
        jl = JoinedLists(a, b)
        jl.remove(3)
        assert b == [4]

    def test_remove_not_found(self):
        jl = JoinedLists([1, 2], [3])
        with pytest.raises(ValueError):
            jl.remove(99)

    def test_empty_lists(self):
        jl = JoinedLists([], [])
        assert len(jl) == 0
        assert list(jl) == []


class TestZOrderList:
    def test_sorts_by_z(self):
        # Elements are (point_with_z, value)
        elements = [
            ([0, 0, 10], "back"),
            ([0, 0, 1], "front"),
            ([0, 0, 5], "middle"),
        ]
        zol = ZOrderList(elements)
        result = list(zol)
        assert result == ["front", "middle", "back"]


class TestTwoDMidPoint:
    def test_midpoint(self):
        p0 = [10, 20]
        p1 = [30, 40]
        mp = TwoDMidPoint(p0, p1)
        assert mp[0] == 20
        assert mp[1] == 30

    def test_none_value(self):
        p0 = [None, 20]
        p1 = [30, 40]
        mp = TwoDMidPoint(p0, p1)
        assert mp[0] is None


class TestThreeDMidPoint:
    def test_midpoint(self):
        p0 = [10, 20, 30]
        p1 = [30, 40, 50]
        mp = ThreeDMidPoint(p0, p1)
        assert mp[0] == 20
        assert mp[1] == 30
        assert mp[2] == 40

    def test_none_value(self):
        p0 = [10, None, 30]
        p1 = [30, 40, 50]
        mp = ThreeDMidPoint(p0, p1)
        assert mp[1] is None


class TestTransformation:
    def test_returns_matrix(self):
        m = transformation((100, 200), (2,), 0.5)
        assert isinstance(m, cairo.Matrix)

    def test_identity_like(self):
        m = transformation((0, 0), (1,), 0)
        # Should be close to identity
        assert pytest.approx(m[0], abs=1e-10) == 1.0
        assert pytest.approx(m[3], abs=1e-10) == 1.0
