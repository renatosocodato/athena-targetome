"""Explicit stable linear interaction models; no inference of molecular causality."""
from numbers import Integral, Real
import numpy as np


def _system(matrix, drive):
    try:
        a = np.asarray(matrix, dtype=float)
        b = np.asarray(drive, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError('Numeric interaction matrix and drive required') from exc
    if a.ndim != 2 or a.shape[0] == 0 or a.shape[0] != a.shape[1] or b.shape != (a.shape[0],) or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('Nonempty finite square interaction matrix and matching drive required')
    radius = float(np.max(np.abs(np.linalg.eigvals(a))))
    if radius >= 1:
        raise ValueError('Unstable model: spectral radius must be below one')
    operator = np.eye(len(b)) - a
    condition = float(np.linalg.cond(operator))
    if not np.isfinite(condition) or condition * np.finfo(float).eps >= 1e-6:
        raise ValueError('Numerically ill-conditioned model; rescale or revise parameters')
    return a, b, operator, radius, condition


def diagnostics(matrix, drive):
    """Report stability and numerical conditioning, not a fit/convergence verdict."""
    _, _, _, radius, condition = _system(matrix, drive)
    return {'spectral_radius': radius, 'operator_condition_number': condition,
            'numerical_condition_limit': 1e-6 / np.finfo(float).eps,
            'interpretation': 'These diagnostics describe the specified model, not biological calibration'}


def equilibrium(matrix, drive):
    """Solve x = A x + b. A[i,j] maps state j into state i.

    Units/scales of x and b must be consistent with A. Stability is that of
    the corresponding discrete iteration, not a claim about a continuous ODE.
    """
    _, b, operator, _, _ = _system(matrix, drive)
    result = np.linalg.solve(operator, b)
    if not np.isfinite(result).all():
        raise ValueError('Nonfinite equilibrium')
    return result


def intervene(matrix, drive, node, change):
    """Add change to external drive b[node]; does not clamp or delete a node.

    Solve the response directly to avoid cancellation when the baseline is large.
    """
    _, b, operator, _, _ = _system(matrix, drive)
    if isinstance(node, bool) or not isinstance(node, Integral) or not 0 <= node < len(b) or isinstance(change, bool) or not isinstance(change, Real) or not np.isfinite(change):
        raise ValueError('Integer node and finite scalar drive change required')
    delta = np.zeros_like(b)
    delta[node] = change
    result = np.linalg.solve(operator, delta)
    if not np.isfinite(result).all():
        raise ValueError('Nonfinite intervention response')
    return result


def _draw_summaries(draws):
    return np.vstack((draws.mean(axis=0), np.quantile(draws, [.025, .975], axis=0)))


def ensemble_intervention(matrices, drives, node, change):
    """Summarize supplied parameter realizations without fitting or censoring draws.

    The caller identifies whether these are prior, posterior, bootstrap or
    sensitivity realizations. Any invalid realization rejects the whole batch;
    instability is never silently filtered to make the summary look favorable.
    """
    matrices = list(matrices)
    drives = list(drives)
    if not matrices or len(matrices) != len(drives):
        raise ValueError('Nonempty paired matrices and drives required')
    responses = []
    width = None
    for index, (matrix, drive) in enumerate(zip(matrices, drives)):
        try:
            response = intervene(matrix, drive, node, change)
            if width is not None and len(response) != width:
                raise ValueError('All realizations must have the same node count')
            width = len(response)
            responses.append(response)
        except ValueError as exc:
            raise ValueError(f'Invalid realization {index}: {exc}') from exc
    draws = np.asarray(responses)
    # Finite draws can overflow the mean's sum or the quantile's interpolation.
    with np.errstate(over='ignore', invalid='ignore'):
        summaries = _draw_summaries(draws)
    needs_scaling = ~np.isfinite(summaries).all(axis=0)
    if needs_scaling.any():
        extreme_draws = draws[:, needs_scaling]
        scale = np.abs(extreme_draws).max(axis=0)
        scaled_summaries = _draw_summaries(extreme_draws / scale) * scale
        original = summaries[:, needs_scaling]
        summaries[:, needs_scaling] = np.where(np.isfinite(original), original, scaled_summaries)
    if not np.isfinite(summaries).all():
        raise ValueError('Intervention summaries exceed supported numeric range')
    mean, lower, upper = summaries
    return {'responses': draws, 'mean': mean, 'q025': lower, 'q975': upper,
            'n_realizations': len(draws)}
