import pygame

W, H = 1440, 880


class Visualizer:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Fly-in - Drone Routing Visualizer")
        self.screen = pygame.display.set_mode((W, H))

        self.background = pygame.image.load("drone_image.jpeg").convert()
        self.background = pygame.transform.scale(self.background, (W, H))
        # self.small = pygame.transform.smoothscale(self.background, (W // 3, H // 3))
        # self.background = pygame.transform.smoothscale(self.small, (W, H))
        self.sound_1 = pygame.mixer.Sound('drone_sound.mp3')
        self.run()

    def run(self):
        running = True
        clock = pygame.time.Clock()

        dt = 0
        player_pos = pygame.Vector2(
            self.screen.get_width() / 2, self.screen.get_height() / 2)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # ! Draw background
            self.sound_1.play()
            self.screen.blit(self.background, (0, 0))

            # ! Draw objects

            pygame.draw.circle(self.screen, (0, 0, 255), player_pos, 75)
            keys = pygame.key.get_pressed()

            if keys[pygame.K_UP]:
                player_pos.y -= 300 * dt
            if keys[pygame.K_DOWN]:
                player_pos.y += 300 * dt
            if keys[pygame.K_RIGHT]:
                player_pos.x += 300 * dt
            if keys[pygame.K_LEFT]:
                player_pos.x -= 300 * dt

            # ! Use the mouse

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # ? Move the cyrcle
                player_pos.x = pos[0]
                player_pos.y = pos[1]
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                player_pos.x = pos[0]
                player_pos.y = pos[1]
               
            # ! MOTION
            
            
                
            # ! flip the display to output our work on the screen
            pygame.display.flip()
            dt = clock.tick(60) / 1000

        pygame.quit()


Visualizer()
