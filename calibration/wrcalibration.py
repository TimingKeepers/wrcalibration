#!   /usr/bin/env   python3
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
import time

# User defined modules
from main.wrcexceptions import *



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
        self.cfg_dict['port-delay'] = {}

    # ------------------------------------------------------------------------ #

    def enable_dbg(self) :
        '''
        Enable debug output.

        This methods enables all debugging info for the added devices.
        '''
        self.show_dbg = True
        for device in self.devices :
            device.show_dbg = True
        if self.instr != None :
            self.instr.show_dbg = True

    # ------------------------------------------------------------------------ #

    def disable_dbg(self) :
        '''
        Disable debug output.

        This methods disables all debugging info for the added devices.
        '''
        self.show_dbg = False
        for device in self.devices :
            device.show_dbg = False
        if self.instr != None :
            self.instr.show_dbg = False

    # ------------------------------------------------------------------------ #

    def add_wr_device(self, name, device_params) :
        '''
        Method to add a WR device (not calibrated).

        This method use the param name to load a concrete WR device controller \
        from module wr_devices.

        Args:
            name (str) : The name param must be the name of a WR device file \
            located in the folder wr_devices.
            device_params (list) : This variable will be passed to WR device constructor. \
            It is expected that device_params contains 2 items : [interface,port]

        Raises:
            DeviceNotFound if name is not a valid WR device name in wr_devices module.
        '''
        try :
            module = "wr_devices.%s" % name
            wr_device = importlib.import_module(module)
            name = getattr(wr_device,"__wrdevice__")
            class_ = getattr(wr_device,name)
            self.devices.append(class_(device_params[0],device_params[1]))

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
            module = "measurement.%s" % name
            wr_device = importlib.import_module(module)
            name = getattr(wr_device,"__meas_instr__")
            class_ = getattr(wr_device,name)
            self.instr = class_(device_params[0])

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
        flag = 0
        with open(cfg_file, 'r', encoding='utf-8') as cfg :
            for line in cfg :
                # Skip date line
                if line[0] == '#' :
                    continue

                if line[0] == '@' :
                    key = line[1:-1]
                    if key == 'fiber-latency'   : flag = 1
                    if key == 'fiber-asymmetry' : flag = 2
                    if key == 'port-delay'      : flag = 3
                    continue

                if flag == 1 :
                    flag = 0
                    delta1 = float( line.split(" ")[0].split(":")[1] )
                    print("delta 1 %f" % delta1)
                    delta2 = float( line.split(" ")[1].split(":")[1][:-1] )
                    print("delta 2 %f" % delta2)
                    self.cfg_dict['fiber-latency']['delta1'] = delta1
                    self.cfg_dict['fiber-latency']['delta2'] = delta2

                if flag == 2 :
                    for i in line.split(" ") :
                        k = i.split(":")[0]
                        v = i.split(":")[1]
                        if v[-1] == '\n' :
                            v = v[:-1]
                            flag = 0
                        self.cfg_dict['fiber-asymmetry'][k] = float(v)

                if flag == 3 :
                    for i in line.split(" ") :
                        k = i.split(":")[0]
                        dtxs = i.split(":")[1].split(",")[0]
                        drxs = i.split(":")[1].split(",")[1]
                        if drxs[-1] == '\n' :
                            drxs = drxs[:-1]
                            flag = 0
                        self.cfg_dict['port-delay'][k] = (float(dtxs), float(drxs))

        print("Configuration loaded.")

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
        master = self.devices[0]
        slave = self.devices[1]

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
            mean_rtt /= n_samples

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

        self.cfg_dict['fiber-latency']['delta1'] = delta1
        self.cfg_dict['fiber-latency']['delta2'] = delta2
        print("Fiber latency : delta1 = %f , delta2 = %f" % (delta1,delta2))

    # ------------------------------------------------------------------------ #

    def fiber_asymmetry(self, n_samples=10, t_samples=5, port = 1, sfp = "blue") :
        '''
        Method to calculate the fiber asymmetry.

        This method calculates the asymmetry for a
        This method calculates the fiber asymmetry for a few meters long fiber \
        (delta_1) and for a few kilometers long (delta_2). First fiber will be
        called f1 and second one f2.
        Calculated values where stored in cfg_dict with the key "fiber-latency".

        Args:
            n_samples (int) : Indicates how many values will be used for computing \
            stadistics values.
            t_samples (int) : The time between samples.
            port (int) : The port used for connecting master to slave.
            sfp (str) : Indicates which sfp is used in WR slave device.

        Raises:
            ValueError if master_chan or slave_chan are not set.
            TriggerNotSet if trigger levels are not set.
            MeasuringError if a time interval value is higher than expected.
        '''
        if len(self.devices) < 2 :
            raise WRDeviceNeeded("To measure fiber latency, at least, 2 WR devices are needed.")

        if self.instr == None :
            raise MeasurementInstrumentNeeded("To measure skew between PPS signals a measurement instrument must be added.")

        if self.cfg_dict['fiber-latency']['delta1'] == 0 :
            raise FiberLatencyNeeded("A valid fiber latency values are needed to use this method.")

        # Assign one device as master and the other as slave
        master = self.devices[0]
        slave = self.devices[1]

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

        # Measure delay between the 2 PPS signals from both WR devices
        skew = []

        for fiber in self.fibers :
            if fiber == 'f1+f2' : continue

            print("Please connect both WR devices with fiber %s and press Enter" % (fiber))
            input()
            print("Now connect their PPS outputs to the measurement instrument and press Enter")
            input()
            time.sleep(1)

            # Wait until servo state in TRANCK PHASE
            if self.show_dbg :
                print("Waiting until TRACK PHASE.....")

            while not slave.in_trackphase() :
                time.sleep(2)

            print("Measuring skew between PPS signals, it should take a long time...")
            mean_skew = self.instr.mean_time_interval(n_samples, t_samples)
            if mean_skew >= 1e-6 :
                raise MeasuringError("Time interval between input 1 and 2 is more than expected. Are the input channels adequately connected?")
            skew.append(mean_skew)

        # Calculate alpha and alpha_n -------------------------

        # Pass time measures from s to ps
        skew[0] = skew[0] * 1e12
        skew[1] = skew[1] * 1e12
        if self.show_dbg :
            print("Mean skew master to slave with f1: %G" % skew[0])
            print("Mean skew master to slave with f2: %G" % skew[1])

        dif = skew[1] - skew[0]
        delta_1 = self.cfg_dict['fiber-latency']['delta1']
        delta_2 = self.cfg_dict['fiber-latency']['delta2']
        alpha = ( 2 * dif ) / ( 0.5 * delta_2 - dif )
        alpha_n = pow(2,40) * ( ((alpha+1)/(alpha+2)) - 0.5 )
        # When measuring with violet sfp in the slave device, it's needed change the sign
        if sfp == "violet" : alpha_n = alpha_n * -1
        self.cfg_dict['fiber-asymmetry']["%s-wr%d"%(sfp,port)] = alpha_n
        print("Fiber asymmetry value for port %d and sfp %s = %d" % (port,sfp,alpha_n))

    # ------------------------------------------------------------------------ #

    def calibrate_device_port() :
        '''
        Method to calibrate a port for a WR device.
        '''
