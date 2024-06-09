import pygame
from utils import bpm_for_time
from game_config import *
from song_generation import extract_filename

class Note():
    def __init__(self, key_index):
        self.key_index = key_index
        self.x = keys[key_index].rect.centerx - 45
        self.y = 0
        self.rect = pygame.Rect(self.x, self.y, 90, 20)
        self.image = pygame.image.load(note_image_paths[key_index]).convert_alpha()  # Assign the image based on key index
        #self.image = pygame.transform.scale(self.image, (80, 80))
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
        screen.blit(self.image, self.rect.topleft)

class Key():
    def __init__(self,x,y,coloridle,coloractive,key):
        self.x = x
        self.y = y
        self.coloridle = coloridle
        self.coloractive = coloractive
        self.key = key
        self.rect = pygame.Rect(self.x,self.y,90,40)
        self.handled = False

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
                        print(f"Key {event.key} pressed at {current_time - start_time - 1000}")
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

            if current_time - start_time > last_note_time + 5000:
                running = False # Go out of loop

            # Display the score on the screen
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            # Update the display
            pygame.display.update()

            if not running:
                break

        EndScreen(score)

class EndScreen():
    """
    Affiche l'écran de fin avec le score final.

    Attributs:
    song_name (str): Le nom de la chanson.
    score (int): Le score final du joueur.
    """
    def __init__(self, score) -> None:
        """
        initialise le variablescore pour l'affichage
        """
        self.score = score
        self.run()

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
            score_text = title_font.render(f"Score: {self.score}", True, (255, 255, 255))
            screen_width, screen_height = screen.get_size()
            text_width = score_text.get_width()
            text_height = score_text.get_height()
            screen.blit(score_text, (screen_width // 2 - text_width // 2 , screen_height // 2 - text_height // 2))
            help_text = font2.render("appuyez sur n'importe quelle touche pour continuer", True, (255, 255, 255))
            screen.blit(help_text, (screen_width // 2 - help_text.get_width() // 2, screen_height // 2 - help_text.get_height() // 2 + 150))
    
            # Update the display
            pygame.display.update()

keys = [
    Key(200, 500, (255, 0, 0), (220, 0, 0), key_1_bind),
    Key(300, 500, (0, 255, 0), (0, 220, 0), key_2_bind),
    Key(400, 500, (0, 0, 255), (0, 0, 220), key_3_bind),
    Key(500, 500, (255, 255, 0), (220, 220, 0), key_4_bind)
    ]