"""
Fly-in — Interactive Drone Routing Visualizer
============================================
Run:  python3 visualizer.py maps/easy/02_simple_fork.txt
Keys: Space=play/pause  ←→=step  ↑↓=speed  R=reset  E=edit mode  Q=quit
"""

import pygame
import sys
import math
import time
from typing import Any
from parser import Parser
from graph import Graph
from algorithm import Dijkstra
from traffic import Traffic

# ══════════════════════════════════════════════════════════════════════
#  PALETTE
# ══════════════════════════════════════════════════════════════════════
C = {
    "bg":           (11,  13,  20),
    "panel":        (16,  20,  32),
    "panel2":       (20,  25,  40),
    "border":       (36,  44,  66),
    "border_hi":    (70,  90, 140),
    "text":         (215, 225, 240),
    "dim":          (70,  84, 106),
    "accent":       (79, 110, 247),
    "accent2":      (50, 180, 230),
    "ok":           (40, 190, 120),
    "warn":         (230, 170,  40),
    "err":          (210,  60,  60),
    "edge":         (44,  56,  84),
    "edge_hi":      (90, 120, 180),
    "white":        (255, 255, 255),
    "black":        (0,   0,   0),
}

ZONE_COL: dict[str, tuple[int, int, int]] = {
    "normal":     (48, 108, 178),
    "priority":   (72, 168,  56),
    "restricted": (196, 126,  28),
    "blocked":    (48,  48,  54),
    "start":      (28, 168, 126),
    "goal":       (208,  76,  36),
}

META_COL: dict[str, tuple[int, int, int]] = {
    "red":     (210,  55,  55), "green":   (50, 200, 100),
    "yellow":  (230, 200,  50), "blue":    (53, 122, 189),
    "purple":  (150,  80, 200), "cyan":    (50, 200, 220),
    "orange":  (230, 140,  30), "brown":   (160, 100,  50),
    "maroon":  (160,  30,  30), "gold":    (240, 200,  20),
    "darkred": (160,  20,  20), "crimson": (210,  30,  70),
    "violet":  (140,  60, 220), "black":   (45,  45,  50),
    "gray":    (140, 140, 150), "rainbow": (180, 100, 255),
    "pink":    (255, 120, 180),
}

DRONE_PAL: list[tuple[int, int, int]] = [
    (255, 220,  50), (50, 220, 255), (255, 100, 120),
    (100, 255, 140), (255, 160,  50), (180, 100, 255),
    (255,  60, 200), (50, 255, 200), (200, 255,  60),
    (255, 190, 100), (100, 200, 255), (255, 140, 180),
    (160, 255, 100), (255, 100,  60), (60, 160, 255),
]

W, H = 1440, 880
PANEL_W = 320
GRAPH_W = W - PANEL_W
NODE_R = 26
DRONE_R = 7
FPS = 60
ANIM_F = 50


# ══════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════
def dcol(did: int) -> tuple[int, int, int]:
    return DRONE_PAL[(did - 1) % len(DRONE_PAL)]


def zone_col(zone: str, graph: Graph) -> tuple[int, int, int]:
    if zone == graph.start:
        return ZONE_COL["start"]
    if zone == graph.end:
        return ZONE_COL["goal"]
    name = graph.zone_color.get(zone, "")
    if name in META_COL:
        return META_COL[name]
    return ZONE_COL.get(graph.zone_type.get(zone, "normal"), ZONE_COL["normal"])


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease(t: float) -> float:
    return 1 - (1 - t) ** 3


def rr(surf: pygame.Surface, col: tuple, rect: pygame.Rect,
       r: int = 8, bw: int = 0, bc: tuple = (0, 0, 0)) -> None:
    pygame.draw.rect(surf, col, rect, border_radius=r)
    if bw:
        pygame.draw.rect(surf, bc, rect, bw, border_radius=r)


def layout_graph(parser: Parser, w: int, h: int,
                 pad: int = 72) -> dict[str, tuple[float, float]]:
    coords = parser.zone_coords
    if not coords:
        return {}
    xs = [v[0] for v in coords.values()]
    ys = [v[1] for v in coords.values()]
    rx = (max(xs) - min(xs)) or 1
    ry = (max(ys) - min(ys)) or 1
    return {
        z: (pad + (x - min(xs)) / rx * (w - 2*pad),
            pad + (1 - (y - min(ys)) / ry) * (h - 2*pad))
        for z, (x, y) in coords.items()
    }


# ══════════════════════════════════════════════════════════════════════
#  MESSAGE LOG
# ══════════════════════════════════════════════════════════════════════
class MsgLog:
    """Typed messages shown at bottom of screen."""
    KINDS = {"info": C["accent2"], "ok": C["ok"],
             "warn": C["warn"], "err": C["err"]}
    MAX = 4

    def __init__(self) -> None:
        self.msgs: list[tuple[str, str, float]] = []  # (kind, text, born)

    def add(self, text: str, kind: str = "info") -> None:
        self.msgs.append((kind, text, time.time()))
        if len(self.msgs) > self.MAX:
            self.msgs.pop(0)

    def draw(self, surf: pygame.Surface, font: pygame.font.Font,
             x: int, y: int) -> None:
        now = time.time()
        for i, (kind, text, born) in enumerate(self.msgs):
            age = now - born
            alpha = max(0, min(255, int(255 * (1 - max(0, age - 4) / 2))))
            col = self.KINDS.get(kind, C["text"])
            s = font.render(text, True, col)
            s.set_alpha(alpha)
            surf.blit(s, (x, y + i * 18))
        # purge old
        self.msgs = [(k, t, b) for k, t, b in self.msgs
                     if now - b < 6]


# ══════════════════════════════════════════════════════════════════════
#  EDIT PANEL  (right-side editor when E is pressed)
# ══════════════════════════════════════════════════════════════════════
class EditPanel:
    ZONE_TYPES = ["normal", "priority", "restricted", "blocked"]
    META_COLORS = ["", "red", "green", "blue", "orange", "gold",
                   "violet", "crimson", "brown", "maroon", "cyan",
                   "purple", "gray", "black"]

    def __init__(self, font: pygame.font.Font,
                 font_sm: pygame.font.Font) -> None:
        self.font = font
        self.font_sm = font_sm
        self.visible = False
        self.zone: str | None = None
        self.fields: dict[str, Any] = {}
        self.active_field: str | None = None
        self.input_buf: str = ""
        self.buttons: list[dict] = []

    def open(self, zone: str, graph: Graph) -> None:
        self.zone = zone
        self.visible = True
        self.fields = {
            "zone_type": graph.zone_type.get(zone, "normal"),
            "color":     graph.zone_color.get(zone, ""),
            "capacity":  str(graph.zone_capacity.get(zone, 1)),
        }
        self.active_field = None
        self.input_buf = ""

    def close(self) -> None:
        self.visible = False
        self.zone = None
        self.active_field = None
        self.input_buf = ""

    def apply(self, graph: Graph, log: MsgLog) -> None:
        if not self.zone:
            return
        z = self.zone

        # zone type
        zt = self.fields["zone_type"]
        if zt in self.ZONE_TYPES:
            graph.zone_type[z] = zt
        else:
            log.add(f"Invalid zone type: {zt}", "err")
            return

        # color
        graph.zone_color[z] = self.fields["color"]

        # capacity
        try:
            cap = int(self.fields["capacity"])
            if cap < 1:
                raise ValueError
            graph.zone_capacity[z] = cap
            # also update costs in graph
            if zt == "restricted":
                for nb in graph.neighbors.get(z, []):
                    graph.costs[(nb, z)] = 2
            elif zt in ("normal", "priority"):
                for nb in graph.neighbors.get(z, []):
                    graph.costs[(nb, z)] = 1
            elif zt == "blocked":
                for nb in graph.neighbors.get(z, []):
                    if z in graph.neighbors.get(nb, []):
                        graph.neighbors[nb].remove(z)
                graph.neighbors[z] = []

            log.add(f"✓ Zone '{z}' updated → {zt} cap={cap}", "ok")
            self.close()
        except ValueError:
            log.add(f"Capacity must be a positive integer", "err")

    def draw(self, surf: pygame.Surface, px: int) -> None:
        if not self.visible or not self.zone:
            return

        # background
        rect = pygame.Rect(px, 0, PANEL_W, H)
        pygame.draw.rect(surf, C["panel2"], rect)
        pygame.draw.line(surf, C["border_hi"], (px, 0), (px, H), 2)

        y = 20
        pw = PANEL_W

        # title
        t = self.font.render("EDIT ZONE", True, C["accent"])
        surf.blit(t, (px + pw//2 - t.get_width()//2, y))
        y += 32

        zn = self.font_sm.render(f"  {self.zone}", True, C["text"])
        surf.blit(zn, (px + pw//2 - zn.get_width()//2, y))
        y += 26

        pygame.draw.line(surf, C["border_hi"], (px+10, y), (px+pw-10, y))
        y += 14

        # ── zone type selector ────────────────────────────
        label = self.font_sm.render("Zone type:", True, C["dim"])
        surf.blit(label, (px+14, y))
        y += 18
        self.buttons = []
        bw = (pw - 28) // 2 - 4
        for i, zt in enumerate(self.ZONE_TYPES):
            bx = px + 14 + (i % 2) * (bw + 8)
            by = y + (i // 2) * 32
            sel = self.fields["zone_type"] == zt
            col = ZONE_COL.get(zt, C["border"])
            bg = col if sel else C["border"]
            rr(surf, bg, pygame.Rect(bx, by, bw, 26), 6,
               2, col if not sel else C["white"])
            ts = self.font_sm.render(zt, True,
                                     C["white"] if sel else C["dim"])
            surf.blit(ts, (bx + bw//2 - ts.get_width()//2,
                           by + 13 - ts.get_height()//2))
            self.buttons.append({"rect": pygame.Rect(bx, by, bw, 26),
                                 "field": "zone_type", "value": zt})
        y += (len(self.ZONE_TYPES)//2) * 32 + 10

        # ── color selector ────────────────────────────────
        pygame.draw.line(surf, C["border"], (px+10, y), (px+pw-10, y))
        y += 10
        label2 = self.font_sm.render("Color:", True, C["dim"])
        surf.blit(label2, (px+14, y))
        y += 18

        cols_per_row = 4
        cw = (pw - 28) // cols_per_row - 4
        for i, mc in enumerate(self.META_COLORS):
            bx = px + 14 + (i % cols_per_row) * (cw + 4)
            by = y + (i // cols_per_row) * 26
            sel = self.fields["color"] == mc
            bg = META_COL.get(mc, C["border"]) if mc else C["border"]
            rr(surf, bg, pygame.Rect(bx, by, cw, 22), 4,
               2, C["white"] if sel else bg)
            name = mc if mc else "none"
            ts = self.font_sm.render(name[:5], True,
                                     C["white"] if mc else C["dim"])
            surf.blit(ts, (bx + cw//2 - ts.get_width()//2,
                           by + 11 - ts.get_height()//2))
            self.buttons.append({"rect": pygame.Rect(bx, by, cw, 22),
                                 "field": "color", "value": mc})
        y += (len(self.META_COLORS)//cols_per_row + 1) * 26 + 10

        # ── capacity input ────────────────────────────────
        pygame.draw.line(surf, C["border"], (px+10, y), (px+pw-10, y))
        y += 10
        label3 = self.font_sm.render("Capacity (max drones):", True, C["dim"])
        surf.blit(label3, (px+14, y))
        y += 18

        inp_rect = pygame.Rect(px+14, y, pw-28, 30)
        active = self.active_field == "capacity"
        rr(surf, C["bg"], inp_rect, 6, 2,
           C["accent"] if active else C["border"])
        val = self.input_buf if active else self.fields["capacity"]
        vs = self.font.render(val + ("|" if active else ""), True, C["text"])
        surf.blit(vs, (inp_rect.x+8, inp_rect.y+7))
        self.buttons.append({"rect": inp_rect, "field": "capacity",
                             "value": "__input__"})
        y += 40

        # ── apply / cancel buttons ─────────────────────────
        pygame.draw.line(surf, C["border"], (px+10, y), (px+pw-10, y))
        y += 14
        bw2 = (pw - 36) // 2
        apply_r = pygame.Rect(px+14,       y, bw2, 34)
        cancel_r = pygame.Rect(px+22+bw2,   y, bw2, 34)
        rr(surf, C["ok"],  apply_r,  8, 0)
        rr(surf, C["err"], cancel_r, 8, 0)
        at = self.font.render("Apply", True, C["white"])
        ct = self.font.render("Cancel", True, C["white"])
        surf.blit(at, (apply_r.centerx - at.get_width()//2,
                       apply_r.centery - at.get_height()//2))
        surf.blit(ct, (cancel_r.centerx - ct.get_width()//2,
                       cancel_r.centery - ct.get_height()//2))
        self.buttons.append(
            {"rect": apply_r,  "field": "__apply__",  "value": ""})
        self.buttons.append(
            {"rect": cancel_r, "field": "__cancel__", "value": ""})

    def handle_click(self, pos: tuple[int, int],
                     graph: Graph, log: MsgLog) -> None:
        for btn in self.buttons:
            if btn["rect"].collidepoint(pos):
                f, v = btn["field"], btn["value"]
                if f == "__apply__":
                    self.apply(graph, log)
                elif f == "__cancel__":
                    self.close()
                    log.add("Edit cancelled", "info")
                elif v == "__input__":
                    self.active_field = f
                    self.input_buf = self.fields.get(f, "")
                else:
                    self.fields[f] = v
                    if f == "zone_type":
                        log.add(f"Type set to '{v}'", "info")
                return

    def handle_key(self, event: pygame.event.Event) -> None:
        if self.active_field != "capacity":
            return
        if event.key == pygame.K_RETURN:
            self.fields["capacity"] = self.input_buf
            self.active_field = None
        elif event.key == pygame.K_ESCAPE:
            self.active_field = None
            self.input_buf = self.fields.get("capacity", "1")
        elif event.key == pygame.K_BACKSPACE:
            self.input_buf = self.input_buf[:-1]
        elif event.unicode.isdigit():
            self.input_buf += event.unicode


# ══════════════════════════════════════════════════════════════════════
#  DRONE SPRITE
# ══════════════════════════════════════════════════════════════════════
class Drone:
    def __init__(self, did: int, pos: tuple[float, float]) -> None:
        self.did = did
        self.x, self.y = float(pos[0]), float(pos[1])
        self.tx, self.ty = self.x, self.y
        self.p = 1.0
        self.color = dcol(did)
        self.trail: list[tuple[float, float]] = []

    def move_to(self, pos: tuple[float, float]) -> None:
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)
        self.tx, self.ty = float(pos[0]), float(pos[1])
        self.p = 0.0

    def update(self, spd: float) -> None:
        if self.p < 1.0:
            self.p = min(1.0, self.p + spd)
            t = ease(self.p)
            self.x = lerp(self.x, self.tx, t)
            self.y = lerp(self.y, self.ty, t)

    def draw(self, surf: pygame.Surface,
             font: pygame.font.Font, show_trail: bool = True) -> None:
        # trail
        if show_trail:
            for i, (tx, ty) in enumerate(self.trail):
                alpha = int(60 * (i+1) / len(self.trail))
                s = pygame.Surface((DRONE_R*2, DRONE_R*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, alpha),
                                   (DRONE_R, DRONE_R), DRONE_R//2)
                surf.blit(s, (int(tx)-DRONE_R, int(ty)-DRONE_R))

        ix, iy = int(self.x), int(self.y)
        # shadow
        sh = pygame.Surface((DRONE_R*4, DRONE_R*4), pygame.SRCALPHA)
        pygame.draw.circle(sh, (0, 0, 0, 70),
                           (DRONE_R*2, DRONE_R*2+3), DRONE_R)
        surf.blit(sh, (ix-DRONE_R*2, iy-DRONE_R*2))
        # body
        pygame.draw.circle(surf, (0, 0, 0),     (ix, iy), DRONE_R+2)
        pygame.draw.circle(surf, self.color,  (ix, iy), DRONE_R)
        pygame.draw.circle(surf, (255, 255, 255), (ix, iy), DRONE_R, 1)
        # id
        lbl = font.render(str(self.did), True, (0, 0, 0))
        surf.blit(lbl, (ix - lbl.get_width()//2, iy - lbl.get_height()//2))


# ══════════════════════════════════════════════════════════════════════
#  VISUALIZER
# ══════════════════════════════════════════════════════════════════════
class Visualizer:
    SPEEDS = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0]

    def __init__(self, graph: Graph, parser: Parser,
                 traffic: Traffic) -> None:
        pygame.init()
        pygame.display.set_caption("Fly-in  ·  Drone Routing Visualizer")
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()

        self.graph = graph
        self.parser = parser
        self.traffic = traffic
        self.nb = traffic.nb_drones

        self.f_xs = pygame.font.SysFont("monospace", 10)
        self.f_sm = pygame.font.SysFont("monospace", 12)
        self.f_md = pygame.font.SysFont("monospace", 13, bold=True)
        self.f_lg = pygame.font.SysFont("monospace", 16, bold=True)
        self.f_xl = pygame.font.SysFont("monospace", 22, bold=True)

        self.layout = layout_graph(parser, GRAPH_W, H - 50)
        self.log = MsgLog()
        self.editor = EditPanel(self.f_md, self.f_sm)

        self.turns: list[list[str]] = []
        self.states: list[dict[int, str]] = []
        self.turn = 0
        self.playing = False
        self.speed = 1.0
        self.frame = 0.0
        self.hovered: str | None = None
        self.show_trail = True

        # drones
        sp = self.layout.get(graph.start, (200.0, 200.0))
        self.drones: dict[int, Drone] = {
            d: Drone(d, sp) for d in range(1, self.nb+1)
        }

        self._rerun()
        self.log.add("Simulation ready — press Space to play", "ok")
        self.log.add("Press E on a zone to edit it", "info")

    # ── simulation ────────────────────────────────────────
    def _rerun(self) -> None:
        d = Dijkstra(self.graph)
        t2 = Traffic(self.graph, d, self.nb)
        turns = t2.run()
        if turns is None:
            self.log.add("No valid path found!", "err")
            self.turns = []
            self.states = [{i: self.graph.start for i in range(1, self.nb+1)}]
        else:
            self.turns = turns
            self.states = self._build_states()
            self.log.add(
                f"✓ Simulation: {len(turns)} turns for {self.nb} drones", "ok")
        self.turn = 0
        self.frame = 0.0
        self.playing = False
        self._place_drones(0)

    def _build_states(self) -> list[dict[int, str]]:
        state: dict[int, str] = {d: self.graph.start
                                 for d in range(1, self.nb+1)}
        out = [dict(state)]
        for turn in self.turns:
            for mv in turn:
                p = mv.split("-")
                did = int(p[0][1:])
                # D1-zone → p = ["D1", "zone"]
                # D1-zone_a-zone_b → p = ["D1", "zone_a", "zone_b"]
                if len(p) == 2:
                    state[did] = p[1]          # normal move
                elif len(p) == 3:
                    state[did] = f"{p[1]}-{p[2]}"  # mid-link
            out.append(dict(state))
        return out

    def _place_drones(self, turn_idx: int) -> None:
        state = self.states[min(turn_idx, len(self.states)-1)]
        groups: dict[str, list[int]] = {}
        for did, zone in state.items():
            groups.setdefault(zone, []).append(did)

        for zone, group in groups.items():
            # mid-link drone: position halfway between the two zones
            if "-" in zone and zone not in self.layout:
                parts = zone.split("-")
                if len(parts) == 2:
                    pa = self.layout.get(parts[0])
                    pb = self.layout.get(parts[1])
                    if pa and pb:
                        pos = ((pa[0]+pb[0])/2, (pa[1]+pb[1])/2)
                    else:
                        continue
                else:
                    continue
            else:
                pos = self.layout.get(zone)
                if not pos:
                    continue

            n = len(group)
            for i, did in enumerate(sorted(group)):
                if n == 1:
                    ox, oy = 0.0, 0.0
                else:
                    ang = (i / n) * 2 * math.pi
                    radius = min(NODE_R - 6, 5 * math.sqrt(n))
                    ox = math.cos(ang) * radius
                    oy = math.sin(ang) * radius
                self.drones[did].move_to((pos[0]+ox, pos[1]+oy))

    # ── draw graph ────────────────────────────────────────
    def _draw_edges(self) -> None:
        for a, b in self.parser.connection:
            pa = self.layout.get(a)
            pb = self.layout.get(b)
            if not pa or not pb:
                continue
            cap = self.graph.link_capacity.get(
                (a, b), self.graph.link_capacity.get((b, a), 1))
            hi = (a == self.hovered or b == self.hovered)
            col = C["edge_hi"] if hi else C["edge"]
            lw = 2 if hi else 1
            pygame.draw.line(self.screen, col,
                             (int(pa[0]), int(pa[1])),
                             (int(pb[0]), int(pb[1])), lw)
            if cap > 1:
                mx = (pa[0]+pb[0])/2
                my = (pa[1]+pb[1])/2
                s = self.f_xs.render(f"×{cap}", True,
                                     C["accent"] if hi else C["dim"])
                self.screen.blit(s, (int(mx)-s.get_width()//2,
                                     int(my)-s.get_height()//2))

    def _draw_nodes(self) -> None:
        mx, my = pygame.mouse.get_pos()
        self.hovered = None
        edit_mode = self.editor.visible

        for zone, (nx, ny) in self.layout.items():
            inx, iny = int(nx), int(ny)
            dist = math.hypot(mx-inx, my-iny)
            hov = dist < NODE_R + 6 and not edit_mode
            if hov:
                self.hovered = zone

            col = zone_col(zone, self.graph)
            dark = tuple(max(0, c-70) for c in col)

            # glow
            if hov or zone in (self.graph.start, self.graph.end):
                r2 = NODE_R + (8 if hov else 4)
                gl = pygame.Surface((r2*4, r2*4), pygame.SRCALPHA)
                pygame.draw.circle(gl, (*col, 45 if hov else 30),
                                   (r2*2, r2*2), r2*2)
                self.screen.blit(gl, (inx-r2*2, iny-r2*2))

            # node body
            pygame.draw.circle(self.screen, dark, (inx, iny), NODE_R+2)
            pygame.draw.circle(self.screen, col,  (inx, iny), NODE_R)
            ring = C["white"] if hov else (90, 110, 150)
            pygame.draw.circle(self.screen, ring, (inx, iny), NODE_R, 2)

            # zone type badge
            zt = self.graph.zone_type.get(zone, "normal")
            badge = {"restricted": "R", "priority": "★",
                     "blocked": "✕"}.get(zt, "")
            if badge:
                bs = self.f_xs.render(badge, True, (255, 255, 200))
                self.screen.blit(bs, (inx+NODE_R-2, iny-NODE_R-2))

            # name
            short = zone if len(zone) <= 13 else zone[:12]+"…"
            ns = self.f_xs.render(short, True,
                                  C["white"] if hov else C["text"])
            self.screen.blit(ns, (inx-ns.get_width()//2, iny+NODE_R+3))

            # capacity
            cap = self.graph.zone_capacity.get(zone, 1)
            if 1 < cap < self.nb:
                cs = self.f_xs.render(f"[{cap}]", True, C["dim"])
                self.screen.blit(cs, (inx-cs.get_width()//2, iny+NODE_R+14))

    def _draw_tooltip(self) -> None:
        if not self.hovered or self.editor.visible:
            return
        zone = self.hovered
        zt = self.graph.zone_type.get(zone, "normal")
        col = self.graph.zone_color.get(zone, "—")
        cap = self.graph.zone_capacity.get(zone, 1)
        cost = {"normal": 1, "priority": 1,
                "restricted": 2, "blocked": "∞"}.get(zt)
        state = self.states[min(self.turn, len(self.states)-1)]
        here = sorted([d for d, z in state.items() if z == zone])

        lines = [
            f"  Zone:     {zone}",
            f"  Type:     {zt}",
            f"  Color:    {col}",
            f"  Capacity: {cap}",
            f"  Cost:     {cost} turn(s)",
            f"  Drones:   {len(here)} here",
        ]
        if here:
            ids = "  " + ", ".join(f"D{d}" for d in here[:10])
            if len(here) > 10:
                ids += f"… +{len(here)-10}"
            lines.append(ids)
        lines.append("")
        lines.append("  [E] to edit this zone")

        tw = max(self.f_sm.size(l)[0] for l in lines) + 20
        th = len(lines)*17 + 14
        px, py = pygame.mouse.get_pos()
        tx = min(px+14, W-PANEL_W-tw-4)
        ty = min(py+14, H-th-4)

        tip = pygame.Surface((tw, th), pygame.SRCALPHA)
        tip.fill((14, 18, 30, 230))
        pygame.draw.rect(tip, (80, 100, 160, 200),
                         tip.get_rect(), 1, border_radius=7)
        for i, line in enumerate(lines):
            c = C["accent"] if "edit" in line else C["text"]
            s = self.f_sm.render(line, True, c)
            tip.blit(s, (8, 6+i*17))
        self.screen.blit(tip, (tx, ty))

    # ── side panel ────────────────────────────────────────
    def _draw_panel(self) -> None:
        px = GRAPH_W
        surf = self.screen
        pygame.draw.rect(surf, C["panel"], (px, 0, PANEL_W, H))
        pygame.draw.line(surf, C["border"], (px, 0), (px, H), 2)

        y = 18
        pw = PANEL_W

        # title
        t = self.f_xl.render("FLY-IN", True, C["text"])
        surf.blit(t, (px+pw//2-t.get_width()//2, y))
        y += 30
        s = self.f_xs.render("Drone Routing Visualizer", True, C["dim"])
        surf.blit(s, (px+pw//2-s.get_width()//2, y))
        y += 18

        self._hl(px, y)
        y += 12

        # stats
        total = len(self.turns)
        state = self.states[min(self.turn, len(self.states)-1)]
        done = sum(1 for z in state.values() if z == self.graph.end)

        rows = [
            ("Turn",      f"{self.turn} / {total}"),
            ("Delivered", f"{done} / {self.nb}"),
            ("Speed",     f"×{self.speed:.2g}"),
            ("Status",    "▶ Playing" if self.playing else "⏸ Paused"),
            ("Edit mode",
             "ON [E=close]" if self.editor.visible else "OFF [E=open]"),
        ]
        for label, val in rows:
            lc = self.f_sm.render(label+":", True, C["dim"])
            vc = self.f_sm.render(val, True,
                                  C["ok"] if "Playing" in val
                                  else C["accent"] if "ON" in val else C["text"])
            surf.blit(lc, (px+14, y))
            surf.blit(vc, (px+pw-vc.get_width()-14, y))
            y += 20

        # progress bar
        y += 4
        bw = pw-28
        pygame.draw.rect(surf, C["border"], (px+14, y, bw, 8), border_radius=4)
        if total:
            fw = int(bw * self.turn/total)
            pygame.draw.rect(surf, C["ok"], (px+14, y, fw, 8), border_radius=4)
        y += 18

        self._hl(px, y)
        y += 10

        # controls
        ct = self.f_md.render("Controls", True, C["dim"])
        surf.blit(ct, (px+14, y))
        y += 18
        ctrls = [
            ("Space",    "Play / Pause"),
            ("→ / ←",   "Step fwd / back"),
            ("↑ / ↓",   "Speed up / down"),
            ("R",        "Rerun simulation"),
            ("E",        "Edit hovered zone"),
            ("T",        "Toggle trail"),
            ("Q / Esc",  "Quit"),
        ]
        for k, v in ctrls:
            ks = self.f_sm.render(k,  True, C["accent"])
            vs = self.f_sm.render(v,  True, C["dim"])
            surf.blit(ks, (px+14, y))
            surf.blit(vs, (px+110, y))
            y += 16
        y += 4

        self._hl(px, y)
        y += 10

        # current moves
        mt = self.f_md.render("This turn moves:", True, C["dim"])
        surf.blit(mt, (px+14, y))
        y += 18
        if 0 < self.turn <= total:
            moves = self.turns[self.turn-1]
            for mv in moves[:9]:
                p = mv.split("-")
                did = int(p[0][1:])
                zn = p[1]
                dc = dcol(did)
                zc = zone_col(zn, self.graph)
                ds = self.f_sm.render(p[0]+"-", True, dc)
                zs = self.f_sm.render(zn[:20],  True, zc)
                surf.blit(ds, (px+14, y))
                surf.blit(zs, (px+14+ds.get_width(), y))
                y += 15
            if len(moves) > 9:
                ms = self.f_xs.render(
                    f"  … +{len(moves)-9} more", True, C["dim"])
                surf.blit(ms, (px+14, y))
                y += 14

        # drone list (bottom)
        lh = min(self.nb, 14)*14+30
        y2 = H - lh - 44
        self._hl(px, y2)
        y2 += 8
        dl = self.f_md.render("Drone positions:", True, C["dim"])
        surf.blit(dl, (px+14, y2))
        y2 += 16
        for d in range(1, min(self.nb+1, 15)):
            zn = state.get(d, "?")
            col = dcol(d)
            pygame.draw.circle(surf, col, (px+20, y2+5), 4)
            done_z = zn == self.graph.end
            tc = ZONE_COL["goal"] if done_z else C["text"]
            short = zn if len(zn) <= 19 else zn[:18]+"…"
            ts = self.f_xs.render(f"D{d}: {short}", True, tc)
            surf.blit(ts, (px+30, y2))
            y2 += 14
        if self.nb > 14:
            ms = self.f_xs.render(f"  … +{self.nb-14} more", True, C["dim"])
            surf.blit(ms, (px+14, y2))

        # done banner
        if self.turn >= total and total > 0 and done == self.nb:
            bs = self.f_lg.render(
                f"✓  All done in {total} turns!", True, C["ok"])
            surf.blit(bs, (px+pw//2-bs.get_width()//2, H-28))

    def _hl(self, px: int, y: int) -> None:
        pygame.draw.line(self.screen, C["border"],
                         (px+10, y), (px+PANEL_W-10, y))

    # ── speed bar ─────────────────────────────────────────
    def _draw_speed_bar(self) -> None:
        bw, bh = 52, 24
        gap = 5
        total = len(self.SPEEDS)*(bw+gap)-gap
        x0 = GRAPH_W//2 - total//2
        y0 = H - 36
        mx, my = pygame.mouse.get_pos()

        for i, sp in enumerate(self.SPEEDS):
            bx = x0 + i*(bw+gap)
            sel = abs(sp-self.speed) < 0.01
            hov = pygame.Rect(bx, y0, bw, bh).collidepoint(mx, my)
            bg = C["accent"] if sel else (
                C["border_hi"] if hov else C["border"])
            rr(self.screen, bg, pygame.Rect(bx, y0, bw, bh), 5)
            ls = self.f_sm.render(f"×{sp:.2g}", True,
                                  C["white"] if sel else C["dim"])
            self.screen.blit(ls, (bx+bw//2-ls.get_width()//2,
                                  y0+bh//2-ls.get_height()//2))

    # ── header bar ────────────────────────────────────────
    def _draw_header(self) -> None:
        s = self.f_xs.render(
            f"  {self.parser.zone_coords and self.graph.start}"
            f"  →  {self.graph.end}"
            f"   |   {len(self.parser.zones)} zones"
            f"   |   {len(self.parser.connection)} connections"
            f"   |   {self.nb} drones",
            True, C["dim"])
        self.screen.blit(s, (10, 5))

    # ── log bar ───────────────────────────────────────────
    def _draw_log(self) -> None:
        self.log.draw(self.screen, self.f_sm, 10, H-80)

    # ── main loop ─────────────────────────────────────────
    def run(self) -> None:
        spd_f = 1.0 / ANIM_F

        while True:
            self.clock.tick(FPS)
            edit_open = self.editor.visible

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    # editor keyboard
                    if edit_open:
                        if event.key == pygame.K_ESCAPE:
                            self.editor.close()
                            self.log.add("Edit cancelled", "info")
                        else:
                            self.editor.handle_key(event)
                        continue

                    k = event.key
                    if k == pygame.K_SPACE:
                        self.playing = not self.playing
                        self.log.add(
                            "▶ Playing" if self.playing else "⏸ Paused")
                    elif k == pygame.K_RIGHT:
                        self._step(+1)
                    elif k == pygame.K_LEFT:
                        self._step(-1)
                    elif k in (pygame.K_UP, pygame.K_EQUALS, pygame.K_PLUS):
                        idx = self.SPEEDS.index(
                            min(self.SPEEDS, key=lambda s: abs(s-self.speed)))
                        self.speed = self.SPEEDS[min(
                            idx+1, len(self.SPEEDS)-1)]
                        self.log.add(f"Speed ×{self.speed:.2g}")
                    elif k in (pygame.K_DOWN, pygame.K_MINUS):
                        idx = self.SPEEDS.index(
                            min(self.SPEEDS, key=lambda s: abs(s-self.speed)))
                        self.speed = self.SPEEDS[max(idx-1, 0)]
                        self.log.add(f"Speed ×{self.speed:.2g}")
                    elif k == pygame.K_r:
                        self.log.add("Rerunning simulation…", "warn")
                        self._rerun()
                    elif k == pygame.K_e:
                        if self.hovered:
                            self.editor.open(self.hovered, self.graph)
                            self.log.add(
                                f"Editing zone '{self.hovered}'", "info")
                        else:
                            self.log.add("Hover a zone then press E", "warn")
                    elif k == pygame.K_t:
                        self.show_trail = not self.show_trail
                        self.log.add(
                            "Trails ON" if self.show_trail else "Trails OFF")
                    elif k in (pygame.K_q, pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if edit_open:
                        self.editor.handle_click(
                            event.pos, self.graph, self.log)
                        # if editor was just closed (apply), rerun
                        if not self.editor.visible:
                            self.log.add(
                                "Rerunning with new settings…", "warn")
                            self._rerun()
                    else:
                        self._handle_speed_click(event.pos)

            # auto advance
            if self.playing and self.turn < len(self.turns):
                self.frame += self.speed
                if self.frame >= ANIM_F:
                    self.frame = 0.0
                    self._step(+1)
            elif self.playing and self.turn >= len(self.turns):
                self.playing = False
                self.log.add(
                    f"✓ Simulation complete in {len(self.turns)} turns", "ok")

            # update drones
            for drone in self.drones.values():
                drone.update(spd_f * self.speed * 5)

            # ── render ──────────────────────────────────
            self.screen.fill(C["bg"])
            self._draw_header()
            self._draw_edges()
            self._draw_nodes()

            for drone in self.drones.values():
                drone.draw(self.screen, self.f_xs, self.show_trail)

            self._draw_tooltip()

            if edit_open:
                self.editor.draw(self.screen, GRAPH_W)
            else:
                self._draw_panel()

            self._draw_speed_bar()
            self._draw_log()

            pygame.display.flip()

    def _step(self, d: int) -> None:
        self.turn = max(0, min(len(self.turns), self.turn+d))
        self._place_drones(self.turn)

    def _handle_speed_click(self, pos: tuple[int, int]) -> None:
        bw, bh = 52, 24
        gap = 5
        total = len(self.SPEEDS)*(bw+gap)-gap
        x0 = GRAPH_W//2 - total//2
        y0 = H - 36
        for i, sp in enumerate(self.SPEEDS):
            if pygame.Rect(x0+i*(bw+gap), y0, bw, bh).collidepoint(pos):
                self.speed = sp
                self.log.add(f"Speed ×{sp:.2g}")
                break


# ══════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════
def main() -> None:
    p = Parser()
    p.load_file()
    p.parse_file()

    g = Graph(p)
    g.build(p)

    d = Dijkstra(g)
    t = Traffic(g, d, p.nb_drones)

    print(f"[fly-in] {p.nb_drones} drones  |  "
          f"{len(p.zones)} zones  |  "
          f"{len(p.connection)} connections")
    print("[fly-in] Launching visualizer…")

    v = Visualizer(g, p, t)
    v.run()


if __name__ == "__main__":
    main()
