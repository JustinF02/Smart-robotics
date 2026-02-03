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


# --- Paramètres du modèle ANN (figure 4) ---
FORWARD_SPEED = 8.0
TURN_SPEED = 4.0
MAX_SENSOR = 4000.0  # Valeur max typique pour les capteurs Thymio

# Poids du modèle ANN (ajustables)
# Entrées : [1, gauche, centre, droite]
# Sorties : y1 (avance/recule), y2 (rotation)
W_fwd = 0.5    # Poids associé au mouvement avancer (diminué)
W_back = -1.0  # Poids associé au mouvement reculer (obstacle devant)
W_pos = 1.0    # Poids associé à une rotation positive de la roue (tourner à droite, augmenté)
W_neg = -1.0   # Poids associé à une rotation négative de la roue (tourner à gauche)
W_ctr = 2.0    # Poids associé à la rotation sur place si obstacle devant
def activation(x):
    # Fonction d'activation non-linéaire (tanh borné entre -1 et 1)
    return math.tanh(x)

while robot.step(timestep) != -1:
    # Lecture et normalisation des capteurs avant
    left = prox_sensors[4].getValue() / MAX_SENSOR
    center = prox_sensors[2].getValue() / MAX_SENSOR
    right = prox_sensors[0].getValue() / MAX_SENSOR
    bias = 1.0

    # Vecteur d'entrée
    x = [bias, left, center, right]

    # Calcul des sorties du réseau (voir schéma)
    # y1 = sortie avance/recule
    # y2 = sortie rotation
    y1 = W_fwd * x[0] + W_back * x[2]  # Avance si pas d'obstacle devant, recule si obstacle devant
    #y2 = W_pos * x[1] + W_neg * x[3]   # Tourne à droite si obstacle à gauche, à gauche si obstacle à droite
    y2 = W_pos * x[1] + W_neg * x[3] + W_ctr * x[2] 
    # Activation non-linéaire
    y1 = activation(y1)
    y2 = activation(y2)

    # Décision vitesse moteurs
    v_left = FORWARD_SPEED * y1 - TURN_SPEED * y2
    v_right = FORWARD_SPEED * y1 + TURN_SPEED * y2

    # Clamp les vitesses pour éviter les valeurs extrêmes
    v_left = max(-FORWARD_SPEED, min(FORWARD_SPEED, v_left))
    v_right = max(-FORWARD_SPEED, min(FORWARD_SPEED, v_right))

    motor_left.setVelocity(v_left)
    motor_right.setVelocity(v_right)

    print(f"Capteurs (norm): L={left:.2f} C={center:.2f} R={right:.2f} | y1={y1:.2f} y2={y2:.2f} | vL={v_left:.2f} vR={v_right:.2f}")
