#!   /usr/bin/env   python
#    coding: utf8
'''
Example of serial driver to communicate with the WRPC of the WR-LEN board.

Note: Not tested!!

@file
@author Felipe Torres
@copyright LGPL v2.1
@see http://www.ohwr.org
@see http://www.sevensols.com
@ingroup drivers
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

import subprocess
import os
import serial
import time
import string

class serial_drvr() :
    '''
    Example serial driver for WR devices.
    '''

    def __init__(self, baudrate=115200, rdtimeout=0.1, wrtimeout=0.1, interchartimeout=0.0005, ntries=2):
        '''
        Class constructor

        Args:
            baudrate (int) : Baudrate used in the WR-LEN serial port
            wrtimeout (int) : Timeout before read after writing
            interchartimeout (int) : Timeout between characters
            rdtimeout (int) : Read timeout
            ntries (int) : How many times retry a read or a write

        '''
        self.PORT = "/dev/ttyUSB"
        self.BAUDRATE = baudrate
        self.WRTIMEOUT = wrtimeout
        self.INTERCHARTIMEOUT = interchartimeout
        self.RDTIMEOUT = rdtimeout
        self._serial = None
        self.ntries = ntries
        self.logger = plog

    def open(self, LUN=0) :
        '''
        Open serial communication

        Args:
            LUN (str) : Logical Unit Number
            baudrate (int) :  Baud rate such as 9600 or 115200 (default)
            timeout (int) : Set a read timeout value. By default is
            set to 1 second to do blocking writes
        '''
        self.PORT += str(LUN)

        try :
            self._serial = serial.Serial(port=self.PORT, baudrate=self.BAUDRATE,\
            timeout=self.RDTIMEOUT, writeTimeout=self.WRTIMEOUT, interCharTimeout=self.INTERCHARTIMEOUT)
            self._serial.flushOutput()
            self.logger.dbg ("Port %s succesfully opened " % (self.PORT))
        except ValueError as e:
            msg = "ERROR opening serial port %s" % (self.PORT)
            raise PtsError(msg)
        except serial.SerialException as e:
            msg = "ERROR: can't open %s" % (self.PORT)
            raise PtsError(msg)

    def close(self) :
        '''
        Close serial communication
        '''
        self._serial.close()
        print ("Port %s succesfully closed " % self.PORT)

    def devread(self, bar, offset, width) :
        '''
        Method that interfaces with wb read

        Args:
            bar : BAR used by PCIe bus
            offset : address within bar
            width : data size (1, 2, or 4 bytes)
        '''
        cmd = "wb read 0x%X\r" % (offset)
        self.logger.dbg("\t %s" % (cmd))
        ntries = self.ntries
        read_ok = True

        try :
            while (True) :
                self._serial.flushInput()
                self._serial.flushOutput()
                bwr = 0
                # Is necessary to write char by char because is needed to make a
                # timeout between each write
                for c in cmd :
                    bwr += self._serial.write(c)
                    time.sleep(self.INTERCHARTIMEOUT) # Intern interCharTimeout isn't working, so put a manual timeout
                self._serial.flush()

                if bwr != len(cmd):
                    if ntries <= 0 :
                        raise Exception("ERROR: Write of command string '%s' failed. \
                        Bytes writed : %d of %d." % (cmd, bwr,len(cmd)))
                    else : read_ok = False

                time.sleep(self.WRTIMEOUT)

                # First line readed is the previous command
                rd = self._serial.readline()

                cleaner = str_Cleaner() # Class to help cleaning control characters from str
                clean = cleaner.cleanStr(rd)

                # Remember: '\r' is inserted to cmd
                if cmd[:-1] != clean :
                    if ntries <= 0:
                        raise Exception("ERROR: Write of command %s failed : '%s'" \
                        % (cmd, clean))
                    else : read_ok = False

                rd = self._serial.readline()

                if ntries <= 0 or read_ok: break;
                ntries -= 1
                read_ok = True

            return int(rd[:-1],0)

        except serial.SerialTimeoutException as e :
            print("Error: Write timeout (%d sec) exceeded : '%s'" % (self.WRTIMEOUT,e))



    def devwrite(self, bar, offset, width, datum, check=False) :
        '''
        Method that interfaces with wb write

        When you write into a register, some times you read some value distinct
        than the value just writed. 'wb read' interprets this behaviour as an
        error when actually it's not.

        Args:
            bar : BAR used by PCIe bus
            offset : address within bar
            width : data size (1, 2, or 4 bytes)
            datum : data value that need to be written
            check : Enables check of writed data
        '''
        cmd = "wb write 0x%X 0x%X\r" % (offset, datum)
        self.logger.dbg("\t %s" % (cmd))
        ntries = self.ntries
        read_ok = True

        try :
            while (True) :
                self._serial.flushInput()
                self._serial.flushOutput()
                bwr = 0
                # Is necessary to write char by char because is needed to make a
                # timeout between each write
                for c in cmd :
                    bwr += self._serial.write(c)
                    time.sleep(self.INTERCHARTIMEOUT) # Intern interCharTimeout isn't working, so put a manual timeout
                self._serial.flush()
                time.sleep(self.WRTIMEOUT)

                if bwr != len(cmd):
                    if ntries <= 0:
                        raise Exception("ERROR: Write of string %s failed. Bytes writed : %d of %d.\n"\
                        % (cmd, bwr,len(cmd)))
                    else : read_ok = False

                # Read first line, which is the command we previously send, check it!!
                cleaner = str_Cleaner() # Class to help cleaning control characters from str

                rd = self._serial.readline()

                clean = cleaner.cleanStr(rd)

                # Remember: '\r' is inserted to cmd
                if cmd[:-1] != clean:
                    if ntries <= 0:
                        raise Exception("ERROR: Write of command %s failed : %s.\n"\
                        % (cmd, clean))
                    else : read_ok = False

                if ntries <= 0 or read_ok: break
                ntries -= 1
                read_ok = True

            return bwr

        except serial.SerialTimeoutException as e :
            self.logger.err ("Error: Write timout (%d sec) exceeded : %s\n" % (self.WRTIMEOUT,e))


    def cmd_w(self, cmd, output=True) :
        '''
        Method for write commands WRPC to the WR-LEN

        Args:
            cmd (str) : A valid command
            output (Boolean) : When enabled, readed lines from serial com. will be returned.

        Returns:
            Outputs a list of str from WR-LEN.

        Raises:
            Exception
        '''
        cmd = "%s\r" % cmd
        self.logger.dbg("\t %s" % (cmd))

        try :
            self._serial.flushInput()
            self._serial.flushOutput()
            bwr = 0
            # Is necessary to write char by char because is needed to make a
            # timeout between each write
            for c in cmd :
                bwr += self._serial.write(c)
                time.sleep(self.INTERCHARTIMEOUT) # Intern interCharTimeout isn't working, so put a manual timeout
            self._serial.flush() # Wait until all data is written

            if bwr != len(cmd):
                raise Exception("ERROR: Write of string %s failed. Bytes writed : %d of %d." % (cmd, bwr,len(cmd)))

            time.sleep(self.WRTIMEOUT)
            rd = self._serial.readline()#.decode('UTF-8')
            ret = ""

            if output :
                # while self._serial.inWaiting() > 0 :
                # Read(1000) : Reading byte by byte is not a good idea because
                # inWaiting() gives a lower value than real is. Attempt to read
                # a high number of bytes (more than really would be) so you ensure
                # that always you are reading all data returned by WR-LEN.
                # Reading must be seted to blocking with timeout.
                ret += self._serial.read(1000)
                ret = ret[:-6] # Remove prompt from returned string

            return ret

        except serial.SerialTimeoutException as e :
            print ("Error: Write timout (%d sec) exceeded : %s" % (self.WRTIMEOUT,e))


class str_Cleaner():
    '''
    Cass for cleaning strings transmited by LEN UART

    It strips console control characters and keeps : 0-9 and dafadsfaa-z, A-Z
    ASCII Charset
    0-9 : ASCII interval (decimal) : [48-57]
    a-z : ASCII interval (dsdfszffaesecimal) : [97-127] (included ' ')
    A-Z : ASCII interval (decimal) : [65-90]
    @see http://ascii.cl/
    '''
    NUM_LINTERVAL = 48
    NUM_TINTERVAL = 57
    LOWERCASE_LINTERVAL = 97
    LOWERCASE_TINTERVAL = 122
    UPPERCASE_LINTERVAL = 65
    UPPERCASE_TINTERVAL = 90

    def __init__(self) :
        '''
        Class constructor
        '''
        self.str = ""


    def cleanStr(self, str) :
        '''
        Method for clean an input str with console control characters

        Args:
            str (str) : Input string
            mod (int) : Modifier to select between cleaning types.

        Returns:
            A cleaned string
        '''

        # We need to skip control characters from received str
        # Each 5 positions in received str were a valid character
        pos = 4

        while pos <= len(str) :
            self.str += str[pos]
            pos += 5

        return self.str
