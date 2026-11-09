import numpy as np
import pytest
from athena_targetome.core import equilibrium,intervene

def test_analytic_chain_and_zero_intervention():
    a=[[0,0],[.5,0]]
    np.testing.assert_allclose(equilibrium(a,[2,1]),[2,2])
    np.testing.assert_allclose(intervene(a,[2,1],0,-1),[-1,-.5])
    np.testing.assert_allclose(intervene(a,[2,1],0,0),[0,0])

@pytest.mark.parametrize('a,b', [([[1,0],[0,.5]],[1,1]),([[0,1]],[1]),([[np.nan]],[1])])
def test_unstable_and_malformed_rejected(a,b):
    with pytest.raises(ValueError):equilibrium(a,b)

def test_no_hidden_fitted_parameters():
    np.testing.assert_allclose(equilibrium([[0]],[3]),[3])
    with pytest.raises(ValueError):intervene([[0]],[3],2,1)


def test_large_baseline_small_drive_response_avoids_cancellation():
    np.testing.assert_allclose(intervene([[0]],[1e30],0,1),[1])


@pytest.mark.parametrize('matrix,drive', [([],[]),([[]],[]),([[0,1e15],[0,0]],[1,1])])
def test_empty_and_ill_conditioned_models_rejected(matrix,drive):
    with pytest.raises(ValueError):equilibrium(matrix,drive)


@pytest.mark.parametrize('node,change', [(True,1),(0,True),(0,[1]),(0,float('inf'))])
def test_intervention_scalar_contract(node,change):
    with pytest.raises(ValueError):intervene([[0]],[1],node,change)


def test_numpy_integer_node_accepted():
    np.testing.assert_allclose(intervene([[0]],[1],np.int64(0),2),[2])


def test_ensemble_reference_and_no_silent_rejection():
    from athena_targetome.core import ensemble_intervention, diagnostics
    result=ensemble_intervention([[[0]],[[.5]]],[[1],[1]],0,1)
    np.testing.assert_allclose(result['responses'],[[1],[2]])
    np.testing.assert_allclose(result['mean'],[1.5])
    assert result['n_realizations']==2
    assert diagnostics([[.5]],[1])['spectral_radius']==.5
    with pytest.raises(ValueError,match='realization 1'):
        ensemble_intervention([[[0]],[[1.1]]],[[1],[1]],0,1)


def test_ensemble_summarizes_extreme_finite_responses():
    from athena_targetome.core import ensemble_intervention

    # The feedforward component spans both signs; the driven node is constant.
    large = 1e308
    matrices = [[[0, 0], [-1, 0]], [[0, 0], [1, 0]]]
    result = ensemble_intervention(matrices, [[0, 0], [0, 0]], 0, large)
    np.testing.assert_array_equal(result['responses'], [[large, -large], [large, large]])
    np.testing.assert_allclose(result['mean'], [large, 0])
    np.testing.assert_allclose(result['q025'], [large, -.95 * large])
    np.testing.assert_allclose(result['q975'], [large, .95 * large])
