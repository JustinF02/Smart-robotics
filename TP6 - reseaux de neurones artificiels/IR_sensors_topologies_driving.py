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
# Couche Entrée vers Cachée
w11 = 1.0  # x1 -> h1
w12 = 1.0  # x2 -> h2

# Couche Cachée vers Sortie
w21 = 0.0  # h1 -> y1
w22 = -2.0 # h1 -> y2 évitement capteur g vers moteur d
w23 = -2.0 # h2 -> y1 évitement capteur d vers moteur g
w24 = 0.0  # h2 -> y2 

# Biais pour avancer par défaut
bias = 1.0

while robot.step(timestep) != -1:

    val_left = prox_sensors[1].getValue() / SENSOR_MAX_VAL
    val_right = prox_sensors[3].getValue() / SENSOR_MAX_VAL
    
    
    #entrée
    X = np.array([val_left, val_right])


    #premiers neurones
    h1 = saturation(X[0] * w11)
    h2 = saturation(X[1] * w12)

    #seconde couche

    y1 = saturation(h1 * w21 + h2 * w23 + bias)
    y2 = saturation(h1 * w22 + h2 * w24 + bias)

    # sortie
    motor_left.setVelocity(y1 * FORWARD_SPEED)
    motor_right.setVelocity(y2 * FORWARD_SPEED)
