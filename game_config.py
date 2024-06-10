import pygame

pygame.init() # bug where faut initiliaser pygame ici aussi sinon erreur de fonts
# Dimensions de la fenêtre
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Menu de démarrage - Jeu de rythme")

FPS = 60 # setting the frames per second of the main menu

# keybinds
key_1_bind = pygame.K_z
key_2_bind = pygame.K_x
key_3_bind = pygame.K_m
key_4_bind = pygame.K_COMMA

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BUTTON_COLOR = (100, 200, 100)
TEXT_COLOR = (255, 255, 255)
BG_COLOR = (30, 30, 30)

# Police d'écriture
title_font = pygame.font.Font(None, 100)
font = pygame.font.Font(None, 30)
font2 = pygame.font.SysFont(None, 40)

# Charger l'image de menu principal avec l'effet parallax
bg_images = [pygame.image.load(f"assets/background-{4-i}.png").convert_alpha() for i in range(1,4)]
bg_offset = [(0, 0), (116, 16), (0, -90)]
bg_speeds = [0.2, 0.3, 0.8]

bg_images[1] = pygame.transform.scale(bg_images[1], (bg_images[1].get_width() * 1.05, bg_images[1].get_height() * 1.05))
bg_images[2] = pygame.transform.scale(bg_images[2], (bg_images[2].get_width() * 1.2, bg_images[2].get_height() * 1.2))

# Charger l'image de menu gameplay
fond_gameplay = pygame.image.load("assets/fond.jpg").convert()
fond_gameplay = pygame.transform.scale(fond_gameplay, (screen_width, screen_height))

# charger les images de tuto
tutorial1 = pygame.image.load('assets/tutorial1.jpg')
tutorial1 = pygame.transform.scale(tutorial1, (screen_width, screen_height))
tutorial2 = pygame.image.load('assets/tutorial2.jpg')
tutorial2 = pygame.transform.scale(tutorial2, (screen_width, screen_height))
# Liste des images a charge pour les notes
note_image_paths = [
    "assets/flèche_gauche.png",
    "assets/flèche_haut.png",
    "assets/flèche_bas.png",
    "assets/flèche_droite.png"
]

key_image_paths = [
    pygame.transform.rotate(pygame.image.load("assets/note.png").convert_alpha(), 90),
    pygame.image.load("assets/note.png").convert_alpha(),
    pygame.transform.rotate(pygame.image.load("assets/note.png").convert_alpha(), 180),
    pygame.transform.rotate(pygame.image.load("assets/note.png").convert_alpha(), 270)
]



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
