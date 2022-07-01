from smExceptions import *

class SM_State:
    def __init__(self, name):
        self._stateName: str = name
        self._transitions: list = []
        self._defaultChildState :"SM_State"= None
        self._enterAction = None
        self._duringAction = None
        self._exitAction = None

    @property
    def stateName(self):
        return self._stateName

    @property
    def transitions(self):
        return tuple(self._transitions)

    def registerTransition(self, condition:str, targetState:"SM_State", action: str = None):
        """Adds a transition between current state and targetState.
        - condition should be a Python expression that evaluates to a bool
        - targetState is the state object representing the state to transition to. It is assumed
            that targetState is known to be a valid SM_State object which shares a parent with
            the current state
        - action (optional) is a string of Python code that is run on the data when the transition
            is taken"""
        try:
            c = compile(condition, "<String>", "eval")
        except SyntaxError as e:
            raise SMBuildException(f"Failed to add transition between {self.stateName} and {targetState.stateName}: syntax error in condition") from e

        try:
            a = compile(condition, "<String>", "exec") if action is not None else None
        except SyntaxError as e:
            raise SMBuildException(f"Failed to add transition between {self.stateName} and {targetState.stateName}: syntax error in action") from e

        self._transitions.append((c, a, targetState))

    @property
    def defaultChildState(self):
        return self._defaultChildState

    @property
    def enterAction(self):
        return self._enterAction

    @enterAction.setter
    def enterAction(self, value:str):
        self._enterAction = compile(value, "<String>", "exec")

class SM_RunningState:
    pass

class SM_Simulation:
    pass