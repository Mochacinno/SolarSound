import pygame
import sys

pygame.init()
pygame.mixer.init()

from game_config import *
from song_library import *
from loading_screen import run_loading_screen
from gameplay import Gameplay

# Function to draw text on screen
def draw_text(surface, text, rect, font, color=BLACK):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def main():
    mp3_files = load_song_list()
    menu = {'selectsong_button_text': selectsong_button_text}

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if button_box.collidepoint(mouse_pos):
                    if menu['selectsong_button_text'] != 'Select Song':
                        #run_loading_screen()
                        Gameplay()
                elif dropdown_button_box.collidepoint(mouse_pos):
                    selected_file = select_file_for_editor(mp3_files)
                    if selected_file and selected_file not in mp3_files:
                        mp3_files.append(selected_file)
                elif selectsong_button_box.collidepoint(mouse_pos):
                    music_library = MusicLibrary()
                    selected_file = music_library.music_chosen
                    if selected_file:
                        menu['selectsong_button_text'] = selected_file

        screen.blit(background_image, (0, 0))

        title_text = title_font.render("SolarSound", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(screen_width // 2, title_y))
        screen.blit(title_text, title_rect)

        pygame.draw.rect(screen, BUTTON_COLOR, button_box)
        draw_text(screen, button_text, button_box, font, TEXT_COLOR)

        pygame.draw.rect(screen, GRAY, dropdown_button_box)
        draw_text(screen, dropdown_button_text, dropdown_button_box, font, TEXT_COLOR)

        pygame.draw.rect(screen, GRAY, selectsong_button_box)
        draw_text(screen, menu['selectsong_button_text'], selectsong_button_box, font, TEXT_COLOR)

        pygame.display.flip()

if __name__ == "__main__":
    main()
