#!   /usr/bin/env   python3
# -*- coding: utf-8 -*
'''
Abstract class to define the API for WR Devices

@file
@date Created on Apr 13, 2015
@author Felipe Torres (torresfelipex1<AT>gmail.com)
@copyright LGPL v2.1
@ingroup wr_devices
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
import enum

class WR_interfaces(enum.Enum) :
    '''
    This class represents the available interfaces for connect with WR devices.
    '''
    usb      = 0
    usb_acm  = 1
    ethernet = 2



class WR_Device() :
    '''
    Abstract class that represents the API to access from Python to some WR device.

    '''
    __metaclass__ = abc.ABCMeta


    # The following methods must be implemented by a concrete class for a WR device.

    @abc.abstractmethod
    def write_sfp_config(self, sfp_sn, port=1, delta_tx = 0, delta_rx = 0, beta = 0) :
        '''
        Abstract method to write the calibration configuration for a SFP

        Args:
            sfp_sn (str) : The serial number of the SFP
            port (int) : Port
            delta_tx (int) : Transmission delay
            delta_rx (int) : Reception delay
            beta (int) : WR Device asymmetry
        '''

    @abc.abstractmethod
    def erase_sfp_config(self) :
        '''
        Abstract method to erase the SFP config DB.

        Some devices may need to erase it before insert new values.
        '''

    @abc.abstractmethod
    def load_sfp_config(self) :
        '''
        Method for matching the stored SFP config with the current parameters.

        '''

    @abc.abstractmethod
    def erase_init(self) :
        '''
        Abstract method for erasing init script.

        This is equivalent to "init erase"
        '''

    @abc.abstractmethod
    def add_init(self, cmd_list) :
        '''
        Abstract method to add a new command to init script.

        This method doesn't check if passed commands are valid.
        Is equivalent to "init add <command>"

        Args:
            cmd (list of str) : A list with commands to add
        '''

    @abc.abstractmethod
    def show_sfp_config(self) :
        '''
        Abstract method to retrieve sfp configuration database.

        This method is equivalent to "sfp show"
        '''

    @abc.abstractmethod
    def ptp_stop(self) :
        '''
        Method to stop ptp
        '''

    @abc.abstractmethod
    def ptp_start(self) :
        '''
        Abstract method to start/restart ptp

        When ptp is already started it works as a restart.
        '''

    @abc.abstractmethod
    def raw_status(self) :
        '''
        Abstract method to retrieve status info from device.
        '''

    @abc.abstractmethod
    def in_trackphase(self) :
        '''
        Abstract method to ask the device if servo state is TRACK PHASE.

        Returns:
            True if servo state is TRACK PHASE.
        '''

    @abc.abstractmethod
    def get_rtt(self) :
        '''
        Abstract method to ask the device for Round-trip time value (in ps).

        Returns:
            Round-trip time value in ps.
        '''

    @abc.abstractmethod
    def get_phy_delays(self) :
        '''
        Abstract method to ask the device for PHY delays.

        Returns:
            A tuple with (Tx delay, Rx delay) both in ps.
        '''
