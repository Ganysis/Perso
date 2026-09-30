"""Aperçus PNG (petit rasteriseur z-buffer, sans dépendance GPU)."""
import numpy as np
from PIL import Image, ImageDraw

FOND = (250, 246, 240)


def items(modele, palette):
    """Liste par segment de (Manifold, couleur RGB) pour une palette."""
    pal = modele.animal.palettes[palette]
    parts = modele.couleurs(palette)
    n = len(modele.segments)
    return [[(parts[f][i], pal["filaments"][f]) for f in parts if not parts[f][i].is_empty()]
            for i in range(n)]


def posed(segs, joints, angles):
    """Rotations cumulées aux articulations (angles en degrés)."""
    out = [segs[0]]
    for i in range(1, len(segs)):
        its = []
        for m, col in segs[i]:
            for k in range(i - 1, -1, -1):
                j = joints[k]
                m = m.translate([-j.x, -j.y, 0]).rotate([0, 0, angles[k]]).translate([j.x, j.y, 0])
            its.append((m, col))
        out.append(its)
    return out


def render(parts, elev, azim, size=(900, 600), zoom=1.0, bg=FOND):
    W, Hh = size
    e, a = np.radians(elev), np.radians(azim)
    fwd = -np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    up0 = np.array([0, 0, 1.0]) if abs(elev) < 89 else np.array([1.0, 0, 0])
    right = np.cross(fwd, up0)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    light = -fwd + np.array([0.3, -0.4, 0.6])
    light /= np.linalg.norm(light)
    tris, cols = [], []
    for seg in parts:
        for m, color in seg:
            mesh = m.simplify(0.03).to_mesh()
            v = np.asarray(mesh.vert_properties)[:, :3]
            t = v[np.asarray(mesh.tri_verts)]
            n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
            n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
            sh = 0.5 + 0.55 * np.clip(n @ light, 0, 1)
            tris.append(t)
            cols.append(sh[:, None] * np.array(color))
    T = np.vstack(tris)
    Cc = np.vstack(cols)
    P = np.stack([T @ right, T @ up, T @ fwd], axis=-1)
    allp = P.reshape(-1, 3)
    c = (allp.max(0) + allp.min(0)) / 2
    span = max((allp[:, 0].max() - allp[:, 0].min()) / W,
               (allp[:, 1].max() - allp[:, 1].min()) / Hh) * 1.12 / zoom
    px = (P[..., 0] - c[0]) / span + W / 2
    py = Hh / 2 - (P[..., 1] - c[1]) / span
    pz = P[..., 2]
    zbuf = np.full((Hh, W), np.inf)
    img = np.empty((Hh, W, 3))
    img[:] = bg
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


def planche(vues, titre, path, W=700, Hh=520, cols=2):
    rows = (len(vues) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, (Hh + 30) * rows + 40), FOND)
    dr = ImageDraw.Draw(sheet)
    dr.text((20, 12), titre, fill=(60, 50, 50))
    for i, (t, im) in enumerate(vues):
        ox, oy = (i % cols) * W, 40 + (i // cols) * (Hh + 30)
        sheet.paste(im.resize((W, Hh)), (ox, oy + 30))
        dr.text((ox + 20, oy + 10), t, fill=(90, 80, 80))
    sheet.save(path)


def apercu(modele, palette, path):
    segs = items(modele, palette)
    n = len(modele.geo.joints)
    wave = posed(segs, modele.geo.joints, [12, -15, -15] + [18] * (n - 3))
    vues = [("3/4 avant", render(segs, 25, 35, (700, 520))),
            ("Dessus", render(segs, 88, -90, (700, 520))),
            ("Articule", render(wave, 60, -60, (700, 520))),
            ("Face", render(segs, 6, 0, (700, 520), zoom=1.6))]
    titre = f"{modele.animal.nom} - {modele.fmt.nom} - {palette}" + (
        f" - {modele.tenue}" if modele.tenue else "")
    planche(vues, titre, path)
    return vues[0][1]
