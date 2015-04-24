#!   /usr/bin/env   python3
# -*- coding: utf-8 -*
'''
Class that implements the interface Calibration_instrument for the Tektronix DPO7354.

@file
@date Created on Apr. 20, 2015
@author Felipe Torres (torresfelipex1<AT>gmail.com)
@copyright LGPL v2.1
@see https://github.com/python-ivi/python-vxi11
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
import time

# User modules
import vxi11

class DPO7354(Calibration_instrument) :
    '''
    Class that implements the interface Calibration_instrument for the Tektronix DPO7354.

    This implementation allow to use a Tektronix DPO7354 Oscilloscope as
    measurement instrument for White Rabbit calibration procedure.
    '''
    def __init__(self, ip) :
        '''
        Constructor

        Args:
            ip (str) :
        '''
        self.instr = vxi11.Instrument(ip, name="DPO 7354")
        self.show_dbg = False

    # ------------------------------------------------------------------------ #

    def trigger_level(self, v_min=0, v_max=5) :
        '''
        Method to determine the best trigger level for each input channel.

        Args:
            v_min (float) : Minimum voltage level for the input signal
            v_max (float) : Maximum voltage level for the input signal

        Returns a float tuple with the trigger level for input channel 1 and 2.
        '''
        return (0.4,0.4)

    # ------------------------------------------------------------------------ #

    def mean_time_interval(self, n_samples, t_samples, input1_trig, input2_trig) :
        '''
        Abstract method to measure time interval between two input signals.

        This will measure delay master to slave. For the best results use
        the method.

        Before using this method, master_chan and slave_chan must be set.

        Args:
            n_samples (int) : Number of measures to be done.
            t_samples (int) : Time between samples (should be greater than 1ms)
            input1_trig (float) : Trigger level for the input 1
            input2_trig (float) : Trigger level for the input 2

        Returns:

        '''

        # Initial device configuration --------------------

        if self.show_dbg :
            print("Setting the initial instrument configuration.")

        # Reset the device
        self.instr.write("*RST")
        time.sleep(3) # Wait 3 seconds for command to complete

        # Use Autoset to simplify the setting process, really needed?
        self.instr.write("AUTOSET EXECUTE") # EXECUTE is equivalent to press AUTOSET button
        time.sleep(0.5)

        # Display used channels
        self.instr.write
        self.instr.write("SELECT:%d ON" % self.master_chan)
        time.sleep(0.5)
        self.instr.write("SELECT:%d ON" % self.slave_chan)
        time.sleep(0.5)

        # Configure the channels
        # Set coupling to AC
        self.instr.write("CH%d:COUPLING DC" % self.master_chan)
        time.sleep(0.5)
        self.instr.write("CH%d:COUPLING DC" % self.slave_chan)
        time.sleep(0.5)

        # Set channel position
        self.instr.write("CH%d:POSITION -2" % self.master_chan)
        time.sleep(0.5)
        self.instr.write("CH%d:POSITION -2" % self.slave_chan)
        time.sleep(0.5)
        # Set channel termination
        self.instr.write("CH%d:TERMINATION 1E6" % self.master_chan)
        time.sleep(0.5)
        self.instr.write("CH%d:TERMINATION 1E6" % self.slave_chan)
        time.sleep(0.5)
        # Set channel scale
        self.instr.write("CH%d:SCALE 600E-3" % self.master_chan)
        time.sleep(0.5)
        self.instr.write("CH%d:SCALE 600E-3" % self.slave_chan)
        time.sleep(0.5)

        # Set horizontal scale TODO:scale value variable
        self.instr.write("CH%d:MODE:SCALE 20E-9" % self.master_chan)
        time.sleep(0.5)
        self.instr.write("CH%d:MODE:SCALE 20E-9" % self.slave_chan)
        time.sleep(0.5)

        #TODO:Maybe set horizontal sample rate HORIZONTAL:MODE:SAMPLERATE

        # Configure the trigger
        self.instr.write("TRIGGER:A:EDGE:SOURCE CH%d" % self.master_chan)
        time.sleep(0.5)
        # TODO: not a fix value for trigger level
        self.instr.write("TRIGGER:A:LEVEL:CH%d 0.4" % self.master_chan)
        time.sleep(0.5)

        # Configure the instrument to measure time delay between PPS signals
        self.instr.write("MEASUREMENT:IMMED:SOURCE1 CH%d" % self.master_chan)
        time.sleep(0.5)
        self.instr.write("MEASUREMENT:IMMED:SOURCE2 CH%d" % self.slave_chan)
        time.sleep(0.5)
        self.instr.write("MEASUREMENT:IMMED:DELAY:DIRECTION FORWARDS")
        time.sleep(0.5)
        self.instr.write("MEASUREMENT:IMMED:DELAY:EDGE1 RISE")
        time.sleep(0.5)
        self.instr.write("MEASUREMENT:IMMED:DELAY:EDGE2 RISE")
        time.sleep(0.5)
        self.instr.write("MEASUREMENT:IMMED:TYPE DELAY")
        time.sleep(0.5)

        # Check for errors in the initial configuration
        errors = self.drv.query("syst:err?")
        if errors[0] != 1 :
            # Throw an exception not a print!!
            print("Error in initial config: " + errors)

        # Measurement -------------------------------------

        mean = 0

        for i in range(n_samples) :
            cur = float(self.instr.ask("MEASUREMENT:IMMED:VALUE?"))
            mean += cur

            if self.show_dbg :
                print("%DPO7354 TINT: %g" % (cur))
            time.sleep(t_samples)
        mean /= n_samples

        print(mean)
        print(type(mean))

        return mean
