#!   /usr/bin/env   python3
# -*- coding: utf-8 -*
'''
Abstract class to define the API for a measurement instrument

@file
@date Created on Apr 16, 2015
@author Felipe Torres (torresfelipex1<AT>gmail.com)
@copyright LGPL v2.1
@ingroup measurement
'''

#------------------------------------------------------------------------------|
#                   GNU LESSER GENERAL PUBLIC LICENSE                          |
#                 ------------------------------------                         |
# This source file is free software; you can redistribute it and/or modify it  |
# under the terms of the GNU Lesser General Public License as published by the |
# Free Software Foundation; either version 2.1 of the License, or (at your     |
# option) any later version. This source is distributed in the hope that it    |
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant   |
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser   |
# General Public License for more details. You should have received a copy of  |
# the GNU Lesser General Public License along with this  source; if not,       |
# download it from http://www.gnu.org/licenses/lgpl-2.1.html                   |
#------------------------------------------------------------------------------|

#-------------------------------------------------------------------------------
#                                   Import                                    --
#-------------------------------------------------------------------------------
# Import system modules
import abc

class Calibration_instrument() :
    '''
    Calibration instrument API

    Abstract class that represents the API that a generic measurement instrument
    must implement to be accepted as calibration instrument for WR Calibration
    procedure.

    The main calibration procedure expects a homogeneus interface to any instrument
    that could be used to measure skew between PPS signals from WR devices.
    '''
    __metaclass__ = abc.ABCMeta

    ## The input channel for the slave signal
    slave_chan  = ""
    ## The input channel for the master signal
    master_chan = ""

    # The following methods must be implemented by a concrete class for a WR device.

    @abc.abstractmethod
    def trigger_level(self, v_min=0, v_max=5) :
        '''
        Abstract method to determine a good trigger level for each input channel.

        Before using this method, master_chan and slave_chan must be set.

        Args:
            v_min (float) : Minimum voltage level for the input signal
            v_max (float) : Maximum voltage level for the input signal

        Returns:
            A float tuple with the trigger level for input channel 1 and 2.

        Raises:
            ValueError if master_chan or slave_chan are not set.
        '''

    # ------------------------------------------------------------------------ #

    @abc.abstractmethod
    def mean_time_interval(self, n_samples, t_samples, input1_trig, input2_trig) :
        '''
        Abstract method to measure time interval between two input signals.

        This method measures time interval between the PPS input from the master
        to the PPS input from the slave. It makes n_samples and calculates the
        mean value.

        Before using this method, master_chan and slave_chan must be set.

        Args:
            n_samples (int) : Number of measures to be done.
            t_samples (int) : Time between samples (should be greater than 1ms)
            input1_trig (float) : Trigger level for the input 1
            input2_trig (float) : Trigger level for the input 2

        Returns:
            The mean time interval master to slave.

        Raises:
            ValueError if master_chan or slave_chan are not set.
        '''
