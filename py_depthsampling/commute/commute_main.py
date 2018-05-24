# -*- coding: utf-8 -*-
"""
Test for commutative property of drain model (deconvolution).

Test for commutative property of drain model (deconvolution) with respect to
subtraction. In other words, does it make a difference whether we:
    - First apply the deconvolution (separately for each condition for each
      subject), subsequently calculate differences between conditions (within
      subjects), and finally take the median across subjects
or
    - First calculate the difference between conditions (within subject),
      apply the deconvolution on the difference score, and finally take the
      median across subject?


Approach A:
(1) Apply deconvolution (separately for each subject and condition).
(2) Calculate difference between conditions (within subjects).
(3) Take median across subjects.

Approach B:
(1) Calculate difference between conditions (within subject).
(2) Apply deconvolution (on differences, separately for each subject).
(3) Take median across subjects.
"""

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


from py_depthsampling.commute.commute_deconv import commute

# -----------------------------------------------------------------------------
# *** Define parameters

# Which draining model to use (1, 2, 3, 4, 5, or 6 - see above for details):
lstMdl = [1]

# Meta-condition (within or outside of retinotopic stimulus area):
lstMetaCon = ['stimulus']

# ROI ('v1' or 'v2'):
lstRoi = ['v1']

# Hemisphere ('rh' or 'lh'):
lstHmsph = ['rh']

# Path of depth-profile to correct (meta-condition, ROI, hemisphere, and
# condition left open):
strPthPrf = '/home/john/PhD/PacMan_Depth_Data/Higher_Level_Analysis/{}/{}_{}_{}.npy'  #noqa

# Output path & prefix for plots (meta-condition, ROI, hemisphere, condition,
# and model index left open):
strPthPltOt = '/home/john/PhD/PacMan_Plots/commutative/{}_{}_{}_{}_deconv_model_{}_'  #noqa

# File type suffix for plot:
strFlTp = '.png'

# Figure scaling factor:
varDpi = 80.0

# Label for axes:
strXlabel = 'Cortical depth level (equivolume)'
strYlabel = 'fMRI signal change [arbitrary units]'

# Condition levels (used to complete file names) - nested list:
lstCon = ['Pd_sst', 'Cd_sst', 'Ps_sst']

# Condition labels:
lstConLbl = ['PacMan Dynamic Sustained',
             'Control Dynamic Sustained',
             'PacMan Static Sustained']

# Which conditions to compare (list of tuples with condition indices):
lstDiff = [(0, 1), (0, 2)]

# Number of resampling iterations for peak finding (for models 1, 2, and 3) or
# random noise samples (models 4 and 5):
# varNumIt = 10000

# Lower & upper bound of percentile bootstrap (in percent), for bootstrap
# confidence interval (models 1, 2, and 3) - this value is only printed, not
# plotted - or plotted confidence intervals in case of model 5:
# varCnfLw = 0.5
# varCnfUp = 99.5

# Limits of y-axis for across subject plot:
varAcrSubsYmin01 = -400.0
varAcrSubsYmax01 = 0.0
varAcrSubsYmin02 = -400.0
varAcrSubsYmax02 = 0.0
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# *** Approach A

# Approach A:
# (1) Apply deconvolution (separately for each subject and condition).
# (2) Calculate difference between conditions (within subjects).
# (3) Take median across subjects.

# Loop through models, ROIs, hemispheres, and conditions to create plots:
for idxMtaCn in range(len(lstMetaCon)):  #noqa
    for idxMdl in range(len(lstMdl)):  #noqa
        for idxRoi in range(len(lstRoi)):
            for idxHmsph in range(len(lstHmsph)):
                for idxDiff in range(len(lstDiff)):

                    # print(lstDiff[idxDiff][0])
                    # print(lstDiff[idxDiff][1])

                    # Path of first depth profile:
                    strTmpPth01 = strPthPrf.format(
                        lstMetaCon[idxMtaCn], lstRoi[idxRoi],
                        lstHmsph[idxHmsph], lstCon[lstDiff[idxDiff][0]])

                    # Path of second depth profile:
                    strTmpPth02 = strPthPrf.format(
                        lstMetaCon[idxMtaCn], lstRoi[idxRoi],
                        lstHmsph[idxHmsph], lstCon[lstDiff[idxDiff][1]])



                    # Load original (i.e. non-convolved) single subject depth
                    # profiles:

# -----------------------------------------------------------------------------
# *** Approach B

# Approach B:
# (1) Calculate difference between conditions (within subject).
# (2) Apply deconvolution (on differences, separately for each subject).
# (3) Take median across subjects.

# -----------------------------------------------------------------------------