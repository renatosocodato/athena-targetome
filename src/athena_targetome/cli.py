"""Explicit-model and parameter-ensemble CLI; never downloads private data."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
from . import core



def main(argv=None):
    parser = argparse.ArgumentParser(description='Explicit interaction-model perturbations')
    sub = parser.add_subparsers(dest='command', required=True)
    ex = sub.add_parser('example', help='Run a synthetic linear-model example')
    ex.add_argument('--output', type=Path, required=True)
    for name in ['run', 'ensemble']:
        command = sub.add_parser(name, help='Read an explicit model JSON; see INPUTS.md')
        command.add_argument('--input', type=Path, required=True)
        command.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if output.exists():
        parser.error('Output directory already exists; choose a new directory')
    try:
        result = analyze(args)
        content = json.dumps(result, indent=2, allow_nan=False) + '\n'
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.athena-targetome-', dir=output.parent) as staging:
            staged = Path(staging) / 'result.json'
            staged.write_text(content)
            output.mkdir(exist_ok=False)
            shutil.move(str(staged), output / 'result.json')
    except (ValueError, KeyError, TypeError, FileNotFoundError, FileExistsError) as exc:
        parser.exit(2, f'Input error: {exc}\n')
    return 0


def analyze(args):
    spec = {'matrix': [[0,.2],[.1,0]], 'drive': [1,1], 'node': 0, 'change': -.5} if args.command == 'example' else json.loads(args.input.read_text())
    if args.command == 'ensemble':
        kind = spec.get('parameter_kind')
        if kind not in ['prior', 'posterior', 'bootstrap', 'sensitivity']:
            raise ValueError('Declare parameter_kind as prior, posterior, bootstrap or sensitivity')
        result = core.ensemble_intervention(spec['matrices'], spec['drives'], spec['node'], spec['change'])
        return {'data_kind': 'user_supplied_parameter_realizations', 'parameter_kind': kind,
                **{key: value.tolist() if hasattr(value, 'tolist') else value for key, value in result.items()},
                'interpretation': 'Quantiles describe supplied parameter realizations. No posterior fitting, sampling diagnosis or model selection was performed.'}
    baseline = core.equilibrium(spec['matrix'], spec['drive'])
    delta = core.intervene(spec['matrix'], spec['drive'], spec['node'], spec['change'])
    return {'data_kind': 'synthetic' if args.command == 'example' else 'user_specified_model',
            'baseline': baseline.tolist(), 'change': delta.tolist(), 'diagnostics': core.diagnostics(spec['matrix'], spec['drive']),
            'intervention_kind': 'additive_external_drive',
            'causal_use': 'conditional on specified stable linear model; not an identified cellular mechanism'}
