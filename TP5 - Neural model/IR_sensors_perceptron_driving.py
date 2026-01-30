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

#0 far left
#1 left
#2 front
#3 right
#4 far right
#5 back left
#6 back right

print("Sampling period : ", timestep, "ms")

# --- Parameters ---
FORWARD_SPEED = 8.0
TURN_SPEED = 4.0

# Seuils d'obstacle
THRESHOLD = 150  # seuil pour binariser la détection obstacle

def wait_ms(duration_ms):
    elapsed = 0
    while elapsed < duration_ms:
        robot.step(timestep)
        elapsed += timestep

# Perceptron à 3 entrées (gauche, centre, droite)
# On choisit des poids pour illustrer la logique :
# - Si obstacle devant, on tourne
# - Si obstacle à gauche, on tourne à droite
# - Si obstacle à droite, on tourne à gauche
# - Sinon, on avance
# Les entrées sont binaires (0: pas d'obstacle, 1: obstacle)

def perceptron_3inputs(x_left, x_center, x_right, w0, w_left, w_center, w_right):
    s = w0 + x_left * w_left + x_center * w_center + x_right * w_right
    # 3 sorties possibles :
    # -1 : tourner à gauche, 0 : avancer, 1 : tourner à droite
    # Ici, on code :
    #   si s < 0 : tourner à gauche
    #   si s == 0 : avancer
    #   si s > 0 : tourner à droite
    if s < 0:
        return -1
    elif s == 0:
        return 0
    else:
        return 1

# Poids du perceptron (exemple)
# On veut :
# - Si obstacle devant, tourner (poids centre fort)
# - Si obstacle à gauche, tourner à droite (poids gauche positif)
# - Si obstacle à droite, tourner à gauche (poids droit négatif)
w0 = 0
w_left = 1
w_center = 2
w_right = -1

while robot.step(timestep) != -1:
    # 7 sensors
    prox = [s.getValue() for s in prox_sensors]
    print(prox)

    # On utilise les capteurs gauche (1), centre (2), droite (3)
    left = prox_sensors[1].getValue()
    center = prox_sensors[2].getValue()
    right = prox_sensors[3].getValue()

    # Binarisation des entrées pour le perceptron
    x_left = 1 if left > THRESHOLD else 0
    x_center = 1 if center > THRESHOLD else 0
    x_right = 1 if right > THRESHOLD else 0

    # Décision du perceptron
    action = perceptron_3inputs(x_left, x_center, x_right, w0, w_left, w_center, w_right)

    if action == 0:
        # Avancer
        motor_left.setVelocity(FORWARD_SPEED)
        motor_right.setVelocity(FORWARD_SPEED)
    elif action == -1:
        # Tourner à gauche
        motor_left.setVelocity(0.0)
        motor_right.setVelocity(TURN_SPEED)
        print("Tourne à gauche (obstacle à droite ou devant)")
        wait_ms(150)
    elif action == 1:
        # Tourner à droite
        motor_left.setVelocity(TURN_SPEED)
        motor_right.setVelocity(0.0)
        print("Tourne à droite (obstacle à gauche ou devant)")
        wait_ms(150)
