
from typing import Optional
from datetime import datetime
import warnings

from . import smLogging

SMExceptionLogger:smLogging.SM_LoggerBC = smLogging.SM_NullLogger

def registerExceptionLogger(logger: smLogging.SM_LoggerBC):
    """
    Set a logger for all exceptions related to StatePy state machines.

    Loggers can be subclassed from SM_LoggerBC
    """
    global SMExceptionLogger
    SMExceptionLogger = logger

class SMException(Exception):
    """
    An exception related to a StatePy state machine.

    To automatically log all StatePy exceptions, use the registerExceptionLogger method.
    """
    def __init__(self, msg: str, **kwargs):
        self.msg = msg
        self._logException(message = msg, **kwargs)

    def __str__(self) -> str:
        s = self.msg
        return s

    def _logException(self, **kwargs):
        kwargs.update({"logTime": datetime.now(), "class": type(self).__name__, "logType": "Exception"})
        with SMExceptionLogger as l:
            logSuccess = l.logData(kwargs)

        if not logSuccess:
            warnings.warn("Logging an error was unsuccessful. " + str(self))

class SMBuildException(SMException):
    pass

class SMStateNotFoundException(SMBuildException):
    pass

class SMRuntimeException(SMException):
    def __init__(self, err: Exception, **kwargs):
        self.err = err
        super().__init__("Execution of a state action raised an error", err = {"errtype": type(err).__name__, "errmsg": str(err)}, **kwargs)

    def __str__(self) -> str:
        s = super().__str__() + ": " + repr(self.err)
        return s

class SMLogException(SMRuntimeException):
    pass

class SMWarning(UserWarning):
    pass

class SMControlWarning(SMWarning):
    pass

class SMLogWarning(SMWarning):
    pass

class SMBuildWarning(SMWarning):
    pass