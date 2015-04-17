#!   /usr/bin/env   python3
# -*- coding: utf-8 -*
'''
Procedure to measure fiber latency

@file
@date Created on Apr 17, 2015
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
import time

N_SAMPLES = 5
TIME_BETWEEN_SAMPLES = 10
FIBERS = ["f1","f2","f1+f2"]

def ref_fiber_latency(master, slave) :
    '''

    '''

    # First set all delays and beta values in sfp database to 0
    master.erase_sfp_config()
    slave.erase_sfp_config()
    #TODO: info sfp
    master.write_sfp_config("AXGE-1254-0531",1)
    master.load_sfp_config()
    slave.write_sfp_config("AXGE-3454-0531",1)
    slave.load_sfp_config()

    # Retrieve Round-trip time and bitslide values for both master and slave
    # WR devices when connected by f1, f2 and f1+f2.
    delays_dict = {}
    rtt_dict = {}

    for fiber in FIBERS :
        print("Please connect both WR devices with fiber %s on port 1 and press Enter"\
        % (fiber))
        input()

        # Wait until servo state in TRANCK PHASE
        while not slave.in_trackphase() :
            time.sleep(1)

        mean_rtt = 0

        for i in range(N_SAMPLES) :
            mean_rtt += slave.get_rtt()
            time.sleep(TIME_BETWEEN_SAMPLES)
        mean_rtt /= N_SAMPLES

        delays_dict[fiber] = slave.get_phy_delays()
        rtt_dict[fiber] = mean_rtt

    # As Rx delays are set to 0 in sfp database, the stat values for Rx
    # are the bitslides
    delay_mm1 = rtt_dict['f1'] - delays_dict['f1']['master'][1] - delays_dict['f1']['slave'][1]
    delay_mm2 = rtt_dict['f2'] - delays_dict['f2']['master'][1] - delays_dict['f2']['slave'][1]
    delay_mm3 = rtt_dict['f1+f2'] - delays_dict['f1+f2']['master'][1] - delays_dict['f1+f2']['slave'][1]

    delta1 = delay_mm3 - delay_mm2
    delta2 = delay_mm3 - delay_mm1

    return (delta1, delta2)
