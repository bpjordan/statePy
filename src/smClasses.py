from types import CodeType
from typing import List, Tuple, Optional, AnyStr, Any
import warnings

from .smExceptions import *

SM_Transition = Tuple[CodeType, "SM_State", Optional[CodeType]]

def runAction(action: Optional[CodeType], locals: dict[AnyStr, Any]):
    #TODO: Figure out how to make this access modules such as pandas and matlib from user input
            # Possible use for a closure
    if action is not None:
        try:
            exec(action, {}, locals)
        except Exception as e:
            raise SMRuntimeException("Execution of a state action failed") from e

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
        self._defaultChildState :Optional["SM_State"] = None
        self._enterAction: Optional[CodeType] = None
        self._duringAction: Optional[CodeType] = None
        self._exitAction: Optional[CodeType] = None

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

    def addTransition(self, condition:str, targetState:"SM_State", action: str = None):
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

        self._transitions.append((c, targetState, a))

        return self

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

    def checkTransitions(self, data: dict[AnyStr, Any]) -> Optional[SM_Transition]:
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


class SM_ActiveState:
    """
    A container for a state that is running in a simulation.
    """
    def __init__(self, stateTemplate: SM_State, simData: Optional[dict[AnyStr, Any]] = None) -> None:
        self.stateTemplate = stateTemplate
        self.childState = SM_ActiveState(stateTemplate.defaultChildState)\
            if stateTemplate.defaultChildState is not None else None
        if simData is not None:
            self.activateState(simData)

    def iterate(self, simData: dict[AnyStr, Any]):
        """
        Run one iteration on the data, mutating it according to the current active state, and taking any valid transitions
            from the current state or its children
        """
        if (t := self.stateTemplate.checkTransitions(simData)) is not None:
            runAction(self.stateTemplate.exitAction, simData)
            self.transition(t, simData)
        else:
            runAction(self.stateTemplate.duringAction, simData)
            if self.childState is not None:
                self.childState.iterate(simData)

    def transition(self, transition: SM_Transition, simData:dict[AnyStr, Any]):
        """
        Transition this active state to another state and activate that state
        """
        runAction(transition[2], simData)
        self.stateTemplate = transition[1]
        self.activateState(simData)

    def activateState(self, simData: dict[AnyStr, Any]):
        """
        Run the state's entry action, set it's child state to the default,
            and recursively activate the child state
        """
        runAction(self.stateTemplate.enterAction, simData)
        self.childState = SM_ActiveState(self.stateTemplate.defaultChildState, simData)\
            if self.stateTemplate.defaultChildState is not None else None
        

class SM_Simulation:
    """
    An object that controls a single simulation of the state machine and exposes its parameters
    """

    def __init__(self, startState:SM_State, inputParams:dict[AnyStr, Any], outputParams:Optional[List[AnyStr]]):
        self.simData = inputParams
        self.outputParams = outputParams
        self.currentState = SM_ActiveState(startState, self.simData)
        self.remainingIterations:Optional[int] = None
        self.isRunning = False
        self.safe = True
        self.elapsedIterations = 0

    def run(self):
        while self.isRunning is True:
            while self.remainingIterations is None or self.remainingIterations > 0:
                self.safe = False
                self.currentState.iterate(self.simData)
                self.elapsedIterations += 1
                self.remainingIterations -= 1
            self.safe = True

    def start(self, iterations=None):

        self.remainingIterations = iterations

        if not self.isRunning:
            self.isRunning = True
            self.run()

    def pause(self):
        """
        Prevent the state machine from continuing without actually stopping the execution thread alltogether
            Useful for safely extracting or logging data in the middle of a run

            Returns the number of state machine iterations left to run. Use this to start back where execution left off.    
            Example usage:
                tmp = s.pause()
                doTheThing()
                s.start(tmp)
        """

        tmp = self.remainingIterations
        self.remainingIterations = 0
        while not self.safe:
            pass

        return tmp

    def wait(self):
        """
        If the simulation has a finite number of iterations remaining, will halt execution of the
            current thread until those iterations complete.
        """
        while self.remainingIterations is not None and self.remainingIterations > 0:
            pass

    def stop(self, after=0):
        if self.isRunning:
            self.remainingIterations = after
            self.wait()
            self.isRunning = False
        else:
            warnings.warn("Attempted to stop a simulation that was already stopped", SMControlWarning)