from controller import Robot
import numpy as np

robot = Robot()
timestep = int(robot.getBasicTimeStep())

#initialisation des moteurs
motor_left = robot.getDevice("motor.left")
motor_right = robot.getDevice("motor.right")
motor_left.setPosition(float('inf'))
motor_right.setPosition(float('inf'))

prox_sensors = []
for i in range(7):
    name = f"prox.horizontal.{i}"
    sensor = robot.getDevice(name)
    sensor.enable(timestep)
    prox_sensors.append(sensor)
    
#0 far left
#1 left
#2 front
#3 right
#4 far right
#5 back left
#6 back right

THRESHOLD = 150  # seuil pour détection obstacle
FORWARD_SPEED = 9.5
SENSOR_MAX_VAL = 4000.0

def saturation(x):
    return np.clip(x, -1.0, 1.0)

#liste des poids
#entrée 1
w11 = 1.0  #influe son moteur
w12 = -3.0 #influe le moteur opposé

#entrée 2
w21 = -2.0  #influe arrêt moteur g
w22 = -2.0  #influe arrêt moteur d

#entrée 3
w31 = -3.0   #influe le moteur opposé
w32 = 1.0 #influe son moteur

#sorties précèdentes
w4 = 0.5 #influence  de la sortie précèdente
w5 = 0.5 #influence de la sortie précèdente

# Biais pour avancer par défaut
bias = 1.0

y1_prev = 0.0
y2_prev = 0.0

while robot.step(timestep) != -1:

    val_left = prox_sensors[1].getValue() / SENSOR_MAX_VAL
    val_front = prox_sensors[2].getValue() / SENSOR_MAX_VAL
    val_right = prox_sensors[3].getValue() / SENSOR_MAX_VAL
    
    
    #entrée
    X = np.array([val_left, val_front, val_right])

    y1 = saturation((X[0] * w11) + (X[1] * w21) + (X[2] * w31) + (y1_prev * w4) + bias)
    y2 = saturation((X[0] * w12) + (X[1] * w22) + (X[2] * w32) + (y2_prev * w5) + bias)


    print(chr(27) + "[2J")
    print(f"left: {X[0]:.2f}, front: {X[1]:.2f}, right: {X[2]:.2f}")
    print(f"y1: {y1:.2f}, y2: {y2:.2f}")

    #mise à jour de la mémoire
    y1_prev = y1
    y2_prev = y2

    # sortie
    motor_left.setVelocity(y1 * FORWARD_SPEED)
    motor_right.setVelocity(y2 * FORWARD_SPEED)

