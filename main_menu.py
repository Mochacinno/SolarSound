import pygame
import sys
import tkinter as tk
from tkinter import filedialog, Listbox, Button, Scrollbar, Label

# Initialisation de Pygame
pygame.init()

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

# Police d'écriture
title_font = pygame.font.Font(None, 100)
font = pygame.font.Font(None, 30)

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
selectsong_button_box = pygame.Rect(selectsong_button_x, selectsong_button_y, selectsong_button_width, selectsong_button_height)
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

def main():
    global selectsong_button_text, dropdown_button_text

    # Initial state
    state = {
        'selectsong_button_text': selectsong_button_text,
        'dropdown_button_text': dropdown_button_text
    }

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_box.collidepoint(event.pos):
                    print("Fichier MP3 sélectionné:", state['selectsong_button_text'])
                if dropdown_button_box.collidepoint(event.pos):
                    # Ouvrir le menu déroulant Tkinter (éditeur)
                    file_editor = Editeur(state)
                    root.wait_window(file_editor.window)
                if selectsong_button_box.collidepoint(event.pos):
                    # Ouvrir le menu déroulant Tkinter (sélection)
                    file_selector = Selecteur(state)
                    root.wait_window(file_selector.window)

        screen.blit(background_image, (0, 0))

        # Afficher le titre du jeu
        title_text = "Solar Sonic"
        title_rect = pygame.Rect(0, title_y, screen_width, 200)
        draw_text(screen, title_text, title_rect, title_font, WHITE)

        # Afficher le bouton de validation
        pygame.draw.rect(screen, PURPLE, button_box)
        draw_text(screen, button_text, button_box, font, WHITE)

        # Afficher le bouton du menu déroulant éditeur
        pygame.draw.rect(screen, GRAY, dropdown_button_box, 2)
        draw_text(screen, state['dropdown_button_text'], dropdown_button_box, font, BLACK)

        # Afficher le bouton du menu déroulant sélection
        pygame.draw.rect(screen, GRAY, selectsong_button_box, 2)
        draw_text(screen, state['selectsong_button_text'], selectsong_button_box, font, BLACK)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
