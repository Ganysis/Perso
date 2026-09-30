"""Vérifie jeux, connexité et amplitude des articulations."""
from chat_flexi import build, JOINTS

p = build()
print("corps par pièce:", [len(q.decompose()) for q in p])
bad = 0
for i in range(len(p) - 1):
    for d in [(0.3, 0, 0), (-0.3, 0, 0), (0, 0.3, 0), (0, -0.3, 0), (0, 0, 0.3), (0, 0, -0.3)]:
        if (p[i].translate(list(d)) ^ p[i + 1]).volume() > 1e-4:
            bad += 1
print("jeux < 0.3 mm:", bad)
for i, j in enumerate(JOINTS):
    ok = 0
    for a in range(2, 92, 2):
        if any((p[i + 1].translate([-j.x, 0, 0]).rotate([0, 0, a * s])
                .translate([j.x, 0, 0]) ^ p[i]).volume() > 1e-3 for s in (1, -1)):
            break
        ok = a
    print(f"articulation {i} (x={j.x}) : ±{ok}°")
