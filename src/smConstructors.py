
from .smClasses import SM_State, SM_Simulation
from .smExceptions import SMBuildException, SMStateNotFoundException
import json

def loadFromJson(jsonFileName: str):
    """
    Returns a list of SM_Simulation objects specified by a json file
    """
    with open(jsonFileName) as jsonFP:
        fullspec = json.load(jsonFP)

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

    sims = [SM_Simulation(stateMachines[simSpec["statemachine"]], simSpec["initialdata"]) for simSpec in fullspec["simulations"]]

    return sims