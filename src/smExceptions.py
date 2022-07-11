
from typing import Optional
from datetime import datetime
import warnings

from . import smLogging

SMExceptionLogger:smLogging.SM_LoggerBC = smLogging.SM_NullLogger

def registerExceptionLogger(logger: smLogging.SM_LoggerBC):
    global SMExceptionLogger
    SMExceptionLogger = logger

class SMException(Exception):
    def __init__(self, msg: str, **kwargs):
        self.msg = msg
        self._logException(message = msg, **kwargs)

    def __str__(self) -> str:
        s = type(self).__name__ + ":" + self.msg
        return s

    def _logException(self, **kwargs):
        kwargs.update({"_logTime": datetime.now()})
        with SMExceptionLogger as l:
            logSuccess = l.logData(kwargs)

        if not logSuccess:
            warnings.warn("Logging an error was unsuccessful. " + str(self))

class SMBuildException(SMException):
    pass

class SMStateNotFoundException(SMBuildException):
    pass

class SMRuntimeException(SMException):
    pass

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