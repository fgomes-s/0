#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de pedra - proposta de renovacao.
Gera duas folhas A4 (Piso 0 e Piso 1) em desenho tecnico a preto e branco.
Saida: SVG + HTML + PDF (via chromium headless).
Cotas em metros, escala 1:75.
"""
import math
import os
import subprocess

SCALE = 75.0
K = 1000.0 / SCALE          # mm por metro
OUT = os.path.dirname(os.path.abspath(__file__))


def n(v):
    s = "%.3f" % v
    return s.rstrip("0").rstrip(".") if "." in s else s


# ----------------------------------------------------------------------------
# geometria (metros)
# ----------------------------------------------------------------------------
T = 0.55        # parede exterior em alvenaria de pedra (existente)
TP = 0.12       # parede interior nova (tabique / gesso cartonado)
TA = 0.30       # muro do quintal / anexo

# volume principal
MX0, MY0, MX1, MY1 = 0.00, 0.00, 5.80, 8.20
IX0, IY0, IX1, IY1 = MX0 + T, MY0 + T, MX1 - T, MY1 - T     # 0.55 0.55 5.25 7.65

# anexo / quintal
AX0, AY0, AX1, AY1 = -4.90, 3.40, 0.00, 10.20
AIX0, AIY0, AIY1 = AX0 + TA, AY0 + TA, AY1 - TA             # -4.60 3.70 9.90

# w.c.
WCX0, WCY0, WCX1, WCY1 = IX0, IY0, 3.55, 2.55

# escada
EX0, EX1 = 4.05, IX1                # largura 1.20
EY_TOP, EY_BOT = IY0, 4.33          # 14 cobertores de 0.27
TREAD = 0.27
BRK_A = ((EX0, 3.08), (EX1, 2.53))  # linha de corte (inferior)
BRK_B = ((EX0, 2.90), (EX1, 2.35))  # linha de corte (superior)

# lavandaria / escritorio (anexo)
LVX0, LVY0, LVX1, LVY1 = -2.70, AIY0, 0.00, 5.40
ESX0, ESY0, ESX1, ESY1 = AIX0, AIY0, -2.82, 7.00


# ----------------------------------------------------------------------------
# folha
# ----------------------------------------------------------------------------
class Sheet(object):
    def __init__(self, ox, oy):
        self.ox, self.oy = ox, oy
        self.body = []
        self.defs = []

    # --- conversao metros -> mm de folha
    def X(self, x):
        return self.ox + x * K

    def Y(self, y):
        return self.oy + y * K

    def add(self, s):
        self.body.append(s)

    # --- primitivas em mm ---------------------------------------------------
    def mline(self, x1, y1, x2, y2, cls="thin"):
        self.add('<line x1="%s" y1="%s" x2="%s" y2="%s" class="%s"/>'
                 % (n(x1), n(y1), n(x2), n(y2), cls))

    def mrect(self, x, y, w, h, cls="thin", fill="none"):
        self.add('<rect x="%s" y="%s" width="%s" height="%s" class="%s" fill="%s"/>'
                 % (n(x), n(y), n(w), n(h), cls, fill))

    def mtext(self, x, y, txt, cls="t-lbl", anchor="middle", rot=None):
        tr = ' transform="rotate(%s %s %s)"' % (n(rot), n(x), n(y)) if rot else ""
        self.add('<text x="%s" y="%s" class="%s" text-anchor="%s"%s>%s</text>'
                 % (n(x), n(y), cls, anchor, tr, txt))

    # --- primitivas em metros ----------------------------------------------
    def line(self, p1, p2, cls="thin"):
        self.mline(self.X(p1[0]), self.Y(p1[1]), self.X(p2[0]), self.Y(p2[1]), cls)

    def rect(self, x0, y0, x1, y1, cls="thin", fill="none"):
        self.mrect(self.X(x0), self.Y(y0), (x1 - x0) * K, (y1 - y0) * K, cls, fill)

    def circle(self, cx, cy, r, cls="thin", fill="none"):
        self.add('<circle cx="%s" cy="%s" r="%s" class="%s" fill="%s"/>'
                 % (n(self.X(cx)), n(self.Y(cy)), n(r * K), cls, fill))

    def ellipse(self, cx, cy, rx, ry, cls="thin", fill="none"):
        self.add('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" class="%s" fill="%s"/>'
                 % (n(self.X(cx)), n(self.Y(cy)), n(rx * K), n(ry * K), cls, fill))

    def poly(self, pts, cls="thin", close=False, fill="none"):
        d = " ".join("%s,%s" % (n(self.X(p[0])), n(self.Y(p[1]))) for p in pts)
        tag = "polygon" if close else "polyline"
        self.add('<%s points="%s" class="%s" fill="%s"/>' % (tag, d, cls, fill))

    def text(self, x, y, txt, cls="t-lbl", anchor="middle", rot=None):
        self.mtext(self.X(x), self.Y(y), txt, cls, anchor, rot)

    def rrect(self, x0, y0, x1, y1, r, cls="thin", fill="none"):
        self.add('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" class="%s" fill="%s"/>'
                 % (n(self.X(x0)), n(self.Y(y0)), n((x1 - x0) * K),
                    n((y1 - y0) * K), n(r * K), cls, fill))

    def g(self, attrs=""):
        self.add("<g %s>" % attrs)

    def gend(self):
        self.add("</g>")


# ----------------------------------------------------------------------------
# paredes
# ----------------------------------------------------------------------------
def _segments(a0, a1, gaps):
    """divide o intervalo [a0,a1] retirando os vaos"""
    pts = sorted([g for g in gaps if g[1] > a0 and g[0] < a1],
                 key=lambda g: g[0])
    segs, cur = [], a0
    for ga, gb in pts:
        ga, gb = max(ga, a0), min(gb, a1)
        if ga > cur:
            segs.append((cur, ga))
        cur = max(cur, gb)
    if cur < a1:
        segs.append((cur, a1))
    return segs


class Band(object):
    """troco de parede recto. 'h' = ao longo de x, 'v' = ao longo de y."""

    def __init__(self, orient, t_out, t_in, span,
                 out_span=None, in_span=None, ops=(), fill="stone"):
        self.o = orient
        self.t_out, self.t_in = t_out, t_in
        self.span = span
        self.out_span = out_span or span
        self.in_span = in_span or span
        self.ops = list(ops)
        self.fill = fill

    def _pt(self, a, t):
        return (a, t) if self.o == "h" else (t, a)

    def rects(self):
        """rectangulos de enchimento, ja descontados os vaos"""
        gaps = [(o["a"], o["b"]) for o in self.ops]
        lo, hi = min(self.t_out, self.t_in), max(self.t_out, self.t_in)
        out = []
        for a, b in _segments(self.span[0], self.span[1], gaps):
            out.append((a, lo, b, hi) if self.o == "h" else (lo, a, hi, b))
        return out

    def fill_pass(self, s):
        for (x0, y0, x1, y1) in self.rects():
            s.rect(x0, y0, x1, y1, cls="nostroke",
                   fill="#fff" if self.fill == "stone" else "#000")

    def draw(self, s):
        gaps = [(o["a"], o["b"]) for o in self.ops]
        # faces
        for t, sp in ((self.t_out, self.out_span), (self.t_in, self.in_span)):
            for a, b in _segments(sp[0], sp[1], gaps):
                s.line(self._pt(a, t), self._pt(b, t), cls="cut")
        # ombreiras + vaos
        for o in self.ops:
            s.line(self._pt(o["a"], self.t_out), self._pt(o["a"], self.t_in), cls="cut")
            s.line(self._pt(o["b"], self.t_out), self._pt(o["b"], self.t_in), cls="cut")
            k = o.get("kind", "door")
            if k == "window":
                window(s, self, o)
            elif k in ("door", "gate"):
                door(s, self, o)


def window(s, band, o):
    """vao envidracado: faces finas + vidro ao centro do vao"""
    a, b = o["a"], o["b"]
    to, ti = band.t_out, band.t_in
    for t, cls in ((to, "thin"), (ti, "thin")):
        s.line(band._pt(a, t), band._pt(b, t), cls=cls)
    mid = to + (ti - to) * 0.5
    d = (ti - to)
    s.line(band._pt(a, mid - d * 0.06), band._pt(b, mid - d * 0.06), cls="med")
    s.line(band._pt(a, mid + d * 0.06), band._pt(b, mid + d * 0.06), cls="med")


def door(s, band, o):
    """folha aberta a 90 graus + arco de abertura"""
    a, b = o["a"], o["b"]
    w = b - a
    to, ti = band.t_out, band.t_in
    out_side = (o.get("swing", "in") == "out")
    face = to if out_side else ti
    other = ti if out_side else to
    tdir = 1.0 if face > other else -1.0
    hinge_a = a if o.get("hinge", "a") == "a" else b
    adir = 1.0 if o.get("hinge", "a") == "a" else -1.0

    if band.o == "h":
        hinge = (hinge_a, face)
        along = (adir, 0.0)
        swing = (0.0, tdir)
    else:
        hinge = (face, hinge_a)
        along = (0.0, adir)
        swing = (tdir, 0.0)

    tip = (hinge[0] + swing[0] * w, hinge[1] + swing[1] * w)
    closed = (hinge[0] + along[0] * w, hinge[1] + along[1] * w)
    th = 0.045
    p1 = hinge
    p2 = tip
    p3 = (tip[0] + along[0] * th, tip[1] + along[1] * th)
    p4 = (hinge[0] + along[0] * th, hinge[1] + along[1] * th)
    s.poly([p1, p2, p3, p4], cls="med", close=True, fill="#fff")
    cross = along[0] * swing[1] - along[1] * swing[0]
    sweep = 1 if cross > 0 else 0
    s.add('<path d="M %s %s A %s %s 0 0 %d %s %s" class="hair" fill="none"/>'
          % (n(s.X(closed[0])), n(s.Y(closed[1])), n(w * K), n(w * K),
             sweep, n(s.X(tip[0])), n(s.Y(tip[1]))))


# ----------------------------------------------------------------------------
# cotagem
# ----------------------------------------------------------------------------
def dim_chain(s, orient, stations, base_mm, ext_from, txt_cls="t-dim", total=False):
    """orient 'h' -> cadeia horizontal; base_mm = y (mm) da linha de cota.
       stations = lista de coordenadas (metros) ao longo do eixo.
       ext_from = coordenada (metros) de onde partem as linhas de chamada
       (escalar ou lista com um valor por estacao)."""
    if not isinstance(ext_from, (list, tuple)):
        ext_from = [ext_from] * len(stations)
    for i in range(len(stations)):
        a = stations[i]
        ext = ext_from[i]
        if orient == "h":
            x = s.X(a)
            y0 = s.Y(ext)
            s.mline(x, y0 + (1.2 if base_mm > y0 else -1.2), x,
                    base_mm + (1.8 if base_mm > y0 else -1.8), "dim")
        else:
            y = s.Y(a)
            x0 = s.X(ext)
            s.mline(x0 + (1.2 if base_mm > x0 else -1.2), y,
                    base_mm + (1.8 if base_mm > x0 else -1.8), y, "dim")
    for i in range(len(stations) - 1):
        a, b = stations[i], stations[i + 1]
        if orient == "h":
            xa, xb = s.X(a), s.X(b)
            s.mline(xa, base_mm, xb, base_mm, "dim")
            for x in (xa, xb):
                s.mline(x - 0.9, base_mm + 0.9, x + 0.9, base_mm - 0.9, "dim")
            lbl = ("%.2f" % (b - a)).replace(".", ",")
            s.mtext((xa + xb) / 2.0, base_mm - 1.1, lbl, txt_cls)
        else:
            ya, yb = s.Y(a), s.Y(b)
            s.mline(base_mm, ya, base_mm, yb, "dim")
            for y in (ya, yb):
                s.mline(base_mm - 0.9, y + 0.9, base_mm + 0.9, y - 0.9, "dim")
            lbl = ("%.2f" % (b - a)).replace(".", ",")
            s.mtext(base_mm - 1.1, (ya + yb) / 2.0, lbl, txt_cls,
                    rot=-90)


def dim_free(s, p1, p2, off, label=None, cls="t-dim"):
    """cota isolada entre dois pontos (metros), deslocada 'off' mm na perpendicular"""
    x1, y1 = s.X(p1[0]), s.Y(p1[1])
    x2, y2 = s.X(p2[0]), s.Y(p2[1])
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    ax, ay = x1 + nx * off, y1 + ny * off
    bx, by = x2 + nx * off, y2 + ny * off
    s.mline(x1 + nx * (off * 0.15), y1 + ny * (off * 0.15), ax + nx * 1.2, ay + ny * 1.2, "dim")
    s.mline(x2 + nx * (off * 0.15), y2 + ny * (off * 0.15), bx + nx * 1.2, by + ny * 1.2, "dim")
    s.mline(ax, ay, bx, by, "dim")
    for (px, py) in ((ax, ay), (bx, by)):
        s.mline(px - ux * 0.9 - nx * 0.9, py - uy * 0.9 - ny * 0.9,
                px + ux * 0.9 + nx * 0.9, py + uy * 0.9 + ny * 0.9, "dim")
    if label is None:
        label = ("%.2f" % (L / K)).replace(".", ",")
    ang = math.degrees(math.atan2(dy, dx))
    if ang > 90 or ang < -90:
        ang += 180
    mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
    rot = ang if abs(ang) > 0.001 else None
    s.mtext(mx - nx * 1.1, my - ny * 1.1, label, cls, rot=rot)


# ----------------------------------------------------------------------------
# mobiliario e equipamento (representacao esquematica de projecto)
# ----------------------------------------------------------------------------
def rot(s, cx, cy, ang):
    s.add('<g transform="rotate(%s %s %s)">' % (n(ang), n(s.X(cx)), n(s.Y(cy))))


def endg(s):
    s.add("</g>")


def duche(s, x0, y0, x1, y1):
    s.rect(x0, y0, x1, y1, "med", "#fff")
    s.rect(x0 + 0.05, y0 + 0.05, x1 - 0.05, y1 - 0.05, "hair")
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    s.circle(cx, cy, 0.05, "hair")


def sanita(s, cx, ytop):
    """sanita encostada a parede em ytop, virada para sul"""
    s.rect(cx - 0.18, ytop, cx + 0.18, ytop + 0.17, "med", "#fff")
    s.ellipse(cx, ytop + 0.42, 0.17, 0.25, "med", "#fff")
    s.ellipse(cx, ytop + 0.42, 0.11, 0.18, "hair")


def bide(s, cx, ytop):
    s.ellipse(cx, ytop + 0.28, 0.16, 0.24, "med", "#fff")
    s.ellipse(cx, ytop + 0.28, 0.07, 0.11, "hair")


def lavatorio(s, x0, ytop, w=0.60, d=0.47):
    s.rrect(x0, ytop, x0 + w, ytop + d, 0.04, "med", "#fff")
    s.ellipse(x0 + w / 2.0, ytop + d * 0.55, w * 0.33, d * 0.29, "hair")
    s.circle(x0 + w / 2.0, ytop + 0.08, 0.035, "hair")


def bancada(s, x0, y0, x1, y1, front="E"):
    """tampo de bancada; 'front' indica a face livre"""
    s.rect(x0, y0, x1, y1, "med", "#fff")


def lavaloica(s, x0, y0, x1, y1):
    s.rect(x0, y0, x1, y1, "med", "#fff")
    s.rect(x0 + 0.05, y0 + 0.06, x1 - 0.05, y1 - 0.06, "hair")
    s.circle((x0 + x1) / 2.0, (y0 + y1) / 2.0, 0.035, "hair")


def placa(s, x0, y0, x1, y1):
    s.rect(x0, y0, x1, y1, "med", "#fff")
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    dx, dy = (x1 - x0) * 0.22, (y1 - y0) * 0.22
    for sx in (-1, 1):
        for sy in (-1, 1):
            s.circle(cx + sx * dx, cy + sy * dy, 0.085, "hair")


def equip_quadrado(s, x0, y0, x1, y1, r=0.19):
    s.rect(x0, y0, x1, y1, "med", "#fff")
    s.circle((x0 + x1) / 2.0, (y0 + y1) / 2.0, r, "hair")


def frigorifico(s, x0, y0, x1, y1):
    s.rect(x0, y0, x1, y1, "med", "#fff")
    s.line((x0 + 0.06, y0 + 0.06), (x0 + 0.06, y1 - 0.06), "hair")


def tanque(s, x0, y0, x1, y1):
    s.rect(x0, y0, x1, y1, "med", "#fff")
    s.rect(x0 + 0.06, y0 + 0.07, x1 - 0.06, y1 - 0.07, "hair")


def cadeira(s, cx, cy, ang=0, w=0.44, d=0.44):
    rot(s, cx, cy, ang)
    s.rect(cx - w / 2.0, cy - d / 2.0, cx + w / 2.0, cy + d / 2.0, "thin", "#fff")
    s.line((cx - w / 2.0, cy - d / 2.0 + 0.09), (cx + w / 2.0, cy - d / 2.0 + 0.09), "hair")
    endg(s)


def mesa_jantar(s, cx, cy, w=1.60, d=0.90):
    s.rect(cx - w / 2.0, cy - d / 2.0, cx + w / 2.0, cy + d / 2.0, "med", "#fff")
    s.rect(cx - w / 2.0 + 0.07, cy - d / 2.0 + 0.07,
           cx + w / 2.0 - 0.07, cy + d / 2.0 - 0.07, "hair")
    for dx in (-0.60, 0.0, 0.60):
        cadeira(s, cx + dx, cy - d / 2.0 - 0.28, 0)
        cadeira(s, cx + dx, cy + d / 2.0 + 0.28, 180)


def sofa(s, x0, y0, x1, y1, back="S"):
    """sofa com costas encostadas ao lado indicado"""
    s.rect(x0, y0, x1, y1, "med", "#fff")
    t = 0.20
    if back == "S":
        s.line((x0, y1 - t), (x1, y1 - t), "thin")
        s.line((x0 + t, y0), (x0 + t, y1 - t), "thin")
        s.line((x1 - t, y0), (x1 - t, y1 - t), "thin")
        w = (x1 - t) - (x0 + t)
        s.line((x0 + t + w / 2.0, y0), (x0 + t + w / 2.0, y1 - t), "hair")
    else:
        s.line((x0 + t, y0), (x0 + t, y1), "thin")
        s.line((x0 + t, y0 + t), (x1, y0 + t), "thin")
        s.line((x0 + t, y1 - t), (x1, y1 - t), "thin")
        h = (y1 - t) - (y0 + t)
        s.line((x0 + t, y0 + t + h / 2.0), (x1, y0 + t + h / 2.0), "hair")


def cadeirao(s, cx, cy, ang=0, w=0.78, d=0.78):
    rot(s, cx, cy, ang)
    x0, y0, x1, y1 = cx - w / 2.0, cy - d / 2.0, cx + w / 2.0, cy + d / 2.0
    s.rect(x0, y0, x1, y1, "med", "#fff")
    s.line((x0, y1 - 0.18), (x1, y1 - 0.18), "thin")
    s.line((x0 + 0.16, y0), (x0 + 0.16, y1 - 0.18), "thin")
    s.line((x1 - 0.16, y0), (x1 - 0.16, y1 - 0.18), "thin")
    endg(s)


def cama(s, cx, ytop, w=1.60, h=2.00):
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    s.rect(x0, ytop, x1, ytop + h, "med", "#fff")
    s.line((x0, ytop + 0.62), (x1, ytop + 0.62), "thin")
    for sgn in (-1, 1):
        px = cx + sgn * w * 0.24
        s.rrect(px - 0.28, ytop + 0.10, px + 0.28, ytop + 0.48, 0.05, "hair")
    s.rect(x0, ytop - 0.09, x1, ytop, "med", "#fff")


def mesinha(s, x0, y0, x1, y1):
    s.rect(x0, y0, x1, y1, "thin", "#fff")
    s.line((x0 + 0.05, y0 + 0.05), (x1 - 0.05, y0 + 0.05), "hair")


def roupeiro(s, x0, y0, x1, y1, front="E", nport=4):
    s.rect(x0, y0, x1, y1, "med", "#fff")
    if front == "E":
        s.line((x1 - 0.06, y0), (x1 - 0.06, y1), "hair")
        step = (y1 - y0) / float(nport)
        for i in range(1, nport):
            s.line((x0, y0 + i * step), (x1, y0 + i * step), "hair")
    else:
        s.line((x0, y1 - 0.06), (x1, y1 - 0.06), "hair")
        step = (x1 - x0) / float(nport)
        for i in range(1, nport):
            s.line((x0 + i * step, y0), (x0 + i * step, y1), "hair")


def secretaria(s, x0, y0, x1, y1):
    s.rect(x0, y0, x1, y1, "med", "#fff")
    s.line((x0 + 0.05, y0 + 0.05), (x1 - 0.05, y0 + 0.05), "hair")


def estante(s, x0, y0, x1, y1, div=4):
    s.rect(x0, y0, x1, y1, "med", "#fff")
    step = (y1 - y0) / float(div)
    for i in range(1, div):
        s.line((x0, y0 + i * step), (x1, y0 + i * step), "hair")


def mesa_redonda(s, cx, cy, r=0.55):
    s.circle(cx, cy, r, "med", "#fff")
    s.circle(cx, cy, r - 0.07, "hair")


def fundo(s, cx, cy, w, h):
    """mancha branca por baixo de texto sobre trama"""
    s.rect(cx - w / 2.0, cy - h / 2.0, cx + w / 2.0, cy + h / 2.0, "nostroke", "#fff")


def vaso(s, cx, cy, r=0.22):
    s.circle(cx, cy, r, "thin", "#fff")
    s.circle(cx, cy, r * 0.55, "hair")


# ----------------------------------------------------------------------------
# tramas
# ----------------------------------------------------------------------------
def stone_polys(x0, y0, x1, y1, cell=3.6, seed=7):
    """alvenaria de pedra irregular: malha deformada, em mm de folha"""
    import random
    rng = random.Random(seed)
    ni = int((x1 - x0) / cell) + 2
    nj = int((y1 - y0) / cell) + 2
    pts = {}
    for i in range(ni + 1):
        for j in range(nj + 1):
            pts[(i, j)] = (x0 + i * cell + rng.uniform(-0.85, 0.85),
                           y0 + j * cell + rng.uniform(-0.85, 0.85))
    out = []
    for i in range(ni):
        for j in range(nj):
            q = [pts[(i, j)], pts[(i + 1, j)], pts[(i + 1, j + 1)], pts[(i, j + 1)]]
            cx = sum(p[0] for p in q) / 4.0
            cy = sum(p[1] for p in q) / 4.0
            ins = []
            for (px, py) in q:
                dx, dy = cx - px, cy - py
                d = math.hypot(dx, dy) or 1.0
                k = min(0.26, d * 0.3)
                ins.append((px + dx / d * k, py + dy / d * k))
            out.append(" ".join("%s,%s" % (n(a), n(b)) for a, b in ins))
    return out


def draw_bands(s, bands, uid):
    """enchimento + trama de pedra recortada + tracado das paredes"""
    for b in bands:
        b.fill_pass(s)
    rr = [r for b in bands if b.fill == "stone" for r in b.rects()]
    xs = [s.X(r[0]) for r in rr] + [s.X(r[2]) for r in rr]
    ys = [s.Y(r[1]) for r in rr] + [s.Y(r[3]) for r in rr]
    clip = "".join('<rect x="%s" y="%s" width="%s" height="%s"/>'
                   % (n(s.X(r[0])), n(s.Y(r[1])),
                      n((r[2] - r[0]) * K), n((r[3] - r[1]) * K)) for r in rr)
    s.add('<defs><clipPath id="cppedra%d">%s</clipPath></defs>' % (uid, clip))
    s.add('<g clip-path="url(#cppedra%d)" fill="none" stroke="#000" stroke-width="0.11">'
          % uid)
    for q in stone_polys(min(xs) - 2, min(ys) - 2, max(xs) + 2, max(ys) + 2):
        s.add('<polygon points="%s"/>' % q)
    s.gend()
    for b in bands:
        b.draw(s)


def pavimento(s, rects, uid, passo=0.60):
    """lajeta de granito: juntas desencontradas, recortadas ao espaco exterior"""
    clip = "".join('<rect x="%s" y="%s" width="%s" height="%s"/>'
                   % (n(s.X(r[0])), n(s.Y(r[1])),
                      n((r[2] - r[0]) * K), n((r[3] - r[1]) * K)) for r in rects)
    s.add('<defs><clipPath id="cplaj%d">%s</clipPath></defs>' % (uid, clip))
    s.add('<g clip-path="url(#cplaj%d)" fill="none" stroke="#000" stroke-width="0.09">'
          % uid)
    x0 = min(r[0] for r in rects)
    x1 = max(r[2] for r in rects)
    y0 = min(r[1] for r in rects)
    y1 = max(r[3] for r in rects)
    j = 0
    y = y0
    while y <= y1 + 0.001:
        s.line((x0, y), (x1, y), "")
        x = x0 + (passo / 2.0 if j % 2 else 0.0)
        while x <= x1 + 0.001:
            s.line((x, y), (x, min(y + passo, y1)), "")
            x += passo
        y += passo
        j += 1
    s.gend()


def stone_pattern():
    """alvenaria de pedra irregular (trama continua entre ladrilhos)"""
    import random
    rng = random.Random(7)
    nc, cs = 6, 3.6
    P = nc * cs
    jx = [0.0] + [rng.uniform(-0.75, 0.75) for _ in range(nc - 1)] + [0.0]
    jy = [0.0] + [rng.uniform(-0.75, 0.75) for _ in range(nc - 1)] + [0.0]
    nx = [0.0] + [rng.uniform(-0.55, 0.55) for _ in range(nc - 1)] + [0.0]
    ny = [0.0] + [rng.uniform(-0.55, 0.55) for _ in range(nc - 1)] + [0.0]
    pts = {}
    for i in range(nc + 1):
        for j in range(nc + 1):
            x, y = i * cs, j * cs
            if 0 < i < nc and 0 < j < nc:
                x += rng.uniform(-0.85, 0.85)
                y += rng.uniform(-0.85, 0.85)
            elif 0 < i < nc:                 # bordo superior / inferior
                x += jx[i]
                y += ny[i]
            elif 0 < j < nc:                 # bordo esquerdo / direito
                y += jy[j]
                x += nx[j]
            pts[(i, j)] = (x, y)
    polys = []
    for i in range(nc):
        for j in range(nc):
            q = [pts[(i, j)], pts[(i + 1, j)], pts[(i + 1, j + 1)], pts[(i, j + 1)]]
            cx = sum(p[0] for p in q) / 4.0
            cy = sum(p[1] for p in q) / 4.0
            ins = []
            for (px, py) in q:
                dx, dy = cx - px, cy - py
                d = math.hypot(dx, dy) or 1.0
                k = min(0.26, d * 0.3)
                ins.append((px + dx / d * k, py + dy / d * k))
            polys.append(" ".join("%s,%s" % (n(a), n(b)) for a, b in ins))
    body = "".join('<polygon points="%s"/>' % q for q in polys)
    return ('<pattern id="stone" width="%s" height="%s" patternUnits="userSpaceOnUse">'
            '<rect width="%s" height="%s" fill="#fff" class="nostroke"/>'
            '<g fill="none" stroke="#000" stroke-width="0.11">%s</g></pattern>'
            % (n(P), n(P), n(P), n(P), body))


LAJETA = (
    '<pattern id="lajeta" width="16" height="16" patternUnits="userSpaceOnUse">'
    '<rect width="16" height="16" fill="#fff" class="nostroke"/>'
    '<g fill="none" stroke="#000" stroke-width="0.09">'
    '<path d="M0 0 H16 M0 8 H16 M0 16 H16 M0 0 V8 M8 0 V8 M16 0 V8 M4 8 V16 M12 8 V16"/>'
    '</g></pattern>'
)

STYLE = """
text{font-family:'Liberation Sans',Helvetica,Arial,sans-serif;fill:#000;stroke:none;
     dominant-baseline:auto}
line,rect,circle,ellipse,polyline,polygon,path{stroke:#000;
     stroke-linecap:butt;stroke-linejoin:miter}
line{fill:none}
.cut{stroke-width:.5}
.med{stroke-width:.26}
.thin{stroke-width:.17}
.hair{stroke-width:.1}
.dim{stroke-width:.13}
.nostroke{stroke:none}
.dash{stroke-width:.16;stroke-dasharray:1.8 1.2}
.cline{stroke-width:.13;stroke-dasharray:5 1.2 1 1.2}
.frame{stroke-width:.7}
.box{stroke-width:.25}
.boxi{stroke-width:.15}
.t-h1{font-size:4.6px;letter-spacing:1.1px}
.t-h2{font-size:3.1px;letter-spacing:.75px}
.t-sub{font-size:2.05px;letter-spacing:.55px}
.t-room{font-size:2.55px;letter-spacing:.62px}
.t-area{font-size:2.05px;letter-spacing:.2px}
.t-lbl{font-size:1.62px;letter-spacing:.14px}
.t-dim{font-size:1.85px;letter-spacing:.1px}
.t-note{font-size:1.95px;letter-spacing:.1px}
.t-tb{font-size:2.3px;letter-spacing:.35px}
.t-tbs{font-size:1.6px;letter-spacing:.3px}
.t-tbl{font-size:1.95px;letter-spacing:.2px}
.t-tbb{font-size:2.75px;letter-spacing:.42px}
"""


def page(sheet, title_id):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" '
        'viewBox="0 0 210 297" shape-rendering="geometricPrecision">'
        '<title>%s</title><defs>%s%s</defs><style>%s</style>'
        '<rect x="0" y="0" width="210" height="297" fill="#fff" class="nostroke"/>'
        '%s</svg>' % (title_id, stone_pattern(), LAJETA, STYLE, "".join(sheet.body)))


# ----------------------------------------------------------------------------
# elementos de folha
# ----------------------------------------------------------------------------
FX0, FY0, FX1, FY1 = 20.0, 10.0, 200.0, 287.0
TB_Y = 255.0


def frame(s):
    s.mrect(FX0, FY0, FX1 - FX0, FY1 - FY0, "frame")
    s.mrect(FX0 + 1.4, FY0 + 1.4, FX1 - FX0 - 2.8, FY1 - FY0 - 2.8, "boxi")


def header(s, titulo, sub):
    s.mtext(FX0 + 3, 23.5, titulo, "t-h1", "start")
    s.mtext(FX0 + 3, 29.2, sub, "t-sub", "start")
    s.mline(FX0 + 3, 31.6, FX1 - 3, 31.6, "box")


def norte(s, cx, cy, r=7.0):
    s.add('<polygon points="%s,%s %s,%s %s,%s %s,%s" class="med" fill="#fff"/>'
          % (n(cx), n(cy - r), n(cx + r * 0.42), n(cy + r * 0.72),
             n(cx), n(cy + r * 0.34), n(cx - r * 0.42), n(cy + r * 0.72)))
    s.add('<polygon points="%s,%s %s,%s %s,%s" class="nostroke" fill="#000"/>'
          % (n(cx), n(cy - r), n(cx + r * 0.42), n(cy + r * 0.72), n(cx), n(cy + r * 0.34)))
    s.mtext(cx, cy - r - 1.8, "N", "t-h2")


def escala_grafica(s, x, y, w_m=5):
    """barra de escala graduada (metros)"""
    seg = K
    h = 1.7
    for i in range(w_m):
        x0 = x + i * seg
        s.mrect(x0, y, seg, h, "boxi", "#000" if i % 2 else "#fff")
        s.mtext(x0, y + h + 2.9, str(i), "t-dim")
    s.mtext(x + w_m * seg, y + h + 2.9, str(w_m), "t-dim")
    s.mtext(x + w_m * seg / 2.0, y - 1.4, "ESCALA  1:75          (m)", "t-lbl")


def caixa_titulo(s, box_title, rows, x0, y0, x1, row_h=4.0):
    """quadro com cabecalho + linhas [(esq, dta)]"""
    hh = 4.6
    h = hh + row_h * len(rows)
    s.mrect(x0, y0, x1 - x0, h, "box")
    s.mline(x0, y0 + hh, x1, y0 + hh, "box")
    s.mtext(x0 + 2, y0 + 3.2, box_title, "t-tbl", "start")
    for i, (a, b) in enumerate(rows):
        yy = y0 + hh + row_h * (i + 1)
        if i < len(rows) - 1:
            s.mline(x0, yy, x1, yy, "boxi")
        s.mtext(x0 + 2, yy - 1.25, a, "t-note", "start")
        if b:
            s.mtext(x1 - 2, yy - 1.25, b, "t-note", "end")
    return y0 + h


def legenda(s, x0, y0, x1, itens):
    """itens: (tipo, texto) com tipo em {stone,new,lajeta,vao,porta}"""
    hh, row_h = 4.6, 4.6
    h = hh + row_h * len(itens)
    s.mrect(x0, y0, x1 - x0, h, "box")
    s.mline(x0, y0 + hh, x1, y0 + hh, "box")
    s.mtext(x0 + 2, y0 + 3.2, "LEGENDA", "t-tbl", "start")
    for i, (tp, txt) in enumerate(itens):
        yy = y0 + hh + row_h * i + 1.1
        sw, sh = 7.0, 2.6
        if tp == "stone":
            s.mrect(x0 + 2, yy, sw, sh, "med", "url(#stone)")
        elif tp == "new":
            s.mrect(x0 + 2, yy, sw, sh, "med", "#000")
        elif tp == "lajeta":
            s.mrect(x0 + 2, yy, sw, sh, "boxi", "url(#lajeta)")
        elif tp == "vao":
            s.mrect(x0 + 2, yy, sw, sh, "thin", "#fff")
            s.mline(x0 + 2, yy + sh / 2.0 - 0.3, x0 + 2 + sw, yy + sh / 2.0 - 0.3, "med")
            s.mline(x0 + 2, yy + sh / 2.0 + 0.3, x0 + 2 + sw, yy + sh / 2.0 + 0.3, "med")
        elif tp == "porta":
            s.mline(x0 + 2, yy + sh, x0 + 2, yy)
            s.add('<path d="M %s %s A %s %s 0 0 1 %s %s" class="hair" fill="none"/>'
                  % (n(x0 + 2 + sw * 0.8), n(yy + sh), n(sw * 0.8), n(sw * 0.8),
                     n(x0 + 2), n(yy + sh - sw * 0.8)))
            s.mline(x0 + 2, yy + sh, x0 + 2, yy + sh - sw * 0.8, "med")
        s.mtext(x0 + 11.5, yy + sh - 0.35, txt, "t-note", "start")
    return y0 + h


def notas(s, x0, y0, x1, linhas, titulo="NOTAS"):
    s.mtext(x0, y0, titulo, "t-tbl", "start")
    s.mline(x0, y0 + 1.1, x1, y0 + 1.1, "boxi")
    for i, ln in enumerate(linhas):
        s.mtext(x0, y0 + 4.5 + i * 3.0, ln, "t-note", "start")


def cartucho(s, desenho, folha):
    x0, y0, x1, y1 = FX0, TB_Y, FX1, FY1
    s.mrect(x0, y0, x1 - x0, y1 - y0, "box")
    xa, xb = 118.0, 162.0
    s.mline(xa, y0, xa, y1, "box")
    s.mline(xb, y0, xb, y1, "box")
    # projecto
    s.mtext(x0 + 3, y0 + 4.2, "PROJECTO", "t-tbs", "start")
    s.mtext(x0 + 3, y0 + 10.0, "CASA DE PEDRA", "t-h2", "start")
    s.mtext(x0 + 3, y0 + 14.6, "PROPOSTA DE RENOVAÇÃO · HABITAÇÃO UNIFAMILIAR T1",
            "t-tb", "start")
    s.mline(x0 + 3, y0 + 17.4, xa - 3, y0 + 17.4, "boxi")
    s.mtext(x0 + 3, y0 + 21.0, "FASE   ESTUDO PRÉVIO — PLANTAS DE ARQUITECTURA", "t-tbs", "start")
    s.mtext(x0 + 3, y0 + 25.0,
            "DESENHO CONCEPTUAL. SUJEITO A LEVANTAMENTO RIGOROSO E A VALIDAÇÃO",
            "t-tbs", "start")
    s.mtext(x0 + 3, y0 + 28.4,
            "ESTRUTURAL DAS PAREDES EXISTENTES. NÃO ESCALAR O DESENHO.", "t-tbs", "start")
    # desenho
    s.mtext(xa + 3, y0 + 4.2, "DESENHO", "t-tbs", "start")
    s.mtext(xa + 3, y0 + 10.6, desenho, "t-tbb", "start")
    s.mline(xa + 3, y0 + 14.0, xb - 3, y0 + 14.0, "boxi")
    s.mtext(xa + 3, y0 + 18.4, "PROPOSTA", "t-tb", "start")
    s.mtext(xa + 3, y0 + 23.4, "COTAS EM METROS", "t-tbs", "start")
    s.mtext(xa + 3, y0 + 27.4, "COTAS EM TOSCO", "t-tbs", "start")
    # dados
    rows = [("ESCALA", "1:75"), ("DATA", "09.2026"), ("FOLHA", folha), ("FORMATO", "A4")]
    for i, (a, b) in enumerate(rows):
        yy = y0 + 7.6 * i
        if i:
            s.mline(xb, yy, x1, yy, "boxi")
        s.mtext(xb + 3, yy + 3.6, a, "t-tbs", "start")
        s.mtext(xb + 3, yy + 7.0, b, "t-tb", "start")


# ----------------------------------------------------------------------------
# escada
# ----------------------------------------------------------------------------
def seta(s, p1, p2):
    s.line(p1, p2, "thin")
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    a = (p2[0] - ux * 0.30 + px * 0.11, p2[1] - uy * 0.30 + py * 0.11)
    b = (p2[0] - ux * 0.30 - px * 0.11, p2[1] - uy * 0.30 - py * 0.11)
    s.add('<polygon points="%s,%s %s,%s %s,%s" class="nostroke" fill="#000"/>'
          % (n(s.X(p2[0])), n(s.Y(p2[1])), n(s.X(a[0])), n(s.Y(a[1])),
             n(s.X(b[0])), n(s.Y(b[1]))))


def escada(s, piso):
    cid = "clipesc%d" % piso
    if piso == 0:
        pts = [(EX0, BRK_A[0][1]), (EX1, BRK_A[1][1]), (EX1, EY_BOT + 0.02),
               (EX0, EY_BOT + 0.02)]
    else:
        pts = [(EX0, EY_TOP), (EX1, EY_TOP), (EX1, BRK_B[1][1]), (EX0, BRK_B[0][1])]
    d = " ".join("%s,%s" % (n(s.X(p[0])), n(s.Y(p[1]))) for p in pts)
    s.add('<defs><clipPath id="%s"><polygon points="%s"/></clipPath></defs>' % (cid, d))
    s.add('<g clip-path="url(#%s)">' % cid)
    s.line((EX0, EY_TOP), (EX0, EY_BOT), "med")          # bordo / limite do lance
    s.line((EX0, EY_BOT), (EX1, EY_BOT), "med")
    for k in range(0, 14):
        y = EY_BOT - k * TREAD
        s.line((EX0, y), (EX1, y), "thin")
    s.gend()
    # linha de corte convencional
    s.line(BRK_A[0], BRK_A[1], "med")
    s.line(BRK_B[0], BRK_B[1], "med")
    if piso == 0:
        seta(s, (4.62, EY_BOT - 0.22), (4.62, 3.30))
        s.text(4.28, 3.95, "SOBE", "t-lbl", "middle", rot=-90)
    else:
        seta(s, (4.62, EY_TOP + 0.45), (4.62, 2.25))
        s.text(4.28, 1.55, "DESCE", "t-lbl", "middle", rot=-90)
        # guarda do vao
        s.line((EX0, EY_TOP + 0.27), (EX0, EY_BOT), "med")
        s.line((EX0 + 0.07, EY_TOP + 0.27), (EX0 + 0.07, EY_BOT), "hair")
        s.line((EX0, EY_BOT), (EX1, EY_BOT), "med")
        s.line((EX0, EY_BOT - 0.07), (EX1, EY_BOT - 0.07), "hair")


# ----------------------------------------------------------------------------
# PISO 0
# ----------------------------------------------------------------------------
def draw_piso0(s):
    # --- pavimento exterior do quintal
    pavimento(s, [(-2.70, 5.52, 0.00, 9.90), (-4.60, 7.12, -2.70, 9.90)], 0)

    bands = [
        # volume principal
        Band("h", 0.00, 0.55, (0.00, 5.80), (0.00, 5.80), (0.55, 5.25),
             [dict(a=2.85, b=3.45, kind="window")]),
        Band("h", 8.20, 7.65, (0.00, 5.80), (0.00, 5.80), (0.55, 5.25),
             [dict(a=0.75, b=1.65, kind="window"),
              dict(a=3.85, b=4.85, kind="door", hinge="b", swing="in")]),
        Band("v", 0.00, 0.55, (0.55, 7.65), (0.00, 8.20), (0.55, 7.65),
             [dict(a=2.75, b=3.35, kind="window"),
              dict(a=5.90, b=6.80, kind="door", hinge="a", swing="in")]),
        Band("v", 5.80, 5.25, (0.55, 7.65), (0.00, 8.20), (0.55, 7.65),
             [dict(a=4.60, b=5.40, kind="window"),
              dict(a=5.70, b=6.70, kind="window")]),
        # divisorias do w.c.
        Band("h", 2.55, 2.67, (0.55, 3.67), (0.55, 3.55), (0.55, 3.67),
             [dict(a=2.60, b=3.30, kind="door", hinge="b", swing="out")], fill="new"),
        Band("v", 3.55, 3.67, (0.55, 2.55), (0.55, 2.55), (0.55, 2.67), [], fill="new"),
        # anexo
        Band("h", 3.40, 3.70, (-4.90, 0.00), (-4.90, 0.00), (-4.60, 0.00),
             [dict(a=-4.10, b=-3.40, kind="window"),
              dict(a=-1.90, b=-1.20, kind="window")]),
        Band("v", -4.90, -4.60, (3.70, 9.90), (3.40, 10.20), (3.70, 9.90),
             [dict(a=4.60, b=5.40, kind="window")]),
        Band("h", 10.20, 9.90, (-4.90, 0.30), (-4.90, 0.30), (-4.60, 0.00),
             [dict(a=-1.80, b=-0.80, kind="gate", hinge="a", swing="in")]),
        Band("v", 0.30, 0.00, (8.20, 9.90), (8.20, 10.20), (8.20, 9.90), []),
        # divisorias do anexo
        Band("v", -2.82, -2.70, (3.70, 7.12), (3.70, 7.00), (3.70, 7.12), [], fill="new"),
        Band("h", 5.52, 5.40, (-2.82, 0.00), (-2.82, 0.00), (-2.70, 0.00),
             [dict(a=-1.50, b=-0.70, kind="door", hinge="a", swing="in")], fill="new"),
        Band("h", 7.12, 7.00, (-4.60, -2.70), (-4.60, -2.70), (-4.60, -2.82),
             [dict(a=-4.50, b=-3.90, kind="window"),
              dict(a=-3.80, b=-3.00, kind="door", hinge="b", swing="out")], fill="new"),
    ]
    draw_bands(s, bands, 0)

    # --- w.c.
    duche(s, 0.55, 0.55, 1.45, 1.45)
    s.text(1.00, 1.24, "DUCHE", "t-lbl")
    sanita(s, 1.72, 0.55)
    bide(s, 2.30, 0.55)
    lavatorio(s, 2.85, 0.55)

    # --- cozinha
    bancada(s, 0.55, 2.67, 1.15, 5.10)
    lavaloica(s, 0.60, 2.80, 1.10, 3.60)
    placa(s, 0.60, 3.90, 1.10, 4.50)
    frigorifico(s, 0.55, 5.10, 1.20, 5.75)
    s.text(0.90, 5.42, "FRIG.", "t-lbl", "middle", rot=-90)

    # --- sala
    mesa_jantar(s, 2.75, 3.80)
    sofa(s, 0.65, 6.70, 2.75, 7.60, "S")
    mesa_redonda(s, 1.70, 5.90, 0.45)
    cadeirao(s, 3.30, 6.80, -90)

    # --- escada
    escada(s, 0)

    # --- lavandaria
    tanque(s, -2.60, 3.78, -2.00, 4.28)
    equip_quadrado(s, -1.90, 3.78, -1.30, 4.38)
    estante(s, -0.45, 3.78, -0.05, 4.88, 3)

    # --- escritorio
    secretaria(s, -4.55, 4.05, -3.90, 5.45)
    cadeira(s, -3.60, 4.75, -90)
    estante(s, -3.32, 3.78, -2.92, 4.88, 3)
    s.text(-4.22, 4.75, "SECRETÁRIA", "t-lbl", "middle", rot=-90)

    # --- quintal
    mesa_redonda(s, -1.35, 6.60, 0.55)
    cadeira(s, -1.35, 5.72, 180)
    cadeira(s, -1.35, 7.48, 0)
    cadeira(s, -2.23, 6.60, 90)
    cadeira(s, -0.47, 6.60, -90)
    for (vx, vy) in ((-2.42, 8.30), (-0.32, 8.70), (-4.35, 7.55), (-2.42, 9.55)):
        vaso(s, vx, vy)

    # --- toponimia
    s.text(1.95, 1.98, "W.C.", "t-room")
    s.text(1.95, 2.33, "6,00 m²", "t-area")
    s.text(2.75, 5.06, "SALA / COZINHA", "t-room")
    s.text(2.75, 5.42, "26,76 m²", "t-area")
    s.text(-1.35, 4.92, "LAVANDARIA", "t-room")
    s.text(-1.35, 5.30, "4,59 m²", "t-area")
    s.text(-3.71, 6.22, "ESCRITÓRIO", "t-room")
    s.text(-3.71, 6.56, "5,87 m²", "t-area")
    fundo(s, -3.65, 8.92, 1.85, 1.35)
    s.text(-3.65, 8.42, "QUINTAL", "t-room")
    s.text(-3.65, 8.76, "17,27 m²", "t-area")
    s.text(-3.65, 9.16, "ESPAÇO EXTERIOR", "t-lbl")
    s.text(-3.65, 9.44, "DESCOBERTO", "t-lbl")
    s.text(4.65, 5.18, "ESCADA", "t-lbl")

    # --- cotagem
    top = s.Y(0.00) - 9.0
    dim_chain(s, "h", [0.00, 0.55, 5.25, 5.80], top, 0.00)
    b1 = s.Y(10.20) + 9.0
    dim_chain(s, "h", [-4.90, -4.60, 0.00], b1, 10.20)
    dim_chain(s, "h", [0.00, 0.75, 1.65, 3.85, 4.85, 5.80], b1, 8.20)
    dim_chain(s, "h", [-4.90, 0.00, 5.80], b1 + 8.0, 10.20)
    l1 = s.X(-4.90) - 8.0
    dim_chain(s, "v", [3.40, 3.70, 9.90, 10.20], l1, -4.90)
    dim_chain(s, "v", [0.00, 10.20], l1 - 7.5, -4.90)
    r1 = s.X(5.80) + 8.0
    dim_chain(s, "v", [0.00, 0.55, 7.65, 8.20], r1, 5.80)
    dim_free(s, (EX0, EY_BOT), (EX1, EY_BOT), 6.0)


# ----------------------------------------------------------------------------
# PISO 1
# ----------------------------------------------------------------------------
def draw_piso1(s):
    bands = [
        Band("h", 0.00, 0.55, (0.00, 5.80), (0.00, 5.80), (0.55, 5.25),
             [dict(a=0.90, b=1.60, kind="window")]),
        Band("h", 8.20, 7.65, (0.00, 5.80), (0.00, 5.80), (0.55, 5.25),
             [dict(a=2.30, b=3.50, kind="window")]),
        Band("v", 0.00, 0.55, (0.55, 7.65), (0.00, 8.20), (0.55, 7.65),
             [dict(a=6.30, b=7.10, kind="window")]),
        Band("v", 5.80, 5.25, (0.55, 7.65), (0.00, 8.20), (0.55, 7.65),
             [dict(a=5.60, b=6.40, kind="window")]),
    ]
    draw_bands(s, bands, 1)

    # cumeeira (elemento acima do plano de corte)
    s.line((2.90, 0.00), (2.90, 8.20), "cline")
    s.text(3.06, 7.20, "CUMEEIRA", "t-lbl", "middle", rot=-90)

    cama(s, 2.60, 0.55)
    mesinha(s, 1.30, 0.55, 1.75, 0.95)
    mesinha(s, 3.45, 0.55, 3.90, 0.95)
    roupeiro(s, 0.55, 2.80, 1.15, 6.00, "E", 4)
    s.text(0.86, 4.40, "ROUPEIRO", "t-lbl", "middle", rot=-90)
    secretaria(s, 1.30, 7.20, 2.40, 7.65)
    s.text(1.85, 7.06, "CÓMODA", "t-lbl")
    cadeirao(s, 4.40, 6.90, 0)

    escada(s, 1)
    s.text(4.65, 3.90, "VAZIO", "t-lbl")

    seta(s, (2.60, 3.35), (1.30, 3.35))
    seta(s, (2.60, 3.35), (3.90, 3.35))
    fundo(s, 2.60, 3.06, 1.85, 0.30)
    s.text(2.60, 3.13, "SENTIDO DO VIGAMENTO", "t-lbl")
    s.text(2.30, 4.52, "QUARTO", "t-room")
    s.text(2.30, 4.88, "29,16 m²", "t-area")

    top = s.Y(0.00) - 9.0
    dim_chain(s, "h", [0.00, 0.55, 5.25, 5.80], top, 0.00)
    bot = s.Y(8.20) + 9.0
    dim_chain(s, "h", [0.00, 2.30, 3.50, 5.80], bot, 8.20)
    dim_chain(s, "h", [0.00, 5.80], bot + 8.0, 8.20)
    l1 = s.X(0.00) - 8.0
    dim_chain(s, "v", [0.00, 0.55, 7.65, 8.20], l1, 0.00)
    dim_chain(s, "v", [0.00, 8.20], l1 - 7.5, 0.00)
    dim_free(s, (EX0, EY_BOT), (EX1, EY_BOT), 6.0)


# ----------------------------------------------------------------------------
# folhas
# ----------------------------------------------------------------------------
LEG0 = [
    ("stone", "PAREDE EXISTENTE — ALVENARIA DE PEDRA (0,55 m)"),
    ("new", "PAREDE NOVA — TABIQUE / GESSO CARTONADO (0,12 m)"),
    ("vao", "VÃO ENVIDRAÇADO"),
    ("porta", "PORTA COM SENTIDO DE ABERTURA"),
    ("lajeta", "PAVIMENTO EXTERIOR EM LAJETA DE GRANITO"),
]
LEG1 = [
    ("stone", "PAREDE EXISTENTE — ALVENARIA DE PEDRA (0,55 m)"),
    ("vao", "VÃO ENVIDRAÇADO"),
    ("porta", "PORTA COM SENTIDO DE ABERTURA"),
]
NOTAS0 = [
    "1.  Cotas em metros, medidas em tosco. A confirmar em obra.",
    "2.  Paredes exteriores em alvenaria de pedra existente (0,55 m), a manter e consolidar.",
    "3.  Paredes interiores novas em tabique de madeira ou gesso cartonado (0,12 m).",
    "4.  Pé-direito do piso 0: 2,60 m sob o vigamento de madeira.",
    "5.  Escada em madeira maciça: 15 espelhos de 0,187 m e 14 cobertores de 0,27 m.",
    "6.  Vãos existentes a manter; novos vãos exigem lintel e verificação estrutural.",
]
NOTAS1 = [
    "1.  Cotas em metros, medidas em tosco. A confirmar em obra.",
    "2.  Pé-direito variável: 2,20 m junto à parede e 3,40 m na cumeeira.",
    "3.  Vigamento e ripado da cobertura à vista, em madeira tratada.",
    "4.  Guarda do vão da escada com 1,00 m de altura, em madeira maciça.",
    "5.  Isolamento térmico aplicado pelo interior da cobertura (0,10 m).",
    "6.  Cobertura de duas águas em telha cerâmica recuperada sobre estrutura a rever.",
]
AREAS0 = [
    ("W.C.", "6,00 m²"),
    ("SALA / COZINHA", "26,76 m²"),
    ("LAVANDARIA", "4,59 m²"),
    ("ESCRITÓRIO", "5,87 m²"),
    ("ÁREA ÚTIL DO PISO 0", "43,22 m²"),
    ("QUINTAL (EXTERIOR)", "17,27 m²"),
]
AREAS1 = [
    ("QUARTO", "29,16 m²"),
    ("ÁREA ÚTIL DO PISO 1", "29,16 m²"),
    ("ÁREA ÚTIL DO PISO 0", "43,22 m²"),
    ("ÁREA ÚTIL TOTAL", "72,38 m²"),
    ("QUINTAL (EXTERIOR)", "17,27 m²"),
]


def folha0():
    s = Sheet(107.33, 76.0)
    frame(s)
    header(s, "PLANTA DO PISO 0",
           "PROPOSTA DE RENOVAÇÃO  ·  ESCALA 1:75  ·  COTAS EM METROS")
    legenda(s, 23.0, 33.0, 103.0, LEG0)
    caixa_titulo(s, "QUADRO DE ÁREAS  ·  PISO 0", AREAS0, 112.0, 35.0, 197.0, 4.0)
    draw_piso0(s)
    norte(s, 75.0, 101.0, 6.4)
    escala_grafica(s, 26.0, 238.0)
    notas(s, 104.0, 233.0, 197.0, NOTAS0)
    cartucho(s, "PLANTA DO PISO 0", "01 DE 02")
    return page(s, "Planta do Piso 0")


def folha1():
    s = Sheet(70.0, 86.0)
    frame(s)
    header(s, "PLANTA DO PISO 1",
           "PROPOSTA DE RENOVAÇÃO  ·  ESCALA 1:75  ·  COTAS EM METROS")
    legenda(s, 23.0, 33.0, 103.0, LEG1)
    caixa_titulo(s, "QUADRO DE ÁREAS", AREAS1, 112.0, 35.0, 197.0, 4.0)
    draw_piso1(s)
    norte(s, 176.0, 96.0, 6.4)
    escala_grafica(s, 26.0, 224.0)
    notas(s, 104.0, 219.0, 197.0, NOTAS1)
    cartucho(s, "PLANTA DO PISO 1", "02 DE 02")
    return page(s, "Planta do Piso 1")


HTML = ('<!DOCTYPE html><html lang="pt"><head><meta charset="utf-8"><title>%s</title>'
        '<style>@page{size:210mm 297mm;margin:0}'
        'html,body{margin:0;padding:0;background:#fff}'
        'svg{display:block;page-break-after:always}</style></head><body>%s</body></html>')


CHROME_CANDIDATOS = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
]


def gerar_pdf():
    """imprime as folhas HTML para PDF A4 com chromium headless"""
    exe = next((c for c in CHROME_CANDIDATOS if os.path.exists(c)), None)
    if not exe:
        print("chromium nao encontrado: PDF nao gerado")
        return
    for nome in ("planta_piso0", "planta_piso1", "plantas"):
        src = os.path.join(OUT, nome + ".html")
        dst = os.path.join(OUT, nome + ".pdf")
        subprocess.run([exe, "--headless", "--disable-gpu", "--no-sandbox",
                        "--no-pdf-header-footer", "--print-to-pdf=" + dst, "file://" + src],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("gerado", os.path.basename(dst))


def main():
    f0, f1 = folha0(), folha1()
    open(os.path.join(OUT, "planta_piso0.svg"), "w", encoding="utf-8").write(f0)
    open(os.path.join(OUT, "planta_piso1.svg"), "w", encoding="utf-8").write(f1)
    open(os.path.join(OUT, "planta_piso0.html"), "w", encoding="utf-8").write(
        HTML % ("Planta do Piso 0", f0))
    open(os.path.join(OUT, "planta_piso1.html"), "w", encoding="utf-8").write(
        HTML % ("Planta do Piso 1", f1))
    open(os.path.join(OUT, "plantas.html"), "w", encoding="utf-8").write(
        HTML % ("Casa de pedra — plantas", f0 + f1))
    print("svg/html gerados em", OUT)
    gerar_pdf()


if __name__ == "__main__":
    main()
