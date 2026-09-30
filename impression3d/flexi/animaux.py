"""Animaux de la collection « Flexi Kawaii ».

Chaque animal ne décrit que ce qui lui est propre : oreilles, parties en
plus (joues, museau), queue, zones de couleur et palettes. Tout le reste
(format, articulations, visage, export) vient du moteur.

Coordonnées « design » (chat v2 de 13 cm), multipliées par l'échelle S.
Palette : 4 filaments max ; "elements" associe chaque zone à un filament,
les zones absentes prennent la couleur du corps.
"""
import math

import numpy as np
from manifold3d import CrossSection, Manifold

from moteur import (BIG, both_sides, box, circle, ellipsoid, ext, mirror_y, polygon,
                    prism_x, rounded, sd_ellipsoid, sd_round_cone)

ORANGE = (255, 150, 60)
BLANC = (250, 248, 242)
NOIR = (40, 36, 40)
ROSE = (255, 140, 170)
GRIS = (150, 156, 168)
GRIS_CLAIR = (200, 205, 215)


class Animal:
    nom = "animal"
    head_c = (10.0, 0.0, 11.0)
    head_r = (16.0, 19.0, 16.0)
    body_len = 48.0
    body_ry = 14.0
    muzzle_w = 1.0
    muzzle_h = 1.0
    tail_tip = 1.2        # rayon du bout de queue / demi-largeur de queue
    tail_bulge = 0.0      # élargissement de la queue vers le bout
    tail_top_extra = 0.0
    # oreilles : base, pointe, rayons (coordonnées design, côté +Y)
    ear = ((7.0, 11.0, 21.0), (9.0, 15.5, 32.0), 5.0, 1.4)
    palettes = {}
    tenue = None

    # --- formes ---------------------------------------------------------
    def ear_parts(self, geo, X, Y, Z):
        S = geo.S
        b, t, r1, r2 = self.ear
        b = tuple(v * S for v in b)
        t = tuple(v * S for v in t)
        out = []
        for s in (1, -1):
            bb, tt = (b, t) if s > 0 else (mirror_y(b), mirror_y(t))
            out.append((sd_round_cone(X, Y, Z, bb, tt, r1 * S, r2 * S), 2.0 * S))
        return out

    def head_parts(self, geo, X, Y, Z):
        parts = self.ear_parts(geo, X, Y, Z)
        if self.tenue == "noeud":
            for c, r in self.bow(geo):
                parts.append((sd_ellipsoid(X, Y, Z, c, r), 0.6 * geo.S))
        return parts

    def extra_parts(self, geo, X, Y, Z):
        return []

    def bow(self, geo):
        """Nœud posé sur la tête, à gauche entre les oreilles."""
        S = geo.S
        cx, cy, cz = 7.0 * S, -7.5 * S, (self.head_c[2] + self.head_r[2] * 0.93 + 1.2) * S
        return [((cx, cy - 3.6 * S, cz - 0.2 * S), (2.6 * S, 3.4 * S, 2.3 * S)),
                ((cx, cy + 3.6 * S, cz - 0.2 * S), (2.6 * S, 3.4 * S, 2.3 * S)),
                ((cx, cy, cz), (1.7 * S, 1.7 * S, 1.9 * S))]

    # --- zones de couleur ---------------------------------------------
    def inner_ear(self, geo):
        S = geo.S
        b, t, r1, _ = self.ear
        by, bz, ty, tz = b[1], b[2], t[1], t[2]
        ax, az = ty - by, tz - bz
        L = math.hypot(ax, az)
        ux, uz = ax / L, az / L
        px, pz = uz, -ux
        p0 = (by + ux * L * 0.35, bz + uz * L * 0.35)
        w = r1 * (1 - 0.35 * 0.7) * 0.6
        tri = [(p0[0] + px * w, p0[1] + pz * w), (p0[0] - px * w, p0[1] - pz * w),
               (by + ux * L * 0.82, bz + uz * L * 0.82)]
        cs = CrossSection()
        for s in (1, -1):
            cs += rounded(polygon([(y * S * s, z * S) for y, z in tri]), 0.6 * S)
        return prism_x(cs, (b[0] + 1.0) * S)

    def socks(self, geo):
        S = geo.S
        m = Manifold()
        for c, r in geo.paws:
            m += box(c[0] - r[0] - 1.0 * S, c[0] + r[0] + 1.0 * S, c[1] - 1.0 * S,
                     c[1] + r[1] + 1.5, -5, c[2] + r[2] + 0.6 * S)
        return both_sides(m)

    def tail_end(self, geo, frac=0.35):
        h = geo.heading[-1]
        d = np.array([math.cos(h), math.sin(h)])
        q = geo.tip - d * geo.tip_r * frac
        half = box(0, 60, -60, 60, -5, 60).rotate([0, 0, math.degrees(h)]) \
            .translate([q[0], q[1], 0])
        ball = Manifold.sphere(geo.tip_r * 1.45, 48).translate(
            [geo.tip[0], geo.tip[1], geo.tip_r * 0.75])
        if geo.ring is not None:
            (rx, ry), rm, w = geo.ring
            ball += Manifold.cylinder(10, rm + w + 1.5, rm + w + 1.5, 48).translate([rx, ry, -2])
        return half ^ ball

    def collar(self, geo):
        j = geo.joints[0]
        r0 = j.rf + 0.2
        band = circle(r0 + 2.4 * geo.S + 0.8) - circle(r0)
        return ext(band.translate([j.x, j.y]), 2.2, 60)

    def regions(self, geo):
        r = {"oreilles_int": self.inner_ear(geo),
             "chaussettes": self.socks(geo),
             "bout_queue": self.tail_end(geo)}
        if self.tenue == "noeud":
            m = Manifold()
            for c, rr in self.bow(geo):
                m += ellipsoid(c, [v + 0.35 for v in rr])
            r["accessoire"] = m
        elif self.tenue == "collier":
            r["accessoire"] = self.collar(geo)
        return r


# ------------------------------------------------------------------------
class Chat(Animal):
    nom = "chat"
    palettes = {
        "roux": {"filaments": {"orange": ORANGE, "blanc": BLANC, "noir": NOIR, "rose": ROSE},
                 "elements": {"corps": "orange", "museau": "blanc", "chaussettes": "blanc",
                              "bout_queue": "blanc", "reflets": "blanc", "yeux": "noir",
                              "bouche": "noir", "nez": "rose", "joues": "rose",
                              "oreilles_int": "rose", "accessoire": "rose"}},
        "gris": {"filaments": {"gris": GRIS, "blanc": BLANC, "noir": NOIR, "rose": ROSE},
                 "elements": {"corps": "gris", "museau": "blanc", "chaussettes": "blanc",
                              "bout_queue": "blanc", "reflets": "blanc", "yeux": "noir",
                              "bouche": "noir", "nez": "rose", "joues": "rose",
                              "oreilles_int": "rose", "accessoire": "rose"}},
        "calico": {"filaments": {"blanc": BLANC, "orange": ORANGE, "noir": NOIR, "rose": ROSE},
                   "elements": {"corps": "blanc", "taches_couleur": "orange",
                                "taches_noir": "noir", "bout_queue": "orange",
                                "reflets": "blanc", "yeux": "noir", "bouche": "noir",
                                "nez": "rose", "joues": "rose", "oreilles_int": "rose",
                                "accessoire": "rose"}},
        "tigre": {"filaments": {"orange": ORANGE, "noir": NOIR, "blanc": BLANC, "rose": ROSE},
                  "elements": {"corps": "orange", "rayures": "noir", "museau": "blanc",
                               "chaussettes": "blanc", "reflets": "blanc", "yeux": "noir",
                               "bouche": "noir", "nez": "rose", "joues": "rose",
                               "oreilles_int": "rose", "accessoire": "rose"}},
    }

    def regions(self, geo):
        r = super().regions(geo)
        S = geo.S
        bc, br = geo.body_c, geo.body_r
        top = bc[2] + br[2]
        hc, hr = geo.head_c, geo.head_r
        # calico : taches
        r["taches_couleur"] = (
            ellipsoid((hc[0] - 0.4 * hr[0], -0.5 * hr[1], hc[2] + hr[2]),
                      (0.55 * hr[0], 0.45 * hr[1], 0.45 * hr[2]))
            + ellipsoid((bc[0] + 0.25 * br[0], -0.35 * br[1], top),
                        (0.33 * br[0], 0.5 * br[1], 0.45 * br[2])))
        r["taches_noir"] = (
            ellipsoid((hc[0] - 0.5 * hr[0], 0.58 * hr[1], hc[2] + 0.9 * hr[2]),
                      (0.42 * hr[0], 0.36 * hr[1], 0.42 * hr[2]))
            + ellipsoid((bc[0] - 0.45 * br[0], 0.3 * br[1], top),
                        (0.28 * br[0], 0.5 * br[1], 0.45 * br[2])))
        # tigré : rayures sur le front, le dos et la queue
        w = max(1.4 * S, 1.0)
        rayures = Manifold()
        for y in (-3.6 * S, 0.0, 3.6 * S):
            rayures += box(hc[0] - 2 * S, BIG, y - w / 2, y + w / 2,
                           hc[2] + 0.74 * hr[2], BIG)
        x0, xn = geo.joints[0].x, geo.joints[geo.n_body_joints - 1].x
        for k in range(5):
            x = x0 - (k + 0.6) * (x0 - xn) / 5.2
            rayures += box(x - w / 2, x + w / 2, -BIG, BIG, 0.42 * top, BIG)
        for frac in (0.22, 0.45, 0.68):
            p, h = geo.tail_point(frac)
            rayures += box(-w / 2, w / 2, -20, 20, 2.0, 40).rotate([0, 0, math.degrees(h)]) \
                .translate([p[0], p[1], 0])
        r["rayures"] = rayures
        return r


# ------------------------------------------------------------------------
class Renard(Animal):
    nom = "renard"
    head_r = (15.5, 20.0, 15.5)
    ear = ((5.5, 10.5, 20.5), (7.5, 16.5, 36.0), 6.0, 1.0)
    muzzle_w = 1.25
    muzzle_h = 1.15
    tail_tip = 1.55
    tail_bulge = 0.45
    palettes = {
        "roux": {"filaments": {"orange": ORANGE, "blanc": BLANC, "noir": NOIR, "rose": ROSE},
                 "elements": {"corps": "orange", "museau": "blanc", "bout_queue": "blanc",
                              "reflets": "blanc", "yeux": "noir", "bouche": "noir",
                              "nez": "noir", "chaussettes": "noir", "bout_oreilles": "noir",
                              "joues": "rose", "oreilles_int": "rose", "accessoire": "rose"}},
        "arctique": {"filaments": {"blanc": BLANC, "gris": GRIS_CLAIR, "noir": NOIR, "rose": ROSE},
                     "elements": {"corps": "blanc", "chaussettes": "gris",
                                  "bout_oreilles": "gris", "reflets": "blanc", "yeux": "noir",
                                  "bouche": "noir", "nez": "noir", "joues": "rose",
                                  "oreilles_int": "rose", "accessoire": "rose"}},
    }

    def extra_parts(self, geo, X, Y, Z):
        S = geo.S
        parts = [(sd_ellipsoid(X, Y, Z, (21.0 * S, 0, 7.2 * S), (6.0 * S, 7.5 * S, 4.8 * S)),
                  3.0 * S)]
        for s in (1, -1):   # joues touffues
            parts.append((sd_ellipsoid(X, Y, Z, (9.0 * S, 17.5 * S * s, 7.5 * S),
                                       (6.0 * S, 5.0 * S, 4.5 * S)), 2.0 * S))
        return parts

    def regions(self, geo):
        r = super().regions(geo)
        b, t, _, _ = self.ear
        zt = (b[2] + 0.62 * (t[2] - b[2])) * geo.S
        r["bout_oreilles"] = box(-BIG, BIG, -BIG, BIG, zt, BIG)
        return r


ANIMAUX = {"chat": Chat, "renard": Renard}
