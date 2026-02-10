from controller import Robot
import numpy as np

# --- Initialisation du Robot ---
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Initialisation des moteurs
motor_left = robot.getDevice("motor.left")
motor_right = robot.getDevice("motor.right")
motor_left.setPosition(float('inf'))
motor_right.setPosition(float('inf'))
motor_left.setVelocity(0.0)
motor_right.setVelocity(0.0)

# Initialisation des 5 capteurs avant (de gauche à droite)
# prox.horizontal.0 à 4 couvrent l'arc avant du Thymio
prox_sensors = []
sensor_names = [
    "prox.horizontal.0", # Extrême gauche (x1)
    "prox.horizontal.1", # Gauche (x2)
    "prox.horizontal.2", # Centre (x3)
    "prox.horizontal.3", # Droite (x4)
    "prox.horizontal.4"  # Extrême droite (x5)
]

for name in sensor_names:
    sensor = robot.getDevice(name)
    sensor.enable(timestep)
    prox_sensors.append(sensor)

# Constantes
FORWARD_SPEED = 3
SENSOR_MAX_VAL = 4000.0
BIAIS = -0.0

def saturation(x):
    """Fonction d'activation avec saturation entre -1 et 1"""
    return np.clip(x, -1.0, 1.0)

# --- Boucle Principale ---
while robot.step(timestep) != -1:
    
    X = np.zeros(5)
    for i in range(5):
        val = prox_sensors[i].getValue()
        X[i] = val / SENSOR_MAX_VAL

    # ---------------------------------------------------------
    # COUCHE 1 : Filtre Spatial (Détection de contraste)
    # ---------------------------------------------------------
    
    w_center = 4.0
    w_voisin = -2.0
    w_voisin_externe = -4.0
    
    Y_spatial = np.zeros(5)
    
    # Application stricte des formules du filtre spatial
    Y_spatial[0] = saturation(w_center*X[0] + w_voisin_externe*X[1])                # Bord Gauche
    Y_spatial[1] = saturation(w_center*X[1] + w_voisin*X[0] + w_voisin*X[2])       # Gauche
    Y_spatial[2] = saturation(w_center*X[2] + w_voisin*X[1] + w_voisin*X[3])       # Centre
    Y_spatial[3] = saturation(w_center*X[3] + w_voisin*X[2] + w_voisin*X[4])       # Droite
    Y_spatial[4] = saturation(w_center*X[4] + w_voisin_externe*X[3])                # Bord Droit

    # Si tous les capteurs voient un mur (ex: tous à 1.0), 
    # Y_spatial sera proche de [0,0,0,0,0] grâce aux poids négatifs.

    # ---------------------------------------------------------
    # COUCHE 2 : Couche Cachée
    # ---------------------------------------------------------
       
    H = np.zeros(3)

    w_cote = 2.0
    w_cote_ext = 2.0
    
    # On ignore les valeurs négatives (inhibition) pour éviter la répulsion
    Y_pos = np.maximum(Y_spatial, 0)
    
    H[0] = saturation(w_cote_ext*Y_pos[0] + w_cote*Y_pos[1])
    H[1] = saturation(1.0*Y_pos[2]) #centre
    H[2] = saturation(w_cote_ext*Y_pos[4] + w_cote*Y_pos[3])

    # ---------------------------------------------------------
    # COUCHE 3 : Sortie Moteurs
    # ---------------------------------------------------------
    
    w_front = 1.0
    w_cross = 1.0
    w_same = -2.0 # Inhibition : le capteur gauche freine la roue gauche

    y1 = saturation(w_cross * H[2] + w_same * H[0] + w_front * H[1] + BIAIS) * FORWARD_SPEED 
    y2 = saturation(w_cross * H[0] + w_same * H[2] + w_front * H[1] + BIAIS) * FORWARD_SPEED

    # Commande des moteurs
    motor_left.setVelocity(y1)
    motor_right.setVelocity(y2)
    print(chr(27) + "[2J")
    print(f"In: {[f'{x:.2f}' for x in X]}")
    print(f"Spatial: {[f'{y:.2f}' for y in Y_spatial]}")
    print(f"Motors: L={y1:.2f} R={y2:.2f}")