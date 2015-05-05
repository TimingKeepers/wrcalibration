<!---
 White Rabbit Auto Device Calibration
 Felipe Torres González
 April-2015
-->

Introduction
============

The **wrcalibration** project aims to automatize the "White Rabbit calibration procedure" described in [guide].

The procedure of calibrating a WR device needs a measurement instrument (such a Oscilloscope or a Timer/Counter) and 2 WR devices.

Also, a couple of fiber cables with different lengths (one of a few meters long and other with a few kilometers long) and two SFP transceivers are needed to make the connections.

Any measurement instrument could be used for the procedure, the only need is to program a class that implements the calibration_instrument interface.

To make possible the communication between the calibration process and the WR device (that will be calibrated), it's necessary to implement the interface wr_device. This makes possible to calibrate any WR device without changing a line of the code for the calibration process.

Guidelines for implementing wr_device interface
===============================================

For the main process it's trasparent if the WR device communication uses a serial port or if it's done by ethernet. This is what a class that implements the wr_device have to do.

You need to open a communication with the device in the class constructor and implement all the abstract methods. Communication's timeouts and the error handling must be done internally. The Error handling have to be adecuated to exceptions defined in the interface.

Guidelines for implementing calibration_instrument interface
============================================================

This interface is designed for automatize the collect of time measures from a oscilloscope or another instrument. If you haven't got a instrument with GPIB interface or any communication bus with the PC, you could implement a class that emulates the measurement procedure introducing manually the measures.

The interface is very simple. It only have a constructor where the communication port should be opened and a method for making time interval measures between the master's PPS and the PPS of the slave device. A second method, trigger_level, is defined for testing multiple trigger levels. If you already know a good trigger value you could skip implementing this method and only make it to return a fixed value.

**IMPORTANT** Note that the precision of the procedure is given by the precession of the measurement instrument.

How to use
==========

Main steps for a full calibration process:

* Turn on two WR devices.
* Turn on the measurement instrument.
* Add the devices and the instrument to the WR_calibration() instantiation using the proper methods.
* Assign the master and slave channel for the instrument.
* Connect both devices with the short fiber (f1) and wait til TRACK PHASE.
* Now you could use the trigger_level method or directly assign the trigger levels in the instrument. It's important make this step at first to achieve good time interval measures.
* At this point the system is ready for starting the process. Start calling fiber_latency method.
* When the fiber latency values delta 1 and delta 2 are calculated you can call fiber_asymmetry.
* With fiber latency and asymmetry measured you can start the port calibration of a uncalibrated device. Note that you need for this step a WR calibrator. The process for using a uncalibrated device as calibrator isn't automatized yet(maybe for a next release). So, if you haven't got a calibrated WR device, you must follow the "4.4 Calibrator pre-calibration" part of [guide].
* Repeat the last step twice if you want to use the port as master or slave port.
* Repeat the last step for each port (that you want to calibrate) of the device.
* Now you have a calibrated WR device. **Congratulations!!**
* To make sure it is well calibrated, you could use the method mean_time_interval of the instrument to measure time difference in PPS signals using different configurations for the fresh-calibrated WR devices.

To make the process faster and a bit less tedious, if you ever use the same fibers, the steps that measure fiber latency and asymmetry could be skipped.
To make this, remember to call method write_config after the calibration process is done. You can load it whenever you want with load_config.
By default it loads (and overwrites) all the measured values in memory for WR_Calibration object. So, save them before you load a file.
