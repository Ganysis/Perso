"""Import d'un modèle 3D texturé (GLB issu de TRELLIS, Meshy...) vers la
collection : modèle plein et étanche, couleurs de la texture réduites à
4 filaments AMS, et option « tête pivotante » imprimée en place.

    python3 importe.py modeles/chat_trellis.json

Le fichier JSON décrit le modèle (voir modeles/chat_trellis.json).
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import CrossSection, JoinType, Manifold, Mesh
from scipy import ndimage
from scipy.spatial import cKDTree
from skimage.measure import marching_cubes

from moteur import (BIG, C, CONE_OFF, FORMATS, OPEN, SKIN, Joint, circle, clean, cone, ext,
                    pinch_points, rect, to_trimesh, union, wedge_front)


# --- Chargement et remise en forme --------------------------------------
def charger(path, longueur, axes, signes):
    """Charge le GLB ; renvoie sommets (mm, X avant, Z haut, posé à z=0),
    faces et couleurs par sommet (RGB 0-255, lues dans la texture)."""
    scene = trimesh.load(path)
    geoms = list(scene.geometry.values()) if hasattr(scene, "geometry") else [scene]
    V, F, Cc, off = [], [], [], 0
    for g in geoms:
        V.append(g.vertices)
        F.append(g.faces + off)
        Cc.append(g.visual.to_color().vertex_colors[:, :3])
        off += len(g.vertices)
    v = np.vstack(V)[:, list(axes)] * np.array(signes, float)
    f = np.vstack(F)
    col = np.vstack(Cc).astype(float)
    k = longueur / (v[:, 0].max() - v[:, 0].min())
    v = v * k
    v -= [(v[:, 0].max() + v[:, 0].min()) / 2, (v[:, 1].max() + v[:, 1].min()) / 2, v[:, 2].min()]
    return v, f, col


def solidifier(v, f, res, fermeture=3.3):
    """Champ de distance signée (mm, négatif dedans) d'un maillage de
    surface quelconque (troué, à parois doubles...). Les trous plus petits
    que `fermeture` sont bouchés sans lisser les creux réels de la surface."""
    m = trimesh.Trimesh(v, f, process=False)
    n = int(min(12e6, m.area / (res * res) * 6))
    pts, _ = trimesh.sample.sample_surface(m, n)
    lo = v.min(0) - 5
    hi = v.max(0) + 5
    shape = np.ceil((hi - lo) / res).astype(int) + 1
    idx = np.floor((pts - lo) / res + 0.5).astype(int)
    surf = np.zeros(shape, bool)
    surf[idx[:, 0], idx[:, 1], idx[:, 2]] = True
    st = ndimage.generate_binary_structure(3, 1)

    def exterieur(s):
        lab, _ = ndimage.label(~s)
        return lab == lab[0, 0, 0]

    K = int(round(fermeture / res))
    o_fin = exterieur(surf)
    o_ferme = exterieur(ndimage.binary_dilation(surf, st, iterations=K))
    d = ndimage.distance_transform_edt(~o_ferme) * res
    plein = ~(o_ferme | (o_fin & (d <= (K + 1) * res)))
    plein = ndimage.binary_fill_holes(plein)
    # on ne garde que le volume principal (pas de poussières flottantes)
    lab, nb = ndimage.label(plein)
    if nb > 1:
        tailles = ndimage.sum(plein, lab, range(1, nb + 1))
        plein = lab == (1 + int(np.argmax(tailles)))
    sdf = (ndimage.distance_transform_edt(~plein) - ndimage.distance_transform_edt(plein)) * res
    sdf = ndimage.gaussian_filter(sdf.astype(np.float32), 1.0)
    return sdf, lo


def champ_vers_manifold(field, lo, res, level=0.0):
    field = field.copy()
    eps = 0.02 * res
    near = np.abs(field - level) < eps
    field[near] = level + np.where(field[near] >= level, eps, -eps)
    verts, faces, _, _ = marching_cubes(field, level=level, spacing=(res, res, res))
    verts += lo
    m = Manifold(Mesh(vert_properties=verts.astype(np.float32), tri_verts=faces.astype(np.uint32)))
    if m.volume() < 0:
        m = Manifold(Mesh(vert_properties=verts.astype(np.float32),
                          tri_verts=faces[:, ::-1].astype(np.uint32)))
    if m.is_empty():
        raise RuntimeError(f"maillage invalide : {m.status()}")
    return m


def noyau(sdf, res):
    """Champ du noyau intérieur (surface à SKIN sous la peau), ouvert :
    les parties plus fines que 2 x OPEN disparaissent (pointes d'oreilles)."""
    core = sdf < -SKIN - OPEN
    d_out = ndimage.distance_transform_edt(~core) * res
    return np.maximum(sdf + SKIN, d_out.astype(np.float32) - OPEN)


# --- Couleurs -----------------------------------------------------------
def etiquettes(col, regles):
    """Étiquette par sommet : 0 = corps, puis dans l'ordre de `regles`."""
    r, g, b = col.T
    L = 0.3 * r + 0.59 * g + 0.11 * b
    sat = col.max(1) - col.min(1)
    env = {"r": r, "g": g, "b": b, "L": L, "sat": sat, "np": np}
    lab = np.zeros(len(col), int)
    for i, (nom, expr) in enumerate(regles, 1):
        m = eval(expr, {"__builtins__": {}}, env) & (lab == 0)
        lab[m] = i
    return lab


def symetriser(v, lab, i_ref, i_cible, zmin):
    """Recopie par symétrie (plan entre les yeux) les sommets d'étiquette
    i_cible situés au-dessus de zmin (ex. intérieur rose d'une seule oreille)."""
    yeux = v[lab == i_ref]
    if len(yeux) < 10:
        return lab
    # deux yeux : séparation selon Y
    ymid = np.median(yeux[:, 1])
    a, b = yeux[yeux[:, 1] < ymid].mean(0), yeux[yeux[:, 1] >= ymid].mean(0)
    n = (b - a)[:2] / np.linalg.norm((b - a)[:2])
    c = (a + b)[:2] / 2
    src = v[(lab == i_cible) & (v[:, 2] > zmin)]
    if not len(src):
        return lab
    d = (src[:, :2] - c) @ n
    miroir = src.copy()
    miroir[:, :2] = src[:, :2] - 2 * d[:, None] * n
    tree = cKDTree(v)
    dist, idx = tree.query(miroir, distance_upper_bound=1.5)
    ok = np.isfinite(dist)
    sel = idx[ok]
    sel = sel[lab[sel] == 0]
    lab = lab.copy()
    lab[sel] = i_cible
    return lab


def zones(sdf, lo, res, v, lab, n, max_zones=None):
    """Zones de couleur (Manifold) : chaque voxel de la bande de surface
    prend l'étiquette du sommet le plus proche ; nettoyage des poussières."""
    band = np.abs(sdf) < 1.8
    ijk = np.argwhere(band)
    pts = ijk * res + lo
    _, idx = cKDTree(v).query(pts)
    vl = lab[idx]
    out = {}
    st = ndimage.generate_binary_structure(3, 1)
    for k in range(1, n + 1):
        mask = np.zeros(sdf.shape, bool)
        sel = ijk[vl == k]
        if not len(sel):
            continue
        mask[sel[:, 0], sel[:, 1], sel[:, 2]] = True
        mask = ndimage.binary_closing(mask, st, iterations=1)
        lab3, nb = ndimage.label(mask)
        if nb:
            tailles = ndimage.sum(mask, lab3, range(1, nb + 1))
            ordre = np.argsort(-tailles)
            if max_zones and max_zones.get(k):
                ordre = ordre[:max_zones[k]]
            ordre = [i for i in ordre if tailles[i] * res ** 3 > 0.4]
            mask &= np.isin(lab3, 1 + np.array(ordre, int))
        if not mask.any():
            continue
        fld = ndimage.gaussian_filter(mask.astype(np.float32), 0.7)
        out[k] = champ_vers_manifold(0.5 - fld, lo, res, 0.0)
    return out


# --- Tête pivotante -----------------------------------------------------
def tete_pivotante(env, fmt, j, corridor):
    """Deux pièces : tête (avant du pivot) et corps, emboîtées en place."""
    tete2d = (corridor ^ j.place2(wedge_front())) + j.place2(circle(j.rf))
    corps2d = rect(-BIG, BIG, -BIG, BIG) - tete2d.offset(C, JoinType.Round)
    tete = ext(tete2d, -1, 200) ^ env
    corps = ext(corps2d, -1, 200) ^ env

    cavity2d = circle(j.rt + C) + (circle(j.rf + 1.0) ^ rect(-BIG, 0.2, -BIG, BIG))
    cut = ext(cavity2d, fmt.low_top, fmt.up_bot)
    apex = fmt.tongue_top + j.cr + CONE_OFF
    cut += cone(fmt.up_bot - 0.01, apex - fmt.up_bot + 0.01, apex)
    tete -= j.place3(cut)
    tete += j.place3(cone(fmt.low_top - 0.01, j.cr + 0.01, fmt.low_top + j.cr))

    tongue2d = circle(j.rt) + rect(-j.rf - C - 1.0, 0, -j.nw / 2, j.nw / 2)
    tongue = ext(tongue2d, fmt.tongue_bot, fmt.tongue_top)
    apex = fmt.low_top + j.cr + CONE_OFF
    tongue -= cone(fmt.tongue_bot - 0.01, apex - fmt.tongue_bot + 0.01, apex)
    tongue += cone(fmt.tongue_top - 0.01, j.cr + 0.01, fmt.tongue_top + j.cr)
    corps += j.place3(tongue)
    return [clean(tete), clean(corps)]


def amplitude(segs, j):
    """Rotation libre de la tête (degrés) dans chaque sens : [gauche, droite]."""
    out = []
    for s in (1, -1):
        ok = 0
        for a in range(2, 42, 2):
            r = segs[0].translate([-j.x, -j.y, 0]).rotate([0, 0, a * s]).translate([j.x, j.y, 0])
            if (r ^ segs[1]).volume() > 1e-2:
                break
            ok = a
        out.append(ok)
    return out


# --- Chaîne complète ----------------------------------------------------
def couleurs(segs, zs, inner, noms, corps):
    """Découpe chaque segment en filaments ; retire un détail qui créerait
    un pincement (maillage non exportable) et le signale."""
    exclus = []
    for essai in range(6):
        dj = 0.011 * essai
        shells = {noms[k]: z.translate([dj, 0.7 * dj, 0.4 * dj]) - inner
                  for k, z in zs.items() if noms[k] not in exclus}
        tout = union(shells.values())
        out = {corps: [clean(s - tout) for s in segs]}
        for f, sh in shells.items():
            out[f] = [clean(s ^ sh) for s in segs]
        pb = [f for f, ps in out.items() if any(len(pinch_points(p)) for p in ps)]
        if not pb:
            break
        if essai >= 3 and [f for f in pb if f != corps]:
            exclus.append(min((f for f in pb if f != corps),
                              key=lambda f: union(out[f]).volume()))
    return out, exclus


def importer(cfg_path):
    t0 = time.time()
    cfg = json.loads(Path(cfg_path).read_text())
    base = Path(cfg_path).parent
    out_dir = Path(__file__).parent / "sorties" / cfg["nom"]
    out_dir.mkdir(parents=True, exist_ok=True)
    res = cfg.get("res", 0.3)

    v, f, col = charger(base / cfg["glb"], cfg["longueur"], cfg["axes"], cfg["signes"])
    cache = Path("/tmp") / f"sdf_{cfg['nom']}_{cfg['longueur']}_{res}.npz"
    if cache.exists():
        z_ = np.load(cache)
        sdf, lo = z_["sdf"], z_["lo"]
    else:
        sdf, lo = solidifier(v, f, res)
        np.savez(cache, sdf=sdf, lo=lo)
    # dessous aplati : on retire zcut mm et on repose à z = 0
    zc = cfg.get("aplatir", 1.2)
    Z = lo[2] + np.arange(sdf.shape[2]) * res
    sdf = np.maximum(sdf, (zc - Z)[None, None, :])
    lo = lo - [0, 0, zc]
    v = v - [0, 0, zc]
    print(f"plein : {time.time() - t0:.0f}s", flush=True)

    env = champ_vers_manifold(sdf, lo, res)
    inner = champ_vers_manifold(noyau(sdf, res), lo + [0.0513, 0.0371, 0.0233], res)

    regles = cfg["regles"]
    lab = etiquettes(col, [(r[0], r[1]) for r in regles])
    for s in cfg.get("symetries", []):
        noms_r = [r[0] for r in regles]
        lab = symetriser(v, lab, noms_r.index(s["ref"]) + 1, noms_r.index(s["cible"]) + 1, s["zmin"] - zc)
    mz = {i + 1: r[3] for i, r in enumerate(regles) if len(r) > 3}
    zs = zones(sdf, lo, res, v, lab, len(regles), mz)
    noms = {i + 1: r[2] for i, r in enumerate(regles)}
    fil = cfg["filaments"]
    corps = next(iter(fil))
    print(f"couleurs : {time.time() - t0:.0f}s", flush=True)

    rapport = {}
    variantes = {"figurine": [env]}
    if "pivot" in cfg:
        p = cfg["pivot"]
        fmt = FORMATS[p.get("format", "mini")]
        j = Joint(p["x"], p["y"], p.get("ang", 0.0), p.get("taille", fmt.j_body))
        cor = CrossSection([p["couloir"]]) if "couloir" in p else rect(-BIG, BIG, -BIG, BIG)
        segs = tete_pivotante(env, fmt, j, cor)
        variantes["tete-pivotante"] = segs
        rapport["tete-pivotante"] = {
            "pieces": [len(s.decompose()) for s in segs],
            "separees": len(union(segs).decompose()) == 2,
            "amplitude_deg": amplitude(segs, j),
        }
    for nom, segs in variantes.items():
        d = out_dir / nom
        d.mkdir(exist_ok=True)
        for old in d.glob("*.stl"):
            old.unlink()
        parts, exclus = couleurs(segs, zs, inner, noms, corps)
        etanche = []
        for k, (fname, ps) in enumerate(sorted(parts.items(), key=lambda kv: kv[0] != corps), 1):
            u = union(ps)
            if u.is_empty():
                continue
            path = d / f"{k}_{fname}.stl"
            to_trimesh(u).export(path)
            etanche.append(trimesh.load(path).is_watertight)
        mono = union(segs)
        to_trimesh(mono).export(d / "monocolore.stl")
        etanche.append(trimesh.load(d / "monocolore.stl").is_watertight)
        t = to_trimesh(mono)
        r = rapport.setdefault(nom, {})
        r.update({"stl_etanches": all(etanche), "details_retires": exclus,
                  "dimensions_mm": [round(float(x), 1) for x in t.extents],
                  "volume_cm3": round(float(t.volume) / 1000, 1)})
        nrm, c, ar = t.face_normals, t.triangles_center, t.area_faces
        over = (nrm[:, 2] < -math.cos(math.radians(40))) & (c[:, 2] > 0.4)
        r["surplombs_mm2"] = round(float(ar[over].sum()), 1)
        try:
            from rendu import planche, posed, render
            its = [[(ps[i], tuple(fil[fn])) for fn, ps in parts.items() if not ps[i].is_empty()]
                   for i in range(len(segs))]
            vues = [("3/4 avant", render(its, 20, 30, (700, 520))),
                    ("Face", render(its, 10, 0, (700, 520))),
                    ("Dessus", render(its, 88, -90, (700, 520))),
                    ("Arriere", render(its, 30, -150, (700, 520)))]
            if nom == "tete-pivotante":
                j = Joint(cfg["pivot"]["x"], cfg["pivot"]["y"], 0, 1)
                tourne = [[(m.translate([-j.x, -j.y, 0]).rotate([0, 0, 18]).translate([j.x, j.y, 0]), c_)
                           for m, c_ in its[0]], its[1]]
                vues[2] = ("Tete tournee", render(tourne, 25, 20, (700, 520)))
            planche(vues, f"{cfg['nom']} - {nom}", d / "apercu.png")
        except Exception as e:  # l'aperçu ne doit pas bloquer l'export
            print("aperçu :", e)
        print(nom, json.dumps(r, ensure_ascii=False), f"{time.time() - t0:.0f}s", flush=True)
    (out_dir / "rapport.json").write_text(json.dumps(rapport, indent=1, ensure_ascii=False))
    return rapport


if __name__ == "__main__":
    importer(sys.argv[1])
