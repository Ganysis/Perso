"""Chat kawaii articulé "print-in-place", sculpté en volume, multicolore (AMS).

Le volume est défini par une fonction de distance signée (SDF) : ellipsoïdes,
cônes arrondis et boîtes arrondies fusionnés en douceur, puis maillé par
marching cubes. Il est ensuite découpé en segments articulés (pivots
verticaux imprimés emboîtés) et les couleurs sont incrustées sur 0,8 mm
d'épaisseur sous la surface.

Sorties (dans le dossier courant) :
    chat_orange.stl, chat_blanc.stl, chat_noir.stl, chat_rose.stl  -> AMS
    chat_monocolore.stl                                              -> 1 couleur

Axe X = vers la tête, Z = hauteur, lit d'impression à z = 0.

Articulation (pivot vertical, vue en coupe) :
    z 7.0-10.0  plaque haute (segment avant) avec creux conique
    z 3.5- 6.5  languette (segment arrière) avec téton conique dessus
    z 0.0- 3.0  plaque basse (segment avant) avec téton conique
Au-dessus de z = 10, la chape se prolonge jusqu'à la surface.
"""
import math

import numpy as np
from manifold3d import CrossSection, JoinType, Manifold, Mesh
from skimage.measure import marching_cubes

# --- Paramètres ---------------------------------------------------------
C = 0.4           # jeu horizontal
LOW_TOP, TONGUE_BOT, TONGUE_TOP, UP_BOT = 3.0, 3.5, 6.5, 7.0
CONE_OFF = 0.6    # décalage vertical des creux coniques (≈ jeu 0.4 à 45°)
WEDGE = 12.0      # demi-angle (°) des encoches en V entre segments
SKIN = 0.8        # épaisseur des incrustations de couleur
RES = 0.35        # pas de la grille de maillage (mm)
SEG = 64
BIG = 500.0

COLORS = {  # nom -> couleur d'aperçu
    "orange": (255, 150, 60),
    "blanc": (250, 248, 242),
    "noir": (40, 36, 40),
    "rose": (255, 140, 170),
}


class Joint:
    """Articulation à l'abscisse x ; s = échelle (queue plus fine)."""

    def __init__(self, x, s=1.0):
        self.x = x
        self.rt = 4.6 * s      # rayon languette
        self.rf = 7.0 * s      # rayon des plaques
        self.nw = 5.0 * s      # largeur du cou
        self.cr = 2.2 * s      # rayon des tétons coniques


JOINTS = [Joint(-4.0), Joint(-20.0), Joint(-35.0), Joint(-52.0),
          Joint(-63.5, 0.8), Joint(-75.0, 0.8), Joint(-86.5, 0.8)]

# --- Forme : champs de distance ----------------------------------------
HEAD_C, HEAD_R = (10.0, 0.0, 11.0), (16.0, 19.0, 16.0)
BODY_C, BODY_R = (-28.0, 0.0, 8.0), (24.0, 14.0, 13.0)
FRONT_PAW = ((-12.0, 12.0, 3.6), (5.0, 4.5, 4.2))
BACK_PAW = ((-43.5, 12.5, 4.2), (5.5, 5.0, 4.8))
EAR_BASE, EAR_TIP = (7.0, 11.0, 21.0), (9.0, 15.5, 32.0)
TAIL_TIP = (-99.0, 0.0, 5.5)


def sd_ellipsoid(X, Y, Z, c, r):
    px, py, pz = (X - c[0]) / r[0], (Y - c[1]) / r[1], (Z - c[2]) / r[2]
    k0 = np.sqrt(px * px + py * py + pz * pz)
    k1 = np.sqrt((px / r[0]) ** 2 + (py / r[1]) ** 2 + (pz / r[2]) ** 2)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


def sd_round_box(X, Y, Z, c, half, rad):
    qx = np.abs(X - c[0]) - (half[0] - rad)
    qy = np.abs(Y - c[1]) - (half[1] - rad)
    qz = np.abs(Z - c[2]) - (half[2] - rad)
    out = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2 + np.maximum(qz, 0) ** 2)
    return out + np.minimum(np.maximum(np.maximum(qx, qy), qz), 0) - rad


def sd_round_cone(X, Y, Z, a, b, r1, r2):
    """Cône arrondi entre les sphères (a, r1) et (b, r2) (Inigo Quilez)."""
    ba = np.subtract(b, a)
    l2 = ba @ ba
    rr = r1 - r2
    a2 = l2 - rr * rr
    il2 = 1.0 / l2
    pax, pay, paz = X - a[0], Y - a[1], Z - a[2]
    y = pax * ba[0] + pay * ba[1] + paz * ba[2]
    z = y - l2
    x2 = ((pax * l2 - ba[0] * y) ** 2 + (pay * l2 - ba[1] * y) ** 2
          + (paz * l2 - ba[2] * y) ** 2)
    y2 = y * y * l2
    z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    d_mid = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1
    d_top = np.sqrt(x2 + z2) * il2 - r2
    d_bot = np.sqrt(x2 + y2) * il2 - r1
    return np.where(np.sign(z) * a2 * z2 > k, d_top,
                    np.where(np.sign(y) * a2 * y2 < k, d_bot, d_mid))


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def mirror_y(p):
    return (p[0], -p[1], p[2])


def cat_sdf(X, Y, Z):
    head = sd_ellipsoid(X, Y, Z, HEAD_C, HEAD_R)
    for s in (1, -1):
        a, b = EAR_BASE, EAR_TIP
        if s < 0:
            a, b = mirror_y(a), mirror_y(b)
        head = smin(head, sd_round_cone(X, Y, Z, a, b, 5.0, 1.4), 2.0)
    body = sd_ellipsoid(X, Y, Z, BODY_C, BODY_R)
    # colonne vertébrale : garantit l'épaisseur autour des articulations
    spine = sd_round_box(X, Y, Z, (-27.0, 0, 4.25), (29.0, 9.0, 7.25), 4.0)
    tail = sd_round_box(X, Y, Z, (-75.0, 0, 4.0), (25.0, 6.6, 7.0), 5.5)
    tail = smin(tail, sd_ellipsoid(X, Y, Z, TAIL_TIP, (7.5, 7.0, 6.5)), 3.0)
    d = smin(head, body, 4.0)
    d = smin(d, spine, 3.0)
    d = smin(d, tail, 4.0)
    for c, r in (FRONT_PAW, BACK_PAW):
        for s in (1, -1):
            d = smin(d, sd_ellipsoid(X, Y, Z, (c[0], s * c[1], c[2]), r), 2.5)
    return np.maximum(d, -Z)          # base plate à z = 0


def sdf_to_manifold(level, shift=0.0):
    # origine décalée : aucun nœud de grille sur les plans de découpe usuels
    x = np.arange(-110.0 + 0.1237 + shift, 32.0, RES)
    y = np.arange(-24.0 + 0.0613 + shift * 0.77, 24.0 + RES, RES)
    z = np.arange(-1.0 + 0.0871 + shift * 0.53, 40.0, RES)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    vol = cat_sdf(X, Y, Z).astype(np.float32)
    # évite les sommets posés pile sur un nœud de grille (arêtes de longueur nulle)
    eps = 0.02 * RES
    near = np.abs(vol - level) < eps
    vol[near] = level + np.where(vol[near] >= level, eps, -eps)
    verts, faces, _, _ = marching_cubes(vol, level=level, spacing=(RES, RES, RES))
    verts += np.array([x[0], y[0], z[0]])
    m = Manifold(Mesh(vert_properties=verts.astype(np.float32),
                      tri_verts=faces.astype(np.uint32)))
    if m.is_empty():
        raise RuntimeError(f"maillage invalide : {m.status()}")
    if m.volume() < 0:
        m = Manifold(Mesh(vert_properties=verts.astype(np.float32),
                          tri_verts=faces[:, ::-1].astype(np.uint32)))
    return m


# --- Outils 2D / 3D -----------------------------------------------------
def circle(r, x=0.0, y=0.0):
    return CrossSection.circle(r, SEG).translate([x, y])


def ellipse(rx, ry, x=0.0, y=0.0):
    return CrossSection.circle(1.0, SEG).scale([rx, ry]).translate([x, y])


def rect(x0, x1, y0, y1):
    return CrossSection.square([x1 - x0, y1 - y0]).translate([x0, y0])


def polygon(pts):
    cs = CrossSection([pts])
    return cs if cs.area() > 0 else CrossSection([pts[::-1]])


def rounded(cs, r):
    return cs.offset(-r, JoinType.Round).offset(r, JoinType.Round)


def x_less(x):
    return rect(x - BIG, x, -BIG, BIG)


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


def prism_x(cs_yz, x0=0.0, x1=60.0):
    """Extrusion le long de X d'un contour dessiné dans le plan (y, z)."""
    m = Manifold.extrude(cs_yz, x1 - x0)
    return m.transform([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]])


def cone(x, z_base, r_base, z_apex):
    return Manifold.cylinder(z_apex - z_base, r_base, 0.0, SEG).translate([x, 0, z_base])


# --- Zones de couleur ---------------------------------------------------
def color_regions():
    black, pink, white_hi, white = (CrossSection() for _ in range(4))
    for s in (1, -1):
        black += ellipse(3.7, 4.5, 8.0 * s, 12.0)                      # yeux
        white_hi += circle(1.4, 8.9 * s, 13.9) + circle(0.65, 6.9 * s, 10.1)
        pink += ellipse(2.8, 1.9, 13.2 * s, 7.6)                        # joues
        ring = circle(1.75, 1.5 * s, 7.4) - circle(0.85, 1.5 * s, 7.4)  # bouche ω
        black += ring ^ rect(-BIG, BIG, -BIG, 7.4)
    pink += rounded(polygon([(-1.9, 9.8), (1.9, 9.8), (0.0, 7.9)]), 0.4)  # nez
    white += ellipse(7.8, 4.4, 0.0, 6.8)                               # museau

    face = dict(x0=12.0)
    noir = prism_x(black, **face)
    rose = prism_x(pink, **face)
    hi = prism_x(white_hi, **face)
    blanc = prism_x(white, **face)
    # intérieur des oreilles (face avant)
    ear = CrossSection()
    for s in (1, -1):
        ear += rounded(polygon([(9.8 * s, 25.0), (14.3 * s, 29.6), (14.9 * s, 24.6)]), 0.6)
    rose += prism_x(ear, x0=8.0)
    # chaussettes : boîte à parois franches (évite les zones tangentes)
    for c, r in (FRONT_PAW, BACK_PAW):
        for s in (1, -1):
            x0, x1 = c[0] - r[0] - 1.0, c[0] + r[0] + 1.0
            y0 = c[1] - 1.0
            box = Manifold.cube([x1 - x0, 30.0, c[2] + r[2] + 0.6 + 5]).translate([x0, y0, -5])
            blanc += box if s > 0 else box.mirror([0, 1, 0])
    blanc += Manifold.cube([30, 60, 60]).translate([-124.0, -30, -5])

    # priorités : reflets > noir > rose > blanc
    noir = noir - hi
    rose = rose - hi - noir
    blanc = (blanc - noir - rose) + hi
    return {"noir": noir, "rose": rose, "blanc": blanc}


# --- Segments -----------------------------------------------------------
def segment(env, ja=None, jb=None):
    """ja : articulation avant (languette) ; jb : articulation arrière (chape)."""
    region = rect(-BIG, BIG, -BIG, BIG)
    if jb is not None:
        region = (region ^ wedge_front(jb.x)) + circle(jb.rf, jb.x)
    if ja is not None:
        region = (region - circle(ja.rf + C, ja.x)) ^ wedge_rear(ja.x)
    solid = ext(region, -1, 60) ^ env

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


def build():
    """Renvoie une liste de segments ; chaque segment = {couleur: Manifold}
    plus la clé "_entier" (segment monocolore)."""
    env = sdf_to_manifold(0.0)
    inner = sdf_to_manifold(-SKIN, shift=0.1511)  # grille décalée
    # zones de couleur = volume de la zone hors du noyau (pas de faces confondues)
    shells = {k: r - inner for k, r in color_regions().items()}
    all_shells = Manifold()
    for sh in shells.values():
        all_shells += sh

    bounds = [(None, JOINTS[0])] + list(zip(JOINTS, JOINTS[1:])) + [(JOINTS[-1], None)]
    segments = []
    for ja, jb in bounds:
        solid = segment(env, ja, jb)
        parts = {}
        for name, sh in shells.items():
            piece = solid ^ sh
            if piece.volume() > 1e-3:
                parts[name] = piece
        # on retire les zones (qui débordent de la surface), pas les pièces :
        # pas de faces confondues, donc pas de pincements dans le maillage
        parts["orange"] = solid - all_shells
        parts = {k: clean(v) for k, v in parts.items()}
        parts["_entier"] = solid
        segments.append(parts)
    return segments


def clean(m, min_vol=0.05):
    """Supprime les éventuels fragments de volume négligeable."""
    out = Manifold()
    for p in m.decompose():
        if p.volume() > min_vol:
            out += p
    return out


def merged(seg):
    return seg["_entier"]


def to_trimesh(m):
    import trimesh
    mesh = m.simplify(0.01).to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=False)


def export_stl(m, path):
    tm = to_trimesh(m)
    tm.export(path)
    return tm


if __name__ == "__main__":
    segs = build()
    whole = [merged(s) for s in segs]
    total = whole[0]
    for w in whole[1:]:
        inter = (total ^ w).volume()
        assert inter < 1e-3, f"collision entre segments : {inter}"
        total += w
    print(f"segments: {len(segs)}  corps disjoints: {len(total.decompose())}")
    for name in COLORS:
        m = Manifold()
        for s in segs:
            if name in s:
                m += s[name]
        tm = export_stl(m, f"chat_{name}.stl")
        print(f"chat_{name}.stl : {tm.volume / 1000:.2f} cm3")
    tm = export_stl(total, "chat_monocolore.stl")
    print("étanche:", tm.is_watertight, " volume: %.1f cm3" % (tm.volume / 1000))
    print("dimensions (mm):", np.round(tm.extents, 1))
