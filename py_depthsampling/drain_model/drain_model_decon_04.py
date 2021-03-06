# -*- coding: utf-8 -*-
"""Deconvolution of GE fMRI depth profiles (draining effect correction)."""

# Part of py_depthsampling library
# Copyright (C) 2018  Ingo Marquardt
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.


import numpy as np


def deconv_04(varNumCon, aryEmp5, aryNseRnd):
    """
    Deconvolution of GE fMRI depth profiles (draining effect correction).

    Function of the model-based correction of draining effect pipeline.

    Function of the depth sampling pipeline.

    Parameters
    ----------
    varNumCon : int
        Number of conditions.

    aryEmp5 : np.array
        Two-dimensional array with depth profiles defined at 5 depth levels,
        separately for each condition: aryEmp5[condition, depthlevel].

    aryNseRnd : np.array
        Array with random noise. For example, random noise sampled from
        Gaussian distribution. Form of the array: aryNseRnd[varNumIt,
        varNumCon, varNumDpth].

    Returns
    -------
    aryNrnRnd : np.array
        Three-dimensional array with corrected depth profiles, of the form
        aryNrn[idxIteration, idxCondition, idxDepth].

    Notes
    -----
    The purpose of this function is to test how sensitive the spatial
    deconvolution (draining effect removal) is to violations of the model
    assumptions. Same as 'model 1', i.e. only correcting draining effect, but
    with Gaussian random error added to the draining effects assumed by
    Markuerkiaga et al. (2016).

    Reference
    ---------
    Markuerkiaga, I., Barth, M., & Norris, D. G. (2016). A cortical vascular
    model for examining the specificity of the laminar BOLD signal.
    Neuroimage, 132, 491-498.
    """
    # *** Deconvolution (removal of draining effect)

    print('------Deconvolution - Model 4 (violation of model assumptions)')

    # Number of random-noise iterations:
    varNumIt = aryNseRnd.shape[0]

    # Array for corrected depth profiles:
    aryNrnRnd = np.zeros((varNumIt, aryEmp5.shape[0], aryEmp5.shape[1]))

    # Layer VI:
    aryNrnRnd[:, :, 0] = aryEmp5[None, :, 0]

    # Layer V:
    aryNrnRnd[:, :, 1] = (aryEmp5[None, :, 1]
                          - ((0.6 / 1.9) * aryNrnRnd[:, :, 0]
                             * aryNseRnd[:, :, 1])
                          )

    # Layer IV:
    aryNrnRnd[:, :, 2] = (aryEmp5[None, :, 2]
                          - ((0.3 / 1.5) * aryNrnRnd[:, :, 1]
                             * aryNseRnd[:, :, 2])
                          - ((0.6 / 1.9) * aryNrnRnd[:, :, 0]
                             * aryNseRnd[:, :, 2])
                          )

    # Layer II/III:
    aryNrnRnd[:, :, 3] = (aryEmp5[None, :, 3]
                          - ((1.3 / 2.2) * aryNrnRnd[:, :, 2]
                             * aryNseRnd[:, :, 3])
                          - ((0.3 / 1.5) * aryNrnRnd[:, :, 1]
                             * aryNseRnd[:, :, 3])
                          - ((0.5 / 1.9) * aryNrnRnd[:, :, 0]
                             * aryNseRnd[:, :, 3])
                          )

    # Layer I:
    aryNrnRnd[:, :, 4] = (aryEmp5[:, 4]
                          - ((0.7 / 1.7) * aryNrnRnd[:, :, 3]
                             * aryNseRnd[:, :, 4])
                          - ((1.3 / 2.2) * aryNrnRnd[:, :, 2]
                             * aryNseRnd[:, :, 4])
                          - ((0.3 / 1.5) * aryNrnRnd[:, :, 1]
                             * aryNseRnd[:, :, 4])
                          - ((0.5 / 1.9) * aryNrnRnd[:, :, 0]
                             * aryNseRnd[:, :, 4])
                          )

    return aryNrnRnd
