import numpy as np
from controller import Robot, Keyboard

# --- Paramètres Globaux ---
dt = 10 #ms
ALPHA = 0.05 #taux apprentissage
speed = 6
TURN_GAIN = 0.45 # < 1.0 => virage plus doux
BASE_FORWARD = 30.0
MODEL_GAIN = 70.0
ACTIVATION_GAIN = 3.0
OBSTACLE_BRAKE_GAIN = 0.95
W = np.zeros((2, 5))
B = np.zeros(2)


def braitenberg(entries, weights, bias, activation_gain):
    return np.tanh(activation_gain * (np.dot(weights, entries) + bias))


def hebb_update(x, y, W, B, alpha):
    if not np.any(x > 0.02):
        return

    y1 = y[0] / 100.0
    y2 = y[1] / 100.0

    for j in range(5):
        xj = x[j]
        W[0][j] = W[0][j] + alpha * y1 * xj
        W[1][j] = W[1][j] + alpha * y2 * xj

    B[0] = B[0] + alpha * y1
    B[1] = B[1] + alpha * y2


def get_manual_command_from_key(key):
    if key == Keyboard.UP:
        return np.array([100.0, 100.0])
    elif key == Keyboard.DOWN:
        return np.array([-100.0, -100.0])
    elif key == Keyboard.LEFT:
        return np.array([-100.0, 100.0])
    elif key == Keyboard.RIGHT:
        return np.array([100.0, -100.0])
    return None

def get_sensors(robot, timestep):
    names = [
        "prox.horizontal.1", # x1
        "prox.horizontal.2", # x2
        "prox.horizontal.3", # x3
        "prox.horizontal.5", # x4 
        "prox.horizontal.6"  # x5
    ]
    sensors = []
    for name in names:
        s = robot.getDevice(name)
        s.enable(timestep)
        sensors.append(s)
    return sensors

# --- Initialisation Robot & Clavier ---
robot = Robot()
keyboard = Keyboard()
timestep = int(robot.getBasicTimeStep())
keyboard.enable(timestep)

left_motor = robot.getDevice("motor.left")
right_motor = robot.getDevice("motor.right")
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

sensors = get_sensors(robot, timestep)

timer = 0
log_counter = 0
prev_key_pressed = False


while robot.step(timestep) != -1:

    timer += timestep
    if timer < dt:
        continue
    
    timer = 0

    #acquisition entrées normalisées
    raw_values = [s.getValue() for s in sensors]
    x = np.clip(np.array(raw_values) / 4000.0, 0.0, 1.0)
    
    #sortie réseau de neurones
    
    y_model = braitenberg(x, W, B, ACTIVATION_GAIN)
    obstacle_level = np.max(x)
    base_forward = BASE_FORWARD * np.clip(1.0 - OBSTACLE_BRAKE_GAIN * obstacle_level, 0.0, 1.0)
    y = np.array([base_forward, base_forward]) + (MODEL_GAIN * y_model)
    y = np.clip(y, -100, 100)
    
    #supervision humaine
    key = keyboard.getKey()
    manual_cmd = get_manual_command_from_key(key)
    override = manual_cmd is not None

    if override:
        y = manual_cmd

    forward_cmd = (y[0] + y[1]) / 2.0
    turn_cmd = ((y[1] - y[0]) / 2.0) * TURN_GAIN
    y = np.array([
        forward_cmd - turn_cmd,
        forward_cmd + turn_cmd
    ])
    y = np.clip(y, -100, 100)

    v_left = (y[0] / 100.0) * speed
    v_right = (y[1] / 100.0) * speed
    
    left_motor.setVelocity(v_left)
    right_motor.setVelocity(v_right)
    
    key_pressed = override
    is_new_key_press = key_pressed and not prev_key_pressed
    if is_new_key_press:
        hebb_update(x, y, W, B, ALPHA)
    prev_key_pressed = key_pressed
    
    
    log_counter += 1
    if log_counter % 20 == 0:
        print(chr(27) + "[2J")
        print(f"Mode: {'MANUEL' if override else 'AUTO'}")
        pass
        print(f"Inputs (x): {np.round(x, 3)}")
        print("Poids W:\n", np.round(W, 3))
        print("Biais B:", np.round(B, 3))