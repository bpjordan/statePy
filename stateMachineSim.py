from types import CodeType
import typing

from smExceptions import *

SM_Transition = typing.Tuple[CodeType, "SM_State", typing.Optional[CodeType]]

class SM_State:
    """
    A State in the state machine.
    
    This class is used to define a state in the state machine which can mutate data as long as it is active.
    This class is not affected by the actual execution of a state machine, meaning that it acts as a template that
        can be used by multiple simulations of the same state machine in parallel.
        
    A State Machine can be defined by simply using the SM_State object representing its entry state, since states
        will contain references to all states that are accesible from them.
        
    States can also act in a hierarchical manner, where a state has a child state machine that runs as long as that
        parent state is active. To make a state a parent state, define a defaultChildState for that state. This becomes
        the default state for the child state machine"""

    def __init__(self, name: str):
        self._stateName: str = name
        self._transitions: list[SM_Transition] = []
        self._defaultChildState :typing.Optional["SM_State"] = None
        self._enterAction: typing.Optional[CodeType] = None
        self._duringAction: typing.Optional[CodeType] = None
        self._exitAction: typing.Optional[CodeType] = None

    @property
    def stateName(self):
        """The human-readable name of this state"""
        return self._stateName

    @property
    def transitions(self):
        """
        The tuple of transitions leading out of this state.
        
        A transition t is a tuple of three elements:
        t[0]: The condition that must be met for this transition to be valid. Check that the transition is valid with eval()
        t[1]: The state to transition to
        t[2]: The action to run when taking the transition. Execute this action with exec()
        """
        return tuple(self._transitions)

    def registerTransition(self, condition:str, targetState:"SM_State", action: str = None):
        """Adds a transition between this state and targetState.
        - condition should be a Python expression that evaluates to a bool
        - targetState is the state object representing the state to transition to. It is assumed
            that targetState is known to be a valid SM_State object which shares a parent with
            the current state
        - action (optional) is a string of Python code that is run on the data when the transition
            is taken"""
        try:
            c = compile(condition, "<String>", "eval")
        except SyntaxError as e:
            raise SMBuildException(f"Failed to add transition from {self.stateName} to {targetState.stateName} (syntax error in condition)") from e

        try:
            a = compile(condition, "<String>", "exec") if action is not None else None
        except SyntaxError as e:
            raise SMBuildException(f"Failed to add transition from {self.stateName} to {targetState.stateName} (syntax error in action)") from e

        self._transitions.append((c, a, targetState))

    @property
    def defaultChildState(self):
        """
        For hierarchical state machines, defines the child state to enter when this state is entered.

        If this state does not have a child state machine, this property is None.
        """
        return self._defaultChildState

    @property
    def enterAction(self):
        """The action to take when entering this state, defined as Python code."""
        return self._enterAction

    @enterAction.setter
    def enterAction(self, value:str):
        try:
            self._enterAction = compile(value, "<String>", "exec")
        except SyntaxError as e:
            raise SMBuildException(f"Failed to add entry action to '{self.stateName}' (syntax error)") from e

    @property
    def duringAction(self):
        """The action to take each iteration that the state machine remains in this state."""
        return self._duringAction

    @duringAction.setter
    def duringAction(self, value:str):
        try:
            self._duringAction = compile(value, "<String>", "exec")
        except SyntaxError as e:
            raise SMBuildException(f"Failed to add during action to '{self.stateName}' (syntax error)") from e

    @property
    def exitAction(self):
        """The action to take when the state machine leaves this state through any of its transitions, defined as Python code"""
        return self._exitAction

    @exitAction.setter
    def exitAction(self, value:str):
        try:
            self._exitAction = compile(value, "<String>", "exec")
        except SyntaxError as e:
            raise SMBuildException(f"Failed to add exit action to state '{self.stateName}' (syntax error)") from e

    def checkTransitions(self, data: dict) -> typing.Optional[SM_Transition]:
        """
        Check for valid transitions leading out of this state.

        Arguments:
            data -- a dictionary containing variables used by the conditions

        Return type:
            If a valid transition is found, returns that transition as a tuple.  
            If no valid transitions are found, returns None.
        """
        for t in self.transitions:
            if eval(t[0], {}, data):
                return t

        return None


class SM_RunningState:
    pass

class SM_Simulation:
    pass