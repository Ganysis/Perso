"""Chat kawaii articulé "print-in-place" (style flexi dragon).

Génère chat_flexi.stl : toutes les pièces sont imprimées déjà emboîtées,
sans support ni assemblage. Axe X = vers la tête, Z = hauteur.

Articulation (pivot vertical, vue en coupe) :
    z 7.0-10.0  plaque haute (segment avant) avec creux conique
    z 3.5- 6.5  languette (segment arrière) avec téton conique dessus
    z 0.0- 3.0  plaque basse (segment avant) avec téton conique
Les segments sont séparés par des encoches en V pour pouvoir tourner.
"""
import math
import sys

import numpy as np
import trimesh
from manifold3d import CrossSection, JoinType, Manifold

# --- Paramètres ---------------------------------------------------------
H = 10.0          # épaisseur totale
C = 0.4           # jeu horizontal
LOW_TOP, TONGUE_BOT, TONGUE_TOP, UP_BOT = 3.0, 3.5, 6.5, 7.0
CONE_OFF = 0.6    # décalage vertical des creux coniques (≈ jeu 0.4 à 45°)
WEDGE = 12.0      # demi-angle (°) des encoches en V -> ~±24° par articulation
EMBOSS = 0.8      # relief du visage
ENGRAVE = 0.6     # profondeur des gravures
SEG = 96
BIG = 500.0


class Joint:
    """Articulation à l'abscisse x ; s = échelle (queue plus fine)."""

    def __init__(self, x, s=1.0):
        self.x = x
        self.rt = 4.6 * s      # rayon languette
        self.rf = 7.0 * s      # rayon des plaques
        self.nw = 5.0 * s      # largeur du cou
        self.cr = 2.2 * s      # rayon des tétons coniques


# --- Outils 2D / 3D -----------------------------------------------------
def circle(r, x=0.0, y=0.0):
    return CrossSection.circle(r, SEG).translate([x, y])


def ellipse(rx, ry, x=0.0, y=0.0):
    return CrossSection.circle(1.0, SEG).scale([rx, ry]).translate([x, y])


def rect(x0, x1, y0, y1):
    return CrossSection.square([x1 - x0, y1 - y0]).translate([x0, y0])


def capsule(x0, y0, x1, y1, r):
    return (circle(r, x0, y0) + circle(r, x1, y1)).hull()


def x_less(x):
    return rect(x - BIG, x, -BIG, BIG)


def polygon(pts):
    cs = CrossSection([pts])
    return cs if cs.area() > 0 else CrossSection([pts[::-1]])


def wedge_front(x):
    """Zone x > x + C + |y|·tan(WEDGE) : arrière d'un segment en pointe."""
    t = math.tan(math.radians(WEDGE)) * BIG
    x0 = x + C
    return polygon([(x0, 0), (x0 + t, -BIG), (x0 + 3 * BIG, -BIG),
                    (x0 + 3 * BIG, BIG), (x0 + t, BIG)])


def wedge_rear(x):
    t = math.tan(math.radians(WEDGE)) * BIG
    x0 = x - C
    return polygon([(x0, 0), (x0 - t, BIG), (x0 - 3 * BIG, BIG),
                    (x0 - 3 * BIG, -BIG), (x0 - t, -BIG)])


def ext(cs, z0, z1):
    return Manifold.extrude(cs, z1 - z0).translate([0, 0, z0])


def cone(x, z_base, r_base, z_apex):
    """Cône d'axe vertical, base à z_base, pointe à z_apex (au-dessus)."""
    return Manifold.cylinder(z_apex - z_base, r_base, 0.0, SEG).translate([x, 0, z_base])


def rounded(cs, r):
    return cs.offset(-r, JoinType.Round).offset(r, JoinType.Round)


def heart(x, y, size):
    r = size * 0.3
    lobes = circle(r, x + r * 0.6, y - r * 0.95) + circle(r, x + r * 0.6, y + r * 0.95)
    tip = polygon([(x + r * 0.9, y - r * 1.85), (x - size * 0.75, y),
                   (x + r * 0.9, y + r * 1.85)])
    return lobes + tip


# --- Segment générique --------------------------------------------------
def segment(outline, ja=None, jb=None):
    """outline : contour 2D ; ja : articulation avant (porte la languette) ;
    jb : articulation arrière (porte la chape)."""
    body = outline
    if jb is not None:
        body = (body ^ wedge_front(jb.x)) + circle(jb.rf, jb.x)
    if ja is not None:
        body = (body - circle(ja.rf + C, ja.x)) ^ wedge_rear(ja.x)
    solid = ext(body, 0, H)

    if ja is not None:
        x = ja.x
        tongue2d = circle(ja.rt, x) + rect(x - ja.rf - C - 1.0, x, -ja.nw / 2, ja.nw / 2)
        tongue = ext(tongue2d, TONGUE_BOT, TONGUE_TOP)
        apex = LOW_TOP + ja.cr + CONE_OFF
        tongue -= cone(x, TONGUE_BOT - 0.01, apex - TONGUE_BOT + 0.01, apex)
        tongue += cone(x, TONGUE_TOP - 0.01, ja.cr + 0.01, TONGUE_TOP + ja.cr)
        solid += tongue

    if jb is not None:
        x = jb.x
        cavity2d = circle(jb.rt + C, x) + (circle(jb.rf + 1.0, x) ^ x_less(x))
        solid -= ext(cavity2d, LOW_TOP, UP_BOT)
        apex = TONGUE_TOP + jb.cr + CONE_OFF
        solid -= cone(x, UP_BOT - 0.01, apex - UP_BOT + 0.01, apex)
        solid += cone(x, LOW_TOP - 0.01, jb.cr + 0.01, LOW_TOP + jb.cr)
    return solid


def engrave(solid, cs):
    return solid - ext(cs, H - ENGRAVE, H + 1)


# --- Tête ---------------------------------------------------------------
HEAD_R = 21.0


def ear(side, r_in, r_tip, half, angle=52.0):
    a = math.radians(angle) * side
    h = math.radians(half)
    return polygon([
        (r_in * math.cos(a - h), r_in * math.sin(a - h)),
        (r_tip * math.cos(a), r_tip * math.sin(a)),
        (r_in * math.cos(a + h), r_in * math.sin(a + h)),
    ])


def head(jb):
    outline = circle(HEAD_R)
    for s in (1, -1):
        outline += rounded(ear(s, 19.0, 32.0, 20.0), 2.2)
    solid = segment(outline, jb=jb)

    # intérieur des oreilles gravé
    inner = CrossSection()
    for s in (1, -1):
        inner += rounded(ear(s, 20.5, 29.5, 11.0), 1.0)
    solid = engrave(solid, inner - circle(HEAD_R - 1.0))

    # grands yeux en relief avec reflets creux, nez, bouche "ω"
    face = CrossSection()
    for s in (1, -1):
        eye = ellipse(5.0, 4.4, 2.5, 9.0 * s)
        eye -= circle(1.6, 4.2, 9.0 * s - 1.4 * s)
        eye -= circle(0.7, 1.0, 9.0 * s + 1.9 * s)
        face += eye
    face += rounded(polygon([(-3.0, -2.0), (-3.0, 2.0), (-5.8, 0.0)]), 0.5)
    for s in (1, -1):
        ring = circle(2.1, -6.6, 1.7 * s) - circle(1.3, -6.6, 1.7 * s)
        face += ring ^ x_less(-6.6)
    solid += ext(face, H - 0.01, H + EMBOSS)

    # joues et moustaches gravées
    marks = CrossSection()
    for s in (1, -1):
        marks += ellipse(2.2, 3.2, -7.0, 13.5 * s)
        for k in (-1, 0, 1):
            w = rect(-0.45, 0.45, 0.0, 4.5).rotate(-14 * k * s)
            marks += w.translate([-3.0 + 2.6 * k, 15.8 * s if s > 0 else -20.3])
    marks = marks ^ circle(HEAD_R - 1.2)
    return engrave(solid, marks)


# --- Corps et queue -----------------------------------------------------
JOINTS = [Joint(-16.0), Joint(-34.0), Joint(-48.0), Joint(-66.0, 0.8),
          Joint(-77.5, 0.8), Joint(-89.0, 0.8), Joint(-100.5, 0.8)]


def build():
    J = JOINTS

    # silhouette globale du corps + queue, découpée en segments
    body = ellipse(29.0, 15.0, -43.0)
    tail = capsule(-60.0, 0, -109.0, 0, 7.2)
    sil = body + tail

    def legs(xc):
        cs = CrossSection()
        for s in (1, -1):
            cs += capsule(xc, 10.0 * s, xc, 19.0 * s, 4.0)
        return cs

    def toes(xc):
        cs = CrossSection()
        for s in (1, -1):
            for dx in (-1.6, 1.6):
                cs += rect(xc + dx - 0.4, xc + dx + 0.4, 19.8 * s - 1.6, 19.8 * s + 1.6)
        return cs

    parts = [head(J[0])]

    # B1 : pattes avant
    xc = -25.0
    seg = segment(sil + legs(xc), J[0], J[1])
    parts.append(engrave(seg, toes(xc)))

    # B2 : dos avec un petit cœur
    seg = segment(sil, J[1], J[2])
    # cœur peu profond : il passe au-dessus du creux conique du pivot
    parts.append(seg - ext(heart(-47.0, 0.0, 7.5), H - 0.4, H + 1))

    # B3 : pattes arrière
    xc = -57.0
    seg = segment(sil + legs(xc), J[2], J[3])
    parts.append(engrave(seg, toes(xc)))

    # queue rayée
    for ja, jb in zip(J[3:], J[4:]):
        xc = (ja.x + jb.x) / 2
        seg = segment(tail, ja, jb)
        stripe = rect(xc - 0.6, xc + 0.6, 3.0, 6.0) + rect(xc - 0.6, xc + 0.6, -6.0, -3.0)
        parts.append(engrave(seg, stripe))
    parts.append(segment(tail, ja=J[-1]))
    return parts


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=True)


if __name__ == "__main__":
    parts = build()
    total = parts[0]
    for p in parts[1:]:
        inter = (total ^ p).volume()
        assert inter < 1e-6, f"collision entre pièces : {inter}"
        total += p
    print(f"pièces: {len(parts)}  corps disjoints: {len(total.decompose())}")
    tm = to_trimesh(total)
    print("étanche:", tm.is_watertight, " volume: %.1f cm3" % (tm.volume / 1000))
    print("dimensions (mm):", np.round(tm.extents, 1))
    out = sys.argv[1] if len(sys.argv) > 1 else "chat_flexi.stl"
    tm.export(out)
    print("écrit", out)
