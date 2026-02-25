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

Ce TP explore l'apprentissage non supervisé et supervisé (par démonstration) sur le robot Thymio en utilisant la règle de Hebb. L'objectif est de permettre au robot d'adapter son comportement en fonction des retours sensoriels et, dans un second temps, d'apprendre des comportements spécifiques guidés par un opérateur humain.

= Exercice 1 : Apprentissage Hebbien non supervisé

Dans ce premier exercice, j'ajoute une règle de Hebb sur le robot. Le robot modifie ses poids $W$ en fonction de la corrélation entre ses entrées de capteurs de proximité et ses sorties moteurs.

L'équation de mise à jour des poids est donnée par :
$ Delta W_"ij" = Delta dot y_i dot x_j $
où $Delta$ est le taux d'apprentissage, $y_i$ l'activité du neurone moteur $i$, et $x_j$ l'entrée du capteur $j$.

Le code implémenté dans `model.py` est le suivant :

#codly(header: [model.py])
```python
avec ALPHA = 0.01
# ∆W = Alpha * y * x.T
dW = ALPHA * np.outer(y, x)
W += dW
``` 


= Exercice 2 : Apprentissage supervisé par démonstration

Dans cette seconde partie, l'ajout d'un enseignement humain par clavier permet de guider le robot vers le bon comportement selon son environnement.
La sortie $y$ est imposée par l'opérateur. La règle de Hebb de la première partie va apprendre l'association entre les entrées et les sorties des moteurs.

Pour stabiliser le comportement, j'ai conservé la structure principale du script et importé trois améliorations :
- activation non linéaire de type Braitenberg ($tanh$),
- mise à jour Hebb déclenchée une seule fois par appui clavier,
- freinage automatique de la vitesse d'avance quand la proximité obstacle augmente.

Le script `reward.py` implémente cette logique :

#codly(header: [Mode Enseignement])
```python
# Saisie clavier pour forcer le comportement
key = keyboard.getKey()
if key == Keyboard.UP:
    y = np.array([100.0, 100.0]) # Avancer
elif key == Keyboard.LEFT:
    y = np.array([-100.0, 100.0]) # Tourner Gauche
#reculer, droite

# Application de la règle de Hebb avec le y imposé
# Front montant clavier: apprentissage une seule fois par appui
is_new_key_press = key_pressed and not prev_key_pressed
if is_new_key_press:
  hebb_update(x, y, W, B, ALPHA)
```

Le calcul en mode autonome est maintenant :

$ y_"model" = tanh(gamma , (W x + B)) $

$ y = [v_"base", v_"base"] + k * y_"model" $

avec :
- $v_"base" = V_0 * max(0, 1 - beta * max(x))$,
- $k$ un gain d'amplification du modèle,
- $gamma$ le gain de l'activation $tanh$.

Cette formulation évite que le robot reste bloqué contre un mur : quand les capteurs voient un obstacle, la vitesse d'avance est réduite, et la composante de rotation apprise par les poids devient dominante.

== Apprendre à reculer face à un mur

Protocole expérimental : saisir THymio, le placer face au mur et reculer avec la touche clavier.

Résultat et observation.

En réalisant cette expérience, j'ai observé que les poids associés aux capteurs de proximité avant ont augmenté, ce qui indique que le robot a appris à associer ces entrées à la sortie de reculer. Le biais appliqué à Thymui a diminué, ce qui lui donne un comportement de peur face à un obstacle. Avec quelques itérations, le robot recule seul face à un mur, même sans intervention.

Avec le déclenchement Hebb sur appui unique, l'apprentissage devient plus contrôlé : une action clavier correspond à un seul incrément de poids, ce qui évite les renforcements excessifs dus au maintien prolongé d'une touche.

== Apprendre à éviter un obstacle

La même expérience est réalisée, mais cette fois-ci en tournant à gauche ou à droite face à un obstacle.

Une fois les poids mis à jour, le robot devrait savoir à faire le tour du labyrinthe sans en avoir jamais fait un avant.

== Réaliser un tour complet



= Conclusion



#hidden_heading[Conclusion]
#emphasis_text("Pour conclure, ")
#text(fill: color.rgb("444444"), weight: "bold")[
  l'intégration d'une activation non linéaire, d'un apprentissage Hebbien événementiel (sur appui clavier) et d'un freinage lié aux capteurs améliore nettement la robustesse du contrôleur. Le robot n'avance plus aveuglément contre les obstacles et exploite mieux les poids appris pour produire des comportements d'évitement et de recul cohérents.
  ]
  #v(40em)