import math
from controller import Supervisor
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
from scipy.spatial import KDTree

def get_walls_point_cloud(walls_config, step=0.01): #step de 1cm.
    fixed_x = []
    fixed_y = []

    for wall in walls_config:
        cx, cy = wall['pos']
        w, h = wall['size']
        angle = wall['angle']

        #si largeur > hauteur -> itération sur x sinon y
        if w > h:
            # Création d'un tableau de points de -w/2 à w/2
            lengths = np.arange(-w/2, w/2, step)
            local_x = lengths
            local_y = np.zeros_like(lengths) #y est au milieu
        else:
            lengths = np.arange(-h/2, h/2, step)
            local_x = np.zeros_like(lengths) #x est àau milieu
            local_y = lengths

        #rotation des points
        c, s = np.cos(angle), np.sin(angle)
        
        #rotation 2D
        rot_x = local_x * c - local_y * s
        rot_y = local_x * s + local_y * c

        #translation et stockage
        fixed_x.extend(rot_x + cx)
        fixed_y.extend(rot_y + cy)

    return fixed_x, fixed_y

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

#iterative closest point avec singular value decomposition
def ICPSVD(fixedX,fixedY,movingX,movingY):
    #https://fr.wikipedia.org/wiki/Iterative_Closest_Point
    #d'après wikipédia
    reqR = np.identity(3) #matrice identité de rotation
    reqT = [0.0, 0.0, 0.0] #matrice nulle de translation
    fixedt = []
    movingt = []

    #nuage fixe
    for i in range(len(fixedX)):
        fixedt.append([fixedX[i], fixedY[i], 0])

    #nuage calculé
    for i in range(len(movingX)):
        movingt.append([movingX[i], movingY[i], 0])

    #1 - sélection des points dans les nuages de départ
    moving = np.asarray(movingt)
    fixed = np.asarray(fixedt)

    #2- mise en correspondance (voisin proche)
    n = np.size(moving,0)
    TREE = KDTree(fixed)

    #mise en correspondance
    for i in range(10):
        #3- pondération des paires de points
        distance, index = TREE.query(moving)
        #4 - rejet (absent ici, tous les points sont comptés)
        #5 - critère de distance (erreur quadrttique)
        err = np.mean(distance**2)

        #centroides
        com = np.mean(moving,0) #nuage calculé
        cof = indxtMean(index,fixed) #nuage fixe

        #6 - Minimisation du critère de distance
        W = np.dot(np.transpose(moving),indxtfixed(index,fixed)) - n*np.outer(com,cof)
        #valeur singulières SVD
        #https://en.wikipedia.org/wiki/Kabsch_algorithm
        # -> calculer la matrice de rotation optimale.
        U , _ , V = np.linalg.svd(W, full_matrices = False)
        tempR = np.dot(V.T,U.T) #rotation locale
        tempT = cof - np.dot(tempR,com) #translation locale (centroide fixe - rotation * centroide calculé)
        
        #maj avec la transformée
        moving = (tempR.dot(moving.T)).T #rotation
        moving = np.add(moving,tempT) #translation
        reqR=np.dot(tempR,reqR)
        reqT = np.add(np.dot(tempR,reqT),tempT)
    
    return reqR, reqT, moving

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

wall_points_x, wall_points_y = get_walls_point_cloud(walls_config, step=0.01)

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

#init plot
plt.ion()    
plot_counter = 0

#variables ICP
last_icp_compute_time = 0.0
icp_interval = 5.0

reqR_stored = np.identity(3)
reqT_stored = [0.0, 0.0, 0.0]
icp_x = []
icp_y = []

#variables odométrie pure sans correction
odo_x = x
odo_y = y
odo_theta = theta
list_odo_x = []
list_odo_y = []

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

            global_angle = theta + angle_lidar
            p_x = x + i * math.cos(global_angle)
            p_y = y + i * math.sin(global_angle)
            
            lidar_points_x.append(p_x)
            lidar_points_y.append(p_y)

        angle_lidar -= angle_increment

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

    odo_x = odo_x + delta_s * math.cos(odo_theta + delta_theta / 2.0)
    odo_y = odo_y + delta_s * math.sin(odo_theta + delta_theta / 2.0)
    odo_theta = odo_theta - delta_theta
    odo_theta = math.atan2(math.sin(odo_theta), math.cos(odo_theta))

    #calcul erreur avec ICP
    dist_err_icp = math.sqrt((x - real_pos[0])**2 + (y - real_pos[1])**2)
    error_with_icp.append(dist_err_icp)

    #calcul error sans ICP
    dist_err_odo = math.sqrt((odo_x - real_pos[0])**2 + (odo_y - real_pos[1])**2)
    error_without_icp.append(dist_err_odo)

    #affichage état robot
    print(chr(27) + "[2J")
    print(f"x : {x}cm / y: {y}cm")
    print(f"left motor speed :{v_l}")
    print(f"right motor speed :{v_r}")
    #print(command)
    print(f"forward command speed: {robot_speed}")


    #application de la commande
    left_speed = robot_speed
    right_speed = robot_speed

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


    motor_left.setVelocity(left_speed)
    motor_right.setVelocity(right_speed)



    current_sim_time = robot.getTime() - start_time

    #attente de 5 secondes.
    if current_sim_time - last_icp_compute_time >= icp_interval:
        
        print(f"\n--- Recalage ICP (t={current_sim_time:.2f}s) ---")
        
        #calcul ICP
        reqR, reqT, moving_corrected = ICPSVD(wall_points_x, wall_points_y, lidar_points_x, lidar_points_y)
        
        #nuage corrigé
        icp_x = moving_corrected[:, 0]
        icp_y = moving_corrected[:, 1]
        
        #correction
        old_x, old_y = x, y
        
        #position au format vecteur
        robot_pos_vector = np.array([x, y, 0.0])
        
        #reqR matrice de rotation
        #reqT vecteur de translation
        corrected_robot_pos = np.dot(reqR, robot_pos_vector) + np.array(reqT)
        
        #coordonnées corrigées
        x = corrected_robot_pos[0]
        y = corrected_robot_pos[1]
        
        #mis à jour de theta.
        delta_theta_icp = math.atan2(reqR[1, 0], reqR[0, 0])
        theta += delta_theta_icp
        theta = math.atan2(math.sin(theta), math.cos(theta))
        
        last_icp_compute_time = current_sim_time

    #affichage plot toutes les 20 itérations
    plot_counter += 1
    if plot_counter % 20 == 0:

        # --- FIGURE 1 : Carte du labyrinthe (Trajectoire XY) ---
        plt.figure(1)
        plt.clf()
        ax = plt.gca()

        # Dessin des murs
        # for wall in walls_config:

        #     corners = get_rotated_rect_corners(wall['pos'], wall['size'], wall['angle'])
        #     ax.add_patch(Polygon(corners, closed=True, facecolor='red', alpha=0.5))

        plt.plot(wall_points_x, wall_points_y, 'k.', markersize=1, label='Murs (Fixed Cloud)')
        plt.plot(lidar_points_x, lidar_points_y, 'b.', markersize=2, label='Lidar')
        if len(icp_x) > 0:
            # On affiche les points tels qu'ils étaient au moment du calcul ICP (en Magenta)
            plt.plot(icp_x, icp_y, 'm+', markersize=2, label='Recalage (update 5s)')
            
            # On affiche une croix Magenta là où l'ICP pense que le robot est vraiment
            plt.plot(x - reqT_stored[0], y - reqT_stored[1], 'mx', markersize=10, markeredgewidth=2, label='Pos. Corrigée')

        plt.plot(list_real_x, list_real_y, 'g--', label='Réel') # Trajectoire réelle
        plt.plot(list_pos_x, list_pos_y, 'b-', label='Estimé') # Trajectoire mesurée
        plt.plot(real_pos[0], real_pos[1], 'go') # Position réelle actuelle
        plt.plot(x, y, 'bo', markersize=8)       # Position estimée actuelle

        plt.axis('equal')
        plt.xlim(-1.0, 1.0)
        plt.ylim(-1.0, 1.0)
        plt.legend()
        plt.title("Trajectoire dans l'environnement")

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

        # --- FIGURE 3 : Comparaison des erreurs en fonction du temps ---
        plt.figure(3)
        plt.clf()
        plt.title("Évolution de l'erreur de position en fonction du temps")
        
        # Courbe rouge : Sans recalage (l'erreur doit monter)
        plt.plot(list_time, error_without_icp, 'r--', label='Sans Recalage (Odométrie)')
        
        # Courbe bleue : Avec recalage (l'erreur doit rester basse)
        plt.plot(list_time, error_with_icp, 'b-', label='Avec Recalage (ICP)')
        
        plt.xlabel('Temps (s)')
        plt.ylabel('Erreur de position (m)')
        plt.legend()
        plt.grid(True)
        
        plt.pause(0.01)
        plt.draw()
        