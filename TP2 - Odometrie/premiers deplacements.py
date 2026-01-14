import math
from controller import Supervisor
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

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
robot_node = robot.getFromDef("Thymio")

#paramètres physique
timestep = int(robot.getBasicTimeStep())
delta_t = timestep / 1000.0 #en secondes
e = 0.054
r = 0.021

#variables d'état
x = 0.151758
y = -0.154528
theta = -2.615814835873021 
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
list_pos_x, list_pos_y, list_pos_theta = [], [], []
list_real_x, list_real_y, list_real_theta = [], [], []
list_time = []
start_time = robot.getTime()

#moteurs
motor_left = robot.getDevice("motor.left")
motor_right = robot.getDevice("motor.right")
motor_left.setPosition(float('inf'))
motor_right.setPosition(float('inf'))   

#TARGETS
target_x = 0.178
target_y = -0.576

#init plot
plt.ion()    
plot_counter = 0

#boucle du programme de contr^ple
while (robot.step(timestep) != -1):
    #recuperation données
    real_pos = robot_node.getPosition() # [x, y, z] dans Webots
    matrix = robot_node.getOrientation()
    real_theta = math.atan2(matrix[3], matrix[0])

    #real values
    list_real_x.append(real_pos[0])
    list_real_y.append(real_pos[1])
    list_real_theta.append(real_theta)

    #estimated values
    list_pos_x.append(x)
    list_pos_y.append(y)
    list_pos_theta.append(theta)

    list_time.append(robot.getTime() - start_time)

    command = keyboard.getKey()
    
    #Odométrie
    #calcul vitesse roues
    v_l = motor_left.getVelocity() 
    v_r = motor_right.getVelocity()
    
    #delta de distance de roues
    delta_l = v_l * r * delta_t
    delta_r = v_r * r * delta_t

    #modèle holonome
    delta_s = (delta_r + delta_l) / 2.0
    delta_theta = (delta_l - delta_r) / (2.0 * e)

    #estimation de la position avec les delta
    x = x + delta_s * math.cos(theta + delta_theta / 2.0)
    y = y + delta_s * math.sin(theta + delta_theta / 2.0)
    theta = theta - delta_theta

    

    #application de la commande
    left_speed = robot_speed
    right_speed = robot_speed

    dx = target_x - x
    dy = target_y - y
    x_target_local = dx * math.cos(theta) + dy * math.sin(theta)
    y_target_local = -dx * math.sin(theta) + dy * math.cos(theta)
    
    #controle clavier
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
    elif command == 83: #S
        robot_speed = 0
        left_speed = 0
        right_speed = 0
        
    #affichage état robot
    print(chr(27) + "[2J")
    print(f"x : {x}cm / y: {y}cm")
    print(f"left motor speed :{v_l}")
    print(f"right motor speed :{v_r}")
    #print(command)
    print(f"forward command speed: {robot_speed}")
    print(f"Cible locale -> x: {x_target_local:.3f}m, y: {y_target_local:.3f}m")    
        
    motor_left.setVelocity(left_speed)
    motor_right.setVelocity(right_speed)
    
    #affichage plot toutes les 20 itérations
    plot_counter += 1
    if plot_counter % 20 == 0:

        # --- FIGURE 1 : Carte du labyrinthe (Trajectoire XY) ---
        plt.figure(1)
        plt.clf()
        ax = plt.gca()
        
        # Dessin des murs
        for wall in walls_config:
            corners = get_rotated_rect_corners(wall['pos'], wall['size'], wall['angle'])
            ax.add_patch(Polygon(corners, closed=True, facecolor='red', alpha=0.5))

        plt.plot(list_real_x, list_real_y, 'g--', label='Réel') # Trajectoire réelle
        plt.plot(list_pos_x, list_pos_y, 'b-', label='Estimé') # Trajectoire mesurée
        plt.plot(real_pos[0], real_pos[1], 'go') # Position réelle actuelle
        plt.plot(x, y, 'bo', markersize=8)       # Position estimée actuelle
        
        plt.axis('equal')
        plt.xlim(-1.0, 1.0)
        plt.ylim(-1.0, 1.0)
        plt.legend()
        plt.title("Trajectoire dans l'environnement")

        # Affichage du point de destination (cible) en rouge
        plt.plot(target_x, target_y, 'rx', markersize=10, label='Cible')
        plt.legend()

        # --- FIGURE 2 : Évolution temporelle (Subplots) ---
        plt.figure(2)
        plt.clf()

        # Subplot X
        plt.subplot(3, 1, 1)
        plt.plot(list_time, list_real_x, 'g', label='Réel')
        plt.plot(list_time, list_pos_x, 'b--', label='Estimé')
        plt.ylabel('X (m)')
        plt.legend()

        # Subplot Y (ou Z selon votre modèle)
        plt.subplot(3, 1, 2)
        plt.plot(list_time, list_real_y, 'g')
        plt.plot(list_time, list_pos_y, 'b--')
        plt.ylabel('Y (m)')

        # Subplot Theta
        plt.subplot(3, 1, 3)
        plt.plot(list_time, list_real_theta, 'g')
        plt.plot(list_time, list_pos_theta, 'b--')
        plt.ylabel('Theta (rad)')
        plt.xlabel('Temps (s)')

        plt.pause(0.01)
        plt.draw()
