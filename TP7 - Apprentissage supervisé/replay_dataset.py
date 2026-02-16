import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
from matplotlib.colors import hsv_to_rgb

FILENAME = 'dataset_webots.hdf5'

if not os.path.exists(FILENAME):
    print(f"Error: {FILENAME} not found.")
    exit()

print(f"Loading {FILENAME} for replay...")

# Load Data
with h5py.File(FILENAME, 'r') as f:
    cmds = f['thymio_commands'][:]   # (N, 2)
    prox = f['thymio_prox'][:]       # (N, 7)
    scans = f['thymio_scans'][:]     # (N, 90, 2) (Cartesian x,y)
    
    # Check if camera data exists
    if 'thymio_cam' in f:
        cam = f['thymio_cam'][:]     # (N, 9)
    else:
        cam = None

n_samples = len(cmds)
print(f"Loaded {n_samples} frames.")

# Setup Figure
fig = plt.figure(figsize=(12, 8))
grid = plt.GridSpec(2, 3, wspace=0.3, hspace=0.3)

# 1. LiDAR Plot (Top Left - Big)
ax_lidar = fig.add_subplot(grid[0, 0:2])
ax_lidar.set_title("LiDAR Scan (Top View)")
ax_lidar.set_xlim(-1, 1) # Adjust based on typical max range (meters)
ax_lidar.set_ylim(-1, 1)
ax_lidar.grid(True)
scatter_lidar = ax_lidar.scatter([], [], s=10, c='blue')
lidar_text = ax_lidar.text(0.02, 0.95, '', transform=ax_lidar.transAxes)

# 1b. Camera features (Top Right)
ax_cam = fig.add_subplot(grid[0, 2])
ax_cam.set_title("Camera (HSV - 3 sectors)")
ax_cam.axis('off')
# create an image 1x3 where each pixel is the RGB color of a sector
cam_img = np.zeros((1, 3, 3))
im_cam = ax_cam.imshow(cam_img, aspect='auto')

# 2. Motor Commands (Bottom Left)
ax_motor = fig.add_subplot(grid[1, 0])
ax_motor.set_title("Motor Commands")
ax_motor.set_ylim(-3.0, 3.0) # VMAX is usually around 9.5
ax_motor.set_xlim(-0.5, 1.5)
ax_motor.set_xticks([0, 1])
ax_motor.set_xticklabels(['Left', 'Right'])
bars_motor = ax_motor.bar([0, 1], [0, 0], color=['red', 'green'])

# 3. Proximity Sensors (Bottom Middle)
ax_prox = fig.add_subplot(grid[1, 1])
ax_prox.set_title("Proximity Sensors (Normalized)")
ax_prox.set_ylim(0, 1.0)
ax_prox.set_xticks(range(7))
bars_prox = ax_prox.bar(range(7), [0]*7, color='green')

# 4. Trajectory / Info (Right column)
ax_info = fig.add_subplot(grid[1, 2])
ax_info.set_title("Replay Info")
ax_info.axis('off')
info_text = ax_info.text(0.05, 0.85, "Starting...", fontsize=10, va='top')

# Playback parameters
SPEED = 4         # frame step (2 -> skip every other frame)
INTERVAL_MS = 20  # delay between frames in milliseconds (smaller = faster)

def init():
    scatter_lidar.set_offsets(np.empty((0, 2)))
    # initialize camera image to gray
    im_cam.set_data(np.ones((1,3,3)) * 0.5)
    return scatter_lidar, bars_motor, bars_prox, im_cam, info_text

def update(frame_index):
    frame = frame_index
    # Update Info
    info_text.set_text(f"Frame: {frame}/{n_samples}\nTime: {frame*0.04:.2f}s\nSpeed: x{SPEED}")

    # Update LiDAR
    current_scan = scans[frame]
    scatter_lidar.set_offsets(current_scan)

    # Update Motors
    current_cmd = cmds[frame]
    for bar, h in zip(bars_motor, current_cmd):
        bar.set_height(h)

    # Update Prox
    current_prox = prox[frame]
    for bar, h in zip(bars_prox, current_prox):
        bar.set_height(h)

    # Update Camera features (if available)
    if 'cam' in globals() and cam is not None:
        # cam layout: [H_L, S_L, V_L, H_C, S_C, V_C, H_R, S_R, V_R]
        vals = cam[frame]
        hsv_sectors = []
        for s in range(3):
            h = np.clip(vals[3*s + 0], 0.0, 1.0)
            s_val = np.clip(vals[3*s + 1], 0.0, 1.0)
            v = np.clip(vals[3*s + 2], 0.0, 1.0)
            hsv_sectors.append([h, s_val, v])
        # convert to RGB and build 1x3 image
        rgb = hsv_to_rgb(np.array(hsv_sectors).reshape((1,3,3)))
        im_cam.set_data(rgb)

    return scatter_lidar, bars_motor.patches[0], bars_motor.patches[1], *bars_prox.patches, im_cam, info_text

# Create Animation
frame_indices = list(range(0, n_samples, SPEED))
anim = FuncAnimation(fig, update, frames=frame_indices,
                     init_func=init, blit=False, interval=INTERVAL_MS)

print("Starting animation window...")
plt.show()
