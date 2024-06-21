import pygame
import sys
import json
import os
import tkinter as tk
from tkinter import filedialog
from game_config import *
from main import draw_text
from song_generation import extract_filename

song_list_file_name = 'config.json'
best_score_file_name = 'best_scores.json'

def save_song_list(song):
    """
    Enregistre la liste des chansons dans un fichier JSON.

    Args:
        song_list (list): La liste des chansons à enregistrer.
    """
    existing_songs = load_song_list()
    existing_songs.append([song, 0])
    # Check if the combined list length exceeds 8
    if len(existing_songs) > 7:
        # If the length exceeds 8, pop the first item
        existing_songs.pop(0)
    with open(song_list_file_name, 'w') as config_file:
        json.dump(existing_songs, config_file)

def load_song_list():
    """
    Charge la liste des chansons à partir d'un fichier JSON.

    Returns:
        list: La liste des chansons chargées.
    """
    if os.path.exists(song_list_file_name):
        with open(song_list_file_name, 'r') as song_list_file:
            song_list = json.load(song_list_file)
            best_scores = load_best_scores()
            combined_list = []
            for song, score in song_list:
                best_score = best_scores.get(song, 0)  # 0 if no best score found
                combined_list.append((song, best_score))
            return combined_list
    return []

def load_best_scores():
    """
    Charge les meilleurs scores à partir d'un fichier JSON.

    Returns:
        dict: Un dictionnaire contenant les meilleurs scores pour chaque chanson.
    """
    if os.path.exists(best_score_file_name):
        with open(best_score_file_name, 'r') as best_score_file:
            return json.load(best_score_file)
    return {}

def select_file_for_editor(song_list):
    """
    Ouvre une boîte de dialogue pour sélectionner un fichier MP3 et l'ajoute à la liste des chansons.

    Args:
        song_list (list): La liste des chansons existantes.

    Returns:
        str: Le chemin du fichier sélectionné, ou None si aucun fichier n'a été sélectionné.
    """
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
    if file_path and file_path not in song_list:
        #song_list.append(file_path)
        save_song_list(file_path)
        #return file_path
    #return None

class MusicLibrary():
    """
    Une classe pour gérer la sélection de musique dans la bibliothèque musicale.

    Attributs:
        music_chosen (str): Le fichier de musique sélectionné.
    """
    def __init__(self) -> None:
        """
        Initialise la classe MusicLibrary et lance la sélection de musique.
        """
        self.music_chosen = self.run()
       
    def blur_surface(surface, amount):
        """
        Floute une surface donnée en réduisant et en agrandissant l'image.

        Paramètres :
        surface (pygame.Surface) : La surface à flouter.
        amount (float) : La quantité de flou à appliquer. Plus la valeur est grande, moins l'image sera floutée.

        Retourne :
        pygame.Surface : La surface floutée.
        """
        scale = 1.0 / amount
        surf_size = surface.get_size()
        scaled_surf = pygame.transform.smoothscale(surface, (int(surf_size[0] * scale), int(surf_size[1] * scale)))
        return pygame.transform.smoothscale(scaled_surf, surf_size)

    def darken_surface(surface, darkness):
        """
        Assombrit une surface donnée en appliquant une superposition noire avec une certaine transparence.
    
        Paramètres :
        surface (pygame.Surface) : La surface à assombrir.
        darkness (int) : Le niveau d'assombrissement (opacité de la superposition noire), allant de 0 (transparent) à 255 (opaque).
    
        Retourne :
        None
        """
        dark_overlay = pygame.Surface(surface.get_size())
        dark_overlay.fill((0, 0, 0))
        dark_overlay.set_alpha(darkness)
        surface.blit(dark_overlay, (0, 0))

    def run(self):
        """
        Exécute l'interface de sélection de musique et retourne le fichier sélectionné.

        Returns:
            str: Le fichier de musique sélectionné.
        """
        file_list = load_song_list()
        file_rects = []
        selected_file = None
        while not selected_file:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for file_rect, file in file_rects:
                        if file_rect.collidepoint(event.pos):
                            selected_file = file
                            break
                    if return_button.collidepoint(event.pos):
                        selected_file = selectsong_button_text

            background = pygame.image.load("assets/background.jpg")
            background = pygame.transform.scale(background, (800, 600))
            blurred_background = MusicLibrary.blur_surface(background, 10)  # Adjust the blur amount
            MusicLibrary.darken_surface(blurred_background, 150)
            screen.blit(blurred_background, (0, 0))
            draw_text(screen, selectsong_button_text, pygame.Rect(0, 50, screen_width, 50), font, WHITE)
            y_offset = 150
            return_button = pygame.Rect(50, 50, 200, 50)
            draw_text(screen, "Retourne", return_button, font, TEXT_COLOR)
            for idx, (file, best_score) in enumerate(file_list):
                file_rect = pygame.Rect(50, y_offset + idx * 50, screen_width - 100, 50)
                pygame.draw.rect(screen, GRAY, file_rect)
                draw_text(screen, f"{extract_filename(file)} - Best Score: {best_score}", file_rect, font, BLACK)
                file_rects.append((file_rect, file))

            pygame.display.flip()
        return selected_file
