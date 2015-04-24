!   /usr/bin/env   python3
# -*- coding: utf-8 -*
'''
Main class for WR Calibration procedure.

@file
@date Created on Apr 23, 2015
@author Felipe Torres (torresfelipex1<AT>gmail.com)
@copyright LGPL v2.1
@see http://www.ohwr.org/projects/white-rabbit/wiki/Calibration
@ingroup calibration
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
import importlib


class WR_calibration() :
    '''
    Main class for WR Calibration procedure.


    '''
    ## Dictionary to store calibration parameters
    cfg_dict = {}

    ## List to handle connected WR devices
    devices = []

    ## Measurement instrument
    instr = None

    ## Debug output, not handle it directly! Use the methods.
    show_dbg = False

    fibers = ["f1","f2","f1+f2"]

    def __init__(self):
        '''
        Constructor
        '''
        self.cfg_dict['fiber-latency'] = {}
        self.cfg_dict['fiber-latency']['delta1'] = 0
        self.cfg_dict['fiber-latency']['delta2'] = 0

        self.cfg_dict['fiber-asymmetry'] = {}
        self.cfg_dict['fiber-asymmetry']['']

    # ------------------------------------------------------------------------ #

    def enable_dbg(self) :
        '''
        Enable debug output.

        This methods enables all debugging info for the added devices.
        '''
        self.show_dbg = True
        for device in devices :
            device.show_dbg = True
        if instr != None :
            instr.show_dbg = True

    # ------------------------------------------------------------------------ #

    def disable_dbg(self) :
        '''
        Disable debug output.

        This methods disables all debugging info for the added devices.
        '''
        self.show_dbg = False
        for device in devices :
            device.show_dbg = False
        if instr != None :
            instr.show_dbg = False

    # ------------------------------------------------------------------------ #

    def add_device(self, name, device_params) :
        '''
        Method to add a WR device (not calibrated).

        This method use the param name to load a concrete WR device controller \
        from module wr_devices.

        Args:
            name (str) : The name param must be the name of a WR device controller \
            located in the folder wr_devices.
            device_params (list) : This variable will be passed to WR device constructor. \
            It is expected that device_params contains 2 items : [interface,port]

        Raises:
            DeviceNotFound if name is not a valid WR device name in wr_devices module.
        '''
        try :
            wr_device = importlib.import_module("wr_devices." % name)
            class_name = getattr(wr_devices,wr_device.__wrdevice__)
            devices.append(clasname(device_params[0],device_params[1]))

        except ImportError as ierr :
            raise DeviceNotFound(ierr.msg)

    # ------------------------------------------------------------------------ #

    def add_meas_instr(self, name, device_params) :
        '''
        Method to add a Measurement instrument.

        This method use the param name to load a concrete Calibration Instrument \
        controller from module calibration.

        Args:
            name (str) : The name param must be the name of a Calibration Instrument \
            controller located in the folder calibration.
            device_params (list) : This variable will be passed to Calibration \
            Instrument constructor. It is expected that device_params contains \
            3 items : [port,master_chan,slave_chan]

        Raises:
            DeviceNotFound if name is not a valid WR device name in wr_devices module.
        '''
        try :
            meas_instr = importlib.import_module("calibration." % name)
            class_name = getattr(meas_instr,meas_instr.__meas_instr__)
            instr = clasname(device_params[0],device_params[1])

        except ImportError as ierr :
            raise DeviceNotFound(ierr.msg)

    # ------------------------------------------------------------------------ #

    def read_config(self, cfg_file) :
        '''
        Method to load a stored calibration configuration from a file.

        This method loads all configuration in the file cfg_file. So any configuration
        in memory will be overwrited. If you want to preserve some measured values
        before read a configuration file you can comment lines in the file with
        "#" or store them to a file using "write_config".

        Args:
            cfg_file(str) : Path to a configuration file.
        '''
        cfg_dict = {}
        with open(config_file, 'r', encoding='utf-8') as cfg :
            for line in cfg :
                print("line : %s" % line)
                if line[0] == '#' :
                    continue
                if line[0] == '@' :
                    key = line[1:-1]
                    print("key : %s" % key)
                    continue
                alpha = int(line.split(" ")[0].split(":")[1])
                print("alpha : %d" % alpha)

                dtx = int(line.split(" ")[1].split(":")[1])
                print("dtx : %d" % dtx)

                drx = int(line.split(" ")[2].split(":")[1])
                print("drx : %d" % drx)

                cfg_dict[key] = [alpha,dtx,drx]

    # ------------------------------------------------------------------------ #

    def write_config(self) :
        '''
        Method to store obtained calibration configuration to a file.
        '''
        pass

    # ------------------------------------------------------------------------ #

    def fiber_latency(self, n_samples=10, t_samples=5) :
        '''
        Method to calculate the reference fiber latency.

        This method calculates the fiber delay for a few meters long fiber \
        (delta_1) and for a few kilometers long (delta_2). First fiber will be
        called f1 and second one f2.
        Calculated values where stored in cfg_dict with the key "fiber-latency".

        Args:
            n_samples (int) : Indicates how many values will be used for computing \
            stadistics values.
            t_samples (int) : The time between samples.

        Raises:
            WRDeviceNeeded
        '''
        if len(self.devices) < 2 :
            raise WRDeviceNeeded("To measure fiber latency, at least, 2 WR devices are needed.")

        # Assign one device as master and the other as slave
        master = devices[0]
        slave = devices[1]

        # WR device configuration -----------------------------------

        # First, set all delays and beta values in sfp database to 0
        if self.show_dbg :
            print("Setting initial parameters in WR devices...\n")
            print("Erasing sfp database...")
        master.erase_sfp_config()
        slave.erase_sfp_config()

        if self.show_dbg :
            print("Writing initial configuration to sfp database...")
        slave.write_sfp_config("AXGE-1254-0531",1)
        master.write_sfp_config("AXGE-3454-0531",1)
        master.load_sfp_config()
        slave.load_sfp_config()
        slave.set_slaveport(1)
        master.set_master()

        if self.show_dbg :
            print("\nStarting fiber latency measurement procedure.\n")

        # Retrieve Round-trip time and bitslide values for both master and slave
        # WR devices when connected by f1, f2 and f1+f2.
        delays_dict = {}
        rtt_dict = {}

        for fiber in self.fibers :
            print("Please connect both WR devices with fiber %s on port 1 and press Enter"\
            % (fiber))
            input()
            time.sleep(1)

            # Wait until servo state in TRANCK PHASE
            if self.show_dbg :
                print("Waiting until TRACK PHASE.....")

            while not slave.in_trackphase() :
                time.sleep(2)

            if self.show_dbg :
                print("Measuring round-trip time (It will take %d s aprox.)..." \
                % (n_samples*t_samples))

            mean_rtt = 0
            for i in range(n_samples) :
                rtt = slave.get_rtt()
                mean_rtt += rtt
                time.sleep(t_samples)
            mean_rtt /= N_SAMPLES

            if self.show_dbg :
                print("Mean rtt : %f" % mean_rtt)

            delays_dict[fiber] = slave.get_phy_delays()
            print(delays_dict[fiber])
            rtt_dict[fiber] = mean_rtt

            # As Rx delays are set to 0 in sfp database, the stat values for Rx
            # are the bitslides
            delay_mm1 = rtt_dict['f1'] - delays_dict['f1']['master'][1] - delays_dict['f1']['slave'][1]
            print("delay_mm1 : %f" % delay_mm1)
            delay_mm2 = rtt_dict['f2'] - delays_dict['f2']['master'][1] - delays_dict['f2']['slave'][1]
            print("delay_mm2 : %f" % delay_mm2)
            delay_mm3 = rtt_dict['f1+f2'] - delays_dict['f1+f2']['master'][1] - delays_dict['f1+f2']['slave'][1]
            print("delay_mm3 : %f" % delay_mm3)

            delta1 = delay_mm3 - delay_mm2
            delta2 = delay_mm3 - delay_mm1

            self.cfg_dict['fiber_latency'] = [delta1,delta2]

            print("Fiber latency values : delta1 = %.1f , delta2 =%.1f" %\
            (delta1,delta2))

    def fiber_asymmetry() :
        '''
        Method to calculate the fiber asymmetry.
        '''

    def calibrate_device_port() :
        '''
        Method to calibrate a port for a WR device.
        '''
