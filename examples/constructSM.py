import src as sm
import threading

"""
Example/test usage of programattic state machine construction. Place in main directory to run
"""

def constructSM():
    redLight = sm.SM_State("Red")
    yellowLight = sm.SM_State("Yellow")
    greenLight = sm.SM_State("Green")

    redLight.addTransition("timeOn > 19", greenLight)
    greenLight.addTransition("timeOn > 9", yellowLight)
    yellowLight.addTransition("timeOn > 2", redLight)

    redLight.duringAction = "timeOn += 1"
    yellowLight.duringAction = "timeOn += 1"
    greenLight.duringAction = "timeOn += 1"

    redLight.enterAction = "timeOn = 0; light = 'red'"
    yellowLight.enterAction = "timeOn = 0; light = 'yellow'"
    greenLight.enterAction = "timeOn = 0; light = 'green'"

    for light in (redLight, yellowLight, greenLight):
        print(light.stateInfo())


    sim = sm.SM_Simulation(redLight, {}, None)

    simThread = threading.Thread(target=sm.SM_Simulation.start, args=(sim, 20))
    simThread.start()
    while sim.remainingIterations is not None and sim.remainingIterations > 0:
        pass
    print(f"{sim.elapsedIterations}: {sim.simData}")

    sim.start(10)
    while sim.remainingIterations is not None and sim.remainingIterations > 0:
        pass
    print(f"{sim.elapsedIterations}: {sim.simData}")
    
    sim.stop(2)
    simThread.join()
    print(f"{sim.elapsedIterations}: {sim.simData}")

    print("Successfully stopped simulation thread")

if __name__ == '__main__':
    constructSM()