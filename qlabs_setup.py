import os

from qvl.qlabs import QuanserInteractiveLabs
from qvl.qcar import QLabsQCar
from qvl.qcar2 import QLabsQCar2
from qvl.yield_sign import QLabsYieldSign
from qvl.stop_sign import QLabsStopSign
from qvl.animal import QLabsAnimal

from qvl.free_camera import QLabsFreeCamera
from qvl.real_time import QLabsRealTime
import pal.resources.rtmodels as rtmodels
from pal.products.qcar import QCAR_CONFIG

def setup(
        initialPosition=[0, 0, 0],
        initialOrientation=[0, 0, 0],
        rtModel=rtmodels.QCAR
    ):

    # Try to connect to Qlabs
    os.system('cls')
    qlabs = QuanserInteractiveLabs()
    print("Connecting to QLabs...")
    try:
        assert qlabs.open("localhost")
        print("Connected to QLabs")
    except:
        print("Unable to connect to QLabs")
        quit()

    # Delete any previous QCar instances and stop any running spawn models
    qlabs.destroy_all_spawned_actors()
    QLabsRealTime().terminate_all_real_time_models()

    # Spawn a QCar at the given initial pose
    if QCAR_CONFIG['cartype']==1:
        hqcar = QLabsQCar(qlabs)
        rtModel = rtmodels.QCAR
    elif QCAR_CONFIG['cartype']==2:
        hqcar = QLabsQCar2(qlabs)
        rtModel = rtmodels.QCAR2

    hqcar.spawn_id(
        actorNumber=0,
        location=[p*10 for p in initialPosition],
        rotation=initialOrientation,
        waitForConfirmation=True
    )
    QLabsAnimal(qlabs).destroy_all_actors_of_class()
    QLabsFreeCamera(qlabs).destroy_all_actors_of_class()
    QLabsStopSign(qlabs).destroy_all_actors_of_class()
    QLabsYieldSign(qlabs).destroy_all_actors_of_class()

    animals = QLabsAnimal(qlabs)
    animals.spawn_degrees(location=[13,26.2,7],rotation=[0,0,180], configuration=2, waitForConfirmation=False)
    animals.spawn_degrees(location=[11,24.8,7],rotation=[0,0,225], configuration=2, waitForConfirmation=False)
    animals.spawn_degrees(location=[9,22.9,7],rotation=[0,0,225], configuration=2, waitForConfirmation=False)
    animals.spawn_degrees(location=[7.3,21.1,7],rotation=[0,0,220], configuration=2, waitForConfirmation=False)
    animals.spawn_degrees(location=[7,18.7,7],rotation=[0,0,120], configuration=2, waitForConfirmation=False)

    # Create two yield signs in this qlabs instance
    yieldsign = QLabsYieldSign(qlabs)
    yieldsign.spawn_degrees([24.4, 35, 0.2], [0, 0, -120], [1.2, 1.2, 1], 0, 1)
    yieldsign.spawn_degrees([2.4, -12.8, 0.2], [0, 0, 160], [1.2, 1.2, 1], 0, 1)

    stop = QLabsStopSign(qlabs)
    stop.spawn_degrees([-11.8, -3.125, 0.2], [0, 0, 145], [1.2, 1.2, 1], 0, 1)
    stop.spawn_degrees([-11.18, 12.85, 0.2], [0, 0, -30], [1.2, 1.2, 1], 0, 1)
    stop.spawn_degrees([13.233, 33.665, 0.149], [0, 0, 225], [1.2, 1.2, 1], 0, 1)

    # Create a new camera view and attach it to the QCar
    hcamera = QLabsFreeCamera(qlabs)
    hcamera.spawn()
    hqcar.possess()

    # Start spawn model
    QLabsRealTime().start_real_time_model(rtModel)

    return hqcar

def terminate():
    QLabsRealTime().terminate_real_time_model("QCar_Workspace")
    QLabsRealTime().terminate_real_time_model("QCar2_Workspace")

if __name__ == '__main__':
    setup()