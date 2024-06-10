import pygame
from game_config import *

class TutorialWindow:
    def __init__(self):

        # Define button properties
        self.button_color = (210, 180, 250)
        self.button_text_color = (0, 0, 0)
        self.button_font = pygame.font.Font(None, 20)

        # Button rectangles
        self.next_button_rect = pygame.Rect(screen_width - 140, screen_height - 60, 120, 40)
        self.previous_button_rect = pygame.Rect(20, screen_height - 60, 120, 40)
        self.ready_button_rect = pygame.Rect(screen_width - 140, screen_height - 60, 120, 40)

        # Tutorial state
        self.tutorial_state = 1
        self.run()

    def draw_button(self, rect, text):
        pygame.draw.rect(screen, self.button_color, rect)
        text_surface = self.button_font.render(text, True, self.button_text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if self.tutorial_state == 1 and self.next_button_rect.collidepoint(mouse_pos):
                        self.tutorial_state = 2
                    elif self.tutorial_state == 2:
                        if self.previous_button_rect.collidepoint(mouse_pos):
                            self.tutorial_state = 1
                        elif self.ready_button_rect.collidepoint(mouse_pos):
                            running = False

            # Draw the current tutorial image
            if self.tutorial_state == 1:
                screen.blit(tutorial1, (0, 0))
                self.draw_button(self.next_button_rect, 'Suivant')
            else:
                screen.blit(tutorial2, (0, 0))
                self.draw_button(self.previous_button_rect, 'Précédent')
                self.draw_button(self.ready_button_rect, 'Prêt à jouer')

            pygame.display.flip()
