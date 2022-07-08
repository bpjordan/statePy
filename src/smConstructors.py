
from .smLogging import SM_LoggerBC, SM_MongoLogger, SM_NullLogger
from .smClasses import SM_State, SM_Simulation
from .smExceptions import SMBuildException, SMStateNotFoundException, SMBuildWarning
import json, jsonschema
from pathlib import Path
import warnings

def loadFromJson(jsonFileName: str):
    """
    Returns a list of SM_Simulation objects specified by a json file
    """
    with open(jsonFileName) as jsonFP:
        fullspec = json.load(jsonFP)

    schemaPath = Path(__file__).with_name("simSchema.json")
    with schemaPath.open() as schemaFP:
        schema = json.load(schemaFP)

    jsonschema.validate(fullspec, schema)

    del schema

    stateMachines = []

    for smSpec in fullspec["statemachines"]:
        sm = {stateSpec["name"]:SM_State.fromDict(stateSpec) for stateSpec in smSpec["states"]}

        for stateSpec in smSpec["states"]:
            for t in stateSpec.get("transitions", ()):
                tCond = t["condition"]
                tDest = sm.get(t["destination"])
                tAct = t.get("action")

                if tDest is None:
                    raise SMStateNotFoundException(f"Couldn't build transition from {stateSpec['name']}: Destination state {t['destination']} not found")

                sm[stateSpec["name"]].addTransition(tCond, tDest, tAct)

        defaultState = sm.get(smSpec["defaultstate"])

        if defaultState is None:
            raise SMStateNotFoundException(f"Couldn't find default state {smSpec['defaultstate']} for a state machine")

        stateMachines.append(defaultState)

    loggers = [loggerFromDict(loggerSpec) for loggerSpec in fullspec["loggers"]]

    sims = [SM_Simulation(startState = stateMachines[simSpec["statemachine"]], inputParams = simSpec["initialdata"],\
                logger=loggers[simSpec["logger"]] if simSpec.get("logger") is not None else None) for simSpec in fullspec["simulations"]]

    return sims

def loggerFromDict(spec:dict) -> SM_LoggerBC:

    host = spec["host"]
    port = spec["port"]
    dbName = spec["dbname"]
    tableName = spec["table"]

    match spec["dbtype"]:
        case "mongo":
            return SM_MongoLogger(host=host, port=port, dbName=dbName, defaultTable=tableName)
        case _:
            warnings.warn("Invalid database type specified for logger", SMBuildWarning)