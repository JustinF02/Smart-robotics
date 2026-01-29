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
  title: [_C4 - Intelligence pour la robotique_: TP4 -- Navigation],
  title_size: 21pt,
  authors_flat: (
    (name:"Justin Ferdinand"),
  ),
  header_content: (
    left: [*SETI C4 - Intelligence pour la robotique* TP4 -- Navigation],
  ),
  page_numbering: "1/1",
  heading_numbering: "I.A.1",
  column_count: 2,
)

= Introduction

Ce TP aborde la problématique de la navigation réactive pour un robot mobile évoluant dans un environnement inconnu et complexe. L'objectif est de permettre au robot de se déplacer de manière autonome sans carte préétablie, en utilisant uniquement les informations d'un lidar.

Pour ce faire, nous implémentons l'algorithme "Follow the Gap" (représenté sur la @FollowTheGap) en exploitant les données d'un lidar 2D. Cette méthode consiste à analyser le nuage de points pour détecter les obstacles, définir des bulles de sécurité, et identifier l'espace libre le plus large afin d'y diriger le robot.

#figure(
  image("/assets/image-3.png"),
  caption: [Schéma illustrant l'algorithme Follow The Gap],
) <FollowTheGap>,

= Méthodologie


Pour implémenter l'algorithme Follow The Gap, j'ai suivi ce repo Github : #link("https://github.com/ghiati/Follow_the_Gap")[(Lien du Git)] qui implémente un script python de ce dernier. Les principales étapes de l'algorithme sont les suivantes :

1. #text(weight: "bold")[Pré-traitement des données lidar] : Les données brutes du lidar sont filtrées pour réduire le champ de vision à l'avant uniquement et retirer les données abbérantes : valeurs infinies remplacées par une distance maximale plafonnée.

2. #text(weight: "bold")[Gestion des obstacles par une bulle de sécurité] : Les bulles de sécurité sont utilisées pour éviter les collisions avec les obstacles détectés par le lidar,

3. #text(weight: "bold")[Recherche du plus grand espace libre] : L'algorithme identifie le plus grand espace libre entre les obstacles pour déterminer le vecteur de déplacement optimal du robot,
4. #text(weight: "bold")[Commande motrice] : Le point cible est sélectionné au milieu de l'espace libre visé, et les commandes motrices sont appliquées pour diriger le robot vers ce point.

= Implémentation en Python


== Pré-traitement des données LIDAR

Ces trois fonctions issues du repo git permettent de filtrer les données lidar, de trouver le plus grand gap et de tirer le point cible au milieu de celui-ci.

```python
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
  """return the index of  the point in the middle of the gap"""
  return int((start_i + end_i) / 2)
```
== Gestion des obstacles : La bulle de sécurité

Pour garantir que le robot ne frôle pas les murs du labyrinthe ou les obstacles, j'ajoute une bulle de sécurité autour de chaque obstacle détecté par le lidar. Cette zone de sécurité est créée en invalidant les mesures du lidar qui se trouvent inférieure à une certaine distance du robot. La zone entière devient donc une zone infranchissable pour le robot telle que visible sur la @obstacles.

#figure(
  image("/assets/image.png"),
  caption: [Affichage des bulles de sécurité autour des obstacles],
) <obstacles>,

Le code suivant montre comment j'ai implémenté cette fonctionnalité :
```python
#trouver le point le plus proche
valid_idxs = np.where((filtered_ranges > 0) & (~np.isinf(filtered_ranges)))[0]
if valid_idxs.size > 0:
    local_min_idx = np.argmin(filtered_ranges[valid_idxs])
    closest_point_idx = int(valid_idxs[local_min_idx])
    min_dist = float(filtered_ranges[closest_point_idx])
else:
    closest_point_idx = None
    min_dist = None

#bulle de sécurité sur le point le plus proche
if closest_point_idx is not None and min_dist is not None and min_dist > 0:
    #calcul de l'angle de la bulle
    angle_bubble = math.atan2(BUBBLE_RADIUS, min_dist)
    bubble_radius_idx = int(math.degrees(angle_bubble) / math.degrees(angle_increment))
    #sécurité au cas où
    if bubble_radius_idx <= 0:
        bubble_radius_idx = int(np.radians(20) / angle_increment) # ~20 degrés

    start_bubble = max(0, closest_point_idx - bubble_radius_idx)
    end_bubble = min(len(proc_ranges) - 1, closest_point_idx + bubble_radius_idx)
    debug_bubble_indices = range(start_bubble, end_bubble+1)
    #La région de la bulle vaut 0 pour empécher le robot d'y aller
    proc_ranges[start_bubble:end_bubble+1] = 0
else:
    #pas de bulle sans obstacle
    debug_bubble_indices = []
```

Le code ci-présent permet de trouver le point le plus proche détecté par le lidar, puis de créer une bulle de sécurité autour de ce point en invalidant les mesures du lidar dans cette zone (mise à zéro). La taille de la bulle est déterminée par un rayon défini (BUBBLE_RADIUS) et l'angle correspondant est calculé en fonction de la distance au point le plus proche.



== Recherche du plus grand espace libre

Une fois les obstacles définis par les bulles de sécurité, j'ai implémenté la recherche du plus grand espace libre entre ces obstacles. Ce gap permet de déterminer la direction dans laquelle le robot doit se diriger. Le code suivant illustre cette étape :

```python
#on trouve l'écart le plus grand dans les données lidar
start_gap, end_gap = find_max_gap(proc_ranges)

target_speed_left = 0
target_speed_right = 0

if start_gap is not None and end_gap is not None:
    #le point le plus loin dans l'écart
    best_point_idx = find_best_point(start_gap, end_gap, proc_ranges)
    
    #ici on va diriger le robot vers ce point
    #calcul de l'angle cible
    angle_target = (fov / 2.0) - (best_point_idx * angle_increment)
    
    #et on fait une commande proportionnelle pour faire une courbe propre
    turn_command = KP_TURN * angle_target 
    
    #calcul vitesse des roues
    target_speed_left = VELOCITY_BASE - turn_command
    target_speed_right = VELOCITY_BASE + turn_command
    
    #vitesse max
    max_motor = 20
    target_speed_left = max(-max_motor, min(max_motor, target_speed_left))
    target_speed_right = max(-max_motor, min(max_motor, target_speed_right))
    
```

Dans le cas où aucun gap n'est trouvé, le robot se dirige vers le côté (gauche ou droite) en fonction de quel côté est le plus libre des deux.

== Commande moteurs

Dès le départ du TP, je n'ai pas mis en place une commande de moteur faisant une rotation sur place pour se diriger vers la cible. J'ai préféré ajouter un gain KP pour faire une commande proportionnelle en fonction de la différence angulaire du robot avec sa cible. Cela permet de faire des trajectoires plus douces et sans arrêts. Cela ne permet pas au robot de voir l'ensemble des gaps disponible mais j'avais observé que celui-ci pouvait finir par faire demi-tour si son point de départ était plus libre que son objectif.

= Résultats et Analyse

Pour démontrer l'efficacité de l'algorithme Follow The Gap, j'ai réalisé plusieurs tests dans un environnement simulé. Les résultats montrent que le robot est capable de naviguer de manière autonome dans le labyrinthe vide (voir la vidéo MerryGoRound.mp4) en réalisant un tour complet. Je remarque également que celui-ci réalise des trajectoires "optimales" pour suivre le tracet graçe à la commande proportionnelle.

En augmentant la vitesse de rotation et de vitesse linéaire, le robot parvient à naviguer plus rapidement. J'observe toute fois qu'une commande trop brutale peut entraîner une perte dans la navigation, notamment dans les virages serrés. Le robot finit alors par s'arrêter face à un mur sans possibilité d'esquive.

Enfin, j'ai terminé mon analyse de l'algorithme par l'ajout de différents obstacles sur le parcours de Thymio, visibles sur la @complexe. J'ai ainsi ajouté des animaux et des bouteilles qui peuvent tomber par contact. Dans mon observation, le robot ne touche pas les bouteilles, ce qui confirme l'efficacité de la bulle de sécurité. Il faut ajouter que le robot possède une certaine largeur l'empéchant de passer outre certains obstacles trop proches. Ces observations sont visibles dans la vidéo MerryGoRound_with_objects.mp4.


#figure(
  image("/assets/image-2.png"),
  caption: [Navigation dans un environnement avec obstacles],
) <complexe>,


= Conclusion


#hidden_heading[Conclusion]
#emphasis_text("Pour conclure,")
#text(fill: color.rgb("444444"), weight: "bold")[Ce TP m'a permis de comprendre et d'implémenter l'algorithme Follow The Gap pour la navigation réactive d'un robot mobile. En utilisant les données d'un lidar, j'ai pu développer un système capable de détecter les obstacles, de définir des zones de sécurité, et de naviguer efficacement dans un environnement inconnu. 

Les résultats que j'observe montrent un algorithme robuste mais qui peut rapidement se perdre lorsque le robot rencontre un obstacle trop proche sans possiblité d'esquiver. J'ajoute ainsi que le retour à l'erreur est difficile dans une situation trop complexe.

Mon implémentation pourrait être améliorée en intégrant un cache des bulles de sécurité pour éviter de recalculer leurs emplacements à chaque itération, évitant ainsi un lag dans la navigation et accélèrant la vitesse de calcul. De plus, il serait possible d'intégrer une stratégie de navigation par cycles limites, permettant une trajectoire plus optimale vers la cible par anticipation des obstacles.
  ]
  #v(40em)