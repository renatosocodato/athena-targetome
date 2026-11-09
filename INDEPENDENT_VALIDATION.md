# Independent implementation and scientific checks

Independent tests compare the linear solver with scipy.linalg.solve, direct fixed-point iteration and known solutions over 30 stable assumed systems, including ensemble responses and a non-normal matrix. Tests cover cancellation, stability and conditioning boundaries.

These checks establish numerical behavior for the stated linear model. They do not identify a molecular mechanism, calibrate a posterior distribution or validate a biological target-prioritization campaign.

These are internal computational checks against independent implementations, public inputs and real engines. No external peer review is claimed. Full execution details are in VALIDATION.md.

## Revision after independent candidate review

Keep ensemble summaries finite for the reviewed extreme responses. Exclude the historical simulation/inference workflow. Hosted execution records for the exact distributions are tracked separately.
