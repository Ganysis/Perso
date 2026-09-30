"""Rendu d'aperçu (PNG) du chat avec un petit rasteriseur z-buffer."""
import numpy as np
from PIL import Image, ImageDraw
from chat_flexi import build, JOINTS, COLORS

J = [j.x for j in JOINTS]


def colored(segs):
    """Liste (Manifold, couleur) à partir des segments."""
    return [[(m, COLORS[k]) for k, m in s.items() if k in COLORS] for s in segs]


def posed(segs, angles):
    out = [segs[0]]
    for i in range(1, len(segs)):
        items = []
        for m, col in segs[i]:
            for k in range(i - 1, -1, -1):
                x = J[k]
                m = m.translate([-x, 0, 0]).rotate([0, 0, angles[k]]).translate([x, 0, 0])
            items.append((m, col))
        out.append(items)
    return out


def render(parts, elev, azim, size=(900, 600), zoom=1.0, center=None):
    W, Hh = size
    e, a = np.radians(elev), np.radians(azim)
    fwd = -np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    up0 = np.array([0, 0, 1.0]) if abs(elev) < 89 else np.array([1.0, 0, 0])
    right = np.cross(fwd, up0); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    tris, cols = [], []
    light = -fwd + np.array([0.3, -0.4, 0.6]); light /= np.linalg.norm(light)
    flat = [it for seg in parts for it in seg]
    for m, color in flat:
        mesh = m.to_mesh()
        v = np.asarray(mesh.vert_properties)[:, :3]
        t = v[np.asarray(mesh.tri_verts)]
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        sh = 0.45 + 0.6 * np.clip(n @ light, 0, 1)
        tris.append(t); cols.append(sh[:, None] * np.array(color))
    T = np.vstack(tris); Cc = np.vstack(cols)
    P = np.stack([T @ right, T @ up, T @ fwd], axis=-1)
    allp = P.reshape(-1, 3)
    c = (allp.max(0) + allp.min(0)) / 2 if center is None else center
    span = max((allp[:, 0].max() - allp[:, 0].min()) / W,
               (allp[:, 1].max() - allp[:, 1].min()) / Hh) * 1.08 / zoom
    px = (P[..., 0] - c[0]) / span + W / 2
    py = Hh / 2 - (P[..., 1] - c[1]) / span
    pz = P[..., 2]
    zbuf = np.full((Hh, W), np.inf); img = np.full((Hh, W, 3), 255.0)
    for k in range(len(T)):
        x, y, z = px[k], py[k], pz[k]
        x0, x1 = int(max(np.floor(x.min()), 0)), int(min(np.ceil(x.max()), W - 1))
        y0, y1 = int(max(np.floor(y.min()), 0)), int(min(np.ceil(y.max()), Hh - 1))
        if x0 > x1 or y0 > y1:
            continue
        d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(d) < 1e-9:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        l0 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
        l1 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
        l2 = 1 - l0 - l1
        inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if not inside.any():
            continue
        zz = l0 * z[0] + l1 * z[1] + l2 * z[2]
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        upd = inside & (zz < sub)
        sub[upd] = zz[upd]
        img[y0:y1 + 1, x0:x1 + 1][upd] = Cc[k]
    return Image.fromarray(img.clip(0, 255).astype(np.uint8))


if __name__ == "__main__":
    segs = colored(build())
    wave = posed(segs, [14, -16, -18, 22, 24, 24, 24])
    views = [
        ("3/4 avant", render(segs, 22, 35)),
        ("Profil", render(segs, 8, 90)),
        ("Articule : ca gigote !", render(wave, 70, -90)),
        ("Face", render(segs[:2], 8, 0, zoom=1.0)),
    ]
    W, Hh = 900, 600
    sheet = Image.new("RGB", (W * 2, (Hh + 40) * 2), "white")
    dr = ImageDraw.Draw(sheet)
    for i, (title, im) in enumerate(views):
        ox, oy = (i % 2) * W, (i // 2) * (Hh + 40)
        sheet.paste(im, (ox, oy + 40))
        dr.text((ox + 20, oy + 12), title, fill="black")
    sheet.save("apercu.png")
    print("ok")
