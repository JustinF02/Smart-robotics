import numpy as np
from controller import Robot

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


robot = Robot()
timestep = int(robot.getBasicTimeStep())

left_motor = robot.getDevice("motor.left")
right_motor = robot.getDevice("motor.right")
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

sensors = get_sensors(robot, timestep)

# Boucle principale
while robot.step(timestep) != -1:

    
    timer += timestep
    if timer < dt:
        continue
    
    timer = 0

    # --- Etape 1 : Acquisition x (Normalisé 0-100) ---
    # x doit être un vecteur colonne (5, 1) ou un array 1D (5,)
    raw_values = [s.getValue() for s in sensors]
    # Normalisation : Webots max ~4000 -> 100
    x = np.array(raw_values) / 40.0 
    
    # --- Etape 2 : Calcul de la sortie y = W.x ---
    # y sera un vecteur de taille 2 [y_left, y_right]
    y = np.dot(W, x)
    
    # Saturation [-100, 100]
    y = np.clip(y, -100, 100)
    
    # --- Etape 3 : Application aux moteurs ---
    # Conversion de la sortie y [-100, 100] vers la vitesse réelle
    # On suppose que 100 correspond à MAX_SPEED
    v_left = (y[0] / 100.0) * speed
    v_right = (y[1] / 100.0) * speed
    
    left_motor.setVelocity(v_left)
    right_motor.setVelocity(v_right)
    
    # --- Etape 4 : Apprentissage (Hebb) ---
    # ∆W = Alpha * y * x.T
    # On doit reformer les dimensions pour le produit extérieur
    # y shape (2,), x shape (5,) -> Outer product donne (2, 5)
    dW = ALPHA * np.outer(y, x)
    
    W += dW


    log_counter += 1
    if log_counter % 20 == 0:
        print("-" * 50)
        print(f"Iteration: {log_counter}")
        print(f"Inputs (x): {np.round(x, 2)}")
        print(f"Outputs (y): {np.round(y, 2)}")
        print("Weights (W) evolution:")
        # Formatage propre de la matrice
        print(np.array2string(W, formatter={'float_kind':lambda x: "%.4f" % x}))