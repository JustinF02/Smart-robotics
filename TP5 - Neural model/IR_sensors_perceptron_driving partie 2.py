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
maxVelocity = 9.53
while robot.step(timestep) != -1:
    # Lecture des capteurs avant gauche et droit
    left_sensor_value = prox_sensors[1].getValue()
    right_sensor_value = prox_sensors[3].getValue()
    # Normalisation
    x1 = left_sensor_value / 1000.0
    x2 = right_sensor_value / 1000.0

    # Poids différents
    w1 = 5  # poids fort pour le capteur gauche
    w2 = 1  # poids faible pour le capteur droit

    # Perceptron à deux entrées
    y1 = w1 * x1 + w2 * x2

    print(f"Left sensor: {x1:.2f}, Right sensor: {x2:.2f}, Output y1: {y1:.2f}")

    # Vitesse de recul proportionnelle à la sortie
    backward_speed = min(max(0.0, y1 * FORWARD_SPEED), maxVelocity)
    if backward_speed > 0.05:
        motor_left.setVelocity(-backward_speed)
        motor_right.setVelocity(-backward_speed)
        print(f"Obstacle devant : recule à {backward_speed:.2f}")
    else:
        motor_left.setVelocity(FORWARD_SPEED)
        motor_right.setVelocity(FORWARD_SPEED)