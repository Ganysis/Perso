"""Transforme un modèle importé (GLB, voir importe.py) en vrai FLEXI
imprimé en place : tête pivotante et queue articulée en plusieurs segments.
La queue sculptée d'origine (souvent collée au flanc, en l'air) est remplacée
par une queue ronde posée au sol, le long du même trajet.

    python3 flexi_import.py modeles/chat_trellis.json

Paramètres dans la section "flexi" du JSON :
    format        : empilement des articulations ("mini")
    cou           : {"x", "y", "taille"} pivot de la tête
    couloir_tete  : polygone 2D autorisé pour la tête (évite la queue)
    queue         : chemin [[x, y], ...] depuis la base (dans le corps)
                    jusqu'au bout ; sortie (mm le long du chemin où la queue
                    quitte le corps), retrait (rayon de la queue sculptée
                    retirée), largeur / hauteur / bout_r (nouvelle queue),
                    espacement / taille (articulations), rayon / rayon_bout
                    (zones de découpe), rayon_v (encoche en V à la base)
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import CrossSection, JoinType, Manifold
from scipy import ndimage
from scipy.spatial import cKDTree

from importe import (champ_vers_manifold, charger, couleurs, etiquettes, noyau, solidifier,
                     symetriser, zones)
from moteur import (BIG, C, CONE_OFF, FORMATS, Joint, circle, cone, ext, rect, sd_sweep,
                    smin, to_trimesh, union, wedge_front, wedge_rear)


# --- Chemin de la queue -------------------------------------------------
def dense(P, step=0.2):
    P = np.asarray(P, float)
    out = [P[0]]
    for a, b in zip(P[:-1], P[1:]):
        n = max(1, int(np.hypot(*(b - a)) / step))
        for t in np.linspace(0, 1, n + 1)[1:]:
            out.append(a + (b - a) * t)
    Q = np.array(out)
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(Q, axis=0).T))])
    return Q, s


def point_at(Q, s, t):
    i = int(np.clip(np.searchsorted(s, t), 1, len(Q) - 1))
    d = Q[i] - Q[i - 1]
    return Q[i], math.atan2(d[1], d[0])


def tube(Q, s, s0, s1, r):
    """Zone 2D : disque de rayon r balayé le long du chemin entre s0 et s1."""
    sel = Q[(s >= s0) & (s <= s1)][::5]
    cs = CrossSection()
    for a, b in zip(sel[:-1], sel[1:]):
        cs += (circle(r, *a) + circle(r, *b)).hull()
    return cs


# --- Champ : nouvelle queue couchée au sol -------------------------------
def smax(a, b, k):
    return -smin(-a, -b, k)


def remplacer_queue(sdf, lo, res, Q, s, q, fmt):
    """Retire la queue sculptée (collée au flanc, en l'air) et la remplace
    par une queue ronde posée au sol le long du même trajet, séparée du
    flanc : c'est elle qui porte les articulations."""
    nx, ny, nz = sdf.shape
    X, Y = np.meshgrid(lo[0] + np.arange(nx) * res, lo[1] + np.arange(ny) * res, indexing="ij")
    d, i = cKDTree(Q).query(np.stack([X.ravel(), Y.ravel()], -1))
    d = d.reshape(nx, ny).astype(np.float32)
    sc = s[i].reshape(nx, ny)
    Zg = (lo[2] + np.arange(nz) * res).astype(np.float32)
    # 1) retrait (au-delà du point de sortie du corps)
    ramp = np.clip((sc - q["sortie"]) / 3.0, 0, 1).astype(np.float32)
    carve = np.where(ramp > 0, (q["retrait"] - d) * ramp - (1 - ramp) * 5, -50).astype(np.float32)
    out = smax(sdf, carve[:, :, None], 1.0).astype(np.float32)
    # 2) nouvelle queue (profil rond à fond plat, bout en boule)
    hw, top, rb = q["largeur"], q["hauteur"], q["bout_r"]
    cols = np.argwhere(d < max(hw, rb) + 4)
    Xc = (lo[0] + cols[:, 0] * res).astype(np.float32)[:, None]
    Yc = (lo[1] + cols[:, 1] * res).astype(np.float32)[:, None]
    shp = (len(cols), nz)
    Xb, Yb, Zb = (np.broadcast_to(Xc, shp), np.broadcast_to(Yc, shp),
                  np.broadcast_to(Zg[None, :], shp))
    Qs = Q[::5]
    tail = sd_sweep(Xb, Yb, Zb, Qs, np.full(len(Qs), hw), -2.0, top, min(hw, top / 2) * 0.95)
    h = math.atan2(*(Q[-1] - Q[-6])[::-1])
    cb = Q[-1] - np.array([math.cos(h), math.sin(h)]) * rb * 0.5
    ball = (np.sqrt((Xb - cb[0]) ** 2 + (Yb - cb[1]) ** 2 + (Zb - rb * 0.85) ** 2) - rb)
    tail = smin(tail, ball.astype(np.float32), 2.0)
    k = np.where(sc[cols[:, 0], cols[:, 1]] < q["sortie"] + 4, 3.0, 0.2).astype(np.float32)[:, None]
    sub = out[cols[:, 0], cols[:, 1]]
    out[cols[:, 0], cols[:, 1]] = smin(sub, tail.astype(np.float32), k)
    return np.maximum(out, -Zg[None, None, :]), d


# --- Segmentation ------------------------------------------------------
def joint_cut(fmt, j):
    """Cavité de la chape (côté segment avant de l'articulation)."""
    cavity2d = circle(j.rt + C) + (circle(j.rf + 1.0) ^ rect(-BIG, 0.2, -BIG, BIG))
    cut = ext(cavity2d, fmt.low_top, fmt.up_bot)
    apex = fmt.tongue_top + j.cr + CONE_OFF
    cut += cone(fmt.up_bot - 0.01, apex - fmt.up_bot + 0.01, apex)
    return j.place3(cut), j.place3(cone(fmt.low_top - 0.01, j.cr + 0.01, fmt.low_top + j.cr))


def joint_tongue(fmt, j):
    tongue2d = circle(j.rt) + rect(-j.rf - C - 1.0, 0, -j.nw / 2, j.nw / 2)
    tongue = ext(tongue2d, fmt.tongue_bot, fmt.tongue_top)
    apex = fmt.low_top + j.cr + CONE_OFF
    tongue -= cone(fmt.tongue_bot - 0.01, apex - fmt.tongue_bot + 0.01, apex)
    tongue += cone(fmt.tongue_top - 0.01, j.cr + 0.01, fmt.tongue_top + j.cr)
    return j.place3(tongue)


def plus_gros(m):
    parts = sorted(m.decompose(), key=lambda p: -p.volume())
    return (parts[0] if parts else m), sum(p.volume() for p in parts[1:])


def bowtie(j):
    """Zone en V (des deux côtés) autour d'une articulation : l'espace qui
    permet aux deux pièces de tourner l'une par rapport à l'autre."""
    return j.place2(rect(-BIG, BIG, -BIG, BIG) - wedge_front() - wedge_rear())


def construire(env, fmt, fx, Q, s):
    """Régions 2D, puis segments 3D avec leurs articulations."""
    cou = Joint(fx["cou"]["x"], fx["cou"]["y"], 0.0, fx["cou"].get("taille", fmt.j_body))
    q = fx["queue"]
    tj, s_j = [], []
    for sk in np.arange(q.get("debut", 0.0), s[-1] - q.get("bout", 12.0), q["espacement"]):
        p, h = point_at(Q, s, sk)
        tj.append(Joint(p[0], p[1], math.degrees(h) + 180.0, q["taille"]))
        s_j.append(sk)

    regs = {}
    for k in range(len(tj)):
        a = tj[k]
        der = k + 1 == len(tj)
        s1 = s[-1] if der else s_j[k + 1]
        r = q["rayon_bout"] if der else q["rayon"]
        reg = tube(Q, s, max(s_j[k] - 10, 0), s1 if der else s1 + 10, q["rayon"])
        if der:
            reg += tube(Q, s, s1 - 14, s1, r)
        reg = (reg - a.place2(circle(a.rf + C))) ^ a.place2(wedge_rear())
        if not der:
            b = tj[k + 1]
            reg = (reg ^ b.place2(wedge_front())) + b.place2(circle(b.rf))
        regs[f"queue{k + 1}"] = reg
    q_all = CrossSection()
    for r in regs.values():
        q_all += r
    q_off = q_all.offset(C, JoinType.Round)

    couloir = CrossSection([fx["couloir_tete"]])
    tete = ((couloir ^ cou.place2(wedge_front())) + cou.place2(circle(cou.rf))) - q_off
    b0 = tj[0]
    corps = (rect(-BIG, BIG, -BIG, BIG) - tete.offset(C, JoinType.Round) - q_off
             - (bowtie(cou) ^ couloir) - (bowtie(b0) ^ circle(q.get("rayon_v", 18.0), b0.x, b0.y)))
    corps += b0.place2(circle(b0.rf))
    corps -= q_off
    regions = {"tete": tete, "corps": corps, **regs}

    solids = {n: ext(r, -1, 200) ^ env for n, r in regions.items()}
    # articulations : (joint, segment avant = chape, segment arrière = languette)
    liens = [(cou, "tete", "corps"), (b0, "corps", "queue1")]
    liens += [(tj[k], f"queue{k}", f"queue{k + 1}") for k in range(1, len(tj))]
    for j, av, ar in liens:
        cut, tenon = joint_cut(fmt, j)
        solids[av] = (solids[av] - cut) + tenon
        solids[ar] = solids[ar] + joint_tongue(fmt, j)
    perdu = {}
    for n in solids:
        solids[n], v = plus_gros(solids[n])
        if v > 1:
            perdu[n] = round(v, 1)
    return solids, liens, perdu


def controles(solids, liens):
    noms = list(solids)
    res = {"pieces": {n: len(m.decompose()) for n, m in solids.items()}}
    tout = union(solids.values())
    res["toutes_separees"] = len(tout.decompose()) == len(solids)
    bad = []
    for j, av, ar in liens:
        for d in [(0.3, 0, 0), (-0.3, 0, 0), (0, 0.3, 0), (0, -0.3, 0), (0, 0, 0.3), (0, 0, -0.3)]:
            if (solids[av].translate(list(d)) ^ solids[ar]).volume() > 1e-3:
                bad.append(f"{av}/{ar}")
                break
    res["jeux_insuffisants"] = bad
    amp = {}
    for j, av, ar in liens:
        # on fait tourner le segment arrière et tout ce qui le suit ? non :
        # amplitude locale = segment arrière seul contre le segment avant
        out = []
        for sg in (1, -1):
            ok = 0
            for a in range(2, 32, 2):
                r = solids[ar].translate([-j.x, -j.y, 0]).rotate([0, 0, a * sg]) \
                    .translate([j.x, j.y, 0])
                if (r ^ solids[av]).volume() > 1e-2:
                    break
                ok = a
            out.append(ok)
        amp[f"{av}/{ar}"] = out
    res["amplitude_deg"] = amp
    return res


def main(cfg_path):
    t0 = time.time()
    cfg = json.loads(Path(cfg_path).read_text())
    base = Path(cfg_path).parent
    fx = cfg["flexi"]
    fmt = FORMATS[fx.get("format", "mini")]
    out_dir = Path(__file__).parent / "sorties" / cfg["nom"] / "flexi"
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
    zc = cfg.get("aplatir", 1.2)
    Z = lo[2] + np.arange(sdf.shape[2]) * res
    sdf = np.maximum(sdf, (zc - Z)[None, None, :])
    lo = lo - [0, 0, zc]
    v = v - [0, 0, zc]

    # couleurs lues sur le modèle d'origine (le visage n'est pas modifié)
    regles = cfg["regles"]
    lab = etiquettes(col, [(r[0], r[1]) for r in regles])
    for sy in cfg.get("symetries", []):
        noms_r = [r[0] for r in regles]
        lab = symetriser(v, lab, noms_r.index(sy["ref"]) + 1, noms_r.index(sy["cible"]) + 1,
                         sy["zmin"] - zc)
    mz = {i + 1: r[3] for i, r in enumerate(regles) if len(r) > 3}
    zs = zones(sdf, lo, res, v, lab, len(regles), mz)

    # queue sculptée remplacée par une queue ronde au sol, articulable
    q = fx["queue"]
    Q, s = dense(q["chemin"])
    sdf2, d = remplacer_queue(sdf, lo, res, Q, s, q, fmt)
    print(f"champ : {time.time() - t0:.0f}s", flush=True)

    env = champ_vers_manifold(sdf2, lo, res)
    inner = champ_vers_manifold(noyau(sdf2, res), lo + [0.0513, 0.0371, 0.0233], res)
    solids, liens, perdu = construire(env, fmt, fx, Q, s)
    print(f"segments : {time.time() - t0:.0f}s", flush=True)

    rap = controles(solids, liens)
    rap["matiere_ecartee_mm3"] = perdu
    noms = {i + 1: r[2] for i, r in enumerate(regles)}
    fil = cfg["filaments"]
    corps = next(iter(fil))
    segs = list(solids.values())
    parts, exclus = couleurs(segs, zs, inner, noms, corps)
    for old in out_dir.glob("*.stl"):
        old.unlink()
    etanche = []
    for k, (fname, ps) in enumerate(sorted(parts.items(), key=lambda kv: kv[0] != corps), 1):
        u = union(ps)
        if u.is_empty():
            continue
        p = out_dir / f"{k}_{fname}.stl"
        to_trimesh(u).export(p)
        etanche.append(trimesh.load(p).is_watertight)
    mono = union(segs)
    to_trimesh(mono).export(out_dir / "monocolore.stl")
    etanche.append(trimesh.load(out_dir / "monocolore.stl").is_watertight)
    t = to_trimesh(mono)
    nrm, cc, ar = t.face_normals, t.triangles_center, t.area_faces
    over = (nrm[:, 2] < -math.cos(math.radians(40))) & (cc[:, 2] > 0.4)
    near = np.zeros(len(cc), bool)
    for j, _, _ in liens:
        near |= (np.hypot(cc[:, 0] - j.x, cc[:, 1] - j.y) < j.rf + 1.5) & (cc[:, 2] < fmt.top + 0.2)
    rap.update({"stl_etanches": all(etanche), "details_retires": exclus,
                "dimensions_mm": [round(float(x), 1) for x in t.extents],
                "volume_cm3": round(float(t.volume) / 1000, 1),
                "surplombs_mm2": round(float(ar[over & ~near].sum()), 1)})
    (out_dir / "rapport.json").write_text(json.dumps(rap, indent=1, ensure_ascii=False))
    print(json.dumps(rap, ensure_ascii=False), f"{time.time() - t0:.0f}s", flush=True)

    # aperçus
    from rendu import planche, render
    its = [[(parts[fn][i], tuple(fil[fn])) for fn in parts if not parts[fn][i].is_empty()]
           for i in range(len(segs))]
    noms_s = list(solids)
    pose = {n: 0.0 for n in noms_s}

    def poser(angles):
        """angles : {nom_articulation_arriere: degrés}, cumulés le long de la queue."""
        out = []
        for i, n in enumerate(noms_s):
            items = its[i]
            chaine = []
            if n == "tete":
                chaine = [(liens[0][0], angles.get("tete", 0))]
            elif n.startswith("queue"):
                k = int(n[5:])
                chaine = [(liens[1 + m][0], angles.get(f"queue{m + 1}", 0)) for m in range(k)][::-1]
            its2 = []
            for m_, c_ in items:
                for j, a in chaine:
                    m_ = m_.translate([-j.x, -j.y, 0]).rotate([0, 0, a]).translate([j.x, j.y, 0])
                its2.append((m_, c_))
            out.append(its2)
        return out

    nq = len([n for n in noms_s if n.startswith("queue")])
    vague = {"tete": -15, **{f"queue{k}": (14 if k % 2 else -14) for k in range(2, nq + 1)}}
    vues = [("3/4 avant", render(its, 20, 30, (700, 520))),
            ("Face", render(its, 10, 0, (700, 520))),
            ("Dessus", render(its, 88, -90, (700, 520))),
            ("Ca bouge : tete + queue", render(poser(vague), 55, -60, (700, 520)))]
    planche(vues, f"{cfg['nom']} - flexi", out_dir / "apercu.png")
    print(f"fini {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1])
