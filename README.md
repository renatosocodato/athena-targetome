# athena-targetome

Explicit interaction-model equilibria, drive perturbations and propagation of supplied parameter realizations. Author: Renato Socodato. Version 0.1.0rc3; prepared for review, not published.

## Install and run

```sh
python -m pip install '.[test]'
athena-targetome example --output example_output
athena-targetome run --input model.json --output model_output
athena-targetome ensemble --input realizations.json --output ensemble_output
python -m pytest tests -q
```

The core package requires NumPy. No data download, cloud account or private directory is needed. Output directories must be new; invalid inputs produce no analysis-output directory. See INPUTS.md for the model equation, orientation, units, stability, numerical conditioning and meaning of a drive intervention.

The Python API in `athena_targetome.core` provides `equilibrium`, `intervene`, `diagnostics` and `ensemble_intervention`. The direct perturbation solve avoids cancellation of small changes from large baselines. Ensemble outputs preserve all supplied draws; an unstable or numerically invalid draw rejects the batch and is never silently censored.


## Interpretation

A model's numerical stability is not evidence that its graph or parameter mapping is biologically correct. Interventions are conditional on the explicitly assumed equations; they do not identify cellular causal effects. Parameter ensembles can express prior, posterior, bootstrap or sensitivity variation, as declared by their source, but this tool does not infer that provenance or fit a posterior. No synthetic hash-derived sampling diagnostics are generated. The supplied example is synthetic. Biological calibration and independent perturbation validation remain separate.

## Independent numerical checks

The test suite compares equilibria against constructed known solutions, SciPy linear solves and a separate fixed-point iteration on 30 fixed stable systems. Perturbation ensembles are checked realization by realization against iteration, including a nonnormal feedforward example. This verifies the declared numerical model; it does not validate a molecular interaction graph or infer causal cellular effects. The test extra includes SciPy; the runtime core still requires only NumPy.


## Scope of this release

The package distributes the documented public API and command-line workflows. The historical grant workflows, project data and unvalidated experimental stages are outside this release.
