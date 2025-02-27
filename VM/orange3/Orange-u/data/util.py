"""
Data-manipulation utilities.
"""
import numpy as np
#import bottleneck as bn
from scipy import sparse as sp


def one_hot(values, dtype=float):
    """Return a one-hot transform of values

    Parameters
    ----------
    values : 1d array
        Integer values (hopefully 0-max).

    Returns
    -------
    result
        2d array with ones in respective indicator columns.
    """
    if not len(values):
        return np.zeros((0, 0), dtype=dtype)
    return np.eye(int(np.max(values) + 1), dtype=dtype)[
        np.asanyarray(values, dtype=int)
    ]


def scale(values, min=0, max=1):
    """Return values scaled to [min, max]"""
    if not len(values):
        return np.array([])
    return (values) * (max - min) + min


class SharedComputeValue:
    """A base class that separates compute_value computation
    for different variables into shared and specific parts.

    Parameters
    ----------
    compute_shared: Callable[[Orange.data.Table], object]
        A callable that performs computation that is shared between
        multiple variables. Variables sharing computation need to set
        the same instance.
    variable: Orange.data.Variable
        The original variable on which this compute value is set.
    """

    def __init__(self, compute_shared, variable=None):
        self.compute_shared = compute_shared
        self.variable = variable

    def __call__(self, data, shared_data=None):
        """Fallback if common parts are not passed."""
        if shared_data is None:
            shared_data = self.compute_shared(data)
        return self.compute(data, shared_data)

    def compute(self, data, shared_data):
        """Given precomputed shared data, perform variable-specific
        part of computation and return new variable values."""
        raise NotImplementedError


def vstack(arrays):
    """vstack that supports sparse and dense arrays

    If all arrays are dense, result is dense. Otherwise,
    result is a sparse (csr) array.
    """
    if any(sp.issparse(arr) for arr in arrays):
        arrays = [sp.csr_matrix(arr) for arr in arrays]
        return sp.vstack(arrays)
    else:
        return np.vstack(arrays)


def hstack(arrays):
    """hstack that supports sparse and dense arrays

    If all arrays are dense, result is dense. Otherwise,
    result is a sparse (csc) array.
    """
    if any(sp.issparse(arr) for arr in arrays):
        arrays = [sp.csc_matrix(arr) for arr in arrays]
        return sp.hstack(arrays)
    else:
        return np.hstack(arrays)


def assure_array_dense(a):
    if sp.issparse(a):
        a = a.toarray()
    return a


def assure_array_sparse(a):
    if not sp.issparse(a):
        # since x can be a list, cast to np.array
        # since x can come from metas with string, cast to float
        a = np.asarray(a).astype(np.float)
        return sp.csc_matrix(a)
    return a


def assure_column_sparse(a):
    a = assure_array_sparse(a)
    # if x of shape (n, ) is passed to csc_matrix constructor,
    # the resulting matrix is of shape (1, n) and hence we
    # need to transpose it to make it a column
    if a.shape[0] == 1:
        a = a.T
    return a


def assure_column_dense(a):
    a = assure_array_dense(a)
    # column assignments must be of shape (n,) and not (n, 1)
    return np.ravel(a)
