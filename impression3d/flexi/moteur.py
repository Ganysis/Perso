"""Moteur de la collection « Flexi Kawaii ».

Un animal = une silhouette (champ de distance signée) + des zones de couleur.
Le moteur se charge de tout le reste, identique pour toute la gamme :
    - le format (mini ~8 cm, porte-clés ~5,5 cm) et les articulations ;
    - la queue articulée, enroulée à plat ;
    - le visage kawaii (grands yeux brillants, joues roses, bouche « ω ») ;
    - les couleurs incrustées (4 filaments max, AMS) ;
    - l'export STL et les vérifications.

Repère : X vers la tête, Z vers le haut, plateau à z = 0.
Coordonnées « design » : celles du chat v2 de 13 cm ; elles sont multipliées
par l'échelle S du format. Les articulations et les jeux sont en mm réels.

Articulation (pivot vertical, vue en coupe, épaisseurs selon le format) :
    plaque haute (segment avant) + creux conique
    languette (segment arrière) + téton conique au-dessus
    plaque basse (segment avant) + téton conique
"""
import math
from dataclasses import dataclass

import numpy as np
from manifold3d import CrossSection, JoinType, Manifold, Mesh
from skimage.measure import marching_cubes

C = 0.4           # jeu horizontal
GAP_Z = 0.5       # jeu vertical
CONE_OFF = 0.6    # décalage vertical des creux coniques (≈ jeu 0.4 à 45°)
WEDGE = 12.0      # demi-angle des encoches en V (≈ ±24° par articulation)
SKIN = 0.8        # épaisseur des incrustations de couleur
OPEN = 0.55       # épaisseur mini du noyau intérieur = 2 x OPEN
SEG = 48
BIG = 400.0


# --- Formats ------------------------------------------------------------
@dataclass(frozen=True)
class Format:
    nom: str
    S: float            # échelle des formes
    plate: float        # épaisseur des plaques d'articulation
    tongue: float       # épaisseur de la languette
    j_body: float       # taille des articulations du corps
    j_tail: float       # taille des articulations de la queue
    n_body: int         # segments de corps
    n_tail: int         # segments de queue (bout compris)
    tail_curl: float    # enroulement total de la queue (degrés)
    tail_lead: float    # longueur droite avant l'enroulement (mm)
    res: float          # pas de maillage (mm)
    anneau: bool = False

    @property
    def low_top(self):
        return self.plate

    @property
    def tongue_bot(self):
        return self.plate + GAP_Z

    @property
    def tongue_top(self):
        return self.tongue_bot + self.tongue

    @property
    def up_bot(self):
        return self.tongue_top + GAP_Z

    @property
    def top(self):
        return self.up_bot + self.plate


FORMATS = {
    "mini": Format("mini", S=0.66, plate=2.4, tongue=2.4, j_body=0.78, j_tail=0.62,
                   n_body=3, n_tail=4, tail_curl=190.0, tail_lead=4.0, res=0.3),
    "porte-cles": Format("porte-cles", S=0.42, plate=2.0, tongue=2.0, j_body=0.56,
                         j_tail=0.5, n_body=2, n_tail=2, tail_curl=50.0, tail_lead=2.0,
                         res=0.22, anneau=True),
}


class Joint:
    """Articulation en (x, y) ; ang = direction (degrés) vers la tête."""

    def __init__(self, x, y, ang, s):
        self.x, self.y, self.ang, self.s = x, y, ang, s
        self.rt = 4.6 * s      # rayon languette
        self.rf = 7.0 * s      # rayon des plaques
        self.nw = 5.0 * s      # largeur du cou
        self.cr = 2.2 * s      # rayon des tétons coniques

    @property
    def pos(self):
        return np.array([self.x, self.y])

    def place2(self, cs):
        return cs.rotate(self.ang).translate([self.x, self.y])

    def place3(self, m):
        return m.rotate([0, 0, self.ang]).translate([self.x, self.y, 0])


# --- Champs de distance -------------------------------------------------
def sd_ellipsoid(X, Y, Z, c, r):
    px, py, pz = (X - c[0]) / r[0], (Y - c[1]) / r[1], (Z - c[2]) / r[2]
    k0 = np.sqrt(px * px + py * py + pz * pz)
    k1 = np.sqrt((px / r[0]) ** 2 + (py / r[1]) ** 2 + (pz / r[2]) ** 2)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


def sd_profile(q1, q2, rad):
    """Rectangle arrondi dans le plan (q1, q2) déjà centré/demi-tailles ôtées."""
    q1, q2 = q1 + rad, q2 + rad
    out = np.sqrt(np.maximum(q1, 0) ** 2 + np.maximum(q2, 0) ** 2)
    return out + np.minimum(np.maximum(q1, q2), 0) - rad


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


def sd_sweep(X, Y, Z, pts, hw, z0, z1, rad):
    """Profil rectangulaire arrondi (demi-largeur hw[i], de z0 à z1) balayé
    le long d'une polyligne horizontale pts (N x 2)."""
    q1 = np.full(X.shape, np.inf, dtype=np.float32)
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ab = b - a
        t = np.clip(((X - a[0]) * ab[0] + (Y - a[1]) * ab[1]) / (ab @ ab), 0, 1)
        d = np.hypot(X - a[0] - t * ab[0], Y - a[1] - t * ab[1])
        w = hw[i] + (hw[i + 1] - hw[i]) * t
        np.minimum(q1, d - w, out=q1)
    zc, hh = (z0 + z1) / 2, (z1 - z0) / 2
    return sd_profile(q1, np.abs(Z - zc) - hh, rad)


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def mirror_y(p):
    return (p[0], -p[1], p[2])


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


def wedge_front():
    """Local : zone x > C + |y|·tan(WEDGE) (en avant de l'articulation)."""
    t = math.tan(math.radians(WEDGE)) * BIG
    return polygon([(C, 0), (C + t, -BIG), (3 * BIG, -BIG), (3 * BIG, BIG), (C + t, BIG)])


def wedge_rear():
    t = math.tan(math.radians(WEDGE)) * BIG
    return polygon([(-C, 0), (-C - t, BIG), (-3 * BIG, BIG), (-3 * BIG, -BIG), (-C - t, -BIG)])


def ext(cs, z0, z1):
    return Manifold.extrude(cs, z1 - z0).translate([0, 0, z0])


def prism_x(cs_yz, x0=0.0, x1=60.0):
    """Extrusion le long de X d'un contour dessiné dans le plan (y, z)."""
    m = Manifold.extrude(cs_yz, x1 - x0)
    return m.transform([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]])


def cone(z_base, r_base, z_apex):
    return Manifold.cylinder(z_apex - z_base, r_base, 0.0, SEG).translate([0, 0, z_base])


def ellipsoid(c, r):
    return Manifold.sphere(1.0, SEG).scale(list(r)).translate(list(c))


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def both_sides(m):
    return m + m.mirror([0, 1, 0])


# --- Géométrie d'un animal dans un format -------------------------------
class Geo:
    """Mise en place d'un animal dans un format : articulations, queue,
    dimensions utiles aux zones de couleur."""

    def __init__(self, animal, fmt):
        self.animal, self.fmt = animal, fmt
        S = self.S = fmt.S
        a = animal
        self.head_c = tuple(v * S for v in a.head_c)
        self.head_r = tuple(v * S for v in a.head_r)
        jb = Joint(0, 0, 0, fmt.j_body)
        jt = Joint(0, 0, 0, fmt.j_tail)
        x0 = self.head_c[0] - 0.875 * self.head_r[0]
        sp = max(2 * jb.rf + C + 1.2, a.body_len * S / fmt.n_body)
        self.joints = [Joint(x0 - i * sp, 0, 0, fmt.j_body) for i in range(fmt.n_body)]
        xn = x0 - fmt.n_body * sp
        self.joints.append(Joint(xn, 0, 0, fmt.j_tail))
        self.n_body_joints = len(self.joints)

        # corps
        self.body_c = ((x0 + xn) / 2, 0.0, 8.0 * S)
        self.body_r = ((x0 - xn) / 2 + 3.0 * S, a.body_ry * S, 13.0 * S)
        mid = lambda i: (self.joints[i].x + self.joints[i + 1].x) / 2
        self.paws = [
            ((mid(0), 12.0 * S, 3.6 * S), (5.0 * S, 4.5 * S, 4.2 * S)),
            ((mid(fmt.n_body - 1), 12.5 * S, 4.2 * S), (5.5 * S, 5.0 * S, 4.8 * S)),
        ]
        self.body_hw = max(self.body_r[1], max(c[1] + r[1] for c, r in self.paws)) + 2.5
        self.spine_hw = jb.rf + 1.6
        self.spine = (x0 + jb.rf + 1.5, xn - 1.0)

        # queue : chemin enroulé, articulations le long du chemin
        self.tail_hw = jt.rf + 1.3
        tsp = 2 * jt.rf + C + 1.2
        tip_len = a.tail_tip * self.tail_hw + 1.5
        total = (fmt.n_tail - 1) * tsp + tip_len
        self.path, self.heading = tail_path((xn, 0.0), total + 0.01, fmt)
        s = np.arange(len(self.path)) * 0.25
        for k in range(1, fmt.n_tail):
            i = int(round(k * tsp / 0.25))
            p, h = self.path[i], self.heading[i]
            self.joints.append(Joint(p[0], p[1], math.degrees(h) + 180.0, fmt.j_tail))
        self.tip = self.path[-1] - np.array([math.cos(self.heading[-1]),
                                             math.sin(self.heading[-1])]) * (
            a.tail_tip * self.tail_hw * 0.55)
        self.tip_r = a.tail_tip * self.tail_hw
        self.tail_s = s
        # anneau de porte-clés
        self.ring = None
        if fmt.anneau:
            h = self.heading[-1]
            d = np.array([math.cos(h), math.sin(h)])
            self.ring = (self.tip + d * (self.tip_r + 2.4), 2.9, 1.95)

    # zones utiles aux animaux
    def tail_point(self, frac):
        i = min(int(frac * (len(self.path) - 1)), len(self.path) - 1)
        return self.path[i], self.heading[i]


def tail_path(start, total, fmt):
    """Chemin de la queue : part vers -X, droit sur tail_lead puis s'enroule
    vers +Y (virgule à plat). Renvoie points (N x 2) et cap (radians)."""
    step = 0.25
    n = int(total / step) + 1
    curv = math.radians(fmt.tail_curl) / max(total - fmt.tail_lead, 1e-6)
    pts, heads = [], []
    x, y, h = start[0], start[1], math.pi
    for i in range(n):
        pts.append((x, y))
        heads.append(h)
        if i * step > fmt.tail_lead:
            h -= curv * step
        x += math.cos(h) * step
        y += math.sin(h) * step
    return np.array(pts), np.array(heads)


# --- Enveloppe (SDF) ----------------------------------------------------
def envelope_sdf(geo, X, Y, Z):
    a, S, fmt = geo.animal, geo.S, geo.fmt
    head = sd_ellipsoid(X, Y, Z, geo.head_c, geo.head_r)
    for d, k in a.head_parts(geo, X, Y, Z):
        head = smin(head, d, k)
    body = sd_ellipsoid(X, Y, Z, geo.body_c, geo.body_r)
    top = fmt.top + 1.0
    sx0, sx1 = geo.spine
    spine = sd_round_box(X, Y, Z, ((sx0 + sx1) / 2, 0, (top - 2) / 2),
                         ((sx0 - sx1) / 2, geo.spine_hw, (top + 2) / 2), 2.5)
    # queue
    step = max(1, int(1.0 / 0.25))
    pts = geo.path[::step]
    pts = np.vstack([[geo.path[0][0] + 3.0, 0.0], pts])
    t = np.linspace(0, 1, len(pts))
    hw = geo.tail_hw * (1 + a.tail_bulge * t ** 2)
    tail = sd_sweep(X, Y, Z, pts, hw, -2.0, top + a.tail_top_extra * S, min(hw[0], 3.5) * 0.9)
    tail = smin(tail, sd_ellipsoid(X, Y, Z, (geo.tip[0], geo.tip[1], geo.tip_r * 0.75),
                                   (geo.tip_r, geo.tip_r, geo.tip_r * 0.95)), 2.0)
    d = smin(head, body, 4.0 * S)
    d = smin(d, spine, 3.0 * S)
    d = smin(d, tail, 3.0 * S)
    for c, r in geo.paws:
        for s in (1, -1):
            d = smin(d, sd_ellipsoid(X, Y, Z, (c[0], s * c[1], c[2]), r), 2.5 * S)
    for dd, k in a.extra_parts(geo, X, Y, Z):
        d = smin(d, dd, k)
    if geo.ring is not None:
        (cx, cy), rm, w = geo.ring
        q1 = np.abs(np.hypot(X - cx, Y - cy) - rm) - w / 2
        ring = sd_profile(q1, np.abs(Z - 1.5) - 1.5, 0.6)
        d = smin(d, ring, 0.8)
    return np.maximum(d, -Z)


def envelope_bounds(geo):
    xs = [geo.head_c[0] + geo.head_r[0] + 4, geo.path[:, 0].max() + 8]
    xmin = geo.path[:, 0].min() - geo.tip_r - 8
    ymax = max(geo.head_r[1] + 10 * geo.S, geo.body_hw, np.abs(geo.path[:, 1]).max() + geo.tip_r * 1.6) + 4
    if geo.ring is not None:
        xmin = min(xmin, geo.ring[0][0] - 6)
        ymax = max(ymax, abs(geo.ring[0][1]) + 6)
    zmax = geo.head_c[2] + geo.head_r[2] + 16 * geo.S
    return (xmin, max(xs)), (-ymax, ymax), (-1.0, zmax)


def sdf_to_manifold(geo, level, shift=0.0):
    res = geo.fmt.res
    (x0, x1), (y0, y1), (z0, z1) = envelope_bounds(geo)
    # grille décalée : aucun nœud sur les plans de découpe usuels
    x = np.arange(x0 + 0.1237 + shift, x1, res, dtype=np.float32)
    y = np.arange(y0 + 0.0613 + shift * 0.77, y1, res, dtype=np.float32)
    z = np.arange(z0 + 0.0871 + shift * 0.53, z1, res, dtype=np.float32)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    vol = envelope_sdf(geo, X, Y, Z).astype(np.float32)
    del X, Y, Z
    if level < 0:
        # noyau intérieur « ouvert » : on supprime les parties plus fines que
        # 2 x OPEN (pointes d'oreilles...), qui deviendraient des pincements
        from scipy.ndimage import distance_transform_edt
        core = vol < level - OPEN
        d_out = distance_transform_edt(~core, sampling=res).astype(np.float32)
        vol = np.maximum(vol - level, d_out - OPEN) + level
    # évite les sommets posés pile sur un nœud (arêtes de longueur nulle)
    eps = 0.02 * res
    near = np.abs(vol - level) < eps
    vol[near] = level + np.where(vol[near] >= level, eps, -eps)
    verts, faces, _, _ = marching_cubes(vol, level=level, spacing=(res, res, res))
    verts += np.array([x[0], y[0], z[0]])
    m = Manifold(Mesh(vert_properties=verts.astype(np.float32),
                      tri_verts=faces.astype(np.uint32)))
    if m.volume() < 0:
        m = Manifold(Mesh(vert_properties=verts.astype(np.float32),
                          tri_verts=faces[:, ::-1].astype(np.uint32)))
    if m.is_empty():
        raise RuntimeError(f"maillage invalide : {m.status()}")
    return m


# --- Visage kawaii commun -----------------------------------------------
def face_regions(geo):
    """Zones du visage, identiques pour toute la collection."""
    S = geo.S
    black_eye, hi, pink_cheek, mouth, nose, muzzle = (CrossSection() for _ in range(6))
    ro = max(1.75 * S, 1.3)
    ri = ro - max(0.9 * S, 0.75)
    for s in (1, -1):
        black_eye += ellipse(3.7 * S, 4.5 * S, 8.0 * S * s, 12.0 * S)
        hi += circle(max(1.4 * S, 0.8), 8.9 * S * s, 13.9 * S)
        hi += circle(max(0.65 * S, 0.5), 6.9 * S * s, 10.1 * S)
        pink_cheek += ellipse(2.8 * S, 1.9 * S, 13.2 * S * s, 7.6 * S)
        cy = ro * 0.86 * s
        ring = circle(ro, cy, 7.4 * S) - circle(ri, cy, 7.4 * S)
        mouth += ring ^ rect(-BIG, BIG, -BIG, 7.4 * S)
    nose += rounded(polygon([(-1.9 * S, 9.8 * S), (1.9 * S, 9.8 * S), (0.0, 7.9 * S)]),
                    0.4 * S)
    muzzle += ellipse(7.8 * S * geo.animal.muzzle_w, 4.4 * S * geo.animal.muzzle_h,
                      0.0, 6.8 * S)
    x0 = geo.head_c[0] + 0.1 * geo.head_r[0]
    return {
        "reflets": prism_x(hi, x0),
        "yeux": prism_x(black_eye, x0),
        "bouche": prism_x(mouth, x0),
        "nez": prism_x(nose, x0),
        "joues": prism_x(pink_cheek, x0),
        "museau": prism_x(muzzle, x0),
    }


# ordre de priorité des éléments de couleur (le premier l'emporte)
PRIORITE = ["reflets", "yeux", "bouche", "nez", "joues", "oreilles_int", "accessoire",
            "bout_oreilles", "museau", "taches_noir", "taches_couleur", "rayures",
            "chaussettes", "bout_queue"]


# --- Segmentation -------------------------------------------------------
def segment(env, fmt, ja=None, jb=None, corridor=None):
    """ja : articulation avant (languette) ; jb : articulation arrière (chape)."""
    region = rect(-BIG, BIG, -BIG, BIG) if corridor is None else corridor
    if jb is not None:
        region = (region ^ jb.place2(wedge_front())) + jb.place2(circle(jb.rf))
    if ja is not None:
        region = (region - ja.place2(circle(ja.rf + C))) ^ ja.place2(wedge_rear())
    solid = ext(region, -1, 80) ^ env

    if ja is not None:
        tongue2d = circle(ja.rt) + rect(-ja.rf - C - 1.0, 0, -ja.nw / 2, ja.nw / 2)
        tongue = ext(tongue2d, fmt.tongue_bot, fmt.tongue_top)
        apex = fmt.low_top + ja.cr + CONE_OFF
        tongue -= cone(fmt.tongue_bot - 0.01, apex - fmt.tongue_bot + 0.01, apex)
        tongue += cone(fmt.tongue_top - 0.01, ja.cr + 0.01, fmt.tongue_top + ja.cr)
        solid += ja.place3(tongue)

    if jb is not None:
        # coupe à x = 0.2 (et non 0) : pas de tangence avec le disque des plaques
        cavity2d = circle(jb.rt + C) + (circle(jb.rf + 1.0) ^ rect(-BIG, 0.2, -BIG, BIG))
        cut = ext(cavity2d, fmt.low_top, fmt.up_bot)
        apex = fmt.tongue_top + jb.cr + CONE_OFF
        cut += cone(fmt.up_bot - 0.01, apex - fmt.up_bot + 0.01, apex)
        solid -= jb.place3(cut)
        solid += jb.place3(cone(fmt.low_top - 0.01, jb.cr + 0.01, fmt.low_top + jb.cr))
    return solid


def corridors(geo):
    """Zone 2D autorisée pour chaque segment (évite qu'une queue enroulée
    soit comptée dans le corps et inversement)."""
    J = geo.joints
    nb = geo.n_body_joints
    out = [None]  # tête
    band = rect(-BIG, BIG, -geo.body_hw, geo.body_hw)
    for i in range(nb - 1):
        out.append(band)
    rc = geo.tail_hw * (1 + geo.animal.tail_bulge) + 2.5
    for i in range(nb - 1, len(J) - 1):
        a, b = J[i], J[i + 1]
        out.append((circle(rc, a.x, a.y) + circle(rc, b.x, b.y)).hull())
    last = J[-1]
    tip = circle(geo.tip_r + 2.5, *geo.tip) + circle(rc, last.x, last.y)
    if geo.ring is not None:
        tip += circle(geo.ring[1] + geo.ring[2] + 1.5, *geo.ring[0])
    out.append(tip.hull())
    return out


def clean(m, min_vol=0.05):
    out = Manifold()
    for p in m.decompose():
        if p.volume() > min_vol:
            out += p
    return out


class Modele:
    """Géométrie complète d'un animal dans un format avec une tenue."""

    def __init__(self, animal, fmt_nom, tenue=None):
        self.animal = animal
        self.fmt = FORMATS[fmt_nom]
        self.tenue = tenue
        animal.tenue = tenue
        self.geo = Geo(animal, self.fmt)
        self.env = sdf_to_manifold(self.geo, 0.0)
        self.inner = sdf_to_manifold(self.geo, -SKIN, shift=0.1511)
        J = self.geo.joints
        bounds = [(None, J[0])] + list(zip(J, J[1:])) + [(J[-1], None)]
        self.segments = [segment(self.env, self.fmt, ja, jb, cor)
                         for (ja, jb), cor in zip(bounds, corridors(self.geo))]
        regions = face_regions(self.geo)
        regions.update(animal.regions(self.geo))
        self.regions = regions
        self.exclus = {}
        self._cache = {}

    def couleurs(self, palette_nom):
        """Découpe en filaments : {nom_filament: [pièces par segment]}.
        Si une coïncidence de surfaces crée un pincement (maillage non
        exportable en STL), les zones sont décalées de quelques centièmes
        de mm ; si le pincement persiste, le plus petit détail de couleur
        en cause est retiré (listé dans self.exclus)."""
        if palette_nom in self._cache:
            return self._cache[palette_nom]
        exclus = set()
        for essai in range(10):
            d = 0.013 * (essai % 3)
            out = self._couleurs(palette_nom, (d, 0.7 * d, 0.4 * d), exclus)
            pts = [pinch_points(p) for ps in out.values() for p in ps]
            pts = np.vstack([p for p in pts if len(p)] or [np.zeros((0, 3))])
            if not len(pts):
                break
            if essai % 3 == 2:
                cand = []
                for el, reg in self.regions.items():
                    if el in exclus:
                        continue
                    (x0, y0, z0, x1, y1, z1) = reg.bounding_box()
                    lo, hi = np.array([x0, y0, z0]) - 0.6, np.array([x1, y1, z1]) + 0.6
                    if np.any(np.all((pts >= lo) & (pts <= hi), axis=1)):
                        cand.append(((reg - self.inner).volume(), el))
                if not cand:
                    break
                exclus.add(min(cand)[1])
        self.exclus[palette_nom] = sorted(exclus)
        self._cache[palette_nom] = out
        return out

    def _couleurs(self, palette_nom, jitter, exclus=()):
        pal = self.animal.palettes[palette_nom]
        fils = list(pal["filaments"])
        assert len(fils) <= 4, "4 filaments maximum (AMS)"
        corps = pal["elements"].get("corps", fils[0])
        zones = {f: Manifold() for f in fils}
        pris = Manifold()
        for el in PRIORITE:
            if el not in self.regions or el in exclus:
                continue
            reg = self.regions[el].translate(list(jitter))
            f = pal["elements"].get(el, corps)
            r = reg - pris
            pris += reg
            if f != corps:
                zones[f] += r
        shells = {f: z - self.inner for f, z in zones.items() if f != corps and not z.is_empty()}
        all_shells = Manifold()
        for sh in shells.values():
            all_shells += sh
        out = {f: [] for f in fils}
        for seg in self.segments:
            for f, sh in shells.items():
                out[f].append(clean(seg ^ sh))
            # on retire les zones (qui débordent), pas les pièces : pas de faces confondues
            out[corps].append(clean(seg - all_shells))
        return out


def pinch_points(m):
    """Positions partagées par plusieurs sommets distincts (float32) : un
    pincement, que le format STL ne sait pas représenter."""
    if m.is_empty():
        return np.zeros((0, 3))
    v = np.asarray(m.to_mesh().vert_properties)[:, :3].astype(np.float32)
    u, c = np.unique(v, axis=0, return_counts=True)
    return u[c > 1]


# --- Export -------------------------------------------------------------
def to_trimesh(m, tol=0.01):
    import trimesh
    mesh = m.simplify(tol).to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=False)


def union(parts):
    m = Manifold()
    for p in parts:
        m += p
    return m
