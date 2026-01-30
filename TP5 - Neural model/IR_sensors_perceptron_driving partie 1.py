from controller import Robot

robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Initialisation des moteurs
motor_left = robot.getDevice("motor.left")
motor_right = robot.getDevice("motor.right")
motor_left.setPosition(float('inf'))
motor_right.setPosition(float('inf'))

# Capteurs IR gauche et droite
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
FORWARD_SPEED = 8.0


# Perceptron générique
def calcul_s(x1, x2, w0, w1, w2):
    return w0 + x1 * w1 + x2 * w2

def activation(s):
    return 1 if s >= 0 else 0

# Poids pour perceptron OU
poids_ou = {'w0': -0.5, 'w1': 1.0, 'w2': 1.0}
# Poids pour perceptron ET
poids_et = {'w0': -1.5, 'w1': 1.0, 'w2': 1.0}

while robot.step(timestep) != -1:

    back_left = 1 if prox_sensors[5].getValue() > THRESHOLD else 0
    back_right = 1 if prox_sensors[6].getValue() > THRESHOLD else 0

    s_et = calcul_s(back_left, back_right, **poids_et)
    y_et = activation(s_et)
    if y_et == 1:
        # Avancer si obstacle derrière
        motor_left.setVelocity(FORWARD_SPEED)
        motor_right.setVelocity(FORWARD_SPEED)
        print("Obstacle derrière : avance !")
    else:
        motor_left.setVelocity(0.0)
        motor_right.setVelocity(0.0)

