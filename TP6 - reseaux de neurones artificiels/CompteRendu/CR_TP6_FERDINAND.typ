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
  title: [_C3 - Intelligence pour la robotique_: TP6 -- Topologies des réseaux de neurones artificiels],
  title_size: 21pt,
  authors_flat: (
    (name:"Justin Ferdinand"),
  ),
  header_content: (
    left: [*SETI C3 - Intelligence pour la robotique* TP6 -- Topologies des réseaux de neurones artificiels],
  ),
  page_numbering: "1/1",
  heading_numbering: "I.A.1",
  column_count: 2,
)

= Les topologies multicouches

== Exercice 1 : Étude d'un perceptron simple

=== Question 1 : Influence d'un poids unique

L'objectif de cette première question est d'observer l'effet d'un poids $w_1 = -0.5$ sur la sortie d'un neurone avec fonction d'activation de saturation entre -1 et 1.

Pour une entrée $x_1 in [-2.0, 2.0]$ avec un pas de 0.2, la sortie est calculée par :
$ y_1 = "sat"(w_1 dot x_1) $

où $"sat"(x) = "clip"(x, -1, 1)$.

#figure(
  image("/assets/image-23.png"),
  caption: [Sortie y1 en fonction de l'entrée x1 avec $w_1 = -0.5$],
) <ex1q1>



*Observations* : La @ex1q1 montre une relation linéaire dans la zone non saturée. Le poids négatif inverse la relation entrée-sortie. Les bornes de saturation (-1 et 1) sont atteintes pour des valeurs d'entrée éloignées de zéro.

=== Question 2 : Variation des poids

Cette question explore l'influence de 15 valeurs de poids différentes dans l'intervalle $[-1.0, 1.0]$ sur la même entrée.

#figure(
  image("/assets/image-24.png"),
  caption: [Influence du poids $w_1$ sur la sortie],
) <ex1q2>

La @ex1q2 illustre plusieurs comportements :
- Dans les zones non saturées, la relation est linéaire : $y = w dot x$
- La pente de la fonction dépend directement de la valeur absolue du poids
- Le signe du poids détermine le sens de la relation (positive ou négative)
- Plus $|w|$ est grand, plus rapidement la saturation est atteinte

=== Question 3 : Réseau multicouche à deux couches

#figure(
    image("/assets/image-28.png"),
    caption: [Architecture du réseau à deux couches étudié],
) <ex1q3archi>
Cette question introduit un réseau à deux couches avec deux neurones cachés. L'architecture visible sur la @ex1q3archi est la suivante :
- *Couche cachée* : deux neurones recevant la même entrée $x_1$
- *Couche de sortie* : un neurone combinant les sorties des neurones cachés

Les poids utilisés sont :
$ w_{11} = 1.0, quad w_{12} = 0.5 quad "(entrée → cachée)" $
$ w_{21} = 3.0, quad w_{22} = -1.0 quad "(cachée → sortie)" $

Les équations sont :
#[
  #set math.equation(numbering: none)
  $ h_1 = "sat"(w_{11} dot x_1) $
  $ h_2 = "sat"(w_{12} dot x_1) $
  $ y = "sat"(w_{21} dot h_1 + w_{22} dot h_2) $
]

#figure(
  image("/assets/image-26.png"),
  caption: [Sortie du réseau à deux couches],
) <ex1q3>

La @ex1q3 montre une fonction non-linéaire plus complexe que les sorties individuelles des neurones. La sortie finale n'est pas monotone :
- Pour $x < -1$ : le premier neurone sature à -1, le second est dans sa zone linéaire. La sortie est dominée par le second neurone.
- Pour $-1 <= x <= 1$ : les deux neurones sont dans leur zone linéaire. La combinaison est une somme pondérée de fonctions linéaires.
- Pour $x > 1$ : le premier neurone sature à 1. La sortie devient la différence entre une constante et la fonction du second neurone.

En augmentant $w_{21}$ à 3.0 (voir @ex1q3variant), l'influence du premier neurone est amplifiée, créant une pente plus raide dans les zones où il est actif.

#figure(
  image("/assets/image-25.png"),
  caption: [Sortie du réseau avec $w_{21} = 3.0$ (influence amplifiée)],
) <ex1q3variant>

*Conclusion* : Les réseaux multicouches permettent de créer des fonctions complexes et non-monotones à partir de combinaisons de fonctions simples (linéarité + saturation). La variation des poids modifie l'influence relative de chaque neurone sur la sortie globale.

== Exercice d'application robotique

=== Démarche suivie

Pour concevoir un réseau capable d'éviter des obstacles avec la contrainte de reculer si l'objet est détecté par les deux capteurs, je me suis inspiré du TP précèdent sur les perceptrons. L'objectif est que chaque capteur influe sur le moteur opposé pour provoquer un virage à l'opposé de l'obstacle.

L'implantation réalisée utilise des valeurs de capteurs normalisées entre 0 et 1. La fonction d'activation utilisée pour tous les neurones est une fonction de saturation limitant l'intervalle de sortie à $[-1, 1]$.

=== Modèle proposé

Dans cette partie, j'utilise le modèle de réseau multicouche à deux couches illustré par la @premierReseau.

- Les neurones d'entrée $x_1$ et $x_2$ correspondent respectivement aux capteurs avant-gauche et avant-droit.
- La couche cachée ($h_1, h_2$) sert de relais pour les valeurs normalisées des capteurs.
- La couche de sortie ($y_1, y_2$) pilote les moteurs (gauche et droit). Elle combine un biais positif pour avancer et des poids négatifs croisés pour reculer ou éviter un obstacle.

#figure(
  image("/assets/image-5.png"),
  caption: [Modèle du réseau servant à l'évitement d'obstacles],
) <premierReseau>

=== Poids du réseau

Les poids ont été déterminés logiquement pour satisfaire les conditions du comportement souhaité:

1. *Couche Entrée $->$ Cachée* (chaque capteur a le même poids) :
   $ w_{11} = 1.0, quad w_{12} = 1.0 $

2. *Couche Cachée $->$ Sortie* :
   $ w_{21} = 0.0, quad w_{24} = 0.0 $ (le capteur n'influence pas son propre capteur)
   $ w_{22} = -2.0 $ (Le capteur gauche $h_1$ influence le moteur droit $y_2$)
   $ w_{23} = -2.0 $ (Le capteur droit $h_2$ influence le moteur gauche $y_1$)

3. *Biais* :
   $ b = 1.0 $ (Injecté à la couche de sortie pour définir la vitesse par défaut)

=== Observations lors de la validation expérimentale

Le comportement observé du robot lors des simulations montre que son réseau de neurones répond correctement à la configuration des murs du labyrinthe. Thymio est capable d'avancer en ligne droite et de tourner lorsque des angles sont détectés. De plus, s'il arrive face à un mur, thymio s'arrête et recule tout en tournant légèrement pour reprendre la route. Durant la simulation, j'ai ajouté des logs montrant les sorties $y_1$ et $y_2$ du réseau. On peut ainsi voir ces valeurs à chaque instant, confirmant la réaction du réseau à la situation courante.

En modifiant $w_{21}$ et $w_{24}$ à 1, j'ai pu observer que le robot ne réagissait pas forcément moins aux obstacles malgrès le fait qu'un capteur influence son propre moteur. Cependant, la trajectoire de celui-ci était moins précise.
En revanche, en mettant ces deux poids à -1, j'ai pu obtenir l'effet recherché de laisser le robot tourner davantage sur lui-même pour éviter un obstacle. Ainsi, chaque capteur influençait également son moteur de manière opposée pour renforcer l'évitement. Cela se voit en simulation lorsque les deux valeurs de y varient.

Pour éviter certains obstacles, j'ai dû utiliser les capteurs latéraux plus éloignés. Il arrivait régulièrement que les capteurs avant gauche et avant droit ne détectent plus l'obstacle.

Le code et la vidéo de la simulation sont disponibles dans le dossier Partie 1 du TP6.

= Mémoire - réseaux récurrents

Dans cette seconde partie, le tp aborde l'implémentation de réseaux récurrents. L'intérêt principal est d'introduire une dépendance temporelle : la sortie du réseau ne dépend plus uniquement de l'instantané des capteurs à l'instant $t$, mais aussi de l'état précédent du système (mémoire à $t-1$). Cela permettra de garder en mémoire la détection d'un obstacle et de corriger le problème de perte d'information rencontré dans la partie précèdente.

== Exercice 2 : Réseau récurrent simple

=== Principe et modèle

L'objectif de cet exercice est d'observer l'effet d'une connexion récurrente sur le comportement temporel d'un neurone. Le modèle utilisé est le suivant :

#[
  #set math.equation(numbering: none)
  $ y(t) = "sat"(w_"in" dot x(t) + w_"rec" dot y(t-1)) $
]

où :
- $x(t)$ est l'entrée au temps $t$
- $y(t)$ est la sortie au temps $t$
- $y(t-1)$ est la sortie au temps précédent (mémoire)
- $w_"in"$ est le poids de l'entrée (fixé à 0.5)
- $w_"rec"$ est le poids récurrent
- $"sat"(x) = "clip"(x, 0, 1)$ est la fonction de saturation

L'entrée est un signal échelon qui s'active à $t = 5$ avec une valeur de 0.3.

=== Cas testés

Deux configurations ont été testées pour observer différents comportements de mémoire :

*Cas (a) : Poids récurrent > 1* ($w_"rec" = 1.2$)
- La rétroaction amplifie le signal à chaque itération
- Comportement de mémorisation forte
- Le neurone tend à rester actif une fois activé

*Cas (b) : Poids récurrent dans [0, 1]* ($w_"rec" = 0.8$)
- Le système se stabilise à une valeur d'équilibre
- Comportement de filtre passe-bas ou de mémoire à court terme
- Le système "oublie" progressivement l'historique

#figure(
  image("/assets/image-27.png"),
  caption: [Comportement du neurone récurrent selon le poids $w_"rec"$],
) <ex2recurrent>

*Conclusion* : Le poids récurrent contrôle la persistance de la mémoire. Un poids > 1 crée une mémoire permanente (instable), tandis qu'un poids < 1 crée une mémoire qui s'estompe progressivement (stable). Ce mécanisme est fondamental pour créer des comportements temporels dans les réseaux de neurones.

== Exercice d'application robotique

=== Implantation proposée

Le modèle utilisé est un réseau monocouche avec connexions récurrentes. Il prend en entrée les capteurs (Gauche, Avant, Droit) et contrôle les deux moteurs.

Les équations d'activation choisies sont :

#[
  #set math.equation(numbering: none)
  $ y_1(t) = (w_{11} x_L + w_{21} x_F + w_{31} x_R \ 
              + w_4 y_1(t-1) + b) $
  $ y_2(t) = (w_{12} x_L + w_{22} x_F + w_{32} x_R \
              + w_5 y_2(t-1) + b) $
]

où b est le biais de marche avant et les poids $w$ ceux présents sur la @deuxiemeReseau

Les sorties $y_1$ (gauche) et $y_2$ (droit) sont réinjectées à l'entrée avec les poids $w_4$ et $w_5$. 

#figure(
  image("/assets/image-7.png"),
  caption: [Modèle de réseau récurrent implémenté],
) <deuxiemeReseau>

== Mise en œuvre

Pour tester l'effet de la mémoire, j'ai modifié le parcours de simulation pour inclure une section plus large avec un obstacle central. Cela permet d'observer comment le robot réagit lorsqu'il perd temporairement la détection de l'obstacle. Le nouveau parcours est visible sur la @parcoursSimu.

J'ai utilisé plusieurs configurations de poids récurrents pour observer différents comportements de mémoire. J'ai ainsi testé des valeurs de $w_4$ et $w_5$ à 0.5, 1.0 et 1.5 pour voir comment cela affecte la persistance de l'activation.

#figure(
  image("/assets/image-11.png"),
  caption: [Parcours de simulation utilisé pour observer les effets de mémoire],
) <parcoursSimu>

== Résultats obtenus

Les résultats suivants montrent la commande de la sortie y2 obtenue avec différentes valeurs de poids récurrents.

Sur la figure @NoMemory, on observe que sans mémoire, la sortie $y_2$ retourne rapidement à 1.0 dès que le capteur ne détecte plus l'obstacle, ce qui peut entraîner une perte de contrôle et une trajectoire erratique.

#figure(
  image("/assets/image-17.png"),
  caption: [Sortie sans mémoire],
) <NoMemory>

#figure(
  image("/assets/image-20.png"),
  caption: [Effet d'une mémoire avec $w_4 = w_5 = 1.5$],
) <RecurrentMemory1.5>

#figure(
  image("/assets/image-19.png"),
  caption: [Effet d'une mémoire avec $w_4 = w_5 = 1.0$],
) <RecurrentMemory1.0>
#figure(
  image("/assets/image-18.png"),
  caption: [Effet d'une mémoire avec $w_4 = w_5 = 0.5$],
) <RecurrentMemory0.5>

Sur les @RecurrentMemory1.5, @RecurrentMemory1.0 et @RecurrentMemory0.5, on observe que l'introduction de la mémoire permet à la sortie $y_2$ de rester activée plus longtemps même lorsque le capteur ne détecte plus l'obstacle. En revanche, l'introduction de la mémoire entraîne un effet oscillant dans la sortie y2, apparanté au lag donné par la mémoire. Cette inertie donne un comportement moins vif et persistant.

Mettre un poids fort peut entraîner une persistance excessive, rendant thymio moins réactif à un nouvel obstacle. Le neurone reste activé trop longtemps.

Mettre un poids réduit sur la mémoire ($w_4 = w_5 = 0.5$) permet de limiter l'effet d'inertie tout en réalisant un lissage sur la commande. D'après les observations que j'ai pu faire, ($w_4 = w_5 = 0.2$) semble être un bon compromis pour garder une bonne réactivité et une mémoire.

= Filtre spatial

== Principe et objectif

Le filtre spatial permet de détecter des contrastes spatiaux dans les données des capteurs. L'objectif est de distinguer un objet ponctuel d'un mur en analysant la distribution spatiale des activations. Le réseau utilise un mécanisme d'influence latérale : chaque neurone amplifie l'activation du capteur qui lui correspond tout en influençant les activations des capteurs voisins.

== Architecture du réseau testé

Le réseau implémenté suit la topologie de la Figure 6 du sujet. Il comporte :
- *5 neurones d'entrée* ($x_1$ à $x_5$) : capteurs de proximité avant du robot
- *5 neurones de sortie* ($y_1$ à $y_5$) : chacun détecte un pic spatial à une position donnée

Les équations d'activation pour chaque neurone de sortie sont :

#[
  #set math.equation(numbering: none)
  $ y_1 = "sat"(4 x_1 - 4 x_2) $
  $ y_2 = "sat"(4 x_2 - 2 x_1 - 2 x_3) $
  $ y_3 = "sat"(4 x_3 - 2 x_2 - 2 x_4) $
  $ y_4 = "sat"(4 x_4 - 2 x_3 - 2 x_5) $
  $ y_5 = "sat"(4 x_5 - 4 x_4) $
]

où $"sat"(x) = "clip"(x, 0, 1)$ est la fonction de saturation.

Les poids positifs (+4) amplifient le signal du capteur principal, tandis que les poids négatifs (-2 ou -4) inhibent les capteurs voisins. Les neurones de bord ($y_1$ et $y_5$) ont une influence plus forte (-4) car ils n'ont qu'un seul voisin.

== Cas d'usage testés

Plusieurs configurations d'entrée ont été testées pour valider le comportement du filtre :

1. *Objet ponctuel central* : $x = [0, 0, 1, 0, 0]$
   - Seul le capteur central détecte l'objet

2. *Mur en biais* : $x = [1.4, 1.2, 1.0, 0.8, 0.6]$
   - Tous les capteurs détectent un obstacle à distances variables

3. *Obstacle étendu central* : $x = [0, 1, 1, 1, 0]$
   - L'objet est détecté sur trois capteurs centraux

4. *Obstacle latéral gauche* : $x = [2.0, 1.5, 1.0, 0, 0]$
   - L'objet est plus proche du côté gauche

#figure(
  image("/assets/image-21.png"),
  caption: [Résultats du filtre spatial sur différentes configurations d'obstacles],
) <resultatFiltreSpatial>

== Résultats et analyse

Les résultats obtenus, illustrés par la @resultatFiltreSpatial, montrent que le filtre spatial remplit correctement son rôle :

- *Objet ponctuel* : La sortie $y_3$ (neurone central) est maximale (~1.0), les autres sorties sont nulles. Le contraste spatial est parfaitement détecté.

- *Mur en biais* : Le neurone correspondant au point le plus proche ($y_1$) présente une activation significative. Les gradients de distance créent un pic spatial localisé.

- *Obstacle étendu* : Plusieurs neurones centraux ($y_2$, $y_3$, $y_4$) s'activent, indiquant une zone de détection large. L'absence d'activation sur les bords signale que ce n'est pas un mur complet.

- *Obstacle latéral* : Les neurones du côté correspondant ($y_1$, $y_2$) s'activent fortement, permettant au robot d'identifier la direction de l'objet.

*Point important* : Dans le cas d'un mur parfaitement frontal où tous les capteurs détectent à la même distance ($x = [1, 1, 1, 1, 1]$), les poids négatifs des voisins compensent exactement les poids positifs centraux. Le résultat est une sortie nulle ou très faible sur tous les neurones, ce qui permet de distinguer un mur d'un objet.

Cette propriété d'influence latérale permet donc au réseau de détecter automatiquement les contrastes spatiaux sans utiliser de règles conditionnelles explicites.

Le code et les analyses de cette partie sont disponibles dans le notebook du TP6.

== Exercice d'application sur Webots

Le robot doit respecter deux contraintes comportementales contradictoires avec une architecture de Braitenberg :
1.  *Attraction* vers un objet isolé (le robot doit se tourner vers lui).
2.  *Arrêt* face à un mur (le robot ne doit pas avancer).

=== 1. Gestion de l'Attraction

Pour gérer l'attraction vers un objet, j'ai utilisé le même filtre spatial que dans la partie précédente. Cependant, j'ai rencontré un problème : le robot était attiré vers l'objet mais aussi repoussé par les zones d'influence latérales générées par le filtre spatial.

En implémentant la topologie visible sur la @topologieAttraction, j'ai constaté que les valeurs négatives générées par le filtre spatial pour les capteurs voisins étaient propagées aux moteurs, ce qui inversait le sens de rotation attendu et provoquait une répulsion.

J'ai ainsi ajouté ces poids suivants pour les connexions du filtre spatial vers les moteurs :

```python
w_cote = 2.0
w_cote_ext = 2.0

w_front = 1.0
w_cross = 1.0
```
#figure(
  image("/assets/image-22.png"),
  caption: [Topologie du réseau utilisé],
) <topologieAttraction>

Cette topologie permet de gérer l'attraction vers un objet, en prenant en compte les influences latérales.

L'attraction vers l'objet est visible sur la vidéo de la simulation disponible dans le dossier Partie 3 du TP6.

=== 2. Gestion de l'Arrêt face au Mur

Une fois l'attraction réglée, le robot avançait vers le mur au lieu de s'arrêter. Le comportement est à réadapter pour que le robot puisse différencer un objet du mur. Les poids précèdemment utilisés pour l'attraction devraient fonctionner mais j'ai remarqué des valeurs abérantes dans les entrées des capteurs latéraux. En effet, après la remarque d'un camarade, je n'avais pas pris en compte le fait que les capteurs latéraux étaient en arc de cercle. Il faut donc appliqué un poids plus fort pour ceux-ci ou de compenser les poids du filtre spatial.

Les nouvelles valeurs de ces points sont les suivantes :
```python
W_spatial = np.array([
        [6.6, -4.0, 0.0, 0.0, 0.0],      # y1 : détecteur extrême gauche
        [-3.2, 4.0, -2.0, 0.0, 0.0],     # y2 : détecteur gauche
        [0.0, -2.0, 4.0, -2.0, 0.0],     # y3 : détecteur centre
        [0.0, 0.0, -2.0, 4.0, -3.2],     # y4 : détecteur droite
        [0.0, 0.0, 0.0, -4.0, 6.6]       # y5 : détecteur extrême droite
    ])
```

Le rapport de valeur entre les capteurs latéraux et gauche/droite face au mur est d'environ 1.66. 

Cette configuration devrait permettre au robot de s'arrêter face au mur mais un bug provoqué dans webot retourne une valeur nulle au capteur central lorsque le robot est face à un mur, ce qui empêche le comportement d'arrêt de se déclencher. J'ai essayé de compenser ce problème en augmentant les poids des capteurs latéraux mais cela n'a pas permis de régler le problème.

Ce comportement est visible sur la vidéo de la simulation disponible dans le dossier Partie 3 du TP6.

= Conclusion


#hidden_heading[Conclusion]
#emphasis_text("Pour conclure, ")
#text(fill: color.rgb("444444"), weight: "bold")[
  ce TP m'a permis de mieux comprendre les différentes topologies de réseaux de neurones artificiels et leur application à la robotique. J'ai pu expérimenter avec des architectures multicouches, récurrentes et des filtres spatiaux pour résoudre des problèmes d'évitement d'obstacles et de détection de contrastes spatiaux. J'ai également constaté l'importance de la configuration des poids et de la topologie du réseau pour obtenir le comportement souhaité. 
  ]
  #v(40em)