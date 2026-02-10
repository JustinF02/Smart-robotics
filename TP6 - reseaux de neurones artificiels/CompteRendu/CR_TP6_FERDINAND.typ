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

= Introduction



= Exercice d'application robotique

== Démarche suivie

Pour concevoir un réseau capable d'éviter des obstacles avec la contrainte de reculer si l'objet est détecté par les deux capteurs, je me suis inspiré du TP précèdent sur les perceptrons. L'objectif est que chaque capteur influe sur le moteur opposé pour provoquer un virage à l'opposé de l'obstacle.

L'implantation réalisée utilise des valeurs de capteurs normalisées entre 0 et 1. La fonction d'activation utilisée pour tous les neurones est une fonction de saturation limitant l'intervalle de sortie à $[-1, 1]$.

== Modèle proposé

Dans cette partie, j'utilise le modèle de réseau multicouche à deux couches illustré par la @premierReseau.

- Les neurones d'entrée $x_1$ et $x_2$ correspondent respectivement aux capteurs avant-gauche et avant-droit.
- La couche cachée ($h_1, h_2$) sert de relais pour les valeurs normalisées des capteurs.
- La couche de sortie ($y_1, y_2$) pilote les moteurs (gauche et droit). Elle combine un biais positif pour avancer et des poids négatifs croisés pour reculer ou éviter un obstacle.

#figure(
  image("/assets/image-5.png"),
  caption: [Modèle du réseau servant à l'évitement d'obstacles],
) <premierReseau>

== Poids du réseau

Les poids ont été déterminés logiquement pour satisfaire les conditions du comportement souhaité:

1. *Couche Entrée $->$ Cachée* (chaque capteur a le même poids) :
   $ w_{11} = 1.0, quad w_{12} = 1.0 $

2. *Couche Cachée $->$ Sortie* :
   $ w_{21} = 0.0, quad w_{24} = 0.0 $ (le capteur n'influence pas son propre capteur)
   $ w_{22} = -2.0 $ (Le capteur gauche $h_1$ influence le moteur droit $y_2$)
   $ w_{23} = -2.0 $ (Le capteur droit $h_2$ influence le moteur gauche $y_1$)

3. *Biais* :
   $ b = 1.0 $ (Injecté à la couche de sortie pour définir la vitesse par défaut)

== Observations lors de la validation expérimentale

Le comportement observé du robot lors des simulations montre que son réseau de neurones répond correctement à la configuration des murs du labyrinthe. THymio est capable d'avancer en ligne droite et de tourner lorsque des angles sont détectés. De plus, s'il arrive face à un mur, thymio s'arrête et recule tout en tournant légèrement pour reprendre la route. Durant la simulation, j'ai ajouté des logs montrant les sorties $y_1$ et $y_2$ du réseau. On peut ainsi voir ces valeurs à chaque instant, confirmant la réaction du réseau à la situation courante.

En modifiant $w_{21}$ et $w_{24}$ à 1, j'ai pu observer que le robot ne réagissait pas forcément moins aux obstacles malgrès le fait qu'un capteur influence son propre moteur. Cependant, la trajectoire de celui-ci était moins précise.
En revanche, en mettant ces deux poids à -1, j'ai pu obtenir l'effet recherché de laisser le robot tourner davantage sur lui-même pour éviter un obstacle. Ainsi, chaque capteur influençait également son moteur de manière opposée pour renforcer l'évitement. Cela se voit en simulation lorsque les deux valeurs de y varient.

Pour éviter certains obstacles, j'ai dû utiliser les capteurs latéraux plus éloignés. Il arrivait régulièrement que les capteurs avant gauche et avant droit ne détectent plus l'obstacle.

Le code et la vidéo de la simulation sont disponibles dans le dossier Partie 1 du TP6.

= Mémoire - réseaux récurrents

Dans cette seconde partie, le tp aborde l'implémentation de réseaux récurrents. L'intérêt principal est d'introduire une dépendance temporelle : la sortie du réseau ne dépend plus uniquement de l'instantané des capteurs à l'instant $t$, mais aussi de l'état précédent du système (mémoire à $t-1$). Cela permettra de garder en mémoire la détection d'un obstacle et de corriger le problème de perte d'information rencontré dans la partie précèdente.

== Implantation proposée

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

Mettre un poids réduit sur la mémoire ($w_4 = w_5 = 0.5$) permet de limiter l'effet d'inertie tout en réalisant un lissage sur la commande.


= JUSTIN, TOUTE LA PARTIE EN DESSOUS EST SUREMENT A REVOIR
#colbreak()
= Filtre spatial

== Exercice d'application sur Webots

== Problématique
Le robot devait respecter deux contraintes comportementales contradictoires avec une architecture de Braitenberg :
1.  *Attraction* vers un objet isolé (le robot doit se tourner vers lui).
2.  *Arrêt* face à un mur (le robot ne doit pas avancer).

== Historique des modifications

=== 1. Correction de l'Attraction (Filtre Spatial)
Initialement, le robot manifestait un comportement de peur (répulsion) face aux objets.

*Analyse :* Le filtre spatial (Couche 1) génère des valeurs négatives (inhibition latérale) autour de l'objet détecté pour accentuer le contraste. Ces valeurs négatives, propagées telles quelles aux moteurs, inversaient le sens de rotation attendu.

*Solution :* Nous avons appliqué une fonction de rectification de type *ReLU* (`np.maximum(Y_spatial, 0)`) en sortie du filtre spatial.

*Justification :* Cela permet de ne conserver que les pics d'activation (la présence de l'objet) pour piloter l'attraction, tout en ignorant les zones d'inhibition qui causaient la répulsion.

=== 2. Gestion de l'Arrêt face au Mur (Le "Nouveau Lien")
Une fois l'attraction réglée, le robot avançait vers le mur au lieu de s'arrêter.
*Analyse :* Face à un mur, les capteurs gauche et droit sont activés simultanément. Dans une architecture "Attraction" classique (connexions croisées positives), l'œil gauche active la roue droite et l'œil droit active la roue gauche. Résultat : les deux roues tournent vers l'avant, le robot percute le mur.

*Solution : Ajout d'un lien d'inhibition ipsilatéral (`w_same`)*
Nous avons ajouté une connexion directe avec un poids négatif entre le capteur et le moteur du même côté (ex: Capteur Gauche $->$ Moteur Gauche).

*Justification mathématique :*
L'équation de commande d'un moteur devient :
$ V_"moteur" = w_"cross" dot H_"opposé" + w_"same" dot H_"côté" $

Cette modification permet de discriminer les deux situations :

- *Cas Objet (ex: à Gauche uniquement) :*
  - Moteur Droit : Reçoit le signal croisé ($w_"cross" > 0$) $->$ Avance.
  - Moteur Gauche : Reçoit l'inhibition directe ($w_"same" < 0$) $->$ Freine/Recule.
  - *Résultat :* Le différentiel de vitesse est maximisé, le robot pivote très vite vers l'objet.

- *Cas Mur (Gauche + Droite actifs) :*
  - Chaque moteur reçoit à la fois l'excitation croisée et l'inhibition directe.
  - Avec nos réglages ($w_"cross" = 1.0, w_"same" = -2.0$), la somme est négative.
  - *Résultat :* Les moteurs se bloquent (ou reculent légèrement), assurant l'arrêt face au mur.




#colbreak()
= Conclusion


#hidden_heading[Conclusion]
#emphasis_text("Pour conclure, ")
#text(fill: color.rgb("444444"), weight: "bold")[
  
  ]
  #v(40em)