# -*- coding: utf-8 -*-
"""
Model-based correction of draining effect.

Function of the depth sampling pipeline.

Notes
-----

This script simulates applies the spatial deconvolution method to data taken
from Huber et al. (2017), Neuron, Figure 3B on page 4 (right side, BOLD, blue
graph representing the most salient experimental condition). The data is from
motor cortex, and here we test what happens if we apply the deconvolution model
defined for V1, to check whether the model generalises. The deconvolution
result can then be compared with the corresponding CBV depth profile also
published by Huber et al. (2017; Figure 3B, left side).

At each depth level, the contribution from lower depth levels is removed based
on the model proposed by Markuerkiaga et al. (2016). The correction for the
draining effect is applyed by a function called by this script. There are three
different option for correction (see respective functions for details):

(1) Only correct draining effect (based on model by Markuerkiaga et al., 2016).

(2) Correct draining effect (based on model by Markuerkiaga et al., 2016) &
    perform scaling to account for different vascular density and/or
    haemodynamic coupling between depth levels based on model by Markuerkiaga
    et al. (2016).

(3) Correct draining effect (based on model by Markuerkiaga et al., 2016) &
    perform scaling to account for different vascular density and/or
    haemodynamic coupling between depth levels based on data by Weber et al.
    (2008). This option allows for different correction for V1 & extrastriate
    cortex.

(4) Same as (1), i.e. only correcting draining effect, but with Gaussian random
    error added to the draining effect assumed by Markuerkiaga et al. (2016).
    The purpose of this is to test how sensitive the results are to violations
    of the model assumptions. If this solution is selected, the error bars in
    the plots do not represent the bootstrapped across-subjects variance, but
    the variance across iterations of random-noise iterations.

(5) Similar to (4), but two different types of error are simulated: (1) random
    error, sampled from a Gaussian distribution, and (2) systematic error. If
    this solution is selected, only the depth profiles for one condition are
    plotted. The error shading in the plots does then not represent the
    bootstrapped across-subjects variance, but the variance across iterations
    of random-noise iterations. In addition, two separate lines correspond to
    the systematic error (lower and upper bound). The random noise is different
    across depth levels, whereas the systematic noise uses one fixed factor
    across all depth levels, reflecting a hypothetical general bias of the
    model.

(6) Similar to (5), but in this version the effect of a systematic
    underestimation of local activity at the deepest depth level (close to WM)
    is tested. The rational for this is that due to partial volume effects
    and/or segmentation errors, the local signal at the deepest depth level
    may have been underestimated. Thus, here we simulate the profile shape
    after deconvolution with substantially higher signal at the deepest GM
    level.

The following data from Markuerkiaga et al. (2016) is used in this script,
irrespective of which draining effect model is choosen:

    "The cortical layer boundaries of human V1 in the model were fixed
    following de Sousa et al. (2010) and Burkhalter and Bernardo (1989):
    layer VI, 20%;
    layer V, 10%;
    layer IV, 40%;
    layer II/III, 20%;
    layer I, 10%
    (values rounded to the closest multiple of 10)." (p. 492)

References
----------
Huber L, Handwerker DA, Jangraw DC, Chen G, Hall A, Stueber C,
    Gonzalez-Castillo J, Ivanov D, Marrett S, Guidi M, Goense J, Poser BA,
    Bandettini PA (2017): High-resolution CBV-fMRI allows mapping of laminar
    activity and connectivity of cortical input and output in human M1. Neuron.

Markuerkiaga, I., Barth, M., & Norris, D. G. (2016). A cortical vascular model
    for examining the specificity of the laminar BOLD signal. Neuroimage, 132,
    491-498.

Weber, B., Keller, A. L., Reichold, J., & Logothetis, N. K. (2008). The
    microvascular system of the striate and extrastriate visual cortex of the
    macaque. Cerebral Cortex, 18(10), 2318-2330.
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


import numpy as np
from scipy.interpolate import griddata
from py_depthsampling.plot.plt_acr_dpth import plt_acr_dpth
from py_depthsampling.plot.plt_dpth_prfl_acr_subs import plt_dpth_prfl_acr_subs
from py_depthsampling.drain_model.drain_model_decon_01 import deconv_01
from py_depthsampling.drain_model.drain_model_decon_02 import deconv_02
from py_depthsampling.drain_model.drain_model_decon_03 import deconv_03
from py_depthsampling.drain_model.drain_model_decon_04 import deconv_04
from py_depthsampling.drain_model.drain_model_decon_05 import deconv_05
from py_depthsampling.drain_model.drain_model_decon_06 import deconv_06
from py_depthsampling.drain_model.find_peak import find_peak

# ----------------------------------------------------------------------------
# *** Define parameters

# Which draining model to use (1, 2, 3, 4, 5, or 6 - see above for details):
varMdl = 1

# Output path & prefix for plots:
strPthPltOt = '/home/john/Desktop/rebuttal_stuff/Huber_et_al_2017/deconvolution_huber_2017'  #noqa

# File type suffix for plot:
strFlTp = '.svg'

# Figure scaling factor:
varDpi = 80.0

# Limits of y-axis for across subject plot:
varAcrSubsYmin01 = 0.0
varAcrSubsYmax01 = 10.0
varAcrSubsYmin02 = 0.0
varAcrSubsYmax02 = 10.0

# Label for axes:
strXlabel = 'Cortical depth level'
strYlabel = 'Percent signal change'

# Condition labels:
lstConLbl = ['BOLD']

# Number of resampling iterations for peak finding (for models 1, 2, and 3) or
# random noise samples (models 4 and 5):
varNumIt = 10000

# Lower & upper bound of percentile bootstrap (in percent), for bootstrap
# confidence interval (models 1, 2, and 3) - this value is only printed, not
# plotted - or plotted confidence intervals in case of model 5:
varCnfLw = 0.5
varCnfUp = 99.5

# Parameters specific to 'model 4' (i.e. random noise model) and 'model 5'
# (random & systematic error model):
if (varMdl == 4) or (varMdl == 5):
    # Extend of random noise (SD of Gaussian distribution to sample noise from,
    # percent of noise to multiply the signal with):
    varNseRndSd = 0.15
    # Extend of systematic noise (only relevant for model 5):
    varNseSys = 0.3

# Parameters specific to 'model 6' (simulating underestimation of deep GM
# signal):
if varMdl == 6:
    # List of fraction of underestimation of empirical deep GM signal. For
    # instance, a value of 0.1 simulates that the deep GM signal was
    # understimated by 10%, and the deepest signal level will be multiplied by
    # 1.1. (Each factor will be represented by a sepearate line in the plot.)
    lstFctr = [0.0, 0.25, 0.5, 0.75]


# ----------------------------------------------------------------------------
# *** Define input data

print('-Model-based correction of draining effect')

# BOLD data

# Data from, of the form Huber et al. (2017), Neuron, Figure 3B on page 4
# (right side, BOLD, blue graph representing the most salient experimental
# condition), of the form aryEmpBold[1, 1, idxDpth].
aryEmpBold = np.array([627.0, 865.0, 1051.0, 1105.0, 1026.0, 915.0, 757.0,
                       613.0, 516.0, 483.0, 459.0, 454.0, 473.0, 471.0, 440.0,
                       414.0, 385.0, 307.0, 203.0, 190.0], ndmin=3)

# The data by Huber et al. (2017) are from CSF to WM, we flip the respective
# axis to bring it in accordance with our convention (from WM to CSF):
aryEmpBold = np.flip(aryEmpBold, 2)

# Scale the data to original scale:
aryEmpBold = np.multiply(aryEmpBold, 0.01)

# Number of subjects:
varNumSub = 1  # aryEmpBold.shape[0]

# Number of conditions:
varNumCon = 1  # aryEmpBold.shape[1]

# Number of equi-volume depth levels in the input data:
varNumDpth = aryEmpBold.shape[2]

# CBV data

# Data from, of the form Huber et al. (2017), Neuron, Figure 3B on page 4
# (left side, CBV, blue graph representing the most salient experimental
# condition), of the form aryEmpBold[1, 1, idxDpth].
aryEmpCbv = np.array([69.0, 237.0, 465.0, 550.0, 611.0, 557.0, 470.0, 418.0,
                      316.0, 279.0, 238.0, 294.0, 327.0, 367.0, 392.0, 409.0,
                      386.0, 295.0, 181.0, 138.0], ndmin=3)

# The data by Huber et al. (2017) are from CSF to WM, we flip the respective
# axis to bring it in accordance with our convention (from WM to CSF):
aryEmpCbv = np.flip(aryEmpCbv, 2)

# Scale the data to original scale:
aryEmpCbv = np.multiply(aryEmpCbv, 0.01)

# Since the purpose of this script is to test the effect of applying our
# deconvolution model, which is defined for V1, to the motor cortex data by
# Huber et al. (2017), we pretent that we are working with data from V1:
strRoi = 'v1'


# ----------------------------------------------------------------------------
# *** Subject-by-subject deconvolution

print('---Subject-by-subject deconvolution')

# Array for single-subject interpolation result (before deconvolution):
aryEmp5SnSb = np.zeros((varNumSub, varNumCon, 5))

if (varMdl != 4) and (varMdl != 5) and (varMdl != 6):
    # Array for single-subject deconvolution result (defined at 5 depth
    # levels):
    aryDecon5 = np.zeros((varNumSub, varNumCon, 5))
    # Array for deconvolution results in equi-volume space:
    aryDecon = np.zeros((varNumSub, varNumCon, varNumDpth))

elif (varMdl == 4) or (varMdl == 5):
    # The array for single-subject deconvolution result has an additional
    # dimension in case of model 4 (number of iterations):
    aryDecon5 = np.zeros((varNumSub, varNumIt, varNumCon, 5))
    # Array for deconvolution results in equi-volume space:
    aryDecon = np.zeros((varNumSub, varNumIt, varNumCon, varNumDpth))
    # Generate random noise for model 4:
    aryNseRnd = np.random.randn(varNumIt, varNumCon, varNumDpth)
    # Scale variance:
    aryNseRnd = np.multiply(aryNseRnd, varNseRndSd)
    # Centre at one:
    aryNseRnd = np.add(aryNseRnd, 1.0)

if varMdl == 5:
    # Additional array for deconvolution results with systematic error,
    # defined at 5 depth levels:
    arySys5 = np.zeros((varNumSub, 2, varNumCon, 5))
    # Array for deconvolutino results with systematic error, defined at
    # empirical depth levels:
    arySys = np.zeros((varNumSub, 2, varNumCon, varNumDpth))

if varMdl == 6:
    # Array for single-subject deconvolution result (defined at 5 depth
    # levels):
    aryDecon5 = np.zeros((varNumSub, len(lstFctr), varNumCon, 5))
    # Array for deconvolution results in equi-volume space:
    aryDecon = np.zeros((varNumSub, len(lstFctr), varNumCon, varNumDpth))

for idxSub in range(0, varNumSub):

    # -------------------------------------------------------------------------
    # *** Interpolation (downsampling)

    # The empirical depth profiles are defined at more depth levels than the
    # draining model. We downsample the empirical depth profiles to the number
    # of depth levels of the model.

    # The relative thickness of the layers differs between V1 & V2.
    if strRoi == 'v1':
        print('------Interpolation - V1')
        # Relative thickness of the layers (layer VI, 20%; layer V, 10%; layer
        # IV, 40%; layer II/III, 20%; layer I, 10%; Markuerkiaga et al. 2016).
        # lstThck = [0.2, 0.1, 0.4, 0.2, 0.1]
        # From the relative thickness, we derive the relative position of the
        # layers (we set the position of each layer to the sum of all lower
        # layers plus half  its own thickness):
        vecPosMdl = np.array([0.1, 0.25, 0.5, 0.8, 0.95])

    elif strRoi == 'v2':
        print('------Interpolation - V2')
        # Relative position of the layers (accordign to Weber et al., 2008,
        # Figure 5C, p. 2322). We start with the absolute depth:
        vecPosMdl = np.array([160.0, 590.0, 1110.0, 1400.0, 1620.0])
        # Divide by overall thickness (1.7 mm):
        vecPosMdl = np.divide(vecPosMdl, 1700.0)

    # Position of empirical datapoints:
    vecPosEmp = np.linspace(np.min(vecPosMdl),
                            np.max(vecPosMdl),
                            num=varNumDpth,
                            endpoint=True)

    # Vector for downsampled empirical depth profiles:
    aryEmp5 = np.zeros((varNumCon, 5))

    # Loop through conditions and downsample the depth profiles:
    for idxCon in range(0, varNumCon):
        # Interpolation:
        aryEmp5[idxCon] = griddata(vecPosEmp,
                                   aryEmpBold[idxSub, idxCon, :],
                                   vecPosMdl,
                                   method='cubic')

    # Put interpolation result for this subject into the array:
    aryEmp5SnSb[idxSub, :, :] = np.copy(aryEmp5)

    # -------------------------------------------------------------------------
    # *** Subtraction of draining effect

    # (1) Deconvolution based on Markuerkiaga et al. (2016).
    if varMdl == 1:
        aryDecon5[idxSub, :, :] = deconv_01(varNumCon,
                                            aryEmp5SnSb[idxSub, :, :])

    # (2) Deconvolution based on Markuerkiaga et al. (2016) & scaling based on
    #     Markuerkiaga et al. (2016).
    elif varMdl == 2:
        aryDecon5[idxSub, :, :] = deconv_02(varNumCon,
                                            aryEmp5SnSb[idxSub, :, :])

    # (3) Deconvolution based on Markuerkiaga et al. (2016) & scaling based on
    #     Weber et al. (2008).
    elif varMdl == 3:
        aryDecon5[idxSub, :, :] = deconv_03(varNumCon,
                                            aryEmp5SnSb[idxSub, :, :],
                                            strRoi=strRoi)

    # (4) Deconvolution based on Markuerkiaga et al. (2016), with random error.
    elif varMdl == 4:
            aryDecon5[idxSub, :, :, :] = deconv_04(varNumCon,
                                                   aryEmp5,
                                                   aryNseRnd)

    # (5) Deconvolution based on Markuerkiaga et al. (2016), with random and
    #     systematic error.
    elif varMdl == 5:
            aryDecon5[idxSub, :, :, :], arySys5[idxSub, :, :, :] = \
                deconv_05(varNumCon, aryEmp5, aryNseRnd, varNseSys)

    # (6) Deconvolution based on Markuerkiaga et al. (2016), with deep GM
    #     signal scaling factor.
    elif varMdl == 6:
            aryDecon5[idxSub, :, :, :] = \
                deconv_06(varNumCon, aryEmp5, lstFctr)

    # -------------------------------------------------------------------------
    # *** Interpolation

    # The original depth profiles were in 'equi-volume' space, and needed to
    # be downsampled in order to apply the deconvolution (because the
    # deconvolution model is defined at a lower number of depth levels than the
    # equivolume space). Here, the results of the deconvolution are brought
    # back into equivolume space. This is advantageous for the creation of
    # depth plots (equal spacing of data points on x-axis), and for the
    # calculation of peak positions (no additional information about relative
    # position of datapoints needs to be passed on).

    # Sampling points for equi-volume space:
    vecIntpEqui = np.linspace(np.min(vecPosMdl),
                              np.max(vecPosMdl),
                              num=varNumDpth,
                              endpoint=True)

    if (varMdl != 4) and (varMdl != 5) and (varMdl != 6):

        # Loop through conditions:
        for idxCon in range(0, varNumCon):

            # Interpolation back into equi-volume space:
            aryDecon[idxSub, idxCon, :] = griddata(vecPosMdl,
                                                   aryDecon5[idxSub,
                                                             idxCon,
                                                             :],
                                                   vecIntpEqui,
                                                   method='cubic')

    elif (varMdl == 4) or (varMdl == 5):

        # Loop through iterations:
        for idxIt in range(0, varNumIt):

            # Loop through conditions:
            for idxCon in range(0, varNumCon):

                # Interpolation back into equi-volume space:
                aryDecon[idxSub, idxIt, idxCon, :] = \
                    griddata(vecPosMdl,
                             aryDecon5[idxSub, idxIt, idxCon, :],
                             vecIntpEqui,
                             method='cubic')

    # For model 5, also resample systematic error term:
    if varMdl == 5:

        # Loop through conditions:
        for idxCon in range(0, varNumCon):

            # Interpolation for lower limit of systematic error term:
            arySys[idxSub, 0, idxCon, :] = \
                griddata(vecPosMdl,
                         arySys5[idxSub, 0, idxCon, :],
                         vecIntpEqui,
                         method='cubic')

            # Interpolation for upper limit of systematic error term:
            arySys[idxSub, 1, idxCon, :] = \
                griddata(vecPosMdl,
                         arySys5[idxSub, 1, idxCon, :],
                         vecIntpEqui,
                         method='cubic')

    # For model 6, loop through deep-GM-signal-intensity-scaling-factors:
    if varMdl == 6:

        # The array now has the form: aryDecon[idxSub, idxFctr, idxCon,
        # idxDepth], where idxFctr corresponds to the
        # deep-GM-signal-intensity-scaling-factors.

        # Loop through factors:
        for idxFctr in range(len(lstFctr)):

            # Loop through conditions:
            for idxCon in range(varNumCon):

                # Interpolation back into equi-volume space:
                aryDecon[idxSub, idxFctr, idxCon, :] = \
                    griddata(vecPosMdl,
                             aryDecon5[idxSub, idxFctr, idxCon, :],
                             vecIntpEqui,
                             method='cubic')


# ----------------------------------------------------------------------------
# *** Peak positions percentile bootstrap

# Bootstrapping in order to obtain an estimate of across-subjects variance is
# not performed for models 4 & 5. (Models 4 & 5 are used to test the effect of
# error in the model assumptions.)
if (varMdl != 4) and (varMdl != 5) and (varMdl != 6):

    print('---Peak positions in depth profiles - percentile bootstrap')

    # We bootstrap the peak finding. Peak finding needs to be performed both
    # before and after deconvolution, separately for all stimulus conditions.

    # Random array with subject indicies for bootstrapping of the form
    # aryRnd[varNumIt, varNumSmp]. Each row includes the indicies of the
    # subjects to the sampled on that iteration.
    aryRnd = np.random.randint(0,
                               high=varNumSub,
                               size=(varNumIt, varNumSub))

    # Loop before/after deconvolution:
    for idxDec in range(2):

        if idxDec == 0:
            print('------UNCORRECTED')

        if idxDec == 1:
            print('------CORRECTED')

        # Array for peak positins before deconvolution, of the form
        # aryPks01[idxCondition, idxIteration]
        aryPks01 = np.zeros((2, varNumCon, varNumIt))

        # Array for actual bootstrap samples:
        aryBoo = np.zeros((varNumIt, varNumDpth))

        # Loop through conditions:
        for idxCon in range(0, varNumCon):

            # Create array with bootstrap samples:
            for idxIt in range(0, varNumIt):

                # Before deconvolution:
                if idxDec == 0:
                    # Take mean across subjects in bootstrap samples:
                    aryBoo[idxIt, :] = np.mean(aryEmpBold[aryRnd[idxIt, :],
                                                          idxCon,
                                                          :],
                                               axis=0)

                # After deconvolution:
                if idxDec == 1:
                    # Take mean across subjects in bootstrap samples:
                    aryBoo[idxIt, :] = np.mean(aryDecon[aryRnd[idxIt, :],
                                                        idxCon,
                                                        :],
                                               axis=0)

            # Find peaks:
            aryPks01[idxDec, idxCon, :] = find_peak(aryBoo,
                                                    varNumIntp=100,
                                                    varSd=0.05,
                                                    lgcStat=False)

            # Median peak position:
            varTmpMed = np.median(aryPks01[idxDec, idxCon, :])

            # Confidence interval (percentile bootstrap):
            varTmpCnfLw = np.percentile(aryPks01[idxDec, idxCon, :], varCnfLw)
            varTmpCnfUp = np.percentile(aryPks01[idxDec, idxCon, :], varCnfUp)

            # Print result:
            strTmp = ('---------Median peak position: '
                      + str(np.around(varTmpMed, decimals=2)))
            print(strTmp)
            strTmp = ('---------Percentile bootstrap '
                      + str(np.around(varCnfLw, decimals=1))
                      + '%: '
                      + str(np.around(varTmpCnfLw, decimals=2)))
            print(strTmp)
            strTmp = ('---------Percentile bootstrap '
                      + str(np.around(varCnfUp, decimals=1))
                      + '%: '
                      + str(np.around(varTmpCnfUp, decimals=2)))
            print(strTmp)


# ----------------------------------------------------------------------------
# *** Plot results

print('---Plot results')

if (varMdl != 4) and (varMdl != 5) and (varMdl != 6):

    # Title and output path:
    strTmpTtl = 'Data from Huber et al. (2017)'
    strTmpPth = (strPthPltOt + 'before_')

    # Combined array with BOLD profiles before and after deconvolution, and CBV
    # profile:
    aryComb = np.concatenate((aryEmpBold[0, :, :],
                              aryDecon[0, :, :],
                              aryEmpCbv[0, :, :]), axis=0)

    # Dummy error array (no error will be plotted):
    aryErr = np.zeros(aryComb.shape)

    # Line labels:
    lstLbl = ['BOLD before deconvolution', 'BOLD after deconvolution', 'CBV']

    # Plot BOLD profiles before and after deconvolution, and CBV profile:
    plt_acr_dpth(aryComb,            # aryData[Condition, Depth]
                 aryErr,                  # aryError[Con., Depth]
                 varNumDpth,         # Number of depth levels (on the x-axis)
                 3,                  # Number of conditions (separate lines)
                 varDpi,             # Resolution of the output figure
                 varAcrSubsYmin01,   # Minimum of Y axis
                 varAcrSubsYmax01,   # Maximum of Y axis
                 False,              # Bool.: whether to convert y axis to %
                 lstLbl,         # Labels for conditions (separate lines)
                 strXlabel,          # Label on x axis
                 strYlabel,          # Label on y axis
                 strTmpTtl,          # Figure title
                 True,               # Boolean: whether to plot a legend
                 (strPthPltOt + strFlTp),
                 varSizeX=2000.0,
                 varSizeY=1400.0,
                 vecX=vecIntpEqui,
                 varNumLblY=5,
                 varPadY=(1, 2),
                 varRound=1)


elif varMdl == 4:

    # For 'model 4', i.e. the random noise model, we are interested in the
    # variance across random-noise iterations. We are *not* interested in the
    # variance across subjects in this case. Because we used the same random
    # noise across subjects, we can average over subjects.
    aryDecon = np.mean(aryDecon, axis=0)

    # Across-subjects mean after deconvolution:
    strTmpTtl = '{} after deconvolution'.format(strRoi.upper())
    strTmpPth = (strPthPltOt + 'after_')
    plt_dpth_prfl_acr_subs(aryDecon,
                           varNumSub,
                           varNumDpth,
                           varNumCon,
                           varDpi,
                           varAcrSubsYmin02,
                           varAcrSubsYmax02,
                           lstConLbl,
                           strXlabel,
                           strYlabel,
                           strTmpTtl,
                           strTmpPth,
                           strFlTp,
                           strErr='prct95',
                           vecX=vecIntpEqui)

elif varMdl == 5:

    # For 'model 5', i.e. the random & systematic noise model, we are
    # interested in the variance across random-noise iterations. We are *not*
    # interested in the variance across subjects in this case. Because we used
    # the same random noise across subjects, we can average over subjects.
    aryDecon = np.mean(aryDecon, axis=0)

    # Random noise - mean across iteratins:
    aryRndMne = np.mean(aryDecon, axis=0)
    # Random noise -  lower percentile:
    aryRndConfLw = np.percentile(aryDecon, varCnfLw, axis=0)
    # Random noise - upper percentile:
    aryRndConfUp = np.percentile(aryDecon, varCnfUp, axis=0)

    # For model 5, we only plot one stimulus condition (condition 4):
    varTmpCon = 3
    aryRndMne = aryRndMne[varTmpCon, :]
    aryRndConfLw = aryRndConfLw[varTmpCon, :]
    aryRndConfUp = aryRndConfUp[varTmpCon, :]

    # Systematic error term - mean across subjects:
    arySysMne = np.mean(arySys, axis=0)

    # Patching together systematic and random error terms:
    aryComb = np.array([aryRndMne,
                        arySysMne[0, varTmpCon, :],
                        arySysMne[1, varTmpCon, :]])

    # aryRndMne.shape
    # arySysMne[0, varTmpCon, :].shape
    # arySysMne[1, varTmpCon, :].shape

    # Patching together array for error shading (no shading for systematic
    # error term):
    aryErrLw = np.array([aryRndConfLw,
                         arySysMne[0, varTmpCon, :],
                         arySysMne[1, varTmpCon, :]])
    aryErrUp = np.array([aryRndConfUp,
                         arySysMne[0, varTmpCon, :],
                         arySysMne[1, varTmpCon, :]])

    # *** Plot response at half maximum contrast across depth

    strTmpTtl = '{}'.format(strRoi.upper())
    strTmpPth = (strPthPltOt + 'after_')

    # Labels for model 5:
    lstLblMdl5 = ['Random error',
                  'Systematic error',
                  'Systematic error']

    # Label for axes:
    strXlabel = 'Cortical depth level (equivolume)'
    strYlabel = 'fMRI signal change [a.u.]'

    # Colour for systematic error plot:
    aryClr = np.array(([22.0, 41.0, 248.0],
                       [230.0, 56.0, 60.0],
                       [230.0, 56.0, 60.0]))
    aryClr = np.divide(aryClr, 255.0)

    plt_acr_dpth(aryComb,            # aryData[Condition, Depth]
                 0,                  # aryError[Con., Depth]
                 varNumDpth,         # Number of depth levels (on the x-axis)
                 3,                  # Number of conditions (separate lines)
                 varDpi,             # Resolution of the output figure
                 0.0,                # Minimum of Y axis
                 2.0,                # Maximum of Y axis
                 False,              # Bool.: whether to convert y axis to %
                 lstLblMdl5,         # Labels for conditions (separate lines)
                 strXlabel,          # Label on x axis
                 strYlabel,          # Label on y axis
                 strTmpTtl,          # Figure title
                 True,               # Boolean: whether to plot a legend
                 (strPthPltOt + 'after' + strFlTp),
                 varSizeX=2000.0,
                 varSizeY=1400.0,
                 aryCnfLw=aryErrLw,
                 aryCnfUp=aryErrUp,
                 aryClr=aryClr,
                 vecX=vecIntpEqui)

elif varMdl == 6:

    # The array now has the form: aryDecon[idxSub, idxFctr, idxCon, idxDepth],
    # where idxFctr corresponds to the
    # deep-GM-signal-intensity-scaling-factors.

    # For 'model 6', i.e. the deep-GM signal underestimation model, we are
    # *not* interested in the variance across subjects, but in the effect of
    # the deep-GM signal scaling factor. Because we used the same deep-GM
    # scaling factor across subjects, we can average over subjects.
    aryDecon = np.mean(aryDecon, axis=0)

    # The array now has the form: aryDecon[idxFctr, idxCon, idxDepth], where
    # idxFctr corresponds to the deep-GM-signal-intensity-scaling-factors.

    # Reduce further; only one stimulus condition is plotted. The
    # deep-GM-signal-intensity-scaling-factors are treated as conditions for
    # the plot.
    aryDecon = aryDecon[:, 3, :]

    # The array now has the form: aryDecon[idxFctr, idxDepth], where idxFctr
    # corresponds to the deep-GM-signal-intensity-scaling-factors.

    # Dummy error array (no error will be plotted):
    aryErr = np.zeros(aryDecon.shape)

    strTmpTtl = '{}'.format(strRoi.upper())
    strTmpPth = (strPthPltOt + 'after_')

    # Labels for model 6 (deep-GM-signal-intensity-scaling-factors):
    lstLblMdl5 = [(str(int(np.around(x * 100.0))) + ' %') for x in lstFctr]

    # Label for axes:
    strXlabel = 'Cortical depth level (equivolume)'
    strYlabel = 'fMRI signal change [a.u.]'

    plt_acr_dpth(aryDecon,           # aryData[Condition, Depth]
                 aryErr,             # aryError[Con., Depth]
                 varNumDpth,         # Number of depth levels (on the x-axis)
                 aryDecon.shape[0],  # Number of conditions (separate lines)
                 varDpi,             # Resolution of the output figure
                 0.0,                # Minimum of Y axis
                 2.0,                # Maximum of Y axis
                 False,              # Bool.: whether to convert y axis to %
                 lstLblMdl5,         # Labels for conditions (separate lines)
                 strXlabel,          # Label on x axis
                 strYlabel,          # Label on y axis
                 strTmpTtl,          # Figure title
                 True,               # Boolean: whether to plot a legend
                 (strPthPltOt + 'after' + strFlTp),
                 varSizeX=2000.0,
                 varSizeY=1400.0,
                 vecX=vecIntpEqui)

# ----------------------------------------------------------------------------
print('-Done.')
