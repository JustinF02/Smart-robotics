import math
import os
import pickle
from controller import Supervisor
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import cv2

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

MODEL_FILENAME = 'ai_controller_model_hyper_prox.model'
FEATURE_MODE = 'lidar_camera'  # 'lidar', 'camera', 'lidar_camera'
CMD_MAX = 2.0
CAM_H_BAND = 20
ALPHA = 0.25  # lissage commandes


def normalize_input_01(arr):
    arr = np.asarray(arr, dtype=np.float32)
    max_val = np.nanmax(arr)
    if max_val > 1.0:
        arr = arr / max_val
    return np.clip(arr, 0.0, 1.0)


def get_lidar_cartesian_features(lidar_device):
    ranges = lidar_device.getRangeImage()
    n_points = len(ranges)
    if n_points == 0:
        return np.zeros((1, 0), dtype=np.float32)

    delta_theta = (2 * math.pi) / n_points
    cartesian = np.zeros((n_points, 2), dtype=np.float32)
    max_range = lidar_device.getMaxRange()

    for i, d in enumerate(ranges):
        if math.isinf(d) or math.isnan(d):
            d = max_range
        angle = i * delta_theta
        cartesian[i, 0] = d * math.sin(angle)
        cartesian[i, 1] = d * math.cos(angle)

    cartesian = normalize_input_01(cartesian)
    return cartesian.reshape(1, -1)


def get_camera_features(camera_device, cam_w, cam_h):
    img_bytes = camera_device.getImage()
    if img_bytes is None:
        return np.zeros((1, 9), dtype=np.float32)

    img_np = np.frombuffer(img_bytes, np.uint8).reshape((cam_h, cam_w, 4))
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    half_band = CAM_H_BAND // 2
    y_start = max(0, (cam_h // 2) - half_band)
    y_end = min(cam_h, (cam_h // 2) + half_band)
    band = img_hsv[y_start:y_end, :]

    w_sec = cam_w // 3
    sectors = [
        band[:, 0:w_sec],
        band[:, w_sec:2 * w_sec],
        band[:, 2 * w_sec:]
    ]

    cam_features = []
    for sec in sectors:
        if sec.size == 0:
            cam_features.extend([0.0, 0.0, 0.0])
            continue

        means = np.mean(sec, axis=(0, 1))
        h_norm = means[0] / 179.0
        s_norm = means[1] / 255.0
        v_norm = means[2] / 255.0
        cam_features.extend([h_norm, s_norm, v_norm])

    cam_features = normalize_input_01(np.array(cam_features, dtype=np.float32))
    return cam_features.reshape(1, -1)


def build_model_input(feature_mode, lidar_device, camera_device, cam_w, cam_h):
    blocks = []

    if feature_mode in ('lidar', 'lidar_camera'):
        blocks.append(get_lidar_cartesian_features(lidar_device))

    if feature_mode in ('camera', 'lidar_camera'):
        blocks.append(get_camera_features(camera_device, cam_w, cam_h))

    if not blocks:
        raise ValueError("FEATURE_MODE invalide. Utiliser 'lidar', 'camera' ou 'lidar_camera'.")

    if len(blocks) == 1:
        return blocks[0]

    return np.concatenate(blocks, axis=1)


    
robot = Supervisor()
robot_node = robot.getFromDef("Thymio")
if robot_node is None:
    print("[WARN] getFromDef('Thymio') a retourné None. Fallback sur getSelf().")
    robot_node = robot.getSelf()

if robot_node is None:
    raise RuntimeError(
        "Impossible de récupérer le nœud robot (getFromDef('Thymio') et getSelf() ont échoué)."
    )

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

# capteurs pour le modèle
camera = robot.getDevice("camera")
camera.enable(timestep)
cam_w = camera.getWidth()
cam_h = camera.getHeight()

lidar = robot.getDevice("lidar")
lidar.enable(timestep)
lidar.enablePointCloud()

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
motor_left.setVelocity(0.0)
motor_right.setVelocity(0.0)

# chargement modèle
model_path = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)
with open(model_path, 'rb') as model_file:
    model = pickle.load(model_file)

expected_features = getattr(model, 'n_features_in_', None)
print(f"Modèle chargé: {MODEL_FILENAME}")
print(f"FEATURE_MODE: {FEATURE_MODE}")
if expected_features is not None:
    print(f"Features attendues par le modèle: {expected_features}")

#TARGETS
target1_x = 0.178
target1_y = -0.576

#init plot
plt.ion()    
plot_counter = 0

# état commande manuelle/auto
manual_mode = False
manual_left = 0.0
manual_right = 0.0
prev_left = 0.0
prev_right = 0.0

print("Commandes: M=toggle manuel/auto, flèches=manuel, S=stop")

#boucle du programme de contr^ple
while (robot.step(timestep) != -1):
    #recuperation données
    if robot_node is None:
        print("[ERREUR] robot_node est None dans la boucle. Arrêt du contrôleur.")
        break

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

    #affichage état robot
    print(chr(27) + "[2J")
    print(f"x : {x}cm / y: {y}cm")
    print(f"left motor speed :{v_l}")
    print(f"right motor speed :{v_r}")
    print(f"Mode: {'MANUEL' if manual_mode else 'AUTO_IA'}")

    # commandes modèle (AUTO)
    model_input = build_model_input(FEATURE_MODE, lidar, camera, cam_w, cam_h)
    if expected_features is not None and model_input.shape[1] != expected_features:
        raise ValueError(
            f"Dimension mismatch: modèle attend {expected_features}, reçu {model_input.shape[1]}"
        )

    pred_norm = model.predict(model_input)[0]
    pred_cmd = np.clip(pred_norm * 2.0, -CMD_MAX, CMD_MAX)

    left_speed = float(pred_cmd[0])
    right_speed = float(pred_cmd[1])
    
    #controle clavier
    if command == ord('M'):
        manual_mode = not manual_mode
    elif command == keyboard.UP:
        manual_mode = True
        manual_left += 0.2
        manual_right += 0.2
    elif command == keyboard.DOWN:
        manual_mode = True
        manual_left -= 0.2
        manual_right -= 0.2
    elif command == keyboard.LEFT:
        manual_mode = True
        manual_left -= 0.2
        manual_right += 0.2
    elif command == keyboard.RIGHT:
        manual_mode = True
        manual_left += 0.2
        manual_right -= 0.2
    elif command == 83: #S
        manual_mode = True
        manual_left = 0.0
        manual_right = 0.0

    manual_left = float(np.clip(manual_left, -CMD_MAX, CMD_MAX))
    manual_right = float(np.clip(manual_right, -CMD_MAX, CMD_MAX))

    if manual_mode:
        left_speed = manual_left
        right_speed = manual_right

    # lissage commandes
    left_speed = ALPHA * left_speed + (1 - ALPHA) * prev_left
    right_speed = ALPHA * right_speed + (1 - ALPHA) * prev_right
    prev_left = left_speed
    prev_right = right_speed

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
        plt.plot(real_pos[0], real_pos[1], 'go') # Position réelle actuelle
        
        plt.axis('equal')
        plt.xlim(-1.0, 1.0)
        plt.ylim(-1.0, 1.0)
        plt.legend()
        plt.title("Trajectoire dans l'environnement")

        plt.pause(0.01)
        plt.draw()
