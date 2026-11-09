"""Independent numerical references on fixed synthetic systems, not fitted biology."""
import numpy as np
from scipy.linalg import solve
from athena_targetome.core import equilibrium, intervene, ensemble_intervention


def iterate(matrix, drive):
    """An independent fixed-point iteration, without calling a linear solver."""
    x = np.zeros(len(drive))
    for _ in range(2000):
        updated = matrix @ x + drive
        if np.max(np.abs(updated-x)) <= 1e-13:
            return updated
        x = updated
    raise AssertionError('Reference iteration did not converge')


def systems():
    # Fixed before this validation run. These realizations are not model fits.
    rng = np.random.default_rng(20261108)
    for _ in range(30):
        matrix = rng.normal(size=(5, 5))
        matrix *= .6 / np.abs(matrix).sum(axis=1).max()
        truth = rng.normal(size=5)
        drive = (np.eye(5)-matrix) @ truth
        yield matrix, drive, truth


def test_equilibrium_recovers_constructed_truth_and_two_independent_references():
    for matrix, drive, truth in systems():
        computed = equilibrium(matrix, drive)
        np.testing.assert_allclose(computed, truth, atol=2e-12, rtol=2e-12)
        np.testing.assert_allclose(computed, solve(np.eye(5)-matrix, drive), atol=2e-12, rtol=2e-12)
        np.testing.assert_allclose(computed, iterate(matrix, drive), atol=2e-12, rtol=2e-12)


def test_intervention_and_ensemble_match_fixed_point_reference_realizations():
    matrices, drives, responses = [], [], []
    delta = np.zeros(5); delta[2] = -.4
    for matrix, drive, _ in systems():
        expected = iterate(matrix, delta)
        np.testing.assert_allclose(intervene(matrix, drive, 2, -.4), expected, atol=2e-12, rtol=2e-12)
        matrices.append(matrix); drives.append(drive); responses.append(expected)
    result = ensemble_intervention(matrices, drives, 2, -.4)
    expected = np.asarray(responses)
    np.testing.assert_allclose(result['responses'], expected, atol=2e-12, rtol=2e-12)
    np.testing.assert_allclose(result['mean'], expected.mean(0), atol=2e-12, rtol=2e-12)
    np.testing.assert_allclose(result['q025'], np.quantile(expected, .025, axis=0), atol=2e-12, rtol=2e-12)
    np.testing.assert_allclose(result['q975'], np.quantile(expected, .975, axis=0), atol=2e-12, rtol=2e-12)


def test_nonnormal_stable_feedforward_system_has_known_response():
    # Nilpotent A is stable despite a large off-diagonal operator norm.
    matrix = np.array([[0., 0., 0.], [20., 0., 0.], [0., 30., 0.]])
    np.testing.assert_allclose(equilibrium(matrix, [1., 0., 0.]), [1., 20., 600.])
    np.testing.assert_allclose(intervene(matrix, [1e30, 0., 0.], 0, 1e-6), [1e-6, 20e-6, 600e-6])
