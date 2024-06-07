import pygame
import sys
import json
import os
import tkinter as tk
from tkinter import filedialog

from config import *

song_list_file_name = 'config.json'

def save_song_list(song_list):
    existing_songs = load_song_list()
    combined_songs = list(set(existing_songs + song_list))
    with open(song_list_file_name, 'w') as config_file:
        json.dump(combined_songs, config_file)

def load_song_list():
    if os.path.exists(song_list_file_name):
        with open(song_list_file_name, 'r') as song_list_file:
            return json.load(song_list_file)
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

class MusicLibrary:
    def __init__(self) -> None:
        self.music_chosen = self.run()

    def run(self):
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
                        selected_file = "Select a music file"

            screen.fill(BG_COLOR)
            draw_text(screen, "Select a music file", pygame.Rect(0, 50, screen_width, 50), font, WHITE)
            y_offset = 150
            return_button = pygame.Rect(50, 50, 200, 50)
            draw_text(screen, "return", return_button, font, TEXT_COLOR)
            for idx, file in enumerate(file_list):
                file_rect = pygame.Rect(50, y_offset + idx * 50, screen_width - 100, 50)
                pygame.draw.rect(screen, GRAY, file_rect)
                draw_text(screen, file, file_rect, font, BLACK)
                file_rects.append((file_rect, file))

            pygame.display.flip()
        return selected_file
