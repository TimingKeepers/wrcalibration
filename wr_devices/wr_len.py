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
from main.wrcexceptions       import *

# This attribute permits dynamic loading inside wrcalibration class.
__wrdevice__ = "WR_LEN"

class WR_LEN(WR_Device) :
    '''
    Class to interface with WR LEN device
    '''

    ## Default timeout when writing a command to WR LEN
    DEF_TIMEOUT = 1.5

    def __init__(self, interface, port, name="WR LEN") :
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
        self.name = name

        #TODO: Utilizar excepciones aquí
        #try :
        self.bus = wb_UART(rdtimeout=0.1, wrtimeout=0.1, interchartimeout=0.01)
        self.bus.open(self.port)

        self.show_dbg = False

        #except Exception, e

    # ------------------------------------------------------------------------ #

    def close(self) :
        '''
        Close bus connection to WR LEN
        '''
        self.bus.close()

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

        if self.show_dbg :
            print("%s << %s" % (self.name, cmd))

        self.bus.cmd_w(cmd, False)
        #TODO: check if insertion was succesfull

    # ------------------------------------------------------------------------ #

    def erase_sfp_config(self) :
        '''
        Method to erase the SFP config DB.

        WR LEN SFP DB has only 4 registers availables (2 types of SFP x 2 ports).
        Before writing a sfp config when DB is full or if you will to rewrite an
        exisiting config, you must to erase DB.
        '''
        self.bus.cmd_w("sfp erase")

        if self.show_dbg :
            print("%s << %s" % (self.name,"sfp erase"))

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

            if self.show_dbg :
                print("%s << %s >> %s" % (self.name,cmd,ret))

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
        time.sleep(self.DEF_TIMEOUT)

        if self.show_dbg :
            print("%s << %s" % (self.name,"init erase"))

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

            if self.show_dbg :
                print("%s << %s" % (self.name,cmd))

            time.sleep(self.DEF_TIMEOUT) # Give enough time to WR LEN for processing it!!

    # ------------------------------------------------------------------------ #

    def show_sfp_config(self) :
        '''
        Method to retrieve sfp configuration database.

        This method is equivalent to "sfp show"
        '''
        return self.bus.cmd_w("sfp show")

    # ------------------------------------------------------------------------ #

    def ptp_stop(self) :
        '''
        Method to stop ptp
        '''
        self.bus.cmd_w("ptp stop")

        if self.show_dbg :
            print("%s << %s" % (self.name,"ptp stop"))

    # ------------------------------------------------------------------------ #

    def ptp_start(self) :
        '''
        Method to start/restart ptp

        When ptp is already started it works as a restart.
        '''
        self.bus.cmd_w("ptp start")

        if self.show_dbg :
            print("%s << %s" % (self.name,"ptp start"))

    # ------------------------------------------------------------------------ #

    def raw_status(self) :
        '''
        Method to retrieve status info from device.

        This is equivalent to "stat" command in WR-LEN
        '''
        if self.show_dbg :
            print("%s << %s" % (self.name,"stat"))

        return self.bus.cmd_w("stat")

    # ------------------------------------------------------------------------ #

    def in_trackphase(self) :
        '''
        Method to ask a device if servo state is TRACK PHASE.

        Returns:
            True if servo state is TRACK PHASE.
        '''
        stat = self.raw_status()

        for i in stat.split(" ") :
            if "ss" in i :

                if self.show_dbg :
                    print("%s << track phase? >> %s" % (self.name,i.split(":")[-1]))

                if "'TRACK_PHASE'" == i.split(":")[-1] :
                    return True
                else : return False

    # ------------------------------------------------------------------------ #

    def get_rtt(self) :
        '''
        Method to ask the device for Round-trip time value (in ps).

        Returns:
            Round-trip time value in ps.
        '''
        stat = self.raw_status()

        for i in stat.split(" ") :
            if "mu" in i :
                return int(i.split(":")[-1])

        #TODO: Lanzar excepción

    # ------------------------------------------------------------------------ #

    def get_phy_delays(self) :
        '''
        Method to ask the device for PHY delays.

        Returns:
            A dict with two keys: master and slave. Each key has associated
            a tuple with values (Tx delay, Rx delay), both in ps.
        '''
        delays = {}
        stat = self.raw_status()

        for i in stat.split(" ") :
            if "dtxm" in i :
                dtxm = int(i.split(":")[-1])
            elif "drxm" in i :
                drxm = int(i.split(":")[-1])
            elif "dtxs" in i :
                dtxs = int(i.split(":")[-1])
            elif "drxs" in i :
                drxs = int(int(i.split(":")[-1]))
                break; # drxs is the last value found in stat output so break the loop

        delays['master'] = (dtxm,drxm)
        delays['slave']  = (dtxs,drxs)

        return delays

    # ------------------------------------------------------------------------ #

    def set_slaveport(self, port) :
        '''
        Method to set "port" to slave mode.

        Raises:
            NotValidPort when port doesn't exists in the used device.
        '''
        if port < 1 and port > 2 :
            raise NotValidPort("WR LEN haven't got %d ports." % port)
        self.bus.cmd_w("mode slave_port%d" % port)
        time.sleep(self.DEF_TIMEOUT)
        self.bus.cmd_w("ptp start")
        time.sleep(self.DEF_TIMEOUT)

        if self.show_dbg :
            print("%s << %s" % (self.name,"mode slave_port%d"%port))


    # ------------------------------------------------------------------------ #

    def set_master(self) :
        '''
        Abstract method to set device to master mode.
        '''
        self.bus.cmd_w("mode master")
        time.sleep(self.DEF_TIMEOUT*2) # Looking PLL takes some time
        self.bus.cmd_w("ptp start")
        time.sleep(self.DEF_TIMEOUT)

        if self.show_dbg :
            print("%s << %s" % (self.name,"mode master"))
