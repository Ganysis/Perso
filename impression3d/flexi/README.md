# Collection « Flexi Kawaii »

![collection](sorties/collection.png)

Animaux articulés imprimés d'une seule pièce (print-in-place), sans support,
en 4 couleurs AMS. **Un seul moteur de style** pour toute la gamme : même
grosse tête chibi, mêmes grands yeux brillants, mêmes joues roses, même
bouche « ω », mêmes articulations, même taille. Chaque animal ne décrit que
sa tête, ses oreilles, sa queue et ses couleurs.

## Gamme actuelle

| Modèle | Formats | Palettes | Tenues |
|---|---|---|---|
| Chat | mini (~8 cm), porte-clés (~5,5 cm) | roux, calico, gris, tigre | nœud, collier |
| Renard | mini, porte-clés | roux, arctique | nœud, collier |

- **mini** : ~78 × 41 × 22 mm, ~21 g de PLA, queue enroulée à plat.
- **porte-clés** : ~54 × 21 × 14 mm, ~5 g, anneau au bout de la queue.

Le détail de chaque modèle (dimensions, poids, amplitude des articulations,
contrôles) est dans `sorties/rapport.json`.

## Imprimer

Dans `sorties/<animal>_<format>[_<tenue>]/<palette>/` :
`1_<couleur>.stl` … `4_<couleur>.stl` + `apercu.png`.

**Bambu Studio / OrcaSlicer + AMS**
1. Glisser **tous les STL du dossier de la palette en même temps**.
2. « Charger comme un seul objet à plusieurs pièces ? » → **Oui**.
3. Attribuer un filament à chaque pièce, trancher.

**Sans AMS** : `monocolore.stl` (dans le dossier du modèle).

| Réglage | Valeur |
|---|---|
| Buse | 0,4 mm |
| Couches | **0,2 mm** (jeux verticaux 0,5 mm) |
| Supports | **aucun** |
| Remplissage | 15 % |
| Bordure (brim) | **non** (souderait les segments) |
| Matériau | PLA |

Première couche bien réglée (trop écrasée = segments soudés). Après
impression, plier chaque articulation à gauche puis à droite pour la libérer.
**Ne pas mettre à l'échelle dans le slicer** : les jeux changeraient ;
les tailles se règlent dans `moteur.py` (`FORMATS`).

## Générer

```bash
pip install manifold3d trimesh numpy scipy scikit-image pillow
python3 generer.py                    # toute la collection (~15 min)
python3 generer.py chat porte-cles    # un animal / un format
```

Chaque modèle est vérifié automatiquement ; `generer.py` échoue si un
contrôle ne passe pas :
- chaque segment d'un seul tenant, segments tous séparés ;
- jeu ≥ 0,3 mm dans toutes les directions entre segments voisins ;
- amplitude de chaque articulation ≥ 16° (en pratique 28 à 32°) ;
- surplombs > 50° hors articulations ;
- STL étanches. Si un détail de couleur trop petit crée un défaut de
  maillage, il est retiré de ce modèle et listé dans `details_retires`
  (ex. intérieur des oreilles du porte-clés calico).

## Ajouter un animal (≈ une journée)

Dans `animaux.py`, créer une sous-classe de `Animal` :

```python
class Lapin(Animal):
    nom = "lapin"
    ear = ((6.0, 6.0, 22.0), (4.0, 9.0, 42.0), 4.5, 2.5)   # base, pointe, rayons
    tail_tip = 1.6                                         # queue pompon
    palettes = {"blanc": {"filaments": {...}, "elements": {...}}}

    def extra_parts(self, geo, X, Y, Z):   # formes en plus (museau, joues...)
        return []

    def regions(self, geo):                # zones de couleur en plus
        return super().regions(geo)
```

puis l'ajouter à `ANIMAUX` et à `COLLECTION` (dans `generer.py`).

Réglages disponibles : `head_c`, `head_r` (tête), `ear` (oreilles),
`body_ry` (largeur du corps), `muzzle_w/h` (museau), `tail_tip`,
`tail_bulge` (queue touffue), et les méthodes `head_parts`, `extra_parts`,
`regions`.

**Éléments de couleur** (du plus prioritaire au moins prioritaire) :
reflets, yeux, bouche, nez, joues, oreilles_int, accessoire, bout_oreilles,
museau, taches_noir, taches_couleur, rayures, chaussettes, bout_queue.
Une palette associe chaque élément à l'un de ses 4 filaments ; les éléments
non cités prennent la couleur du corps.

## Tenues

Une tenue = une forme en plus (optionnelle) + une zone « accessoire » :
- `noeud` : nœud en relief sur la tête ;
- `collier` : bande de couleur autour du cou.

Pour en ajouter une (foulard, chapeau, lunettes…) : l'ajouter dans
`Animal.head_parts` (forme) et `Animal.regions` (couleur). Elle est alors
disponible pour **tous** les animaux.

## Principe technique

- Forme : fonction de distance signée (ellipsoïdes, cônes arrondis, profil
  balayé pour la queue, fusions douces), maillée par marching cubes.
- Découpe en segments par encoches en V ; articulation = languette pincée
  entre deux plaques, deux tétons coniques à 45° comme pivot.
- Couleurs : coque de 0,8 mm sous la surface, intersectée avec les zones.
