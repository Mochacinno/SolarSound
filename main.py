import pygame
import sys

pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()

from game_config import *
from song_library import *
from loading_screen import run_loading_screen
from gameplay import Gameplay

# Function to draw text on screen
def draw_text(surface, text, rect, font, color=BLACK):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

#Lerp function for interpolation
def lerp(start, end, t):
    return start + t * (end - start)

def main():
    mp3_files = load_song_list()
    menu = {'selectsong_button_text': selectsong_button_text}
    
    mouse_in_window = True
    parallax_pos = 1
    target_parallax_pos = 1
    easing = 0.2

    def draw_bg():
        for i, bg_image in enumerate(bg_images):
            screen.blit(bg_image, (((parallax_pos * bg_speeds[i]) - (bg_image.get_width() - screen_width) // 2) + bg_offset[i][0], bg_offset[i][1]))

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                # Check if the mouse is in the window
                mouse_in_window = pygame.mouse.get_focused()
                 # Get the current mouse position
                mouse_x, mouse_y = event.pos
                
                target_parallax_pos = ((mouse_x - (screen_width // 2)) / screen_width) * 100

                # # Determine the direction of the mouse movement
                # if mouse_x > previous_mouse_x:
                #     parallax_pos += 5
                # elif mouse_x < previous_mouse_x:
                #     parallax_pos -= 5
                # Update the previous mouse position
                # previous_mouse_x = mouse_x

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
        if not mouse_in_window:
            target_parallax_pos = 0

        # interpolate for smooth parallax
        parallax_pos = lerp(parallax_pos, target_parallax_pos, easing)

        #screen.blit(background_image, (0, 0))
        draw_bg()

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
    main()
