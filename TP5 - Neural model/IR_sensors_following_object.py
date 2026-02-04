import math
from controller import Robot

robot = Robot()
timestep = int(robot.getBasicTimeStep())

print(chr(27) + "[2J")
print("Initialization of thymio_variables controller")

motor_left = robot.getDevice("motor.left")
motor_right = robot.getDevice("motor.right")
motor_left.setPosition(float('inf'))
motor_right.setPosition(float('inf'))

# --- Proximity sensors ---
prox_sensors = []
for i in range(7):
    name = f"prox.horizontal.{i}"
    sensor = robot.getDevice(name)
    sensor.enable(timestep)
    prox_sensors.append(sensor)

#0 far right
#1 right
#2 front
#3 left
#4 far left
#5 back left
#6 back right

print("Sampling period : ", timestep, "ms")


FORWARD_SPEED = 8.0
TURN_SPEED = 4.0
MAX_SENSOR = 4000.0

W_fwd = 1.0
W_stop = -6.0
W_pos = -2.0
W_neg = 2.0

SEUIL_STOP = 0.6
def activation(x):
    return math.tanh(x)

while robot.step(timestep) != -1:
    
    left = prox_sensors[4].getValue() / MAX_SENSOR
    center = prox_sensors[2].getValue() / MAX_SENSOR
    right = prox_sensors[0].getValue() / MAX_SENSOR
    bias = 1.0

    #vecteur d'entrée
    x = [bias, left, center, right]

    #calcul perceptron pour le suivi d'objet
    y1 = W_fwd * x[0] + W_stop * center
    y2 = W_pos * left + W_neg * right

    y1 = activation(y1)
    y2 = activation(y2)

    #arrêt si objet proche devant
    if center > SEUIL_STOP:
        v_left = 0.0
        v_right = 0.0
        action = "STOP (objet très proche devant)"
    else:
        v_left = FORWARD_SPEED * y1 - TURN_SPEED * y2
        v_right = FORWARD_SPEED * y1 + TURN_SPEED * y2
        action = "Suivi objet (avance/tourne)"

    #plafonnement des vitesses
    v_left = max(-FORWARD_SPEED, min(FORWARD_SPEED, v_left))
    v_right = max(-FORWARD_SPEED, min(FORWARD_SPEED, v_right))

    motor_left.setVelocity(v_left)
    motor_right.setVelocity(v_right)

    print(f"Capteurs (norm): L={left:.2f} C={center:.2f} R={right:.2f} | y1={y1:.2f} y2={y2:.2f} | vL={v_left:.2f} vR={v_right:.2f} | {action}")

    print(f"Capteurs (norm): L={left:.2f} C={center:.2f} R={right:.2f} | y1={y1:.2f} y2={y2:.2f} | vL={v_left:.2f} vR={v_right:.2f}")
