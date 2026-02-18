# Copyright 1996-2019 Cyberbotics Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Thymio Data Collection Controller (HDF5)
Implements:
1. Sensor processing (Prox, Lidar, Camera)
2. Hybrid control (ANN + Manual)
3. HDF5 Data Logging
"""

from controller import Robot, Keyboard
import math
import os
import numpy as np
import cv2
import h5py

os.environ['QT_QPA_PLATFORM'] = 'xcb'

# --- CONSTANTS ---
MAX_PROX_RAW = 4500.0  # Max value for clamping
LIDAR_SAMPLES = 90
CAM_H_BAND = 20
EPSILON = 1e-6

# Robot setup
robot = Robot()
timestep = int(robot.getBasicTimeStep())
keyboard = robot.getKeyboard()
keyboard.enable(timestep)

# Devices
camera = robot.getDevice("camera")
camera.enable(timestep)
cam_w = camera.getWidth()
cam_h = camera.getHeight()

lidar = robot.getDevice('lidar')
lidar.enable(timestep)
lidar.enablePointCloud() # Use range image for calculations

prox_sensors = []
for i in range(7):
    s = robot.getDevice('prox.horizontal.'+str(i))
    s.enable(timestep)
    prox_sensors.append(s)

motor_left = robot.getDevice("motor.left")
motor_right = robot.getDevice("motor.right")
motor_left.setPosition(float('inf'))
motor_right.setPosition(float('inf'))
motor_left.setVelocity(0.0)
motor_right.setVelocity(0.0)

#storage Initialization
storage = {
    'prox': [],
    'scans': [],
    'cam': [],
    'cmds': []
}

# Control State
manual_override = False
left_speed_man = 0.0
right_speed_man = 0.0

# Smoothing State
v_left_prev = 0.0
v_right_prev = 0.0
ALPHA = 0.1
VMAX = 2.0

#key Mapping
KEY_FWD = Keyboard.UP
KEY_BACK = Keyboard.DOWN
KEY_LEFT = Keyboard.LEFT
KEY_RIGHT = Keyboard.RIGHT
KEY_STOP = ord('S')
KEY_SAVE = ord('X')

print("Starting Data Collection. Press 'X' to save and exit.")

while robot.step(timestep) != -1:
    
    # --- 1. SENSOR PROCESSING ---
    
    # 1.1 Proximity Sensors
    #pipeline: Clamp -> Sqrt -> L1 Norm
    raw_prox = np.array([s.getValue() for s in prox_sensors])
    # Eq (1)
    prox_clamped = np.minimum(raw_prox, MAX_PROX_RAW)
    # Eq (2)
    prox_sqrt = np.sqrt(prox_clamped / MAX_PROX_RAW)
    # Eq (3)
    prox_sum = np.sum(prox_sqrt) + EPSILON
    prox_norm = prox_sqrt / prox_sum
    
    # 1.2 LiDAR
    ranges = lidar.getRangeImage()
    n_points = len(ranges)
    delta_theta = (2 * math.pi) / n_points 
    
    cartesian_scan = []
    for i in range(n_points):
        d = ranges[i]
        #handle inf
        if math.isinf(d):
            d = lidar.getMaxRange()
        
        angle = i * delta_theta
        
        #standard mathematical conversion
        x = d * math.sin(angle)
        y = d * math.cos(angle)
        cartesian_scan.append([x, y])
        
    cartesian_scan = np.array(cartesian_scan)
        
    # 1.3 Camera
    img_bytes = camera.getImage()
    #webots returns BGRA (4 channels)
    img_np = np.frombuffer(img_bytes, np.uint8).reshape((cam_h, cam_w, 4))
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    #central Band
    #height h=20 centered
    y_start = int((cam_h // 2) - 10)
    y_end = int((cam_h // 2) + 10)
    #safety Check
    y_start = max(0, y_start)
    y_end = min(cam_h, y_end)
    
    band = img_hsv[y_start:y_end, :]
    
    #sectors
    w_sec = cam_w // 3
    s_left = band[:, 0:w_sec]
    s_center = band[:, w_sec:2*w_sec]
    s_right = band[:, 2*w_sec:]
    
    sectors = [s_left, s_center, s_right]
    cam_features = []
    
    for sec in sectors:
        if sec.size == 0:
             cam_features.extend([0,0,0])
             continue
             
        #mean per channel (H, S, V)
        means = np.mean(sec, axis=(0,1))
        
        #normalize
        h_norm = means[0] / 179.0
        s_norm = means[1] / 255.0
        v_norm = means[2] / 255.0
        
        cam_features.extend([h_norm, s_norm, v_norm])
        
    cam_features = np.array(cam_features)
    
    # --- 2. CONTROL ---
    p_left = prox_norm[0]
    p_center = prox_norm[2]
    p_right = prox_norm[4]
    
    target_speed = 6.0
    k_avoid = 12.0
    
    # simple strategy: 
    turn_cmd = (p_left - p_right) * k_avoid
    #central obstacle slows both and assists turn
    slow_cmd = p_center * k_avoid
    
    v_l_ann = target_speed + turn_cmd - slow_cmd
    v_r_ann = target_speed - turn_cmd - slow_cmd
    
    #clamp ANN
    v_l_ann = max(min(v_l_ann, VMAX), -VMAX)
    v_r_ann = max(min(v_r_ann, VMAX), -VMAX)

    #manual Override Logic
    key = keyboard.getKey()
    
    MANUAL_STEP = 0.25  #increment per step
    
    if key == KEY_STOP:
        manual_override = True
        left_speed_man = 0
        right_speed_man = 0
        print("Manual: STOP")
    elif key == KEY_FWD:
        manual_override = True
        left_speed_man += MANUAL_STEP
        right_speed_man += MANUAL_STEP
    elif key == KEY_BACK:
        manual_override = True
        left_speed_man -= MANUAL_STEP
        right_speed_man -= MANUAL_STEP
    elif key == KEY_LEFT:
        manual_override = True
        left_speed_man -= MANUAL_STEP
        right_speed_man += MANUAL_STEP
    elif key == KEY_RIGHT:
        manual_override = True
        left_speed_man += MANUAL_STEP
        right_speed_man -= MANUAL_STEP
    elif key == KEY_SAVE:
        print("Stopping simulation and writing data...")
        break
    else:
        if key == -1:
             manual_override = False
    
    #clamp Manual
    left_speed_man = max(min(left_speed_man, VMAX), -VMAX)
    right_speed_man = max(min(right_speed_man, VMAX), -VMAX)

    #target Selection
    if manual_override:
        target_l = left_speed_man
        target_r = right_speed_man
    else:
        target_l = v_l_ann
        target_r = v_r_ann
        
    #output Smoothing
    #ensure command is progressive and smooth
    cmd_l = ALPHA * target_l + (1 - ALPHA) * v_left_prev
    cmd_r = ALPHA * target_r + (1 - ALPHA) * v_right_prev
    
    #update state
    v_left_prev = cmd_l
    v_right_prev = cmd_r
    
    motor_left.setVelocity(cmd_l)
    motor_right.setVelocity(cmd_r)
    
    # --- 3. save in list ---
    storage['prox'].append(prox_norm)
    storage['scans'].append(cartesian_scan)
    storage['cam'].append(cam_features)
    storage['cmds'].append([cmd_l, cmd_r])

# --- 4. enregistrement HDF5 ---
cmds_arr = np.array(storage['cmds'])
prox_arr = np.array(storage['prox'])
scans_arr = np.array(storage['scans'])
cam_arr = np.array(storage['cam'])

print(f"Saving {len(cmds_arr)} samples to dataset_webots.hdf5...")

try:
    with h5py.File('dataset_webots.hdf5', 'w') as f:
        f.create_dataset('thymio_commands', data=cmds_arr)
        f.create_dataset('thymio_prox', data=prox_arr)
        f.create_dataset('thymio_scans', data=scans_arr)
        f.create_dataset('thymio_cam', data=cam_arr)
    print("Success. File closed.")
except Exception as e:
    print(f"Error saving HDF5: {e}")

robot.step(timestep)

