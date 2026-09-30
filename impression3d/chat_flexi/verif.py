"""Vérifie jeux, connexité, amplitude des articulations et surplombs."""
import numpy as np
import trimesh

from chat_flexi import JOINTS, build, merged

segs = build()
p = [merged(s) for s in segs]
print("corps par segment:", [len(q.decompose()) for q in p])
bad = 0
for i in range(len(p) - 1):
    for d in [(0.3, 0, 0), (-0.3, 0, 0), (0, 0.3, 0), (0, -0.3, 0), (0, 0, 0.3), (0, 0, -0.3)]:
        if (p[i].translate(list(d)) ^ p[i + 1]).volume() > 1e-3:
            bad += 1
print("jeux < 0.3 mm:", bad)
for i, j in enumerate(JOINTS):
    ok = 0
    for a in range(2, 62, 2):
        if any((p[i + 1].translate([-j.x, 0, 0]).rotate([0, 0, a * s])
                .translate([j.x, 0, 0]) ^ p[i]).volume() > 1e-2 for s in (1, -1)):
            break
        ok = a
    print(f"articulation {i} (x={j.x}) : ±{ok}°")

# surplombs extérieurs > 50° (hors fond et hors mécanisme interne)
t = trimesh.load("chat_monocolore.stl")
n, c, a = t.face_normals, t.triangles_center, t.area_faces
over = (n[:, 2] < -np.cos(np.radians(40))) & (c[:, 2] > 0.3)
outer = over & ~((c[:, 2] > 2.9) & (c[:, 2] < 7.1))
print(f"surplombs > 50° hors articulations : {a[outer].sum():.1f} mm² "
      f"(sur {a.sum():.0f} mm²)")
if outer.any():
    print("  zones z:", np.round(np.percentile(c[outer, 2], [0, 50, 100]), 1),
          " x:", np.round(np.percentile(c[outer, 0], [0, 50, 100]), 1))
