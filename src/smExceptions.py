

class SMException(Exception):
    pass

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