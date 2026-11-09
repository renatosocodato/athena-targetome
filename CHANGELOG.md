# 0.1.0rc4

- Keep ensemble summaries finite for the reviewed extreme responses. Exclude the historical simulation/inference workflow.

# 0.1.0rc3

- Solved additive-drive responses directly, avoiding cancellation of a small perturbation on a very large baseline.
- Rejected empty systems, nonfinite values, ill-conditioned operators and boolean intervention indices; accepted NumPy integer indices.
- Added stability/conditioning diagnostics and explicit documentation of matrix orientation, units and discrete-time stability.
- Added parameter-ensemble API/CLI with caller-declared origin and no silent filtering of unstable realizations.
- Removed unrelated CLI options and the Pandas dependency from the public core; original workflow dependencies remain optional.
- Invalid models no longer leave partial output directories; added analytic, conditioning, parameter-ensemble and CLI tests.

# 0.1.0rc1

Initial review candidate: explicit stable linear-model API, synthetic example and separately retained state-conditioned workflow.

## 0.1.0rc3

Added independent SciPy and fixed-point references on 30 fixed synthetic stable systems, exact nonnormal feedforward response, and realization-level ensemble comparison. No fitted biological parameters or causal claims added.
