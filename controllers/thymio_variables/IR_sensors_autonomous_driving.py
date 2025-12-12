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
FRONT_THRESHOLD = 150
BACK_THRESHOLD = 100
SIDE_THRESHOLD = 120

def wait_ms(duration_ms):
    elapsed = 0
    while elapsed < duration_ms:
        robot.step(timestep)
        elapsed += timestep
       
       
while robot.step(timestep) != -1:

    # 7 sensors
    prox = [s.getValue() for s in prox_sensors]
    print(prox)
    
    far_left  = prox_sensors[0].getValue()
    left      = prox_sensors[1].getValue()
    front     = prox_sensors[2].getValue()
    right     = prox_sensors[3].getValue()
    far_right = prox_sensors[4].getValue()
    back_left  = prox_sensors[5].getValue()
    back_right = prox_sensors[6].getValue()

    # driving

    # 1 - front obstacle
    if front > FRONT_THRESHOLD:
        motor_left.setVelocity(-TURN_SPEED)
        motor_right.setVelocity(-TURN_SPEED)
        wait_ms(600)
    
        # turn on the more open side
        if left < right:
            motor_left.setVelocity(0.0)
            motor_right.setVelocity(TURN_SPEED)
        else:
            motor_left.setVelocity(TURN_SPEED)
            motor_right.setVelocity(0.0)
    
        wait_ms(800)
        continue

    
    # 2 - left wall near
    elif left > FRONT_THRESHOLD or far_left > SIDE_THRESHOLD:
        motor_left.setVelocity(TURN_SPEED)
        motor_right.setVelocity(0.0)
        wait_ms(100)
        print("turning right !")
    
    # 3 - right wall near
    elif right > FRONT_THRESHOLD or far_right > SIDE_THRESHOLD:
        motor_left.setVelocity(0.0)
        motor_right.setVelocity(TURN_SPEED)
        wait_ms(100)
        print("turning left !")
    
    # 4 - drive
    else:
        motor_left.setVelocity(FORWARD_SPEED)
        motor_right.setVelocity(FORWARD_SPEED)
