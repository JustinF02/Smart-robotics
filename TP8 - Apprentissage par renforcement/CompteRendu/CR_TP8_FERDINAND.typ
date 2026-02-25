#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.1": *
#import "@preview/subpar:0.2.2"
#show: codly-init.with()

#import "../../lib/latemplate.typ": latemplate
#import "../../lib/lalib.typ": place_at, emphasis_text, insert_toc, insert_annex_page, hidden_heading

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
  title: [_C3 - Intelligence pour la robotique_: TP8 -- Apprentissage par renforcement],
  title_size: 21pt,
  authors_flat: (
    (name:"Justin Ferdinand"),
  ),
  header_content: (
    left: [*SETI C3 - Intelligence pour la robotique* TP8 -- Apprentissage par renforcement],
  ),
  page_numbering: "1/1",
  heading_numbering: "I.A.1",
  column_count: 2,
)


= Introduction

Ce TP explore l'apprentissage par renforcement en opposition à l'apprentissage supervisé du TP précédent. L'objectif est de permettre au robot Thymio d'apprendre à s'adapter à son environnement en fonction de ses expériences et des interventions humaines, sans nécessiter de données d'entraînement préalables. Cela s'oppose donc à la création d'un jeu de données d'entraînement pour un apprentissage supervisé, et à la nécessité de fournir des sorties cibles à partir d'entrées enregistrées.

= Exercice 1 : Apprentissage de Hebb

Dans ce premier exercice, j'ajoute une règle de Hebb sur le robot. Le robot modifie ses poids $W$ en fonction de la corrélation entre ses entrées de capteurs de proximité et ses sorties moteurs.

L'équation de mise à jour des poids est donnée par :
$ Delta W_"ij" = Delta dot y_i dot x_j $
où $Delta$ est le taux d'apprentissage, $y_i$ l'activité du neurone moteur $i$, et $x_j$ l'entrée du capteur $j$.

Le code implémenté dans `reward.py` est le suivant :

#codly(header: [reward.py])
```python
avec ALPHA = 0.05
# ∆W = Alpha * y * x.T
dW = ALPHA * np.outer(y, x)
W += dW
``` 

Ici, j'ai mis un taux d'apprentissage de 0.05 pour que les poids évoluent plus rapidement lors de mes tests.

= Exercice 2 : Apprentissage supervisé

Dans cette seconde partie, l'ajout d'un enseignement humain par clavier permet de guider le robot vers le bon comportement selon son environnement.
La sortie $y$ est imposée par l'opérateur. La règle de Hebb de la première partie va apprendre l'association entre les entrées et les sorties des moteurs.

Pour stabiliser le comportement, j'ai conservé la structure principale du script et importé trois améliorations :
- activation non linéaire de type Braitenberg ($tanh$),
- mise à jour Hebb déclenchée une seule fois par appui clavier,
- ralentissement du robot quand la proximité obstacle augmente pour que Thymio ait le temps de réagir.

Le script `reward.py` implémente cette logique :

#codly(header: [Mode Enseignement])
```python
def get_manual_command_from_key(key):
    if key == Keyboard.UP:
        return np.array([100.0, 100.0])
    elif key == Keyboard.DOWN:
        return np.array([-100.0, -100.0])
    elif key == Keyboard.LEFT:
        return np.array([-100.0, 100.0])
    elif key == Keyboard.RIGHT:
        return np.array([100.0, -100.0])
    return None

key_pressed = override
is_new_key_press = key_pressed and not prev_key_pressed
if is_new_key_press:
  hebb_update(x, y, W, B, ALPHA)
prev_key_pressed = key_pressed
```

Le calcul en mode autonome est maintenant :

#codly(header: [Contrôle moteur])
```python
forward_cmd = (y[0] + y[1]) / 2.0
turn_cmd = ((y[1] - y[0]) / 2.0) * TURN_GAIN
y = np.array([
    forward_cmd - turn_cmd,
    forward_cmd + turn_cmd
])
y = np.clip(y, -100, 100)

v_left = (y[0] / 100.0) * speed
v_right = (y[1] / 100.0) * speed
```

Avec TURN_GAIN une valeur qui permet d'adoucir les virages et speed une vitesse de base réduite lorsque les capteurs de proximité détectent un obstacle proche.

== Apprendre à reculer face à un mur

#text("Protocole expérimental :", weight: "bold") saisir THymio, le placer face au mur et reculer avec la touche clavier.

#text("Résultat et observation :", weight: "bold")

En réalisant cette expérience, j'ai observé que les poids associés aux capteurs de proximité avant ont augmenté, ce qui indique que le robot a appris à associer ces entrées à la sortie de reculer. Le biais appliqué à Thymui a diminué, ce qui lui donne un comportement de peur face à un obstacle. Avec quelques itérations, le robot recule seul face à un mur, même sans intervention. Ce comportement est visible sur la vidéo `mouvement_de_peur.mp4`.

```
Poids W:
 [[-0.061 -0.068 -0.117  0.     0.   ]
 [-0.134 -0.032  0.017  0.     0.   ]]
```

== Réaliser un tour complet avec obstacles

//TODO: insérer vidéo du robot qui fait le tour du labyrinthe avec des obstacles

Je rencontre beaucoup de diffultés pour réaliser un entraînement de thymio dans le circuit. En effet, le robot a du mal à percevoir les obstacles que je lui donne. Qu'il s'agisse de bouteilles, d'animaux ou des murs ajoutés, les capteurs de proximité indiquent des valeurs nulles alors même que l'obstacle se trouve face à lui.

#figure(
  image("/assets/image-30.png"),
  caption: "Thymio face à un obstacle (mur) qu'il ne détecte pas."
)

#figure(
  image("/assets/image-31.png"),
  caption: "Circuit de test avec obstacles sur la course"
)
== Réaliser un tour complet sans obstacles

Pour réaliser un tour complet sans obstacles, j'ai placé le robot dans le circuit et j'ai utilisé les touches de direction pour le guider dans les virages. Après un tour dans chaque sens, le robot a réussi à faire un tour complet de manière autonome, en ajustant sa trajectoire en fonction des entrées des capteurs et des virages.

La vidéo est dispobible dans `tour_complet_sans_obstacles.mp4`.

```
Poids W:
 [[0.095 -0.047 -0.21  0.     0.   ]
 [-0.195 -0.053  0.11  0.     0.   ]]

Biais B:
 [-0.05 -0.095]
```

= Conclusion

#hidden_heading[Conclusion]
#emphasis_text("Pour conclure, ")
#text(fill: color.rgb("444444"), weight: "bold")[
  


  On pourrait supposer que l'utilisation de capteurs plus précis comme le LiDAR ou la vision par caméra permettrait d'améliorer les performances du robot.

  De même que l'apprentissage supervisé, le réseau de neurone n'apprend pas à faire le tour du labyrinthe, mais plutôt à réagir à des situations spécifiques. Par exemple, il apprend à reculer face à un mur ou à tourner face à un obstacle, mais il ne développe pas une stratégie globale pour naviguer dans le labyrinthe. Il lui arrive de se retourner si un obstacle l'empêche de voir la bonne direction à prendre. De plus, la mauvaise perception des capteurs de Thymio selon le type d'obstacle (couleurs ou forme) empêche le réseau de percevoir les entrées réelles et donc d'avoir une sortie idéale pour la situation donnée.
  ]
  #v(40em)