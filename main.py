import pygame
import sys
import multiprocessing
from song_generation import extract_filename

pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()

from game_config import *
from song_library import *
from loading_screen import *
from gameplay import Gameplay

# Function to draw text on screen
def draw_text(surface, text, rect, font, color=BLACK):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

class ParallaxBg:
    """
    Une classe pour gérer l'effet de parallaxe en arrière-plan dans une application Pygame.

    Attributs:
        bg_images (list): Une liste d'images d'arrière-plan.
        bg_offsets (list): Une liste de tuples contenant les décalages pour chaque image d'arrière-plan.
        bg_speeds (list): Une liste de vitesses pour chaque image d'arrière-plan pour l'effet de parallaxe.
        easing_factor (float): Le facteur pour adoucir le mouvement de parallaxe.
        target_parallax_pos (float): La position cible pour l'effet de parallaxe.
        parallax_pos (float): La position actuelle de l'effet de parallaxe.
    """
    def __init__(self, bg_images, bg_offsets, bg_speeds) -> None:
        """
        Initialise la classe ParallaxBg avec des images d'arrière-plan, des décalages et des vitesses.

        Args:
            bg_images (list): Une liste d'images d'arrière-plan.
            bg_offsets (list): Une liste de tuples contenant les décalages pour chaque image d'arrière-plan.
            bg_speeds (list): Une liste de vitesses pour chaque image d'arrière-plan pour l'effet de parallaxe.
        """
        self.bg_images = bg_images
        self.bg_offsets = bg_offsets
        self.bg_speeds = bg_speeds
        self.easing_factor = 0.2
        self.target_parallax_pos = 1
        self.parallax_pos = 1

    #Lerp function for interpolation
    def lerp(self, start, end, easing_factor) -> float:
        """
        Effectue une interpolation linéaire entre les valeurs de début et de fin.

        Args:
            start (float): La valeur de départ.
            end (float): La valeur de fin.
            easing_factor (float): Le facteur pour adoucir l'interpolation.

        Returns:
            float: La valeur interpolée.
        """
        return start + easing_factor * (end - start)

    def draw_bg(self, parallax_pos):
        """
        Dessine les images d'arrière-plan avec l'effet de parallaxe.

        Args:
            parallax_pos (float): La position actuelle de l'effet de parallaxe.
        """
        for i, bg_image in enumerate(self.bg_images):
            screen.blit(bg_image, (((parallax_pos * self.bg_speeds[i]) - (bg_image.get_width() - screen_width) // 2) + self.bg_offsets[i][0], self.bg_offsets[i][1]))
    
    def update_parallax_pos(self):
        """
        Met à jour la position de l'effet de parallaxe et dessine les images d'arrière-plan.
        """
        self.parallax_pos = self.lerp(self.parallax_pos, self.target_parallax_pos, self.easing_factor)
        self.draw_bg(self.parallax_pos)

    def parallax(self, event=None):
        """
        Met à jour la position cible pour l'effet de parallaxe en fonction du mouvement de la souris.

        Args:
            event (pygame.event.Event, optionnel): L'événement contenant la position de la souris. Par défaut à None.
        """
        # Check if the mouse is in the window
        self.mouse_in_window = pygame.mouse.get_focused()

        if self.mouse_in_window:
            # Get the current mouse position
            if event:
                mouse_x, mouse_y = event.pos
                self.target_parallax_pos = ((mouse_x - (screen_width // 2)) / screen_width) * 100
        else:
            self.target_parallax_pos = 0

        self.update_parallax_pos()

main_menu_bg = ParallaxBg(bg_images, bg_offset, bg_speeds)

# Process flag
editor_process = None

def reset_editor_process():
    global editor_process
    editor_process = None

def select_file_for_editor_process(song_list):
    select_file_for_editor(song_list)
    reset_editor_process()

def main():
    global editor_process

    mp3_files = load_song_list()
    menu = {'selectsong_button_text': selectsong_button_text}

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                main_menu_bg.parallax(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if button_box.collidepoint(mouse_pos):
                    song_path = menu['selectsong_button_text']
                    if song_path != 'Select Song':

                        chart_path = f'charts/{extract_filename(song_path)}.txt'
                        if not os.path.exists(chart_path):
                            run_loading_screen(song_path)
                        else:
                            Gameplay(song_path)
                elif dropdown_button_box.collidepoint(mouse_pos):
                    # Start the select file for editor function in a separate process
                    if editor_process is None or not editor_process.is_alive():
                        editor_process = multiprocessing.Process(target=select_file_for_editor_process, args=(mp3_files,))
                        editor_process.start()
                elif selectsong_button_box.collidepoint(mouse_pos):
                    music_library = MusicLibrary()
                    selected_file = music_library.music_chosen
                    if selected_file:
                        menu['selectsong_button_text'] = selected_file
        
        main_menu_bg.parallax()

        title_text = title_font.render("SolarSound", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(screen_width // 2, title_y))
        screen.blit(title_text, title_rect)

        pygame.draw.rect(screen, BUTTON_COLOR, button_box)
        draw_text(screen, button_text, button_box, font, TEXT_COLOR)

        pygame.draw.rect(screen, GRAY, dropdown_button_box)
        draw_text(screen, dropdown_button_text, dropdown_button_box, font, TEXT_COLOR)

        pygame.draw.rect(screen, GRAY, selectsong_button_box)
        draw_text(screen, menu['selectsong_button_text'], selectsong_button_box, font, TEXT_COLOR)

        pygame.display.update()

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')  # Required for Windows
    main()
