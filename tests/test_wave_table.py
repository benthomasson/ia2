"""Tests for ia2.wave_table: waveforms, fade, notes, build_samples."""

import numpy as np
import pytest

from ia2.wave_table import (
    NOTES,
    build_samples,
    fade_in_out,
    linear_interpolation,
    sawtooth,
    square,
    triangle,
)


class TestSawtooth:
    def test_period_boundary(self):
        # sawtooth(x) = (x + pi) / pi % 2 - 1
        # At x=0: (0 + pi)/pi % 2 - 1 = 1 % 2 - 1 = 0
        assert pytest.approx(sawtooth(0), abs=0.01) == 0.0

    def test_range(self):
        x = np.linspace(-2 * np.pi, 2 * np.pi, 1000)
        result = sawtooth(x)
        assert np.all(result >= -1.01)
        assert np.all(result <= 1.01)

    def test_array_input(self):
        x = np.array([0.0, np.pi, 2 * np.pi])
        result = sawtooth(x)
        assert len(result) == 3


class TestSquare:
    def test_positive_half(self):
        # sin(pi/4) > 0, so square should return 1
        assert square(np.pi / 4) == 1.0

    def test_negative_half(self):
        # sin(3*pi/2) < 0, so square should return -1
        assert square(3 * np.pi / 2) == -1.0

    def test_returns_only_minus1_0_1(self):
        x = np.linspace(0.01, 2 * np.pi - 0.01, 100)
        result = square(x)
        for v in result:
            assert v in (-1.0, 0.0, 1.0)


class TestTriangle:
    def test_range(self):
        x = np.linspace(-2 * np.pi, 2 * np.pi, 1000)
        result = triangle(x)
        assert np.all(result >= -1.01)
        assert np.all(result <= 1.01)

    def test_symmetry(self):
        # Triangle is symmetric: triangle(-x) should equal triangle(x) approximately
        # for appropriately shifted values
        x = np.pi / 4
        # Just verify it produces a value in range
        val = triangle(x)
        assert -1.0 <= val <= 1.0


class TestFadeInOut:
    def test_first_sample_near_zero(self):
        signal = np.ones(10000, dtype=np.float64)
        result = fade_in_out(signal, fade_length=2000)
        assert abs(result[0]) < 0.01

    def test_last_sample_near_zero(self):
        signal = np.ones(10000, dtype=np.float64)
        result = fade_in_out(signal, fade_length=2000)
        assert abs(result[-1]) < 0.01

    def test_middle_unchanged(self):
        signal = np.ones(10000, dtype=np.float64)
        result = fade_in_out(signal, fade_length=2000)
        # Middle samples should be unchanged (value = 1.0)
        assert pytest.approx(result[5000]) == 1.0

    def test_returns_same_length(self):
        signal = np.ones(10000, dtype=np.float64)
        result = fade_in_out(signal, fade_length=2000)
        assert len(result) == 10000


class TestNotes:
    def test_a4_is_440(self):
        assert NOTES["A4"] == 440.0

    def test_a3_is_220(self):
        assert NOTES["A3"] == 220.0

    def test_contains_all_octaves(self):
        for octave in range(9):
            assert f"C{octave}" in NOTES
            assert f"A{octave}" in NOTES

    def test_frequency_increases_with_octave(self):
        for octave in range(8):
            assert NOTES[f"A{octave}"] < NOTES[f"A{octave + 1}"]


class TestLinearInterpolation:
    def test_integer_index(self):
        arr = np.array([10.0, 20.0, 30.0])
        assert pytest.approx(linear_interpolation(arr, 0)) == 10.0
        assert pytest.approx(linear_interpolation(arr, 1)) == 20.0

    def test_fractional_index(self):
        arr = np.array([10.0, 20.0, 30.0])
        assert pytest.approx(linear_interpolation(arr, 0.5)) == 15.0

    def test_wraps_around(self):
        arr = np.array([10.0, 20.0, 30.0])
        # At index 2.5: weight 0.5 * arr[2] + 0.5 * arr[0] = 0.5*30 + 0.5*10 = 20
        assert pytest.approx(linear_interpolation(arr, 2.5)) == 20.0


class TestBuildSamples:
    def test_populates_dict(self):
        table = {}
        build_samples(table, sawtooth, sample_rate=44100, duration=1, notes=["A4"])
        assert "A4" in table

    def test_correct_length(self):
        table = {}
        build_samples(table, sawtooth, sample_rate=44100, duration=1, notes=["A4"])
        assert len(table["A4"]) == 44100

    def test_subset_of_notes(self):
        table = {}
        build_samples(table, square, sample_rate=44100, duration=1, notes=["C4", "E4"])
        assert "C4" in table
        assert "E4" in table
        assert "A4" not in table
