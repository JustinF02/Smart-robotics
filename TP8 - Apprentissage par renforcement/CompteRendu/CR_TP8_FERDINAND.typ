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

Ce TP explore l'apprentissage non supervisé et supervisé (par démonstration) sur le robot Thymio en utilisant la règle de Hebb. L'objectif est de permettre au robot d'adapter son comportement en fonction des retours sensoriels et, dans un second temps, d'apprendre des comportements spécifiques guidés par un opérateur humain.

= Exercice 1 : Apprentissage Hebbien non supervisé

Dans ce premier exercice, j'ajoute une règle de Hebb sur le robot. Le robot modifie ses poids $W$ en fonction de la corrélation entre ses entrées de capteurs de proximité et ses sorties moteurs.

L'équation de mise à jour des poids est donnée par :
$ \u{0394} W_{"ij"} = \u{0391} \cdot y_i \cdot x_j $
où $\u{0391}$ est le taux d'apprentissage, $y_i$ l'activité du neurone moteur $i$, et $x_j$ l'entrée du capteur $j$.

Le code implémenté dans `model.py` est le suivant :

#codly(languages: ("python", ), header: "model.py")
```python
avec ALPHA = 0.01
# ∆W = Alpha * y * x.T
dW = ALPHA * np.outer(y, x)
W += dW
``` 


= Exercice 2 : Apprentissage supervisé par démonstration

Dans cette seconde partie, l'ajout d'un enseignement humain par clavier permet de guider le robot vers le bon comportement selon son environnement.
La sortie $y$ est imposée par l'opérateur. La règle de Hebb de la première partie va apprendre l'association entre les entrées et les sorties des moteurs.

Le script `reward.py` implémente cette logique :

#codly(languages: ("python", ), header: "Mode Enseignement")
```python
# Saisie clavier pour forcer le comportement
key = keyboard.getKey()
if key == Keyboard.UP:
    y = np.array([100.0, 100.0]) # Avancer
elif key == Keyboard.LEFT:
    y = np.array([-100.0, 100.0]) # Tourner Gauche
#reculer, droite

# Application de la règle de Hebb avec le y imposé
for j in range(5):
    # w_jl <- w_jl + alpha * y1 * xj
    W[0][j] = W[0][j] + ALPHA * y1 * x[j]
    W[1][j] = W[1][j] + ALPHA * y2 * x[j]
```

== Apprendre à reculer face à un mur

Protocole expérimental : saisir THymio, le placer face au mur et reculer avec la touche clavier.

Résultat et observation.

== Apprendre à éviter un obstacle

Avec une bouteille, la placer proche des capteurs d'un côté et controler le robot

Une fois les poids mis à jour, le robot devrait savoir à faire le tour du labyrinthe sans en avoir jamais fait un avant.
= Conclusion



#hidden_heading[Conclusion]
#emphasis_text("Pour conclure, ")
#text(fill: color.rgb("444444"), weight: "bold")[

  ]
  #v(40em)