"""Unit tests for numeric-feature support labeling (synthetic fixtures only)."""

from __future__ import annotations

import unittest

from evaluation.support.mask import (
    SUPPORT_LABELS,
    label_support_point,
    nearest_train_distance,
    out_of_range_kinds,
)


class SupportMaskTests(unittest.TestCase):
    def setUp(self) -> None:
        # Columns: spatial proxy, environmental, temporal (year offset)
        self.train = [
            [0.0, 10.0, 0.0],
            [1.0, 12.0, 0.0],
            [0.5, 11.0, 1.0],
            [0.2, 9.5, 1.0],
        ]
        self.kinds = ["spatial", "environmental", "temporal"]

    def test_supported_near_train_in_range(self) -> None:
        label = label_support_point(
            [0.4, 10.5, 0.5],
            self.train,
            feature_kinds=self.kinds,
            support_max_distance=1.0,
            weak_max_distance=2.5,
        )
        self.assertEqual(label, "SUPPORTED")
        self.assertIn(label, SUPPORT_LABELS)

    def test_weak_support_by_distance(self) -> None:
        # In-range midpoint between distant train rows → WEAK_SUPPORT by distance
        train = [[0.0, 10.0, 0.0], [10.0, 10.0, 0.0]]
        query = [5.0, 10.0, 0.0]
        label = label_support_point(
            query,
            train,
            feature_kinds=self.kinds,
            support_max_distance=1.0,
            weak_max_distance=6.0,
        )
        self.assertEqual(label, "WEAK_SUPPORT")
        dist = nearest_train_distance(query, train)
        self.assertIsNotNone(dist)
        assert dist is not None
        self.assertGreater(dist, 1.0)
        self.assertLessEqual(dist, 6.0)

    def test_spatial_extrapolation(self) -> None:
        label = label_support_point(
            [5.0, 10.5, 0.5],
            self.train,
            feature_kinds=self.kinds,
        )
        self.assertEqual(label, "SPATIAL_EXTRAPOLATION")
        self.assertEqual(
            out_of_range_kinds([5.0, 10.5, 0.5], self.train, self.kinds),
            ["spatial"],
        )

    def test_environmental_extrapolation(self) -> None:
        label = label_support_point(
            [0.4, 40.0, 0.5],
            self.train,
            feature_kinds=self.kinds,
        )
        self.assertEqual(label, "ENVIRONMENTAL_EXTRAPOLATION")

    def test_temporal_extrapolation(self) -> None:
        label = label_support_point(
            [0.4, 10.5, 9.0],
            self.train,
            feature_kinds=self.kinds,
        )
        self.assertEqual(label, "TEMPORAL_EXTRAPOLATION")

    def test_unsupported_multi_kind_or_far(self) -> None:
        multi = label_support_point(
            [5.0, 40.0, 0.5],
            self.train,
            feature_kinds=self.kinds,
        )
        self.assertEqual(multi, "UNSUPPORTED")

        far_in_range = label_support_point(
            [1.0, 12.0, 1.0],
            [[0.0, 10.0, 0.0]],
            feature_kinds=self.kinds,
            support_max_distance=0.1,
            weak_max_distance=0.5,
        )
        self.assertEqual(far_in_range, "UNSUPPORTED")

        empty = label_support_point([0.0, 0.0, 0.0], [], feature_kinds=self.kinds)
        self.assertEqual(empty, "UNSUPPORTED")

    def test_untyped_range_violation_is_unsupported(self) -> None:
        label = label_support_point([10.0], [[0.0], [1.0]])
        self.assertEqual(label, "UNSUPPORTED")


if __name__ == "__main__":
    unittest.main()
