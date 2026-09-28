"""Unit tests for the constant prevalence baseline (synthetic labels only)."""

from __future__ import annotations

import unittest

from fishai.models.frameworks.baselines.prevalence import PrevalenceBaseline


class PrevalenceBaselineTests(unittest.TestCase):
    def test_fit_mean_and_constant_predictions(self) -> None:
        y = [0, 1, 1, 0, 1]
        model = PrevalenceBaseline().fit(y)
        self.assertAlmostEqual(model.prevalence_, 0.6)
        self.assertEqual(model.n_train_, 5)
        preds = model.predict_proba(4)
        self.assertEqual(preds, [0.6, 0.6, 0.6, 0.6])
        self.assertEqual(model.predict([[], [], []]), [0.6, 0.6, 0.6])

    def test_deterministic_across_refits(self) -> None:
        y = [1, 0, 1, 1, 0, 0, 1, 0]
        a = PrevalenceBaseline().fit(y).predict_proba(10)
        b = PrevalenceBaseline().fit(list(y)).predict_proba(10)
        self.assertEqual(a, b)
        self.assertTrue(all(p == a[0] for p in a))

    def test_all_zeros_and_all_ones(self) -> None:
        z = PrevalenceBaseline().fit([0, 0, 0])
        self.assertEqual(z.predict_proba(2), [0.0, 0.0])
        o = PrevalenceBaseline().fit([1, 1])
        self.assertEqual(o.predict_proba(3), [1.0, 1.0, 1.0])

    def test_fit_required(self) -> None:
        with self.assertRaises(RuntimeError):
            PrevalenceBaseline().predict_proba(1)
        with self.assertRaises(ValueError):
            PrevalenceBaseline().fit([])


if __name__ == "__main__":
    unittest.main()
