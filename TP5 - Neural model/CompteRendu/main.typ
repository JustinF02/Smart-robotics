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
Ce TP a pour objectif de découvrir le fonctionnement du perceptron, un modèle de neurone artificiel simple, et d’en comprendre les applications à travers des exemples théoriques (modélisation d’opérateurs logiques) puis pratiques (contrôle d’un robot Thymio).

= Perceptron : implantation d’une porte logique

== Définition des variables d’entrée

Les variables d’entrée du perceptron, $x_1$ et $x_2$, prennent les valeurs 0 ou 1.

== Fonction de calcul de la somme pondérée

La sortie du perceptron est déterminée par la somme pondérée suivante :

$s = w_0 + x_1 \cdot w_1 + x_2 \cdot w_2$

où $w_0$ est le biais, $w_1$ et $w_2$ les poids associés aux entrées.

== Fonction d’activation

La fonction d’activation utilisée est une fonction seuil :


$y =$
- 1 si $s \geq 0$,
- 0 si $s < 0$,

== Validation sur les opérateurs logiques

On teste le perceptron pour modéliser les fonctions logiques OU (OR) et ET (AND) à l’aide de tables de vérité et de choix appropriés des poids.

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

= Exercice d’application

Dans cette partie, j'ai repris le TP1 réalisé sur les capteurs infrarouge du robot Thymio.

Le modèle de navigation prend les valeurs de ces capteurs en entrée.

== Principe de l'algorithme

Le robot utilise ses capteurs avant (gauche, centre, droite) pour détecter les obstacles et décide de tourner ou d’avancer selon la sortie du perceptron :

- Si obstacle devant, il tourne sur lui-même.
- Si obstacle à gauche, il tourne à droite.
- Si obstacle à droite, il tourne à gauche.
- Sinon, il avance.

De plus, si les deux capteurs arrière détectent un obstacle, le robot avance pour éviter de rester bloqué. Les rayons infrarouges de Thymio sont visibles sur la figure @capteursIR.

#figure(
  image("/img/photo_robot.png"),
  caption: [Capture d'écran du robot Thymio avec les capteurs infrarouge],
) <capteursIR>

== Extrait de code (simplifié)

```python
#binarisation des entrées
x_left = 1 if left > THRESHOLD else 0
x_center = 1 if center > THRESHOLD else 0
x_right = 1 if right > THRESHOLD else 0
x_back_left = 1 if back_left > THRESHOLD else 0
x_back_right = 1 if back_right > THRESHOLD else 0

#perceptron ET arrière : avancer si obstacle détecté par les deux capteurs arrière
y_back = 1 if (x_back_left == 1 and x_back_right == 1) else 0

if y_back == 1:
  #avancer si obstacle derrière
  motor_left.setVelocity(FORWARD_SPEED)
  motor_right.setVelocity(FORWARD_SPEED)
else:
  #navigation avant avec perceptron
  action = perceptron_3inputs(x_left, x_center, x_right, w0, w_left, w_center, w_right)
  if action == 0:
    motor_left.setVelocity(FORWARD_SPEED)
    motor_right.setVelocity(FORWARD_SPEED)
  elif action == -1:
    motor_left.setVelocity(0.0)
    motor_right.setVelocity(TURN_SPEED)
  elif action == 1:
    motor_left.setVelocity(TURN_SPEED)
    motor_right.setVelocity(0.0)
```

Ce code permet au robot de naviguer de façon réactive et autonome, en s’appuyant sur un perceptron pour la prise de décision à partir des capteurs. Je remarque que la navigation reste naïve car le robot peut se retrouver face à un mur et tourner dans le mauvais sens.

Cela s'explique par le fait que l'activation du capteur central seul emploie le poids fort $"w_center" = 2$, donnant une sortie activée = 1, ce qui fait tourner le robot à gauche. Si le robot se retrouve face à un mur, il tournera toujours à gauche, restant bloqué.


#colbreak()
= Conclusion


#hidden_heading[Conclusion]
#emphasis_text("Pour conclure,")
#text(fill: color.rgb("444444"), weight: "bold")[Ce TP 
  ]
  #v(40em)