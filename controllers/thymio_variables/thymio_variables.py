import math
from controller import Supervisor
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
from scipy.spatial import KDTree

#from https://github.com/ghiati/Follow_the_Gap/blob/main/gap_follow/scripts/reactive_node.py
def preprocess_lidar(ranges):
    """ Preprocess the LiDAR scan array:
        1. Setting each value to the mean over some window
        2. Rejecting high values (eg. > 3m)
    """
    proc_ranges = np.array(ranges)
    proc_ranges[np.isinf(proc_ranges)] = MAX_LIDAR_DIST
    proc_ranges[proc_ranges > MAX_LIDAR_DIST] = MAX_LIDAR_DIST
    return proc_ranges

def find_max_gap(free_space_ranges):
    free_space = np.where(free_space_ranges > 0)[0]
    if len(free_space) == 0:
        return None, None

    max_gap = (0, 0)
    current_gap = (free_space[0], free_space[0])

    for i in range(1, len(free_space)):
        if free_space[i] == free_space[i-1] + 1:
            current_gap = (current_gap[0], free_space[i])
        else:
            if current_gap[1] - current_gap[0] > max_gap[1] - max_gap[0]:
                max_gap = current_gap
            current_gap = (free_space[i], free_space[i])

    if current_gap[1] - current_gap[0] > max_gap[1] - max_gap[0]:
        max_gap = current_gap

    return max_gap

def find_best_point(start_i, end_i, ranges):
    """Start_i & end_i are start and end indices of max-gap range, respectively
    Return index of best point in ranges
    Naive: Choose the furthest point within ranges and go there
    """
    best_point = np.argmax(ranges[start_i:end_i]) + start_i
    return best_point

def get_rotated_rect_corners(center_pos, size, angle_rad):
    cx, cy = center_pos
    w, h = size[0] / 2.0, size[1] / 2.0 # Demi-largeur et demi-hauteur

    #calcul des coins des murs par rapport aux coordonnées et tailles
    corners_local = np.array([[-w, -h], [w, -h], [w, h], [-w, h]])

    #position
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    rot_matrix = np.array([[c, -s], [s, c]])

    #appliquer la matrice de rotation sur les coins
    rotated_corners = corners_local.dot(rot_matrix.T)

    #ajout du centre
    final_corners = rotated_corners + np.array([cx, cy])
    return final_corners

#centre de masse d'un groupe de points
def indxtMean(index,arrays):
    indxSum = np.array([0.0, 0.0 ,0.0])
    for i in range(np.size(index,0)):
        indxSum = np.add(indxSum, np.array(arrays[index[i]]), out = indxSum ,casting = 'unsafe')
    return indxSum/np.size(index,0)

#tri des points dans un tableau.
def indxtfixed(index,arrays):
    T = []
    for i in index:
        T.append(arrays[i])
    return np.asanyarray(T)

def get_rotated_rect_corners(center_pos, size, angle_rad):
    cx, cy = center_pos
    w, h = size[0] / 2.0, size[1] / 2.0 # Demi-largeur et demi-hauteur

    #calcul des coins des murs par rapport aux coordonnées et tailles
    corners_local = np.array([[-w, -h], [w, -h], [w, h], [-w, h]])

    #position
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    rot_matrix = np.array([[c, -s], [s, c]])

    #appliquer la matrice de rotation sur les coins
    rotated_corners = corners_local.dot(rot_matrix.T)

    #ajout du centre
    final_corners = rotated_corners + np.array([cx, cy])
    return final_corners

#constantes
ROBOT_RADIUS = 0.9
SAFETY_MARGIN = 0.4
BUBBLE_RADIUS = ROBOT_RADIUS + SAFETY_MARGIN
MAX_LIDAR_DIST = 1 #depuis webot
VELOCITY_BASE = 4.0
KP_TURN = 2.0

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

robot = Supervisor()
robot_node = robot.getSelf()


# LIDAR
lidar = robot.getDevice('lidar')
lidar.enable(int(robot.getBasicTimeStep()))
lidar.enablePointCloud()


#paramètres physique
timestep = int(robot.getBasicTimeStep())
delta_t = timestep / 1000.0 #en secondes
e = 0.054
r = 0.021

#variables d'état
robot_speed = 0
rotation_speed = 2

keyboard = robot.getKeyboard()
keyboard.enable(timestep)

#Listes pour stocker le temps et l'orientation réelle
list_time = []
list_real_theta = []
list_pos_theta = []
start_time = robot.getTime()

#historiques pour les graphiques
list_real_x, list_real_y, list_real_theta = [], [], []
list_time = []
start_time = robot.getTime()

#moteurs
motor_left = robot.getDevice("motor.left")
motor_right = robot.getDevice("motor.right")
motor_left.setPosition(float('inf'))
motor_right.setPosition(float('inf'))  

#init plot
plt.ion()
plt.show(block=False)    
plot_counter = 0


#stocker les erreurs
error_with_icp = []
error_without_icp = []

while (robot.step(timestep) != -1):
    #recuperation données
    real_pos = robot_node.getPosition()
    matrix = robot_node.getOrientation()
    real_theta = math.atan2(matrix[3], matrix[0])

    #LIDAR
    point_cloud = lidar.getRangeImage()

    lidar_points_x = []
    lidar_points_y = []
    fov = lidar.getFov()
    angle_lidar = fov/2
    angle_increment = fov / lidar.getHorizontalResolution()

    for i in point_cloud:

        if not math.isinf(i):

            # filtrage TP navigation
            if abs(angle_lidar) <= math.pi / 2:
                global_angle = real_theta + angle_lidar
                p_x = real_pos[0] + i * math.cos(global_angle)
                p_y = real_pos[1] + i * math.sin(global_angle)
                
                lidar_points_x.append(p_x)
                lidar_points_y.append(p_y)

        angle_lidar -= angle_increment

    # ------------------------------------------------------------------
    # --- ALGORITHME FOLLOW THE GAP (Intégré ici) ---
    # ------------------------------------------------------------------
    
    # Etape 0: Preprocessing
    proc_ranges = preprocess_lidar(point_cloud)
    
    # Etape 1: Trouver le point le plus proche
    closest_point_idx = np.argmin(proc_ranges)
    min_dist = proc_ranges[closest_point_idx]
    
    # Etape 2: Safety Bubble (Mettre à 0 autour du point le plus proche)
    # Rayon de la bulle en RADIANS / increment
    # Approximation de l'angle couvert par le rayon : arc = r * theta -> theta = arc / dist
    # Ici on simplifie souvent par un angle fixe ou calculé
    angle_bubble = math.atan2(BUBBLE_RADIUS, min_dist) if min_dist > 0 else 0
    bubble_radius_idx = int(math.degrees(angle_bubble) / math.degrees(angle_increment))
    # Ou version fixe du screen : radius = rb
    bubble_radius_idx = int(np.radians(20) / angle_increment) # Ex: 20 degrés de bulle

    start_bubble = max(0, closest_point_idx - bubble_radius_idx)
    end_bubble = min(len(proc_ranges) - 1, closest_point_idx + bubble_radius_idx)
    debug_bubble_indices = range(start_bubble, end_bubble)
    proc_ranges[start_bubble:end_bubble] = 0 # "All nonzero points are free space" -> bubble is 0
    
    # Etape 3: Max Gap
    start_gap, end_gap = find_max_gap(proc_ranges)
    
    target_speed_left = 0
    target_speed_right = 0
    
    if start_gap is not None and end_gap is not None:
        # Etape 4: Find Best Point (Le plus loin dans le gap)
        best_point_idx = find_best_point(start_gap, end_gap, proc_ranges)
        
        # --- CALCUL COMMANDE MOTEUR (CONTROL) ---
        # Convertir l'index "best_point" en angle pour piloter le robot
        # Attention: Dans ta boucle de plot, angle_lidar commence à +FOV/2 (Gauche) et descend.
        # Donc index 0 = Gauche (+), dernier index = Droite (-)
        
        # Recalcul de l'angle cible par rapport au robot
        angle_target = (fov / 2.0) - (best_point_idx * angle_increment)
        
        turn_command = KP_TURN * angle_target 
        
        # Mixage arcade drive
        target_speed_left = VELOCITY_BASE - turn_command
        target_speed_right = VELOCITY_BASE + turn_command
        
        # Saturation pour protéger les moteurs
        max_motor = 6
        target_speed_left = max(-max_motor, min(max_motor, target_speed_left))
        target_speed_right = max(-max_motor, min(max_motor, target_speed_right))
        
        # Debug visuel dans la console
        # print(f"Best Idx: {best_point_idx}, Angle: {angle_target:.2f}, L: {target_speed_left:.2f}, R: {target_speed_right:.2f}")

    else:
        # Pas de gap trouvé (mur partout ?) -> Rotation sur place ou arrêt
        target_speed_left = 2.0
        target_speed_right = -2.0
        print("NO GAP FOUND - Rotating")
    


    #affichage état robot
    print(chr(27) + "[2J")
    print(f"x : {real_pos[0]}cm / y: {real_pos[1]}cm")
    #print(command)
    print(f"forward command speed: {robot_speed}")

    motor_left.setVelocity(target_speed_left)
    motor_right.setVelocity(target_speed_right)

    #real values
    list_real_x.append(real_pos[0])
    list_real_y.append(real_pos[1])
    list_real_theta.append(real_theta)

    current_sim_time = robot.getTime() - start_time


    #affichage plot toutes les 20 itérations
    plot_counter += 1
    if plot_counter % 20 == 0:
        plt.figure(1)
        plt.clf()
        ax = plt.gca()
        
        # Murs
        for wall in walls_config:
            corners = get_rotated_rect_corners(wall['pos'], wall['size'], wall['angle'])
            ax.add_patch(Polygon(corners, closed=True, facecolor='red', alpha=0.5))

        # Points Lidar
        plt.plot(lidar_points_x, lidar_points_y, 'b.', markersize=2, label='Lidar')
        plt.plot(lidar_points_x, lidar_points_y, 'b.', markersize=2, label='Lidar')
        
        if 'debug_bubble_indices' in locals():
            bx_list, by_list = [], []
            for idx in debug_bubble_indices:
                # On utilise la distance brute (point_cloud) car proc_ranges est à 0 ici
                dist = point_cloud[idx]
                if math.isinf(dist): dist = 3.0 # Sécurité
                
                # Conversion index -> angle (Même logique que ta boucle lidar)
                angle_local = (fov / 2.0) - (idx * angle_increment)
                angle_global = real_theta + angle_local
                
                bx = real_pos[0] + dist * math.cos(angle_global)
                by = real_pos[1] + dist * math.sin(angle_global)
                bx_list.append(bx)
                by_list.append(by)
            
            # Affichage en MAGENTA (cercles)
            plt.plot(bx_list, by_list, 'mo', markersize=4, label='Obstacle Bubble')

        # B. DESSINER LE RAYON DU ROBOT (Cercle pointillé autour du robot)
        # Cela montre la marge que tu utilises pour tes calculs (BUBBLE_RADIUS)
        robot_circle = plt.Circle((real_pos[0], real_pos[1]), bubble_radius_idx, color='r', fill=False, linestyle='--', linewidth=1.5, label='Robot Safety Radius')
        ax.add_artist(robot_circle)

        # C. AFFICHER LES CONSTANTES (Texte sur le graphique)
        # Gap actuel trouvé
        gap_info = f"Gap Idx: {start_gap}-{end_gap}" if start_gap else "No Gap"
        # Texte récapitulatif
        debug_text = (
            f"Vitesse Base: {VELOCITY_BASE}\n"
            f"Bubble Radius (rb): {BUBBLE_RADIUS}m\n"
            f"K_p (Gain): {KP_TURN}\n"
            f"{gap_info}"
        )
        # Affichage en haut à gauche (coordonnées graphiques)
        plt.text(-0.95, 0.70, debug_text, fontsize=9, bbox=dict(facecolor='white', alpha=0.9, edgecolor='black'))
        # Visualisation du "Best Point" (Gap)
        # On recalcule sa position globale pour l'afficher en vert
        if 'best_point_idx' in locals() and start_gap is not None:
             best_dist = proc_ranges[best_point_idx]
             best_angle_local = (fov / 2.0) - (best_point_idx * angle_increment)
             best_angle_global = real_theta + best_angle_local
             bx = real_pos[0] + best_dist * math.cos(best_angle_global)
             by = real_pos[1] + best_dist * math.sin(best_angle_global)
             plt.plot(bx, by, 'yo', markersize=8, label='Target Gap') # Point Jaune/Orange

        plt.plot(list_real_x, list_real_y, 'g--', label='Réel')
        plt.plot(real_pos[0], real_pos[1], 'go') 

        plt.axis('equal')
        plt.xlim(-1.0, 1.0)
        plt.ylim(-1.0, 1.0)
        plt.legend()
        plt.title("Follow The Gap")
        plt.pause(0.01)
        plt.draw()