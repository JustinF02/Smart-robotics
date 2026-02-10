import numpy as np
import matplotlib.pyplot as plt
from controller import Supervisor



robot = Supervisor()
robot_node = robot.getSelf()
timestep = int(robot.getBasicTimeStep())

#initialisation des moteurs
motor_left = robot.getDevice("motor.left")
motor_right = robot.getDevice("motor.right")
motor_left.setPosition(float('inf'))
motor_right.setPosition(float('inf'))


prox_sensors = []
for i in range(7):
    name = f"prox.horizontal.{i}"
    sensor = robot.getDevice(name)
    sensor.enable(timestep)
    prox_sensors.append(sensor)
    
#0 far left
#1 left
#2 front
#3 right
#4 far right
#5 back left
#6 back right

THRESHOLD = 150  # seuil pour détection obstacle
FORWARD_SPEED = 9.5
SENSOR_MAX_VAL = 4000.0

def saturation(x):
    return np.clip(x, -1.0, 1.0)

#liste des poids
#entrée 1
w11 = 1.0  #influe son moteur
w12 = -3.0 #influe le moteur opposé

#entrée 2
w21 = -2.0  #influe arrêt moteur g
w22 = -2.0  #influe arrêt moteur d

#entrée 3
w31 = -3.0   #influe le moteur opposé
w32 = 1.0 #influe son moteur




# ============== CONFIGURATION ==============
USE_MEMORY = True #True = avec mémoire | False = sans mémoire
bias = 1.0
#sorties précèdentes
w4 = 0.2 #influence  de la sortie précèdente
w5 = 0.2 #influence de la sortie précèdente
# ===========================================

y1_prev = 0.0
y2_prev = 0.0

#historique pour les graphiques
list_real_x = []
list_real_y = []
list_y1 = []
list_y2 = []
list_time = []
plot_counter = 0
time_counter = 0.0

plt.ion()


while robot.step(timestep) != -1:
    
    #récupération position réelle
    real_pos = robot_node.getPosition()

    #récupération valeurs capteurs
    val_left = prox_sensors[1].getValue() / SENSOR_MAX_VAL
    val_front = prox_sensors[2].getValue() / SENSOR_MAX_VAL
    val_right = prox_sensors[3].getValue() / SENSOR_MAX_VAL
    
    #entrée
    X = np.array([val_left, val_front, val_right])

    #calcul selon la configuration
    if USE_MEMORY:
        #avec mémoire
        y1 = saturation((X[0] * w11) + (X[1] * w21) + (X[2] * w31) + (y1_prev * w4) + bias)
        y2 = saturation((X[0] * w12) + (X[1] * w22) + (X[2] * w32) + (y2_prev * w5) + bias)
    else:
        #sans mémoire
        y1 = saturation((X[0] * w11) + (X[1] * w21) + (X[2] * w31) + bias)
        y2 = saturation((X[0] * w12) + (X[1] * w22) + (X[2] * w32) + bias)

    #enregistrement historique
    list_real_x.append(real_pos[0])
    list_real_y.append(real_pos[1])
    list_y1.append(y1)
    list_y2.append(y2)
    list_time.append(time_counter)
    time_counter += timestep / 1000.0

    print(chr(27) + "[2J")
    print(f"left: {X[0]:.2f}, front: {X[1]:.2f}, right: {X[2]:.2f}")
    print(f"y1: {y1:.2f}, y2: {y2:.2f}")

    #mise à jour de la mémoire
    y1_prev = y1
    y2_prev = y2

    #sortie
    motor_left.setVelocity(y1 * FORWARD_SPEED)
    motor_right.setVelocity(y2 * FORWARD_SPEED)
    
    #affichage graphiques
    plot_counter += 1
    if plot_counter % 20 == 0:
        mode_label = "AVEC MÉMOIRE (Réseau Récurrent)" if USE_MEMORY else "Sans mémoire"
        
        plt.figure(1, figsize=(15, 4))
        plt.clf()
        
        #sous-graphique 1: Trajectoire
        plt.subplot(1, 3, 1)
        plt.plot(list_real_x, list_real_y, 'g-', linewidth=2, label='Trajectoire réelle')
        plt.plot(real_pos[0], real_pos[1], 'go', markersize=8, label='Position actuelle')
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        plt.xlabel('X (m)')
        plt.ylabel('Y (m)')
        plt.title(f'Trajectoire du robot\n({mode_label})')
        plt.legend()
        
        #sous-graphique 2: y1 (moteur gauche)
        plt.subplot(1, 3, 2)
        color_y1 = 'b' if USE_MEMORY else 'orange'
        plt.plot(list_time, list_y1, color=color_y1, linewidth=2.5, label=f'y1 - {mode_label}')
        plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        plt.grid(True, alpha=0.3)
        plt.xlabel('Temps (s)')
        plt.ylabel('Sortie normalisée')
        plt.title('Moteur gauche (y1)')
        plt.legend(loc='best', fontsize=9)
        plt.ylim(-1.2, 1.2)
        
        #sous-graphique 3: y2 (moteur droit)
        plt.subplot(1, 3, 3)
        color_y2 = 'r' if USE_MEMORY else 'purple'
        plt.plot(list_time, list_y2, color=color_y2, linewidth=2.5, label=f'y2 - {mode_label}')
        plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        plt.grid(True, alpha=0.3)
        plt.xlabel('Temps (s)')
        plt.ylabel('Sortie normalisée')
        plt.title('Moteur droit (y2)')
        plt.legend(loc='best', fontsize=9)
        plt.ylim(-1.2, 1.2)
        
        plt.tight_layout()
        plt.pause(0.01)
        plt.draw()

plt.ioff()
plt.show()

    