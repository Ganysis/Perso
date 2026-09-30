# Chat kawaii articulé (flexi, print-in-place, AMS)

![aperçu](apercu.png)

Chat sculpté en volume (13 × 3,8 × 3,3 cm), 8 segments imprimés déjà
emboîtés : tête, pattes avant, ventre, pattes arrière, 4 segments de queue.
Chaque articulation pivote de ±26 à 30°. Aucun support, aucun assemblage.

## Fichiers

| Fichier | Usage |
|---|---|
| `chat_orange.stl` | corps (couleur principale) |
| `chat_blanc.stl` | museau, reflets des yeux, chaussettes, bout de queue |
| `chat_noir.stl` | yeux, bouche |
| `chat_rose.stl` | nez, joues, intérieur des oreilles |
| `chat_monocolore.stl` | version une seule couleur (sans AMS) |

Les couleurs sont incrustées sur 0,8 mm sous la surface : elles
s'emboîtent exactement dans le corps (même repère, aucun chevauchement).

## Impression multicolore (Bambu Studio / OrcaSlicer + AMS)

1. Glisser **les 4 fichiers `chat_orange/blanc/noir/rose.stl` en même temps**
   dans le logiciel.
2. À la question « Charger ces fichiers comme un seul objet à plusieurs
   pièces ? », répondre **Oui**.
3. Dans la liste des objets, attribuer un filament à chaque pièce.
4. Ne pas redimensionner (voir plus bas), trancher, imprimer.

## Réglages conseillés

| Réglage | Valeur |
|---|---|
| Buse | 0,4 mm |
| Hauteur de couche | **0,2 mm** (jeux verticaux de 0,5 mm) |
| Supports | **aucun** |
| Remplissage | 15 % |
| Parois | 2 à 3 |
| Matériau | PLA |
| Bordure (brim) | non : elle souderait les segments entre eux |

Première couche bien réglée : trop écrasée, elle peut souder les segments
par le bas. **Après impression**, plier doucement chaque articulation à
gauche puis à droite pour la libérer.

**Ne pas mettre à l'échelle dans le slicer** : les jeux (0,4 mm) seraient
modifiés. Pour changer la taille ou la forme, modifier les constantes de
`chat_flexi.py` (`HEAD_R`, `BODY_R`, `JOINTS`…) et régénérer.

## Régénérer

```bash
pip install manifold3d trimesh numpy scikit-image pillow
python3 chat_flexi.py      # génère les 5 STL (~30 s)
python3 verif.py           # jeux, amplitude des articulations, surplombs
python3 rendu.py           # régénère apercu.png (~1 min)
```

Articulations trop dures (imprimante peu précise) : augmenter `C`
(jeu horizontal) de 0.4 à 0.5.

## Principe

- Volume défini par une fonction de distance signée (ellipsoïdes, cônes
  arrondis, fusions douces), maillé par marching cubes.
- Découpe en segments séparés par des encoches en V ; chaque articulation
  est une languette pincée entre deux plaques, avec deux tétons coniques à
  45° (imprimables sans support) qui servent de pivot.
- Zones de couleur = coque de 0,8 mm sous la surface, intersectée avec des
  motifs (yeux, joues…) projetés sur la face.
