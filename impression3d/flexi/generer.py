"""Génère la collection : STL par filament, version monocolore, aperçus,
et vérifie chaque modèle (pièces séparées, jeux, articulations, surplombs,
étanchéité).

    python3 generer.py                 # toute la collection
    python3 generer.py chat mini       # un animal / un format
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import trimesh

from animaux import ANIMAUX
from moteur import Modele, to_trimesh, union
from rendu import apercu, planche

SORTIES = Path(__file__).parent / "sorties"

# (animal, format, tenue) -> palettes
COLLECTION = [
    ("chat", "mini", None, ["roux", "calico", "gris", "tigre"]),
    ("chat", "mini", "noeud", ["gris"]),
    ("chat", "mini", "collier", ["roux"]),
    ("chat", "porte-cles", None, ["roux", "calico"]),
    ("renard", "mini", None, ["roux", "arctique"]),
    ("renard", "porte-cles", None, ["roux"]),
]


def verifier(m):
    """Contrôles géométriques ; renvoie un dict de résultats."""
    segs = m.segments
    J = m.geo.joints
    res = {"corps_par_segment": [len(s.decompose()) for s in segs]}
    total = union(segs)
    res["pieces_disjointes"] = len(total.decompose())
    bad = 0
    for i in range(len(segs) - 1):
        for d in [(0.3, 0, 0), (-0.3, 0, 0), (0, 0.3, 0), (0, -0.3, 0), (0, 0, 0.3), (0, 0, -0.3)]:
            if (segs[i].translate(list(d)) ^ segs[i + 1]).volume() > 1e-3:
                bad += 1
    res["jeux_insuffisants"] = bad
    amp = []
    for i, j in enumerate(J):
        ok = 0
        for a in range(4, 44, 4):
            hit = False
            for s in (1, -1):
                r = segs[i + 1].translate([-j.x, -j.y, 0]).rotate([0, 0, a * s]) \
                    .translate([j.x, j.y, 0])
                if (r ^ segs[i]).volume() > 1e-2:
                    hit = True
                    break
            if hit:
                break
            ok = a
        amp.append(ok)
    res["amplitude_deg"] = amp
    # surplombs > 50° hors mécanismes d'articulation
    t = to_trimesh(total)
    n, c, ar = t.face_normals, t.triangles_center, t.area_faces
    over = (n[:, 2] < -np.cos(np.radians(40))) & (c[:, 2] > 0.4)
    near = np.zeros(len(c), bool)
    for j in J:
        near |= (np.hypot(c[:, 0] - j.x, c[:, 1] - j.y) < j.rf + 1.5) & (c[:, 2] < m.fmt.top + 0.2)
    res["surplombs_mm2"] = round(float(ar[over & ~near].sum()), 1)
    res["dimensions_mm"] = [round(float(v), 1) for v in t.extents]
    res["volume_cm3"] = round(float(t.volume) / 1000, 2)
    res["poids_pla_g"] = round(float(t.volume) / 1000 * 1.24, 1)
    return res, t


def ok(res):
    return (all(v == 1 for v in res["corps_par_segment"])
            and res["pieces_disjointes"] == len(res["corps_par_segment"])
            and res["jeux_insuffisants"] == 0
            and min(res["amplitude_deg"]) >= 16
            and res.get("stl_etanches", True))


def generer(filtre=()):
    SORTIES.mkdir(exist_ok=True)
    rapport = {}
    vignettes = []
    for animal, fmt, tenue, palettes in COLLECTION:
        if filtre and (animal, fmt)[:len(filtre)] != tuple(filtre):
            continue
        t0 = time.time()
        nom = f"{animal}_{fmt}" + (f"_{tenue}" if tenue else "")
        dossier = SORTIES / nom
        dossier.mkdir(exist_ok=True)
        m = Modele(ANIMAUX[animal](), fmt, tenue)
        res, mono = verifier(m)
        mono.export(dossier / "monocolore.stl")
        etanche = [trimesh.load(dossier / "monocolore.stl").is_watertight]
        for pal in palettes:
            d = dossier / pal
            d.mkdir(exist_ok=True)
            for old in d.glob("*.stl"):
                old.unlink()
            parts = m.couleurs(pal)
            for k, (fil, ps) in enumerate(parts.items(), 1):
                u = union(ps)
                if u.is_empty():
                    continue
                path = d / f"{k}_{fil}.stl"
                to_trimesh(u).export(path)
                etanche.append(trimesh.load(path).is_watertight)
            vignettes.append((f"{animal} {fmt} {pal}" + (f" {tenue}" if tenue else ""),
                              apercu(m, pal, d / "apercu.png")))
        res["stl_etanches"] = all(etanche)
        res["details_retires"] = {p: e for p, e in m.exclus.items() if e}
        res["valide"] = ok(res)
        res["duree_s"] = round(time.time() - t0)
        rapport[nom] = res
        print(nom, json.dumps(res, ensure_ascii=False), flush=True)
    if not filtre:
        (SORTIES / "rapport.json").write_text(json.dumps(rapport, indent=1, ensure_ascii=False))
        planche(vignettes, "Collection Flexi Kawaii", SORTIES / "collection.png",
                W=560, Hh=420, cols=4)
    return rapport


if __name__ == "__main__":
    r = generer(sys.argv[1:])
    sys.exit(0 if all(v["valide"] for v in r.values()) else 1)
