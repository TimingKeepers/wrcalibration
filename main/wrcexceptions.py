class DeviceNotFound(Exception):
    '''The device name given not correspond to any WR Device in wr_devices module'''
    pass

class MasterNotSet(Exception) :
    '''The master device is not added to main wr calibration process'''
    pass

class MasterNotSet(Exception) :
    '''The slave device is not added to main wr calibration process'''
    pass

class WRDeviceNeeded(Exception) :
    '''This exception is raised when the main process needs more WR devices added'''
    pass

class NotValidPort(Exception) :
    '''The device haven't got the port'''
    pass

class WRDeviceNeeded(Exception) :
    '''No WR devices added'''
    pass

class MeasurementInstrumentNeeded(Exception) :
    '''No measurement instrument added'''
    pass

class FiberLatencyNeeded(Exception) :
    '''Measurement of fiber latency is needed'''
    pass

class FiberAsymmetryNeeded(Exception) :
    '''Measurement of fiber asymmetry is needed'''
    pass

class TriggerNotSet(Exception) :
    '''The trigger levels for the inputs are not set'''
    pass

class InputNotSet(Exception) :
    '''The input channels of the measurement instrument are not set'''
    pass

class MeasuringError(Exception) :
    '''An error occured while measuirng time interval'''
    pass

class MeasureError(Exception) :
    '''A wrong measured value'''
    pass
