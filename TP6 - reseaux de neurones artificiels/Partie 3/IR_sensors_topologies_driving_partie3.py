from controller import Robot
import numpy as np

robot = Robot()
timestep = int(robot.getBasicTimeStep())

motor_left = robot.getDevice("motor.left")
motor_right = robot.getDevice("motor.right")
motor_left.setPosition(float('inf'))
motor_right.setPosition(float('inf'))
motor_left.setVelocity(0.0)
motor_right.setVelocity(0.0)

prox_sensors = []
sensor_names = [
    "prox.horizontal.0", # Extrême gauche (x1)
    "prox.horizontal.1", # Gauche (x2)
    "prox.horizontal.2", # Centre (x3)
    "prox.horizontal.3", # Droite (x4)
    "prox.horizontal.4"  # Extrême droite (x5)
]

for name in sensor_names:
    sensor = robot.getDevice(name)
    sensor.enable(timestep)
    prox_sensors.append(sensor)


FORWARD_SPEED = 3
SENSOR_MAX_VAL = 4200.0

def saturation(x):
    return np.clip(x, -1.0, 1.0)

while robot.step(timestep) != -1:
    
    X = np.zeros(5)
    for i in range(5):
        val = prox_sensors[i].getValue()
        X[i] = val / SENSOR_MAX_VAL

    # ----------------------------
    # COUCHE 1 : Filtre Spatial
    # ----------------------------

    W_spatial = np.array([
        [6.6, -4.0, 0.0, 0.0, 0.0],   # x1
        [-3.2, 4.0, -2.0, 0.0, 0.0],  # x2
        [0.0, -2.0, 4.0, -2.0, 0.0],  # x3
        [0.0, 0.0, -2.0, 4.0, -3.2],  # x4
        [0.0, 0.0, 0.0, -4.0, 6.6]    # x5
    ])
    
    #calcul des sorties du filtre spatial
    Y_spatial_raw = W_spatial @ X
    Y_spatial = np.array([saturation(y) for y in Y_spatial_raw])


    # ----------------------------
    # COUCHE 2 : Couche Cachée
    # ----------------------------
       
    H = np.zeros(3)

    w_cote = 2.0
    w_cote_ext = 2.0
    
    Y_pos = np.maximum(Y_spatial, 0)
    
    H[0] = saturation(w_cote_ext*Y_pos[0] + w_cote*Y_pos[1])
    H[1] = saturation(1.0*Y_pos[2]) #centre
    H[2] = saturation(w_cote_ext*Y_pos[4] + w_cote*Y_pos[3])

    # ----------------------------
    # COUCHE 3 : Sortie Moteurs
    # ----------------------------
    
    w_front = 1.0
    w_cross = 1.0
    y1 = saturation(w_cross * H[2] + w_front * H[1]) * FORWARD_SPEED 
    y2 = saturation(w_cross * H[0] + w_front * H[1]) * FORWARD_SPEED

    #commande des moteurs
    motor_left.setVelocity(y1)
    motor_right.setVelocity(y2)
    print(chr(27) + "[2J")
    print(f"In: {[f'{x:.2f}' for x in X]}")
    print(f"Spatial: {[f'{y:.2f}' for y in Y_spatial]}")
    print(f"Motors: L={y1:.2f} R={y2:.2f}")