import pygame
import time


class Visualizer:
    def __init__(self, graph, turns):
        pygame.init()

        self.graph = graph
        self.turns = turns

        self.width = 1400
        self.height = 900

        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )

        pygame.display.set_caption("FLY-IN Visualizer")

        self.drone_pos = {}

        self.scale = 50
        self.offset_x = 150
        self.offset_y = 450

    def world_to_screen(self, zone):
        x, y = self.graph.zone_positions[zone]

        return (
            self.offset_x + x * self.scale,
            self.offset_y - y * self.scale
        )

    def draw_graph(self):
        self.screen.fill((20, 20, 20))

        # connections
        drawn = set()

        for zone, neighbors in self.graph.neighbors.items():
            x1, y1 = self.world_to_screen(zone)

            for nxt in neighbors:
                edge = tuple(sorted([zone, nxt]))

                if edge in drawn:
                    continue

                drawn.add(edge)

                x2, y2 = self.world_to_screen(nxt)

                pygame.draw.line(
                    self.screen,
                    (120, 120, 120),
                    (x1, y1),
                    (x2, y2),
                    2
                )

        # zones
        for zone in self.graph.zone_positions:
            x, y = self.world_to_screen(zone)

            pygame.draw.circle(
                self.screen,
                (50, 150, 255),
                (x, y),
                12
            )

    def draw_drones(self):
        for drone, zone in self.drone_pos.items():
            x, y = self.world_to_screen(zone)

            pygame.draw.circle(
                self.screen,
                (255, 80, 80),
                (x, y),
                6
            )

    def initialize_drones(self):
        start = self.graph.start

        for turn in self.turns:
            for move in turn:
                drone = move.split("-")[0]

                if drone not in self.drone_pos:
                    self.drone_pos[drone] = start

    def run(self):
        self.initialize_drones()

        running = True

        for turn_index, turn in enumerate(self.turns):

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if not running:
                break

            for move in turn:
                drone, zone = move.split("-")
                self.drone_pos[drone] = zone

            self.draw_graph()
            self.draw_drones()

            pygame.display.flip()

            print(
                f"Turn {turn_index + 1}/{len(self.turns)}"
            )

            time.sleep(0.3)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.quit()