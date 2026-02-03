#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.1": *
#import "@preview/subpar:0.2.2"
#show: codly-init.with()

#import "latemplate.typ": latemplate
#import "lalib.typ": place_at, emphasis_text, insert_toc, insert_annex_page, hidden_heading

#set par(
  first-line-indent: 1em,
  spacing: 1.2em,
  justify: true,
)

#set text(size: 12pt)

// Enable equation numbering for subfigure references
#set math.equation(numbering: "1.")

// ==== Body ====

#show: latemplate.with(
  title: [_C3 - Intelligence pour la robotique_: TP5 -- Navigation par perceptron],
  title_size: 21pt,
  authors_flat: (
    (name:"Justin Ferdinand"),
  ),
  header_content: (
    left: [*SETI C3 - Intelligence pour la robotique* TP5 -- Navigation par perceptron],
  ),
  page_numbering: "1/1",
  heading_numbering: "I.A.1",
  column_count: 2,
)

= Introduction
Ce TP a pour objectif de découvrir le fonctionnement du perceptron, un modèle de neurone artificiel simple, et d'en comprendre les applications à travers des exemples théoriques (modélisation d'opérateurs logiques) puis pratiques (contrôle d'un robot Thymio).

= Perceptron : implantation d'une porte logique

== Définition des variables d'entrée

Les variables d'entrée du perceptron, $x_1$ et $x_2$, prennent les valeurs 0 ou 1.

== Fonction de calcul de la somme pondérée

La sortie du perceptron est déterminée par la somme pondérée suivante :

$s = w_0 + x_1 \cdot w_1 + x_2 \cdot w_2$

où $w_0$ est le biais, $w_1$ et $w_2$ les poids associés aux entrées.

== Fonction d'activation

La fonction d'activation utilisée est une fonction seuil :


$y =$
- 1 si $s \geq 0$,
- 0 si $s < 0$,

== Validation sur les opérateurs logiques

On teste le perceptron pour modéliser les fonctions logiques OU (OR) et ET (AND) à l'aide de tables de vérité et de choix appropriés des poids.

```python
import pandas as pd

#table de vérité pour OU (OR)
poids_ou = {'w0': -0.5, 'w1': 1.0, 'w2': 1.0}
#table de vérité pour ET (AND)
poids_et = {'w0': -1.5, 'w1': 1.0, 'w2': 1.0}

combinaisons = [(0,0), (0,1), (1,0), (1,1)]

#test pour l'opérateur OU
resultats_ou = []
for x1, x2 in combinaisons:
    s = calcul_s(x1, x2, **poids_ou)
    y = activation(s)
    resultats_ou.append({'x1': x1, 'x2': x2, 's': s, 'y': y})
df_ou = pd.DataFrame(resultats_ou)

#test pour l'opérateur ET
resultats_et = []
for x1, x2 in combinaisons:
    s = calcul_s(x1, x2, **poids_et)
    y = activation(s)
    resultats_et.append({'x1': x1, 'x2': x2, 's': s, 'y': y})
df_et = pd.DataFrame(resultats_et)

print('Table de vérité OU (OR)')
print(df_ou)
print('\nTable de vérité ET (AND)')
print(df_et)
```

#figure(
  table(
    columns: (auto, auto, auto, auto),
    inset: 10pt,
    align: horizon,
    table.header(
      [x₁], [x₂], [s], [y],
    ),
    
    [0], [0], [-0.5], [0],
    [0], [1], [0.5], [1],
    [1], [0], [0.5], [1],
    [1], [1], [1.5], [1],
  ),
  caption: [Résultat du test pour l'opérateur OU (OR)],
)<tabledeveriteOU>

#figure(
  table(
  columns: (auto, auto, auto, auto),
  inset: 10pt,
  align: horizon,
  table.header(
    [x₁], [x₂], [s], [y],
  ),
  
  [0], [0], [-1.5], [0],
  [0], [1], [-0.5], [0],
  [1], [0], [-0.5], [0],
  [1], [1], [0.5], [1],
  ),
  caption: [Résultat du test pour l'opérateur ET (AND)],
)<tabledeveriteET>

#colbreak()

= Exemple d'application sur webots

Dans cette application, on utilise un perceptron pour contrôler le robot Thymio dans Webots à partir de ses capteurs infrarouge arrière. Les valeurs des capteurs arrière gauche et arrière droit sont binarisées, puis passées en entrée d'un perceptron modélisant une porte logique ET. Si les deux capteurs détectent un obstacle, le robot avance pour s'éloigner de l'obstacle. Sinon, il s'arrête.

Pour implémenter cela, j'ai repris mon code du TP1 en modifiant le contrôle de navigation par le perceptron ET arrière.

```python
def calcul_s(x1, x2, w0, w1, w2):
  return w0 + x1 * w1 + x2 * w2

def activation(s):
  return 1 if s >= 0 else 0

#poids pour perceptron ET
poids_et = {'w0': -1.5, 'w1': 1.0, 'w2': 1.0}

while robot.step(timestep) != -1:
  back_left = 1 if prox_sensors[5].getValue() > THRESHOLD else 0
  back_right = 1 if prox_sensors[6].getValue() > THRESHOLD else 0

  s_et = calcul_s(back_left, back_right, **poids_et)
  y_et = activation(s_et)
  if y_et == 1:
    #avancer si obstacle derrière
    motor_left.setVelocity(FORWARD_SPEED)
    motor_right.setVelocity(FORWARD_SPEED)
    print("Obstacle derrière : avance !")
  else:
    motor_left.setVelocity(0.0)
    motor_right.setVelocity(0.0)
```

Ce code montre comment un perceptron simple peut être utilisé pour réagir à la détection d'obstacles à l'arrière du robot et générer un comportement d'évitement vers l'avant.

= Perceptron analogue

Dans cette partie, on implémente un perceptron analogique à une entrée pour contrôler la vitesse de recul du robot Thymio en fonction de la distance à un obstacle détecté par le capteur avant. La sortie du perceptron est proportionnelle à la valeur du capteur, ce qui permet d'adapter la vitesse de recul : plus l'obstacle est proche, plus le robot recule vite.

```python

while robot.step(timestep) != -1:
  front_sensor_value = prox_sensors[2].getValue()
  #normalisation de la valeur du capteur
  x1 = front_sensor_value / 1000.0
  #poids du perceptron
  w1 = 4
  y1 = w1 * x1
  print(f"Front sensor value: {front_sensor_value}, Normalized: {x1}, Output y1: {y1}")
  #vitesse de recul proportionnelle à la sortie
  backward_speed = min(max(0.0, y1 * FORWARD_SPEED), maxVelocity)
  print(f"Calculated backward speed: {y1 * FORWARD_SPEED}")
  if backward_speed > 0.05:  # seuil pour éviter les petits bruits
    motor_left.setVelocity(-backward_speed)
    motor_right.setVelocity(-backward_speed)
    print(f"Obstacle devant : recule à {backward_speed:.2f}")
  else:
    motor_left.setVelocity(FORWARD_SPEED)
    motor_right.setVelocity(FORWARD_SPEED)
```

Ce code illustre le fonctionnement d'un perceptron analogique : la sortie n'est plus binaire, mais continue, et permet un contrôle proportionnel de la vitesse du robot selon la proximité de l'obstacle détecté. Cela nous permet d'obtenir les commandes de recul suivantes :

```sh
Front sensor value: 261.2632287380115, Normalized: 0.2612632287380115, Output y1: 1.045052914952046
Calculated backward speed: 8.360423319616368
Front obstacle : move backward at 8.36
Front sensor value: 325.08905221648115, Normalized: 0.32508905221648116, Output y1: 1.3003562088659246
Calculated backward speed: 10.402849670927397
Front obstacle : move backward at 9.53
Front sensor value: 58.500129297333025, Normalized: 0.058500129297333024, Output y1: 0.2340005171893321
Calculated backward speed: 1.8720041375146568
Front obstacle : move backward at 1.87
```

J'observe ainsi une réponse proportionnelle à la distance de l'obstacle, avec une vitesse de recul plus élevée lorsque l'obstacle est proche.

#pagebreak()
== Perceptron analogue à deux entrées

On peut implémenter le perceptron analogique à deux entrées, comme illustré dans la figure 3 du sujet. Ici, chaque entrée correspond à la valeur normalisée d'un capteur (par exemple, capteur avant gauche et capteur avant droit). Les poids $w_1$ et $w_2$ permettent de moduler l'influence de chaque capteur sur la sortie du perceptron.

Si l'on choisit $w_1$ beaucoup plus grand que $w_2$, la sortie sera principalement influencée par le capteur associé à $w_1$.

```python
while robot.step(timestep) != -1:
  left_sensor_value = prox_sensors[1].getValue()
  right_sensor_value = prox_sensors[3].getValue()
  #normalisations
  x1 = left_sensor_value / 1000.0
  x2 = right_sensor_value / 1000.0
  #poids différents des capteurs
  w1 = 5 #gauche
  w2 = 1#droite
  
  #perceptron à deux entrées
  y1 = w1 * x1 + w2 * x2
  print(f"Left sensor: {x1:.2f}, Right sensor: {x2:.2f}, Output y1: {y1:.2f}")
  #vitesse de recul proportionnelle à la sortie
  backward_speed = min(max(0.0, y1 * FORWARD_SPEED), maxVelocity)
  if backward_speed > 0.05:
    motor_left.setVelocity(-backward_speed)
    motor_right.setVelocity(-backward_speed)
    print(f"Obstacle devant : recule à {backward_speed:.2f}")
  else:
    motor_left.setVelocity(FORWARD_SPEED)
    motor_right.setVelocity(FORWARD_SPEED)
```

Ce code montre que le capteur associé au poids le plus fort a une influence dominante sur la sortie du perceptron et donc sur la vitesse de recul du robot. En modifiant les valeurs de $w_1$ et $w_2$, on peut observer expérimentalement l'effet de chaque capteur sur le comportement du robot dans le même scénario :

Avec capteur gauche plus influent ($w_1 = 5$, $w_2 = 1$) :
```sh
Left sensor: 0.00, Right sensor: 0.00, Output y1: 0.00
Left sensor: 0.31, Right sensor: 0.00, Output y1: 1.57
Front obstacle : move backward at 9.53
```

Le capteur gauche influe fortement sur la sortie, entraînant un recul rapide car le le mur gauche est proche.

Avec capteur droit plus influent ($w_1 = 1$, $w_2 = 5$) :
```sh
Left sensor: 0.01, Right sensor: 0.00, Output y1: 0.01
Front obstacle : move backward at 0.09
```

Ici, le capteur droit ayant peu d'influence et ne rencontrant pas d'obstacle, la sortie reste faible mais positive car toujours influencée par le capteur gauche.

#colbreak()

= Véhicule de brateinberg


== Principe de l'algorithme

Le robot utilise ses capteurs avant (gauche, centre, droite) pour détecter les obstacles et décide de tourner ou d'avancer selon la sortie du perceptron :

- Si obstacle devant, il tourne sur lui-même.
- Si obstacle à gauche, il tourne à droite.
- Si obstacle à droite, il tourne à gauche.
- Sinon, il avance.

De plus, si les deux capteurs arrière détectent un obstacle, le robot avance pour éviter de rester bloqué. Les rayons infrarouges de Thymio sont visibles sur la @capteursIR.

#figure(
  image("/img/photo_robot.png"),
  caption: [Capture d'écran du robot Thymio avec les capteurs infrarouge],
) <capteursIR>

== Extrait de code


Le code suivant implémente le modèle de la @ANNmodel pour la navigation autonome du robot Thymio. Les capteurs avant sont normalisés et utilisés comme entrées d'un réseau de neurones simple: la sortie y1 contrôle l'avance/recul, y2 la rotation.

#text("Explication des poids", weight: "bold"):



- $W_"fwd"$ : favorise l'avancée du robot en l'absence d'obstacle.
- $W_"back"$ : s'oppose à l'avancée si un obstacle est détecté devant. Plus $|W_"back"|$ est grand, plus le robot recule de manière rapide.
- $W_"pos"$ : fait tourner le robot à droite si un obstacle est détecté à gauche.
- $W_"neg"$ : fait tourner le robot à gauche si un obstacle est détecté à droite.
- $W_"ctr"$ : force une rotation sur place si un obstacle est détecté devant.

#text("Équations de calcul", weight: "bold"):

Les sorties du réseau sont calculées ainsi:
$
y_1 = W_"fwd" dot 1 + W_"back" dot "center"
$

$
y_2 = W_"pos" dot "left" + W_"neg" dot "right" + W_"ctr" dot "center"
$

où left, center et right sont les valeurs normalisées des capteurs avant gauche, centre et droite.

Après application d'une fonction d'activation non-linéaire, les vitesses des roues sont données par :

$
v_"left" = V_"fwd" dot y_1 - V_"turn" dot y_2
$
$
v_"right" = V_"fwd" dot y_1 + V_"turn" dot y_2
$


où $V_"fwd"$ est la vitesse pour avancer et $V_"turn"$ la vitesse de rotation.

#figure(
  image("/assets/image-4.png"),
  caption: [Modèle d'ANN proposé],
) <ANNmodel>

```python

FORWARD_SPEED = 8.0
TURN_SPEED = 4.0
MAX_SENSOR = 4000.0  #https://www.cyberbotics.com/doc/guide/thymio2?version=R2019a-rev1

# Entrées : [1, gauche, centre, droite]
# Sorties : y1 (avance/recule), y2 (rotation)
W_fwd = 0.5    # avancer
W_back = -1.0  # reculer
W_pos = 1.0    # tourner à droite
W_neg = -1.0   # tourner à gauche

def activation(x):
    #activation linéaire
    return math.tanh(x)

while robot.step(timestep) != -1:
    #normalisation
    left = prox_sensors[4].getValue() / MAX_SENSOR
    center = prox_sensors[2].getValue() / MAX_SENSOR
    right = prox_sensors[0].getValue() / MAX_SENSOR
    bias = 1.0

    x = [bias, left, center, right]

    # Calcul des sorties du réseau
    # y1 = sortie avance/recule
    # y2 = sortie rotation

    #W_back > W_fwd car on veut reculer si un obstacle est devant
    y1 = W_fwd * x[0] + W_back * x[2]


    #si obstacle à gauche -> tourner à droite.
    #si obstacle à droite -> tourner à gauche
    y2 = W_pos * x[1] + W_neg * x[3]

    #sorties activées
    y1 = activation(y1)
    y2 = activation(y2)

    #vitesse des roues
    v_left = FORWARD_SPEED * y1 - TURN_SPEED * y2
    v_right = FORWARD_SPEED * y1 + TURN_SPEED * y2

    #vitesse plafonnée
    v_left = max(-FORWARD_SPEED, min(FORWARD_SPEED, v_left))
    v_right = max(-FORWARD_SPEED, min(FORWARD_SPEED, v_right))

    motor_left.setVelocity(v_left)
    motor_right.setVelocity(v_right)

    print(f"Capteurs (norm): L={left:.2f} C={center:.2f} R={right:.2f} | y1={y1:.2f} y2={y2:.2f} | vL={v_left:.2f} vR={v_right:.2f}")
```

Je remarque alors que le robot thymio réagit de manière fluide à la présence des murs dans le parcours. Il est capable de faire un tour complet selon la simulation puisque son raisonnement qui reste naîf ne lui permet pas de comprendre qu'elle est la direction prendre. Il lui arrive ainsi de faire demi-tour et repartir en sens inverse.

Deux vidéos démontrent cette capacité de navigation autonome dans le dossier, l'une dans un environnement sans obstacle, l'autre avec.

#colbreak()
= Conclusion


#hidden_heading[Conclusion]
#emphasis_text("Pour conclure, ")
#text(fill: color.rgb("444444"), weight: "bold")[ce TP m'a permis de comprendre le fonctionnement des perceptrons, tant binaires qu'analogiques, et leur application au contrôle de robots. J'ai pu expérimenter avec différents poids et observer comment ils influencent le comportement du robot Thymio dans Webots. L'implémentation d'un modèle de véhicule de Braitenberg m'a également aidé à saisir comment des réseaux de neurones simples peuvent générer des comportements complexes à partir de signaux sensoriels. Ce TP a renforcé mes compétences en programmation robotique et en intelligence artificielle appliquée à la robotique.
  ]
  #v(40em)