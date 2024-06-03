import pygame
import sys
import os
from pygame import mixer
from utils import bpm_for_time
import tkinter as tk
from tkinter import filedialog


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
font = pygame.font.Font(None, 36)

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
dropdown_button_text = "Editer la liste des fichiers MP3"

# Bouton du menu déroulant de sélection
selectsong_button_box = pygame.Rect(selectsong_button_x, selectsong_button_y, dropdown_button_width, dropdown_button_height)
selectsong_button_text = "Selectionner la musique"

# Liste des fichiers MP3 précédemment utilisés
mp3_files = []
selected_file = None

def draw_text(surface, text, rect, font, color=BLACK):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = rect.center

    if text_rect.width > rect.width:
        # Tronquer le texte si nécessaire
        while text_rect.width > rect.width and len(text) > 0:
            text = text[:-1]
            text_surface = font.render(text + "...", True, color)
            text_rect = text_surface.get_rect()
            text_rect.center = rect.center

    surface.blit(text_surface, text_rect.topleft)

# CLASSES
class Note():
    def __init__(self, key_index):
        self.key_index = key_index
        self.x = keys[key_index].rect.centerx - 45
        self.y = 0
        self.rect = pygame.Rect(self.x, self.y, 90, 20)
        self.surface = pygame.Surface((90, 20), pygame.SRCALPHA)
        self.surface.fill((255, 0 , 0))
        self.alpha = 255  # Initial alpha value
        self.dissolving = False
    
    def update(self, speed):
        self.y += speed
        self.rect.y = self.y

    def dissolve(self):
        if self.alpha > 0:
            self.alpha -= 20  # Adjust the decrement to control dissolve speed
            if self.alpha < 0:
                self.alpha = 0
            self.surface.set_alpha(self.alpha)

    def draw(self, screen):
        screen.blit(self.surface, self.rect.topleft)

class Key():
    def __init__(self,x,y,coloridle,coloractive,key):
        self.x = x
        self.y = y
        self.coloridle = coloridle
        self.coloractive = coloractive
        self.key = key
        self.rect = pygame.Rect(self.x,self.y,90,40)
        self.handled = False

# initialising keys
keys = [
    Key(100,500,(255,0,0),(220,0,0),pygame.K_z),
    Key(200,500,(0,255,0),(0,220,0),pygame.K_x),
    Key(300,500,(0,0,255),(0,0,220),pygame.K_m),
    Key(400,500,(255,255,0),(220,220,0),pygame.K_COMMA),
]

clock = pygame.time.Clock()

def load(map):
    mixer.music.load(map+".mp3")

    with open(map+'.txt', 'r') as file:
        lines = file.readlines()
    
    start_time = None
    bpms = []
    beatmap = []
    beats_in_measure = []

    # Parse START_TIME
    index = 0
    while index < len(lines) and lines[index].strip() != "START_TIME:":
        index += 1
    index += 1  # Move to the value line
    if index < len(lines):
        start_time = int(lines[index].strip())
    
    # Parse BPMS
    index += 1  # Move past START_TIME value line
    while index < len(lines) and lines[index].strip() != "BPMS:":
        index += 1
    index += 1  # Move to the first BPM line
    while index < len(lines) and lines[index].strip() and lines[index].strip() != "NOTES:":
        line = lines[index].strip().rstrip(',')
        time, bpm = line.split(':')
        bpms.append([int(bpm), int(time)])
        index += 1
    
    # Parse NOTES
    index += 1  # Move to the first note line
    while index < len(lines):
        line = lines[index].strip().rstrip(',')
        note_info = list(map(int, line.split(':')))
        beatmap.append(note_info)
        index += 1
    
    return start_time, bpms, beatmap

class Gameplay():
    def __init__(self, selectsong_button_text):
        self.map = selectsong_button_text[:-4]
        self.start_time, self.bpms, self.beatmap = load(self.map)
        self.note_speed = 1
        self.BPM = 0
        self.notes = []
        self.note_index = 0
        self.run()
        
    def run(self):
        running = True
        while running:
            mixer.music.play()
            while mixer.music.get_pos() < self.start_time:
                pass

            while True:
                screen.blit(background_image, (0, 0))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            break
                        for key in keys:
                            if event.key == key.key:
                                key.handled = True

                current_time = mixer.music.get_pos()
                while self.note_index < len(self.beatmap) and current_time >= self.beatmap[self.note_index][1]:
                    note_info = self.beatmap[self.note_index]
                    note = Note(note_info[0])
                    self.notes.append(note)
                    self.note_index += 1
                
                for note in self.notes:
                    note.update(self.note_speed)
                    note.draw(screen)

                    if note.dissolving:
                        note.dissolve()
                    if note.y >= screen_height:
                        note.dissolving = True
                
                for key in keys:
                    if key.handled:
                        for note in self.notes:
                            if note.key_index == keys.index(key) and key.rect.colliderect(note.rect):
                                note.dissolving = True
                                key.handled = False
                    pygame.draw.rect(screen, key.coloractive if key.handled else key.coloridle, key.rect)

                pygame.display.update()
                clock.tick(60)
                
                if not running:
                    break

def select_file_for_editor():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers MP3", "*.mp3")])
    print(file_path)
    root.destroy()
    return file_path



def select_music_file():
    file_list = [f for f in os.listdir('.') if f.endswith('.mp3')]
    selected_file = None
    while not selected_file:
        screen.fill(BG_COLOR)
        draw_text(screen, "Select a music file", pygame.Rect(0, 50, screen_width, 50), font, WHITE)
        y_offset = 150
        for idx, file in enumerate(file_list):
            file_rect = pygame.Rect(50, y_offset + idx * 40, screen_width - 100, 30)
            pygame.draw.rect(screen, GRAY, file_rect)
            draw_text(screen, file, file_rect, font, BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if file_rect.collidepoint(event.pos):
                        selected_file = file
        pygame.display.flip()
    return selected_file

# Main game loop
menu = {
    'selectsong_button_text': selectsong_button_text
}

while True:
    screen.blit(background_image, (0, 0))

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
                selected_file = select_file_for_editor()
                if selected_file and selected_file not in mp3_files:
                    mp3_files.append(selected_file)
            elif selectsong_button_box.collidepoint(mouse_pos):
                selected_file = select_music_file()
                if selected_file:
                    menu['selectsong_button_text'] = selected_file

    # Afficher le titre et les boutons
    title_text = title_font.render("Jeu de rythme", True, TEXT_COLOR)
    title_rect = title_text.get_rect(center=(screen_width // 2, title_y))
    screen.blit(title_text, title_rect)

    pygame.draw.rect(screen, BUTTON_COLOR, button_box)
    draw_text(screen, button_text, button_box, font, TEXT_COLOR)

    pygame.draw.rect(screen, GRAY, dropdown_button_box)
    draw_text(screen, dropdown_button_text, dropdown_button_box, font, TEXT_COLOR)
    
    pygame.draw.rect(screen, GRAY, selectsong_button_box)
    draw_text(screen, menu['selectsong_button_text'], selectsong_button_box, font, TEXT_COLOR)

    pygame.display.update()
