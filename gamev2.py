import pygame
import sys
import os
from pygame import mixer
from utils import bpm_for_time
import tkinter as tk
from tkinter import filedialog
import json


# Initialisation de Pygame
pygame.init()
mixer.init()

# Dimensions de la fenêtre
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Menu de démarrage - Jeu de rythme")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BUTTON_COLOR = (100, 200, 100)
TEXT_COLOR = (255, 255, 255)
BG_COLOR = (30, 30, 30)

# Police d'écriture
title_font = pygame.font.Font(None, 100)
font = pygame.font.Font(None, 20)

# Charger l'image de fond
background_image = pygame.image.load("assets/background.jpg")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# Dimensions des éléments
button_width = 220
button_height = 40
dropdown_button_width = 400
dropdown_button_height = 40
selectsong_button_width = 400
selectsong_button_height = 40

# Calcul des positions centrées
title_y = 20
button_x = (screen_width - button_width) // 2
button_y = 350
selectsong_button_x = (screen_width - dropdown_button_width) // 2
selectsong_button_y = 270
dropdown_button_x = (screen_width - dropdown_button_width) // 2
dropdown_button_y = 430

# Bouton de validation
button_box = pygame.Rect(button_x, button_y, button_width, button_height)
button_text = "Valider et jouer"

# Bouton du menu déroulant d'édition
dropdown_button_box = pygame.Rect(dropdown_button_x, dropdown_button_y, dropdown_button_width, dropdown_button_height)
dropdown_button_text = "Ajouter une musique au Jeu"

# Bouton du menu déroulant de sélection
selectsong_button_box = pygame.Rect(selectsong_button_x, selectsong_button_y, dropdown_button_width, dropdown_button_height)
selectsong_button_text = "Bibliothèque de musique"

# Initial list of MP3 files
mp3_files = []

# Function to draw text on screen
def draw_text(surface, text, rect, font, color=BLACK):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

# Class for managing the music library
class MusicLibrary:
    def __init__(self) -> None:
        self.music_chosen = self.run()

    def run(self):
        file_list = load_song_list()
        selected_file = None
        while not selected_file:
            screen.fill(BG_COLOR)
            draw_text(screen, "Select a music file", pygame.Rect(0, 50, screen_width, 50), font, WHITE)
            y_offset = 150
            for idx, file in enumerate(file_list):
                file_rect = pygame.Rect(50, y_offset + idx * 50, screen_width - 100, 50)
                pygame.draw.rect(screen, GRAY, file_rect)
                draw_text(screen, file, file_rect, font, BLACK)
                
                # Event handling inside the main loop
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if file_rect.collidepoint(event.pos):
                            selected_file = file

            pygame.display.flip()
        return selected_file


class Gameplay():
    def __init__(self):
        #self.map = selectsong_button_text[:-4]
        self.beatmap = load("Music+Beatmaps/nhelv")
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
            screen.fill((0, 0, 0))

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in key_press_times:
                        key_press_times[event.key].append(current_time - start_time - 1000)

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
                if not k[key.key]:
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
                            for press_time in key_press_times[key.key]:
                                if abs(press_time - time_frame) < 60:  # SCORING SYSTEM
                                    note.dissolving = True  # Start the dissolve effect
                                    key_press_times[key.key].remove(press_time)  # Remove the handled key press time
                                    score += 1  # Increment the score when a note is hit
                                    break

            # Display the score on the screen
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            # Update the display
            pygame.display.update()
                
            if not running:
                break

CONFIG_FILE = 'config.json'

def save_song_list(song_list):
    with open(CONFIG_FILE, 'w') as config_file:
        json.dump(song_list, config_file)

def load_song_list():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config_file:
            return json.load(config_file)
    return []

def select_file_for_editor(song_list):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
    if file_path and file_path not in song_list:
        song_list.append(file_path)
        save_song_list(song_list)
        return file_path
    return None

# Main game loop
menu = {
    'selectsong_button_text': selectsong_button_text
}

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if button_box.collidepoint(mouse_pos):
                if menu['selectsong_button_text'] != selectsong_button_text:
                    Gameplay(menu['selectsong_button_text'])
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

    # Display title and buttons
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