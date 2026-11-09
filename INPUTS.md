# Explicit-model input contracts

`run` accepts JSON with `matrix` (nonempty square array), `drive` (matching vector), `node` (integer, zero-based) and `change` (finite scalar). All entries must be finite. `matrix[i][j]` maps state j into state i in `x = A x + b`. The units/scales of states, drive and coefficients must be consistent and supplied by the scientific model specification; no units are inferred.

The spectral radius of A must be below one, corresponding to stability of the discrete iteration. This is not an assertion about a continuous-time ODE. Numerical conditioning of `I-A` is also checked; an operator with `cond(I-A) * machine_epsilon >= 1e-6` is rejected. This numerical tolerance concerns floating-point sensitivity, not biological model acceptance. Outputs report spectral radius and conditioning so behavior near that boundary remains visible.

`change` adds to external drive `b[node]`. It does not clamp a state, remove a node or assert a molecular knockout mechanism. The response is solved directly as `(I-A)^-1 delta_b`, preventing subtraction cancellation when the baseline is enormous relative to the requested change.

`ensemble` accepts JSON with `matrices`, `drives`, `node`, `change` and `parameter_kind`, one of `prior`, `posterior`, `bootstrap` or `sensitivity`. The caller supplies all realizations and their provenance. Every realization must have the same node count and pass input/stability/conditioning validation. Any invalid realization rejects the batch rather than silently dropping an unfavorable draw. Outputs include every response, mean and 2.5/97.5 percentiles. Those quantiles describe the supplied parameter realizations; they are not automatically credible intervals. No posterior fitting, R-hat/ESS calculation or calibration occurs in this API.

This public API is a stable linear specified model. It is distinct from the separately packaged original state-conditioned estimation workflow, which has its own assumptions and data requirements. Neither interface is claimed to be a Boolean network implementation or an identified cellular intervention effect.
