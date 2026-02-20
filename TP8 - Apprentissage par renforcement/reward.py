import numpy as np
from controller import Robot, Keyboard

# --- Paramètres Globaux ---
dt = 10 #ms
ALPHA = 0.05 #taux apprentissage
speed = 6
TURN_GAIN = 0.45 # < 1.0 => virage plus doux
W = np.zeros((2, 5))
B = np.zeros(2)

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

    # --- Etape 1 : Acquisition x (normalisé 0-1) ---
    raw_values = [s.getValue() for s in sensors]
    x = np.clip(np.array(raw_values) / 4000.0, 0.0, 1.0)
    
    # --- Etape 2 & Exo 2 : Calcul de y (Modèle ou Clavier ?) ---
    
    # D'abord, on calcule ce que le robot "veut" faire (Réseau de neurones)
    y_model = np.dot(W, x) + B
    y = np.clip(y_model, -100, 100)

    # Si rien n'est perçu, avancer doucement par défaut
    if np.max(x) < 0.02:
        y = np.array([30.0, 30.0])
    
    # Ensuite, on regarde si l'humain intervient (Algorithme 2)
    key = keyboard.getKey()
    
    override = False # Indicateur si l'humain force la commande
    
    if key == Keyboard.UP:
        y = np.array([100.0, 100.0])
        override = True
        #print("Enseignement: AVANCER")
        
    elif key == Keyboard.DOWN:
        y = np.array([-100.0, -100.0])
        override = True
        #print("Enseignement: RECULER")
        
    elif key == Keyboard.LEFT:
        y = np.array([-100.0, 100.0]) # Tourner sur place gauche
        override = True
        #print("Enseignement: GAUCHE")
        
    elif key == Keyboard.RIGHT:
        y = np.array([100.0, -100.0]) # Tourner sur place droite
        override = True
        #print("Enseignement: DROITE")

    # Pondération de la rotation pour éviter les réactions trop violentes
    forward_cmd = (y[0] + y[1]) / 2.0
    turn_cmd = ((y[1] - y[0]) / 2.0) * TURN_GAIN
    y = np.array([
        forward_cmd - turn_cmd,
        forward_cmd + turn_cmd
    ])
    y = np.clip(y, -100, 100)

    # --- Etape 3 : Application aux moteurs ---
    # Conversion y [-100, 100] -> Vitesse réelle
    v_left = (y[0] / 100.0) * speed
    v_right = (y[1] / 100.0) * speed
    
    left_motor.setVelocity(v_left)
    right_motor.setVelocity(v_right)
    
    # --- Etape 4 : Règle de Hebb (pendant l'enseignement manuel) ---
    if override and np.any(x > 0.02):
        y1 = y[0] / 100.0
        y2 = y[1] / 100.0

        for j in range(5):
            xj = x[j]
            W[0][j] = W[0][j] + ALPHA * y1 * xj
            W[1][j] = W[1][j] + ALPHA * y2 * xj

        B[0] = B[0] + ALPHA * y1
        B[1] = B[1] + ALPHA * y2
    
    # --- Logs ---
    log_counter += 1
    if log_counter % 20 == 0:
        print(chr(27) + "[2J")
        print(f"Mode: {'MANUEL' if override else 'AUTO'}")
        pass
        print(f"Inputs (x): {np.round(x, 3)}")
        print("Poids W:\n", np.round(W, 3))
        print("Biais B:", np.round(B, 3))