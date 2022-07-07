

class SMException(Exception):
    pass

class SMBuildException(SMException):
    pass

class SMStateNotFoundException(SMBuildException):
    pass

class SMRuntimeException(SMException):
    pass

class SMWarning(UserWarning):
    pass

class SMControlWarning(SMWarning):
    pass