import pygame
import sys
import tkinter as tk
from tkinter import filedialog, Listbox, Button, Scrollbar, Label
from pygame import mixer
from utils import bpm_for_time

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
PURPLE = (70, 50, 200)
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

# Créer l'interface Tkinter pour le menu déroulant
root = tk.Tk()
root.withdraw()  # Masquer la fenêtre principale Tkinter

class Editeur:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(root)
        self.window.title("Editer les fichiers MP3")

        self.label = Label(self.window, text="Liste des fichiers MP3")
        self.label.pack()

        self.listbox = Listbox(self.window, selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=1)

        self.scrollbar = Scrollbar(self.window, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.add_button = Button(self.window, text="Ajouter un fichier", command=self.add_file)
        self.add_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.remove_button = Button(self.window, text="Supprimer le fichier", command=self.remove_file)
        self.remove_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.select_button = Button(self.window, text="Valider et retourner", command=self.validate_and_return)
        self.select_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.update_listbox()

    def add_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers MP3", "*.mp3")])
        if file_path:
            if file_path not in mp3_files:
                mp3_files.append(file_path)
                self.update_listbox()

    def remove_file(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            mp3_files.pop(selected_index[0])
            self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for file in mp3_files:
            self.listbox.insert(tk.END, file)

    def validate_and_return(self):
        self.parent['selectsong_button_text'] = "Selectionner la musique"
        self.window.destroy()

class Selecteur:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(root)
        self.window.title("Sélectionner un fichier MP3")

        self.label = Label(self.window, text="Liste des fichiers MP3")
        self.label.pack()

        self.listbox = Listbox(self.window, selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=1)

        self.scrollbar = Scrollbar(self.window, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.select_button = Button(self.window, text="Sélectionner le fichier", command=self.select_file)
        self.select_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Afficher les fichiers dans le menu déroulant
        for file in mp3_files:
            self.listbox.insert(tk.END, file)

    def select_file(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            self.parent['selectsong_button_text'] = mp3_files[selected_index[0]]
            self.window.destroy()

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
    index += 1  # Move past the BPMS section header
    while index < len(lines):
        stripped_line = lines[index].strip()
        if stripped_line:
            if "," in stripped_line:
                if beats_in_measure:
                    beatmap.append(beats_in_measure)
                    beats_in_measure = []
            else:
                beat = [int(block) for block in stripped_line]
                beats_in_measure.append(beat)
        index += 1
    
    if beats_in_measure:
        beatmap.append(beats_in_measure)
    
    #print(start_time)
    #print(bpms)
    #print(beatmap)
    #print(len(beatmap))
    bpm = bpm_for_time(bpms, start_time)
    measure_time = int(240000 / bpm)
    #print(f"measure_time: {measure_time}")
    current_time = start_time

    res = []
    for beats_per_mesure in beatmap:
        #print(f"measure_time: {measure_time}")
        for i in range(len(beats_per_mesure)):
            # Calculate the time for the current beat by adding the time for the previous beat
            beats_per_mesure[i] = (beats_per_mesure[i], (current_time + ((measure_time // (len(beats_per_mesure))) * (i))))
            # Update the previous time for the next iteration
        current_time += measure_time
        #print(current_time)
        bpm = bpm_for_time(bpms, current_time)
        #print(f"for bpm: {bpm}")
        measure_time = int(240000 / bpm)
        res.append(beats_per_mesure)

    # print(res)
    # [[([1, 0, 0, 0], 250.0), ([0, 0, 0, 0], 500.0), ([0, 0, 0, 0], 750.0), ([0, 0, 0, 0], 1000.0)], [([0, 1, 0, 0], 1333.3333333333333), ([0, 0, 0, 1], 1666.6666666666665), ([1, 0, 0, 0], 1999.9999999999998)], [([0, 0, 0, 0], 2250.0), ([1, 0, 0, 0], 2500.0), ([0, 0, 0, 0], 2750.0), ([0, 0, 0, 0], 3000.0)]]
    notes = []
    for beats in res:
        for beat, time in beats:
            for key_index in range(len(beat)):
                if beat[key_index] == 1:
                    #notes.append((pygame.Rect(keys[key_index].rect.centerx - 25,0,50,25), time))
                    notes.append((Note(key_index), time))
    
    return notes

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
                print("yes")
                Gameplay()
            elif dropdown_button_box.collidepoint(mouse_pos):
                Editeur(menu)
            elif selectsong_button_box.collidepoint(mouse_pos):
                Selecteur(menu)

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
