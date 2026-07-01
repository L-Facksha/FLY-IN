from parser import Parser
from traffic import Traffic
from algorithm import Dijkstra
from graph import Graph
import pygame
import sys
import math

# ── 1. Setup ─────────────────────────────────────────────────────────
W, H = 1440, 880

# ── 2. Colors ─────────────────────────────────────────────────────────
BG = (15, 17, 23)
EDGE_COL = (44, 56, 84)
TEXT_COL = (220, 228, 240)
DRONE_COLORS = [
    (255, 220, 50), (50, 220, 255), (255, 100, 120),
    (100, 255, 140), (255, 160, 50), (180, 100, 255),
    (255, 140, 200), (100, 200, 255),
]


def to_screen(x: float, y: float,
              coords: dict, pad: int = 120) -> tuple[int, int]:
    """Convert zone coordinates to screen pixel position."""
    xs = [v[0] for v in coords.values()]
    ys = [v[1] for v in coords.values()]
    rx = (max(xs) - min(xs)) or 1
    ry = (max(ys) - min(ys)) or 1
    sx = int(pad + (x - min(xs)) / rx * (W - 2 * pad))
    sy = int(pad + (1 - (y - min(ys)) / ry) * (H - 2 * pad))
    return sx, sy


class Visualizer:
    def __init__(self, graph: Graph, parser: Parser,
                 traffic: Traffic) -> None:
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Fly-in - Drone Routing Visualizer")
        self.clock = pygame.time.Clock()

        # ── fonts ────────────────────────────────────────────────────
        self.font_sm = pygame.font.SysFont("monospace", 12)
        self.font_md = pygame.font.SysFont("monospace", 15, bold=True)
        self.font_lg = pygame.font.SysFont("monospace", 22, bold=True)

        # ── background image ─────────────────────────────────────────
        try:
            bg_raw = pygame.image.load("drone_image.jpeg").convert()
            self.background: pygame.Surface | None = pygame.transform.scale(
                bg_raw, (W, H))
        except Exception:
            self.background = None  # fallback to solid color if missing

        # ── sound ────────────────────────────────────────────────────
        try:
            self.sound: pygame.mixer.Sound | None = pygame.mixer.Sound(
                "drone_sound.mp3")
            self.sound.set_volume(0.4)
        except Exception:
            self.sound = None

        # ── graph data ───────────────────────────────────────────────
        self.graph = graph
        self.parser = parser
        self.traffic = traffic
        self.nb = traffic.nb_drones

        self.layout: dict[str, tuple[int, int]] = {}
        for zone, (x, y) in parser.zone_coords.items():
            self.layout[zone] = to_screen(x, y, parser.zone_coords)

        self.turns = traffic.run()
        self.states = self._build_states()

        # ── playback state ───────────────────────────────────────────
        self.turn = 0                  # current turn index (int)
        self.turn_f: float = 0.0      # fractional turn for smooth interpolation
        self.playing = False
        self.speed: float = 1.0       # turns per second (UP/DOWN to change)

        # ── particle trails ──────────────────────────────────────────
        # list of [x, y, vx, vy, life, color]
        self.particles: list[list] = []

    # ─────────────────────────────────────────────────────────────────
    # State building
    # ─────────────────────────────────────────────────────────────────

    def _build_states(self) -> list[dict[int, str]]:
        """Build a snapshot of drone positions after each turn."""
        state: dict[int, str] = {
            d: self.graph.start for d in range(1, self.nb + 1)
        }
        snapshots = [dict(state)]
        for turn in self.turns:
            for mv in turn:
                parts = mv.split("-")
                did = int(parts[0][1:])
                if len(parts) == 2:
                    state[did] = parts[1]
                elif len(parts) == 3:
                    state[did] = f"{parts[1]}-{parts[2]}"
            snapshots.append(dict(state))
        return snapshots

    # ─────────────────────────────────────────────────────────────────
    # Position helpers
    # ─────────────────────────────────────────────────────────────────

    def _zone_px(self, zone: str) -> tuple[int, int]:
        """Pixel position of a zone or mid-link."""
        if "-" in zone and zone not in self.layout:
            parts = zone.split("-")
            if len(parts) == 2:
                pa = self.layout.get(parts[0], (0, 0))
                pb = self.layout.get(parts[1], (0, 0))
                return ((pa[0] + pb[0]) // 2, (pa[1] + pb[1]) // 2)
        return self.layout.get(zone, (0, 0))

    def _interp_pos(self, drone_id: int, t: float) -> tuple[int, int]:
        """Smoothly interpolate drone position between turn floor and ceil."""
        idx_a = max(0, int(t))
        idx_b = min(len(self.states) - 1, idx_a + 1)
        frac = t - idx_a

        zone_a = self.states[idx_a].get(drone_id, self.graph.start)
        zone_b = self.states[idx_b].get(drone_id, self.graph.start)

        ax, ay = self._zone_px(zone_a)
        bx, by = self._zone_px(zone_b)

        # smooth-step easing: frac² * (3 - 2*frac)
        s = frac * frac * (3 - 2 * frac)
        return (int(ax + (bx - ax) * s), int(ay + (by - ay) * s))

    # ─────────────────────────────────────────────────────────────────
    # Particles
    # ─────────────────────────────────────────────────────────────────

    def _emit_particles(self, x: int, y: int,
                        color: tuple[int, int, int]) -> None:
        """Spawn a few trail particles at (x, y)."""
        import random
        for _ in range(3):
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-1.5, 1.5)
            life = random.randint(8, 18)
            self.particles.append([x, y, vx, vy, life, color])

    def _update_particles(self) -> None:
        """Move particles and remove dead ones."""
        alive = []
        for p in self.particles:
            p[0] += p[2]   # x += vx
            p[1] += p[3]   # y += vy
            p[4] -= 1      # life -= 1
            if p[4] > 0:
                alive.append(p)
        self.particles = alive

    def _draw_particles(self) -> None:
        """Draw each live particle as a fading dot."""
        for p in self.particles:
            x, y, _, _, life, color = p
            alpha = min(255, life * 14)
            r = max(1, life // 4)
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, alpha), (r, r), r)
            self.screen.blit(surf, (int(x) - r, int(y) - r))

    # ─────────────────────────────────────────────────────────────────
    # Drawing
    # ─────────────────────────────────────────────────────────────────

    def _draw_edges(self) -> None:
        """Draw connections with a subtle glow."""
        for a, b in self.parser.connection:
            pa = self.layout.get(a)
            pb = self.layout.get(b)
            if pa and pb:
                # glow: wider, darker line behind
                pygame.draw.line(self.screen, (30, 40, 70), pa, pb, 6)
                pygame.draw.line(self.screen, EDGE_COL, pa, pb, 2)

                # link capacity label at midpoint
                cap = self.graph.get_link_capacity(a, b)
                mx, my = (pa[0] + pb[0]) // 2, (pa[1] + pb[1]) // 2
                lbl = self.font_sm.render(f"×{cap}", True, (120, 130, 160))
                self.screen.blit(lbl, (mx - lbl.get_width() // 2, my - 10))

    def _draw_nodes(self) -> None:
        """Draw zones as glowing circles."""
        NODE_R = 28
        for zone, pos in self.layout.items():
            zt = self.graph.zone_type.get(zone, "normal")
            col: tuple[int, int, int] = {
                "normal":     (50, 110, 180),
                "priority":   (70, 180, 60),
                "restricted": (200, 120, 30),
                "blocked":    (50, 50, 55),
            }.get(zt, (50, 110, 180))

            if zone == self.graph.start:
                col = (28, 180, 130)
            elif zone == self.graph.end:
                col = (220, 70, 40)

            # outer glow ring
            glow_surf = pygame.Surface(
                (NODE_R * 4, NODE_R * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*col, 40),
                               (NODE_R * 2, NODE_R * 2), NODE_R * 2)
            self.screen.blit(glow_surf,
                             (pos[0] - NODE_R * 2, pos[1] - NODE_R * 2))

            # main circle + border
            pygame.draw.circle(self.screen, col, pos, NODE_R)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, NODE_R, 2)

            # zone name + capacity
            cap = self.graph.get_zone_capacity(zone)
            name_lbl = self.font_sm.render(zone[:10], True, TEXT_COL)
            cap_lbl = self.font_sm.render(f"cap:{cap}", True, (160, 170, 190))
            self.screen.blit(name_lbl,
                             (pos[0] - name_lbl.get_width() // 2,
                              pos[1] + NODE_R + 3))
            self.screen.blit(cap_lbl,
                             (pos[0] - cap_lbl.get_width() // 2,
                              pos[1] + NODE_R + 16))

    def _draw_drones(self, dt: float) -> None:
        """Draw each drone at its smoothly interpolated position."""
        DRONE_R = 10

        # group by interpolated pixel position for offset
        pos_map: dict[int, tuple[int, int]] = {}
        bucket: dict[tuple[int, int], list[int]] = {}
        for did in range(1, self.nb + 1):
            px, py = self._interp_pos(did, self.turn_f)
            pos_map[did] = (px, py)
            bucket.setdefault((px, py), []).append(did)

        for did in range(1, self.nb + 1):
            px, py = pos_map[did]
            col = DRONE_COLORS[(did - 1) % len(DRONE_COLORS)]

            # spread if multiple drones share the same pixel bucket
            group = bucket[(px, py)]
            n = len(group)
            i = group.index(did)
            if n > 1:
                angle = (i / n) * 2 * math.pi
                px += int(math.cos(angle) * 16)
                py += int(math.sin(angle) * 16)

            # emit trail particles while playing
            if self.playing:
                self._emit_particles(px, py, col)

            # draw drone: shadow + colored dot + ID
            pygame.draw.circle(self.screen, (0, 0, 0),
                               (px + 2, py + 2), DRONE_R + 2)
            pygame.draw.circle(self.screen, (0, 0, 0),
                               (px, py), DRONE_R + 2)
            pygame.draw.circle(self.screen, col, (px, py), DRONE_R)

            lbl = self.font_sm.render(str(did), True, (0, 0, 0))
            self.screen.blit(lbl,
                             (px - lbl.get_width() // 2,
                              py - lbl.get_height() // 2))

    def _draw_hud(self) -> None:
        """Draw HUD: turn, speed, controls."""
        total = len(self.turns)
        lines = [
            f"Turn : {int(self.turn_f)} / {total}",
            f"Speed: {self.speed:.1f}x  (↑↓ to change)",
            f"{'▶ Playing' if self.playing else '⏸ Paused'}",
            "",
            "Space  = play / pause",
            "→ / ←  = next / prev turn",
            "↑ / ↓  = speed up / down",
            "Q      = quit",
        ]
        # semi-transparent panel behind HUD
        panel = pygame.Surface((260, len(lines) * 22 + 16), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 140))
        self.screen.blit(panel, (6, 6))

        for i, line in enumerate(lines):
            s = self.font_md.render(line, True, TEXT_COL)
            self.screen.blit(s, (14, 14 + i * 22))

        # centered title at top
        title = self.font_lg.render("Fly-in Drone Visualizer", True,
                                    (180, 200, 255))
        self.screen.blit(title, (W // 2 - title.get_width() // 2, 10))

    # ─────────────────────────────────────────────────────────────────
    # Main loop
    # ─────────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Start the pygame event loop."""
        sound_playing = False

        while True:
            dt = self.clock.tick(60) / 1000.0   # seconds since last frame

            # ── events ──────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.playing = not self.playing
                    elif event.key == pygame.K_RIGHT:
                        self.turn_f = min(len(self.turns),
                                          math.floor(self.turn_f) + 1.0)
                    elif event.key == pygame.K_LEFT:
                        self.turn_f = max(0.0,
                                          math.ceil(self.turn_f) - 1.0)
                    elif event.key == pygame.K_UP:
                        self.speed = min(10.0, round(self.speed + 0.5, 1))
                    elif event.key == pygame.K_DOWN:
                        self.speed = max(0.25, round(self.speed - 0.25, 2))
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()

            # ── sound ────────────────────────────────────────────────
            if self.sound:
                if self.playing and not sound_playing:
                    self.sound.play(loops=-1)
                    sound_playing = True
                elif not self.playing and sound_playing:
                    self.sound.stop()
                    sound_playing = False

            # ── auto advance (smooth) ────────────────────────────────
            if self.playing:
                self.turn_f += self.speed * dt
                if self.turn_f >= len(self.turns):
                    self.turn_f = float(len(self.turns))
                    self.playing = False
                    if self.sound:
                        self.sound.stop()
                    sound_playing = False

            self.turn = int(self.turn_f)

            # ── particles ────────────────────────────────────────────
            self._update_particles()

            # ── draw ─────────────────────────────────────────────────
            if self.background:
                # dim the background so graph stays readable
                self.screen.blit(self.background, (0, 0))
                dim = pygame.Surface((W, H), pygame.SRCALPHA)
                dim.fill((0, 0, 0, 160))
                self.screen.blit(dim, (0, 0))
            else:
                self.screen.fill(BG)

            self._draw_particles()
            self._draw_edges()
            self._draw_nodes()
            self._draw_drones(dt)
            self._draw_hud()
            pygame.display.flip()


def main() -> None:
    """Entry point."""
    p = Parser()
    p.load_file()
    p.parse_file()

    g = Graph(p)
    g.build(p)

    d = Dijkstra(g)
    t = Traffic(g, d, p.nb_drones)

    v = Visualizer(g, p, t)
    v.run()


if __name__ == "__main__":
    main()
