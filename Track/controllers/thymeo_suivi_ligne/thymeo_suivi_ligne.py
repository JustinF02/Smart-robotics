"""thymeo_suivi_ligne controller."""

from controller import Robot

robot = Robot()
timestep = int(robot.getBasicTimeStep())

left_sensor = robot.getDevice('prox.ground.0')
right_sensor = robot.getDevice('prox.ground.1')
left_sensor.enable(timestep)
right_sensor.enable(timestep)

left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

max_speed = 6.0
turn_speed = 3.0

while robot.step(timestep) != -1:
    left_val = left_sensor.getValue()
    right_val = right_sensor.getValue()

    print(f"[DEBUG] Left sensor: {left_val:.2f}, Right sensor: {right_val:.2f}")

    if left_val < 500 and right_val < 500:
        print("Status: On line, move forward")
        left_motor.setVelocity(max_speed)
        right_motor.setVelocity(max_speed)
    elif left_val < 500:
        print("Status: Line detected on left, turn left")
        left_motor.setVelocity(turn_speed)
        right_motor.setVelocity(max_speed)
    elif right_val < 500:
        print("Status: Line detected on right, turn right")
        left_motor.setVelocity(max_speed)
        right_motor.setVelocity(turn_speed)
    else:
        print("Status: Line lost, searching")
        left_motor.setVelocity(turn_speed)
        right_motor.setVelocity(-turn_speed)
