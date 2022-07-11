
from typing import Optional
from pymongo import MongoClient
import abc

class SM_LoggerBC(metaclass=abc.ABCMeta):
    """
    Base class defining a simulation logger for logging data to a database.

    Implement the following methods to use:
    start(): establish a connection to the database
    logData(data:dict): Log the data specified in the data argument to the database
    stop(): safely teardown the database connection
    """

    def __init__(self, host:str, port:int, dbName:str, defaultTable:str = "simData"):
        self.host = host
        self.port = port
        self.dbName = dbName
        self.defaultTable = defaultTable

        self.client = None
        self.dbConn = None
        self.tableConn = None
        pass

    @abc.abstractmethod
    def start(self):
        """
        Abstract method that connects to the database
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """
        Abstract method that closes the connection to the database
        """
        pass

    @abc.abstractmethod
    def logData(self, data:dict) -> bool:
        pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

class SM_NullLoggerClass(SM_LoggerBC):
    def __init__(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def logData(self, data: dict) -> bool:
        return True

SM_NullLogger = SM_NullLoggerClass()

class SM_MongoLogger(SM_LoggerBC):
    def start(self, table:Optional[str] = None):
        self.client = MongoClient(self.host, self.port)
        self.dbConn = self.client[self.dbName]
        self.tableConn = self.dbConn[table if table is not None else self.defaultTable]

    def stop(self):
        self.client.close()
        self.tableConn = None
        self.dbConn = None
        self.client = None

    def logData(self, data: dict) -> bool:
        result = self.tableConn.insert_one(data)
        return result.acknowledged