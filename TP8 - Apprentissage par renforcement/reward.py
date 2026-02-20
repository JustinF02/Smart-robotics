import numpy as np
from controller import Robot, Keyboard

# --- Paramètres Globaux ---
dt = 100 #ms
ALPHA = 0.0001 #taux apprentissage
speed = 3
W = np.zeros((2, 5))

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
keyboard.enable(timestep) # Activer le clavier

left_motor = robot.getDevice("motor.left")
right_motor = robot.getDevice("motor.right")
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

sensors = get_sensors(robot, timestep)

#variable pour le timer
timer = 0
#compteur pour les logs
log_counter = 0


while robot.step(timestep) != -1:

    timer += timestep
    if timer < dt:
        continue
    
    timer = 0

    # --- Etape 1 : Acquisition x (Normalisé 0-100) ---
    raw_values = [s.getValue() for s in sensors]
    x = np.array(raw_values) / 40.0 # Normalisation approx [0, 100]
    
    # --- Etape 2 & Exo 2 : Calcul de y (Modèle ou Clavier ?) ---
    
    # D'abord, on calcule ce que le robot "veut" faire (Réseau de neurones)
    y_model = np.dot(W, x)
    y = np.clip(y_model, -100, 100)
    
    # Ensuite, on regarde si l'humain intervient (Algorithme 2)
    key = keyboard.getKey()
    
    override = False # Indicateur si l'humain force la commande
    
    if key == Keyboard.UP:
        y = np.array([100.0, 100.0])
        override = True
        print("Enseignement: AVANCER")
        
    elif key == Keyboard.DOWN:
        y = np.array([-100.0, -100.0])
        override = True
        print("Enseignement: RECULER")
        
    elif key == Keyboard.LEFT:
        y = np.array([-100.0, 100.0]) # Tourner sur place gauche
        override = True
        print("Enseignement: GAUCHE")
        
    elif key == Keyboard.RIGHT:
        y = np.array([100.0, -100.0]) # Tourner sur place droite
        override = True
        print("Enseignement: DROITE")

    # --- Etape 3 : Application aux moteurs ---
    # Conversion y [-100, 100] -> Vitesse réelle
    v_left = (y[0] / 100.0) * speed
    v_right = (y[1] / 100.0) * speed
    
    left_motor.setVelocity(v_left)
    right_motor.setVelocity(v_right)
    
    # --- Etape 4 : Règle de Hebb (Algorithm 3) ---
    # Seulement si on perçoit quelque chose (pour éviter d'apprendre du bruit)
    if np.any(x > 0.1): 
        
        # y1 correspond à y[0] (moteur gauche), y2 à y[1] (moteur droit)
        y1 = y[0]
        y2 = y[1]
        
        # Algorithme 3 : "for j dans {1,2,3,4,5}" (ici 0 à 4)
        for j in range(5):
            xj = x[j]
            
            # Ligne 3: w_jl <- w_jl + alpha * y1 * xj
            W[0][j] = W[0][j] + ALPHA * y1 * xj
            
            # Ligne 4: w_jr <- w_jr + alpha * y2 * xj
            W[1][j] = W[1][j] + ALPHA * y2 * xj
    
    # --- Logs ---
    log_counter += 1
    if log_counter % 20 == 0:
        # print("-" * 30)
        # print(f"Mode: {'MANUEL' if override else 'AUTO'}")
        pass
        # print(f"Inputs (x): {np.round(x, 1)}")
        # print("Poids W:", np.round(W, 3))