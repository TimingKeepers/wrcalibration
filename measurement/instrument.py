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

class Instrument() :
    '''
    Abstract class that represents the API to a generic measurement instrument.

    The main calibration procedure expects a homogeneus interface to any instrument
    that could be used to measure skew between PPS signals from WR devices.
    '''
    __metaclass__ = abs.ABCMeta

    # The following methods must be implemented by a concrete class for a WR device.

    @abc.abstractmethod
    def
