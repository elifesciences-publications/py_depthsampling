# -*- coding: utf-8 -*-
"""
Plot difference between conditions.

Plot mean of between stimulus conditions difference, with SEM.
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


from py_depthsampling.diff.diff_sem import diff_sem
from py_depthsampling.diff.diff_sem_sngle import diff_sem_sngle


# -----------------------------------------------------------------------------
# *** Define parameters

# Which parameter to plot - 'mean' or 'median'.
strParam = 'mean'

# Which draining model to plot ('' for none):
lstMdl = ['_deconv_model_1']

# Meta-condition (within or outside of retinotopic stimulus area):
lstMetaCon = ['stimulus']
# lstMetaCon = ['periphery']

# ROI ('v1', 'v2', or 'v3'):
lstRoi = ['v1', 'v2', 'v3']

# Hemisphere ('rh' or 'lh'):
lstHmsph = ['rh']

# Path of corrected depth-profiles (meta-condition, ROI, hemisphere,
# condition, and model index left open):
strPthData = '/home/john/Dropbox/PacMan_Depth_Data/Higher_Level_Analysis/{}/{}_{}_{}{}.npz'  #noqa

# Output path & prefix for plots (meta-condition, ROI, hemisphere, and
# model index left open):
strPthPltOt = '/home/john/Dropbox/PacMan_Plots/diff/{}_{}_{}{}_SEM'  #noqa

# Output path for single subject plot, (ROI, metacondition, hemisphere, drain
# model, and condition left open):
strPthPtlSnglOt = '/home/john/Dropbox/PacMan_Plots/diff_sngle/{}_{}_{}{}_{}'

# File type suffix for plot:
strFlTp = '.png'

# Figure scaling factor:
varDpi = 120.0

# Label for axes:
strXlabel = 'Cortical depth level'
strYlabel = 'Signal change [%]'

# Condition levels (used to complete file names):
# lstCon = ['Pd_sst', 'Ps_sst', 'Cd_sst']
lstCon = ['Pd_sst', 'Cd_sst']
# lstCon = ['Pd_sst', 'Ps_sst_plus_Cd_sst']
# lstCon = ['Pd_trn', 'Ps_trn', 'Cd_trn']
# lstCon = ['Pd_trn', 'Ps_trn', 'Cd_trn', 'Ps_trn_plus_Cd_trn']

# Condition labels:
lstConLbl = lstCon

# Which conditions to compare (list of tuples with condition indices):
# lstDiff = [(0, 1), (0, 2), (1, 2)]
lstDiff = [(0, 1)]
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# *** Loop through ROIs / conditions

# Loop through models, ROIs, hemispheres, and conditions to create plots:
for idxMtaCn in range(len(lstMetaCon)):  #noqa
    for idxMdl in range(len(lstMdl)):  #noqa
        for idxRoi in range(len(lstRoi)):
            for idxHmsph in range(len(lstHmsph)):

                # Limits of axes can be adjusted based on ROI, condition,
                # hemisphere, deconvolution model.

                if lstMetaCon[idxMtaCn] == 'periphery':
                    varYmin = -0.25
                    varYmax = 0.25
                    varNumLblY = 3
                    tplPadY = (0.1, 0.1)
                if lstMetaCon[idxMtaCn] == 'stimulus':
                    varYmin = -0.2  # -0.25
                    varYmax = 0.4  # 0.5
                    varNumLblY = 4
                    tplPadY = (0.0, 0.0)

                # Create average plots:
                diff_sem(strPthData.format(lstMetaCon[idxMtaCn],
                                           lstRoi[idxRoi],
                                           lstHmsph[idxHmsph],
                                           '{}',
                                           lstMdl[idxMdl]),
                         (strPthPltOt.format(lstMetaCon[idxMtaCn],
                                             lstRoi[idxRoi],
                                             lstHmsph[idxHmsph],
                                             lstMdl[idxMdl])
                          + strFlTp),
                         lstCon,
                         lstConLbl,
                         varYmin=varYmin,
                         varYmax=varYmax,
                         tplPadY=tplPadY,
                         varNumLblY=varNumLblY,
                         varDpi=varDpi,
                         strXlabel=strXlabel,
                         strYlabel=strYlabel,
                         lgcLgnd=True,
                         lstDiff=lstDiff,
                         strParam=strParam)

                # Create single subject plot(s):
                diff_sem_sngle(strPthData.format(lstMetaCon[idxMtaCn],
                                                 lstRoi[idxRoi],
                                                 lstHmsph[idxHmsph],
                                                 '{}',
                                                 lstMdl[idxMdl]),
                               (strPthPtlSnglOt.format(lstRoi[idxRoi],
                                                       lstMetaCon[idxMtaCn],
                                                       lstHmsph[idxHmsph],
                                                       lstMdl[idxMdl],
                                                       '{}')
                                + strFlTp),
                               lstCon,
                               lstConLbl,
                               strXlabel='Cortical depth level (equivolume)',
                               strYlabel='Subject',
                               lstDiff=lstDiff)
# -----------------------------------------------------------------------------
