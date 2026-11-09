import subprocess
import sys
from pathlib import Path
import pytest

def test_example_and_no_overwrite(tmp_path):
    out=tmp_path/'example'
    command=[sys.executable,'-m','athena_targetome','example','--output',str(out)]
    subprocess.run(command,check=True,capture_output=True)
    assert (out/'result.json').is_file()
    second=subprocess.run(command,capture_output=True)
    assert second.returncode!=0


def test_ensemble_cli_declares_origin_and_propagates_all_draws(tmp_path):
    import json
    inp=tmp_path/'ensemble.json'
    inp.write_text(json.dumps({'matrices':[[[0]],[[.5]]],'drives':[[1],[1]],'node':0,'change':1,'parameter_kind':'sensitivity'}))
    out=tmp_path/'out'
    subprocess.run([sys.executable,'-m','athena_targetome','ensemble','--input',str(inp),'--output',str(out)],check=True,capture_output=True)
    result=json.loads((out/'result.json').read_text())
    assert result['n_realizations']==2 and result['parameter_kind']=='sensitivity'
    assert result['mean']==[1.5]


def test_bad_model_does_not_leave_output(tmp_path):
    inp=tmp_path/'bad.json';inp.write_text('{"matrix":[[2]],"drive":[1],"node":0,"change":1}')
    out=tmp_path/'failed'
    p=subprocess.run([sys.executable,'-m','athena_targetome','run','--input',str(inp),'--output',str(out)],capture_output=True)
    assert p.returncode!=0 and not out.exists()
