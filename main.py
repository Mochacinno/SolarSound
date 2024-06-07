import pygame
import sys
from pygame import mixer
import tkinter as tk
from tkinter import filedialog
import json
import os

from game_config import *
from song_library import MusicLibrary, select_file_for_editor, load_song_list
from loading_screen import run_loading_screen
from gameplay import Gameplay

pygame.init()
mixer.init()

# Function to draw text on screen
def draw_text(surface, text, rect, font, color=BLACK):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

class Gameplay():
    def __init__(self):
        #self.map = selectsong_button_text[:-4]
        self.beatmap = load("Music+Beatmaps/sink")
        self.note_speed = 1
        self.BPM = 0
        self.notes = []
        self.note_index = 0
        self.run()
        
    def run(self):
        # Initialize a dictionary to store key press times
        key_press_times = {key.key: [] for key in keys}
        # Reset game variables
        start_time = pygame.time.get_ticks()
        current_time = start_time
        score = 0
        music_started = False
        clock = pygame.time.Clock()
        speed = 500

        running = True
        while running:
            screen.fill((255, 255, 255))

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in key_press_times:
                        key_press_times[event.key].append(current_time - start_time - 1000)
                        print(f"Key {event.key} pressed at {current_time - start_time - 1000}")

            # Update the current time
            dt = clock.tick(60)  # Get the time passed since the last frame in milliseconds
            current_time += dt  # Update current time

            # Check if the music hasn't started yet and the elapsed time is greater than or equal to 1000 milliseconds (1 second)
            if not music_started and current_time - start_time >= 1000 + 69 - 175:
                # Start playing the music
                pygame.mixer.music.play()
                music_started = True

            # Check key presses
            k = pygame.key.get_pressed()
            for key in keys:
                if k[key.key]:
                    pygame.draw.rect(screen, key.coloridle, key.rect)
                    key.handled = False
                else:
                    pygame.draw.rect(screen, key.coloractive, key.rect)
                    key.handled = True

            # Spawn and move notes
            for note, time_frame in self.beatmap[:]:
                if current_time - start_time >= time_frame:
                    if not note.dissolving:
                        note.update((speed / 1000) * dt)  # Move the note down
                    else:
                        note.dissolve()
                        if note.alpha == 0:
                            self.beatmap.remove((note, time_frame))
    
                    note.draw(screen)
    
                # Check if the note should be hit based on the key press times
                if not note.dissolving:
                    for key in keys:
                        if note.key_index == keys.index(key):
                            texte_score_time = 0
                            for press_time in key_press_times[key.key]:
                                if abs(press_time - time_frame) < 30:  # SCORING SYSTEM
                                    note.dissolving = True  # Start the dissolve effect
                                    key_press_times[key.key].remove(press_time)  # Remove the handled key press time
                                    score += 2  # Increment the score when a note is hit
                                    texte_score_time = current_time
                                    #print(f'1 {texte_score_time}')

                                    # Créer une surface contenant le texte
                                    texte = "Perfect"
                                    image_texte = font2.render(texte, True, GRAY)

                                    # Obtenir le rectangle de l'image du texte pour le positionnement
                                    rect_texte = image_texte.get_rect()

                                    # Centrer le texte au milieu de la fenêtre
                                    rect_texte.center = (400, 300)
                                    screen.blit(image_texte, rect_texte) 

                                    '''if abs(texte_score_time-current_time)>1000:
                                        print(f'2 {texte_score_time-current_time}')
                                        print(current_time)

                                        screen.blit(" ", rect_texte) 
                                    '''

                                elif abs(press_time - time_frame) < 50:  # SCORING SYSTEM
                                    note.dissolving = True  # Start the dissolve effect
                                    key_press_times[key.key].remove(press_time)  # Remove the handled key press time
                                    score += 1  # Increment the score when a note is hit
                                    texte_score_time = current_time
                                    #print(f'1 {texte_score_time}')
                                    # Créer une surface contenant le texte
                                    texte = "Good"
                                    image_texte = font2.render(texte, True, GRAY)

                                    # Obtenir le rectangle de l'image du texte pour le positionnement
                                    rect_texte = image_texte.get_rect()

                                    # Centrer le texte au milieu de la fenêtre
                                    rect_texte.center = (400, 300)
                                    screen.blit(image_texte, rect_texte) 

                                    '''if abs(texte_score_time-current_time)>1000:
                                        print(f'2 {texte_score_time-current_time}')
                                        print(current_time)

                                        screen.blit(" ", rect_texte)    
                                    '''

            # Display the score on the screen
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))
    
            # Update the display
            pygame.display.update()
                
            if not running:
                break


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
                        run_loading_screen()
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

        pygame.display.update()

if __name__ == "__main__":
    main()
