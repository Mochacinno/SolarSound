import pygame
import json
from utils import bpm_for_time
from game_config import *
from song_generation import extract_filename

# Dictionnaire pour stocker les meilleurs scores
best_scores = {}

def load_best_scores():
    """
    Charge les meilleurs scores depuis un fichier JSON.
    """
    global best_scores
    try:
        with open("best_scores.json", "r") as file:
            best_scores = json.load(file)
    except FileNotFoundError:
        best_scores = {}

def save_best_scores():
    """
    Sauvegarde les meilleurs scores dans un fichier JSON.
    """
    with open("best_scores.json", "w") as file:
        json.dump(best_scores, file)

class Note():
    def __init__(self, key_index):
        self.key_index = key_index
        self.x = keys[key_index].rect.centerx - 45
        self.y = 0
        self.rect = pygame.Rect(self.x, self.y, 90, 20)
        self.image = pygame.image.load(note_image_paths[key_index]).convert_alpha()  # Assign the image based on key index
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.alpha = 255  # Initial alpha value
        self.dissolving = False
    
    def update(self, speed):
        """
        Met à jour la position de la note en fonction de la vitesse.

        Paramètres:
        speed (int): La vitesse à laquelle la note se déplace.
        """
        self.y += speed
        self.rect.y = self.y

    def dissolve(self):
        """
        Fait disparaître progressivement la note en diminuant sa transparence.
        """
        if self.alpha > 0:
            self.alpha -= 20  # Adjust the decrement to control dissolve speed
            if self.alpha < 0:
                self.alpha = 0
            self.image.set_alpha(self.alpha)

    def draw(self, screen):
        """
        Dessine la note sur l'écran.

        Paramètres:
        screen (pygame.Surface): La surface sur laquelle dessiner la note.
        """
        image_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, image_rect.topleft)

class Key():
    def __init__(self, x, y, key_index, key):
        self.x = x
        self.y = y
        self.key = key
        self.rect = pygame.Rect(self.x, self.y, 90, 40)
        self.image = key_image_paths[3-key_index]
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.handled = False

    def draw(self, screen):
        """
        Dessine le key sur l'écran.

        Paramètres:
        screen (pygame.Surface): La surface sur laquelle dessiner la note.
        """
        image_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, image_rect.topleft)

class Gameplay():
    """
    Gère la logique de jeu et les événements.

    Attributs:
    song_name (str): Le nom de la chanson.
    beatmap (list): La carte de rythme (beatmap) chargée.
    note_speed (int): La vitesse des notes.
    BPM (int): Le BPM de la chanson.
    notes (list): Liste des notes.
    note_index (int): L'index de la note actuelle.
    """
    def __init__(self, song_path):
        """
        Initialise les paramètres du jeu
        """
        #self.map = selectsong_button_text[:-4]
        self.song_name = extract_filename(song_path)
        self.beatmap = self.load(song_path)
        self.note_speed = 1
        self.BPM = 0
        self.notes = []
        self.note_index = 0
        self.run()

    # LOADING SONG Function
    def load(self, song_path):
        """
        Charge la musique et la carte de rythme (beatmap) pour le jeu.

        Paramètres:
        map (str): Le nom de la carte de rythme à charger, sans l'extension de fichier.

        Retourne:
        notes (list): Une liste de tuples contenant des objets Note et leurs temps associés.
        """
        pygame.mixer.music.load(song_path)
        song_name = extract_filename(song_path)
        with open(f"charts/{song_name}.txt", 'r') as file:
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

        bpm = bpm_for_time(bpms, start_time)
        measure_time = int(240000 / bpm)
        current_time = start_time

        res = []
        for beats_per_mesure in beatmap:
            for i in range(len(beats_per_mesure)):
                # Calculate the time for the current beat by adding the time for the previous beat
                beats_per_mesure[i] = (beats_per_mesure[i], (current_time + ((measure_time // (len(beats_per_mesure))) * (i))))
                # Update the previous time for the next iteration
            current_time += measure_time
            bpm = bpm_for_time(bpms, current_time)
            measure_time = int(240000 / bpm)
            res.append(beats_per_mesure)

        # print(res)
        # [[([1, 0, 0, 0], 250.0), ([0, 0, 0, 0], 500.0), ([0, 0, 0, 0], 750.0), ([0, 0, 0, 0], 1000.0)], [([0, 1, 0, 0], 1333.3333333333333), ([0, 0, 0, 1], 1666.6666666666665), ([1, 0, 0, 0], 1999.9999999999998)], [([0, 0, 0, 0], 2250.0), ([1, 0, 0, 0], 2500.0), ([0, 0, 0, 0], 2750.0), ([0, 0, 0, 0], 3000.0)]]
        notes = []
        for beats in res:
            for beat, time in beats:
                for key_index in range(len(beat)):
                    if beat[key_index] == 1:
                        notes.append((Note(key_index), time))

        return notes

    def run(self):
        """
        Lance la boucle principale du jeu.
        """
        # Initialize a dictionary to store key press times
        key_press_times = {key.key: [] for key in keys}
        # Reset game variables
        start_time = pygame.time.get_ticks()
        current_time = start_time
        score = 0
        music_started = False
        clock = pygame.time.Clock()
        speed = 500

        # Last note time
        last_note_time = self.beatmap[-1][1]

        texte = "" # pour le score

        running = True
        while running:
            screen.blit(fond_gameplay, (0,0))
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in key_press_times:
                        key_press_times[event.key].append(current_time - start_time - 1000)
                        #print(f"Key {event.key} pressed at {current_time - start_time - 1000}")

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
                    key.draw(screen)
                    key.handled = False
                else:
                    key.draw(screen)
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
                                if abs(press_time - time_frame) < 50:  # SCORING SYSTEM
                                    note.dissolving = True  # Start the dissolve effect
                                    key_press_times[key.key].remove(press_time)  # Remove the handled key press time
                                    score += 500  # Increment the score when a note is hit

                                    # Créer une surface contenant le texte
                                    texte = "Perfect !"

                                elif abs(press_time - time_frame) < 80:  # SCORING SYSTEM
                                    note.dissolving = True  # Start the dissolve effect
                                    key_press_times[key.key].remove(press_time)  # Remove the handled key press time
                                    score += 300  # Increment the score when a note is hit
                                    # Créer une surface contenant le texte
                                    texte = "Good !"
                                
                                elif abs(press_time - time_frame) < 200:  # SCORING SYSTEM
                                    note.dissolving = True  # Start the dissolve effect
                                    key_press_times[key.key].remove(press_time)  # Remove the handled key press time
                                    score += 100  # Increment the score when a note is hit
                                    # Créer une surface contenant le texte
                                    texte = "Late !"

                image_texte = font2.render(texte, True, GRAY)
                # Obtenir le rectangle de l'image du texte pour le positionnement
                rect_texte = image_texte.get_rect()
                # Centrer le texte à la fenêtre
                rect_texte.center = (400, 400)
                screen.blit(image_texte, rect_texte) 

            if current_time - start_time > last_note_time + 5000:
                running = False # Go out of loop

            # Display the score on the screen
            score_texte = font.render(f"Score: {score}", True, GRAY)
            score_rect_texte = score_texte.get_rect()
            # Centrer le texte à la fenêtre
            score_rect_texte.center = (400, 430)
            screen.blit(score_texte, score_rect_texte)

            # Update the display
            pygame.display.update()

            if not running:
                break

        # Mettre à jour le meilleur score
        if self.song_name in best_scores:
            if score > best_scores[self.song_name]:
                best_scores[self.song_name] = score
        else:
            best_scores[self.song_name] = score

        # Sauvegarder les meilleurs scores
        save_best_scores()

        EndScreen(self.song_name, score, best_scores[self.song_name])


class EndScreen():
    """
    Affiche l'écran de fin avec le score final.

    Attributs:
    song_name (str): Le nom de la chanson.
    score (int): Le score final du joueur.
    """
    def __init__(self, song_name, score, best_score) -> None:
        """
        initialise le variablescore pour l'affichage
        """
        self.song_name = song_name
        self.best_score = best_score
        self.score = score
        self.run()
    
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
        Lance la boucle principale de l'écran de fin.
        """
        running = True
        while running:
            screen.fill((0, 0, 0))

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    running = False
        
            # Display the score on the screen
            background = pygame.image.load("assets/background.jpg")
            background = pygame.transform.scale(background, (800, 600))
            blurred_background = EndScreen.blur_surface(background, 10)  # Adjust the blur amount
            EndScreen.darken_surface(blurred_background, 150)
            screen.blit(blurred_background, (0, 0))
            score_text = title_font.render(f"Score: {self.score}", True, (255, 255, 255))
            best_score_text = font.render(f"Meilleur score : {self.best_score}", True, (255, 255, 255))
            song_name_text = font2.render(f"{self.song_name}", True, (255, 255, 255))
            screen_width, screen_height = screen.get_size()
            score_text_width = score_text.get_width()
            score_text_height = score_text.get_height()
            best_score_text_width = best_score_text.get_width()
            best_score_text_height = best_score_text.get_height()
            screen.blit(score_text, (screen_width // 2 - score_text_width // 2 , screen_height // 2 - score_text_height // 2))
            screen.blit(best_score_text, (screen_width // 2 - best_score_text_width // 2 , screen_height // 2 - best_score_text_height // 2 + 100))
            screen.blit(song_name_text, (screen_width // 2 - best_score_text_width // 2 , screen_height // 2 - best_score_text_height // 2 + 300))
            help_text = font2.render("appuyez sur n'importe quelle touche pour continuer", True, (255, 255, 255))
            screen.blit(help_text, (screen_width // 2 - help_text.get_width() // 2, screen_height // 2 - help_text.get_height() // 2 + 150))

    
            # Update the display
            pygame.display.update()

keys = [
    Key(200, 500, 0, key_1_bind),
    Key(300, 500, 1, key_2_bind),
    Key(400, 500, 2, key_3_bind),
    Key(500, 500, 3, key_4_bind)
    ]