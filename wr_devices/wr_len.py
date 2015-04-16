#!   /usr/bin/env   python3
#    coding: utf8
'''
Main program for running a WR device's calibration

@file
@author Felipe Torres (torresfelipex1<AT>gmail.com)
@date Created on Apr 13, 2015
@copyright LGPL v2.1
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

# System modules
import time
import re

# User modules
from pts_core.bridges.wb_uart import *
from wr_devices.wr_device     import *

class WR_LEN(WR_Device) :
    '''
    Class to interface with WR LEN device
    '''

    ## Default timeout when writing a command to WR LEN
    DEF_TIMEOUT = 1

    def __init__(self, interface, port) :
        '''
        Class constructor

        Args:
            interface (WR_interfaces) : Which interface use to communicate with the device.
            port (int) : Port (or IP direction) used by WR device.
        '''
        int = ""
        if interface == WR_interfaces.usb : self.interface = "/dev/ttyUSB%d" % port
        else :
            pass # Raise ....

        self.port = port
        self.name = "WR LEN"

        #TODO: Utilizar excepciones aquí
        #try :
        self.bus = wb_UART(rdtimeout=0.1, wrtimeout=0.1, interchartimeout=0.001)
        self.bus.open(self.port)

        #except Exception, e

    # ------------------------------------------------------------------------ #

    def write_sfp_config(self, sfp_sn, port, delta_tx = 0, delta_rx = 0, beta = 0) :
        '''
        Method to write the calibration configuration for a SFP

        By now it doesn't check if passed config is inserted succesfully.

        Args:
            sfp_sn (str) : The serial number of the SFP
            port (int) : Port
            delta_tx (int) : Transmission delay
            delta_rx (int) : Reception delay
            beta (int) : WR Device asymmetry
        '''

        # Example command : sfp add AXGE-1254-0531 wr0 0 0 0
        cmd = "sfp add %s wr%d %d %d %d" % \
        (sfp_sn, port-1, delta_tx, delta_rx, beta)
        self.bus.cmd_w(cmd, False)
        #TODO: check if insertion was succesfull
        time.sleep(self.DEF_TIMEOUT) # Give enough time to WR LEN for processing it!!

    # ------------------------------------------------------------------------ #

    def erase_sfp_config(self) :
        '''
        Method to erase the SFP config DB.

        WR LEN SFP DB has only 4 registers availables (2 types of SFP x 2 ports).
        Before writing a sfp config when DB is full or if you will to rewrite an
        exisiting config, you must to erase DB.
        '''

        self.bus.cmd_w("sfp erase")
        time.sleep(self.DEF_TIMEOUT) # Give enough time to WR LEN for processing it!!

    # ------------------------------------------------------------------------ #

    def load_sfp_config(self) :
        '''
        Method for matching the stored SFP config with the current parameters.

        This is equivalent to :
        - ptp stop
        - sfp detect
        - sfp match
        - ptp start

        Returns:
            How many SFP configurations are matched.
        '''
        cmd_list = [\
        "ptp stop",
        "sfp detect",
        "sfp match",
        "ptp start"\
        ]

        ret = ""
        count = 0
        for cmd in cmd_list :
            ret += self.bus.cmd_w(cmd)
            time.sleep(self.DEF_TIMEOUT) # Give enough time to WR LEN for processing it!!

        count = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape("matched"), ret))

        return count

    # ------------------------------------------------------------------------ #

    def erase_init(self) :
        '''
        Method for erasing init script.

        This is equivalent to "init erase"
        '''
        self.bus.cmd_w("init erase",False)
        time.sleep(self.DEF_TIMEOUT) # Give enough time to WR LEN for processing it!!

    # ------------------------------------------------------------------------ #

    def add_init(self, cmd_list) :
        '''
        Method to add a new command to init script.

        This method doesn't check if passed commands are valid.
        Is equivalent to "init add <command>"

        Args:
            cmd (list of str) : A list with commands to add
        '''
        for cmd in cmd_list :
            self.bus.cmd_w("init add %s" % cmd,False)
            time.sleep(self.DEF_TIMEOUT) # Give enough time to WR LEN for processing it!!

    # ------------------------------------------------------------------------ #

    def show_sfp_config(self) :
        '''
        Method to retrieve sfp configuration database.

        This method is equivalent to "sfp show"
        '''
        ret = self.bus.cmd_w("sfp show")
        time.sleep(self.DEF_TIMEOUT) # Give enough time to WR LEN for processing it!!

        return ret

    # ------------------------------------------------------------------------ #

    def ptp_stop(self) :
        '''
        Method to stop ptp
        '''
        self.bus.cmd_w("ptp stop")
        time.sleep(self.DEF_TIMEOUT) # Give enough time to WR LEN for processing it!!

    # ------------------------------------------------------------------------ #

    def ptp_start(self) :
        '''
        Method to start/restart ptp

        When ptp is already started it works as a restart.
        '''
        self.bus.cmd_w("ptp start")
        time.sleep(self.DEF_TIMEOUT) # Give enough time to WR LEN for processing it!!
