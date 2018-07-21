import numpy as np
from numpy.testing import assert_allclose
import unittest
from dc_integration.distribution import CACGMMTrainer
from dc_integration.distribution import ComplexAngularCentralGaussian
import itertools


class TestCACGMM(unittest.TestCase):
    def test_gmm(self):
        samples = 10000
        weight = np.array([0.3, 0.7])
        num_classes = weight.shape[0]
        labels = np.random.choice(
            range(num_classes), size=(samples,), p=weight
        )
        covariance = np.array(
            [
                [[10, 1 + 1j, 1 + 1j], [1 - 1j, 5, 1], [1 - 1j, 1, 2]],
                [[2, 0, 0], [0, 3, 0], [0, 0, 2]],
            ]
        )
        covariance /= np.trace(covariance, axis1=-2, axis2=-1)[..., None, None]
        dimension = covariance.shape[-1]
        x = np.zeros((samples, dimension), dtype=np.complex128)

        for l in range(num_classes):
            cacg = ComplexAngularCentralGaussian(
                covariance=covariance[l, :, :]
            )
            x[labels == l, :] = cacg.sample(size=(np.sum(labels == l),))

        model = CACGMMTrainer().fit(x, num_classes=2)

        # Permutation invariant testing
        permutations = list(itertools.permutations(range(2)))
        best_permutation, best_cost = None, np.inf
        for p in permutations:
            cost = np.linalg.norm(model.cacg.covariance[p, :] - covariance)
            if cost < best_cost:
                best_permutation, best_cost = p, cost

        assert_allclose(
            model.cacg.covariance[best_permutation, :], covariance, atol=0.1
        )
