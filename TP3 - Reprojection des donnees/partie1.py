import math
from controller import Supervisor
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

# --- FONCTIONS ---
def multmatr(X, Y, T):
    res = []
    res.append(X[0]*Y[0] + X[3]*Y[1] + X[6]*Y[2] + T[0])
    res.append(X[1]*Y[0] + X[4]*Y[1] + X[7]*Y[2] + T[1])
    res.append(X[2]*Y[0] + X[5]*Y[1] + X[8]*Y[2] + T[2])
    return res

def get_rotated_rect_corners(center_pos, size, angle_rad):
    cx, cy = center_pos
    w, h = size[0] / 2.0, size[1] / 2.0 
    corners_local = np.array([[-w, -h], [w, -h], [w, h], [-w, h]])
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    rot_matrix = np.array([[c, -s], [s, c]])
    rotated_corners = corners_local.dot(rot_matrix.T)
    final_corners = rotated_corners + np.array([cx, cy])
    return final_corners

# --- MURS ---
walls_config = [
    {'pos': (-0.16, 0.23), 'size': (0.01, 1.0), 'angle': 0.0},
    {'pos': (0.05, 0.73), 'size': (0.43, 0.01), 'angle': 0.0},
    {'pos': (0.25, 0.0), 'size': (0.4, 0.01), 'angle': 0.0},
    {'pos': (0.0732246, -0.0387871), 'size': (0.1, 0.01), 'angle': 0.785398},
    {'pos': (0.631834, -0.215563), 'size': (0.1, 0.01), 'angle': 0.785398},
    {'pos': (0.0732248, 0.0319252), 'size': (0.1, 0.01), 'angle': 2.35619},
    {'pos': (0.631834, 0.2087), 'size': (0.1, 0.01), 'angle': 2.35619},
    {'pos': (0.242929, 0.696599), 'size': (0.1, 0.01), 'angle': 2.35619},
    {'pos': (-0.124765, 0.696599), 'size': (0.1, 0.01), 'angle': 0.785398},
    {'pos': (0.214645, -0.717604), 'size': (0.1, 0.01), 'angle': -2.356195},
    {'pos': (0.00251402, -0.47719), 'size': (0.1, 0.01), 'angle': -2.356195},
    {'pos': (-0.612664, -0.314557), 'size': (0.1, 0.01), 'angle': -2.356195},
    {'pos': (-0.612664, -0.710533), 'size': (0.1, 0.01), 'angle': 2.35619},
    {'pos': (-0.4, -0.27), 'size': (0.49, 0.01), 'angle': 0.0},
    {'pos': (-0.16, -0.51), 'size': (0.4, 0.01), 'angle': 0.0},
    {'pos': (0.46, -0.25), 'size': (0.43, 0.01), 'angle': 0.0},
    {'pos': (-0.2, -0.75), 'size': (0.9, 0.01), 'angle': 0.0},
    {'pos': (0.47, 0.25), 'size': (0.4, 0.01), 'angle': 0.0},
    {'pos': (0.04, -0.01), 'size': (0.01, 1.0), 'angle': 0.0},
    {'pos': (0.25, -0.5), 'size': (0.01, 0.5), 'angle': 0.0},
    {'pos': (-0.65, -0.5), 'size': (0.01, 0.5), 'angle': 0.0},
    {'pos': (0.27, 0.49), 'size': (0.01, 0.48), 'angle': 0.0},
    {'pos': (0.67, 0.0), 'size': (0.01, 0.5), 'angle': 0.0}
]

# --- INIT ---
robot = Supervisor()
robot_node = robot.getFromDef("Thymio")

lidar = robot.getDevice('lidar')
lidar.enable(int(robot.getBasicTimeStep()))
lidar.enablePointCloud()

timestep = int(robot.getBasicTimeStep())
robot_speed = 0
rotation_speed = 2

keyboard = robot.getKeyboard()
keyboard.enable(timestep)

motor_left = robot.getDevice("motor.left")
motor_right = robot.getDevice("motor.right")
motor_left.setPosition(float('inf'))
motor_right.setPosition(float('inf'))   

theta = -2.615814835873021
list_time = []
list_real_x, list_real_y, list_real_theta = [], [], []
start_time = robot.getTime()

plt.ion()    
plot_counter = 0

# --- BOUCLE ---
while (robot.step(timestep) != -1):

    # Données réelles
    pos = robot_node.getPosition()
    rotation = robot_node.getOrientation()
    real_theta = math.atan2(rotation[3], rotation[0]) 

    #LIDAR 
    point_cloud = lidar.getRangeImage()
    lidar_points_x = []
    lidar_points_y = []

    fov = lidar.getFov()
    angle_lidar = fov / 2
    angle_increment = fov / lidar.getHorizontalResolution()

    for dist in point_cloud:
            
        global_angle = real_theta + angle_lidar
        p_x = pos[0] + dist * math.cos(global_angle)
        p_y = pos[1] + dist * math.sin(global_angle)

        lidar_points_x.append(p_x)
        lidar_points_y.append(p_y)
        
        # Balayage vers la droite
        angle_lidar -= angle_increment
    
    # Stockage
    list_real_x.append(pos[0])
    list_real_y.append(pos[1])
    list_real_theta.append(real_theta)
    list_time.append(robot.getTime() - start_time)

    # Commandes
    command = keyboard.getKey()
    print(chr(27) + "[2J")
    print(f"x : {pos[0]:.2f}m / y: {pos[1]:.2f}m")
    
    left_speed = robot_speed
    right_speed = robot_speed
    
    if command == keyboard.UP:
        robot_speed += 0.2
        if robot_speed > 6: robot_speed = 6
    elif command == keyboard.DOWN:
        robot_speed -= 0.2
        if robot_speed < -6: robot_speed = -6
    elif command == keyboard.LEFT:
        left_speed = robot_speed - rotation_speed 
        right_speed = robot_speed + rotation_speed
    elif command == keyboard.RIGHT:
        left_speed = robot_speed + rotation_speed
        right_speed = robot_speed - rotation_speed
    elif command == 83: # S
        robot_speed = 0
        left_speed = 0
        right_speed = 0
        
    motor_left.setVelocity(left_speed)
    motor_right.setVelocity(right_speed)
    
    # Plot
    plot_counter += 1
    if plot_counter % 20 == 0:
        plt.figure(1)
        plt.clf()
        ax = plt.gca()
        
        for wall in walls_config:
            corners = get_rotated_rect_corners(wall['pos'], wall['size'], wall['angle'])
            ax.add_patch(Polygon(corners, closed=True, facecolor='red', alpha=0.5))

        plt.plot(lidar_points_x, lidar_points_y, 'b.', markersize=2, label='Lidar')
        plt.plot(list_real_x, list_real_y, 'g--', label='Réel')
        plt.plot(pos[0], pos[1], 'go')
        
        plt.axis('equal')
        plt.xlim(-1.0, 1.0)
        plt.ylim(-1.0, 1.0)
        plt.legend()
        plt.title(f"Trajectoire Robot)")

        plt.pause(0.01)
        plt.draw()