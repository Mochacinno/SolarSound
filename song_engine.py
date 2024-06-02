import pygame
from pygame import mixer
from utils import bpm_for_time

mixer.init()

font = pygame.font.init()
clock = pygame.time.Clock()

# now we will create a map by making a txt file

screen = pygame.display.set_mode((800, 600))

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

# FUNCTIONS

clock = pygame.time.Clock()

def load(map):

    #mixer.music.load(map + "click.mp3")
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
    print(f"measure_time: {measure_time}")
    current_time = start_time

    res = []
    for beats_per_mesure in beatmap:
        print(f"measure_time: {measure_time}")
        for i in range(len(beats_per_mesure)):
            # Calculate the time for the current beat by adding the time for the previous beat
            beats_per_mesure[i] = (beats_per_mesure[i], (current_time + ((measure_time // (len(beats_per_mesure))) * (i))))
            # Update the previous time for the next iteration
        current_time += measure_time
        #print(current_time)
        bpm = bpm_for_time(bpms, current_time)
        print(f"for bpm: {bpm}")
        measure_time = int(240000 / bpm)
        res.append(beats_per_mesure)

    # print(res)
    # [[([1, 0, 0, 0], 250.0), ([0, 0, 0, 0], 500.0), ([0, 0, 0, 0], 750.0), ([0, 0, 0, 0], 1000.0)], [([0, 1, 0, 0], 1333.3333333333333), ([0, 0, 0, 1], 1666.6666666666665), ([1, 0, 0, 0], 1999.9999999999998)], [([0, 0, 0, 0], 2250.0), ([1, 0, 0, 0], 2500.0), ([0, 0, 0, 0], 2750.0), ([0, 0, 0, 0], 3000.0)]]
    notes = []
    for beats in res:
        for beat, time in beats:
            for key_index in range(len(beat)):
                if beat[key_index] == 1:
                    #notes.append((pygame.Rect(keys[key_index].rect.centerx - 25,0,50,25), time))m,
                    notes.append((Note(key_index), time))
    return notes
    
# Loading a certain map
song_name = "sink"
map_rect = load("Music+Beatmaps/"+song_name)

# Main loop
current_time = 0

score = 0  # Initialize the score

#speed in pixels per second. If the coloured boxes are at 500y and it spawns at 0y, at 500 pps, 1 second is the time the boxes will reach the player.
speed = 500

start_time = pygame.time.get_ticks()
music_started = False  # Flag to track whether music has started
    
# Initialize a dictionary to store key press times
key_press_times = {key.key: [] for key in keys}

# Constants
WIDTH, HEIGHT = 800, 600
BG_COLOR = (30, 30, 30)
BUTTON_COLOR = (100, 200, 100)
TEXT_COLOR = (255, 255, 255)
FONT_SIZE = 24
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50
font = pygame.font.Font(None, 36)

# Define a button class
class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback

    def draw(self, screen):
        pygame.draw.rect(screen, BUTTON_COLOR, self.rect)
        text_surface = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()

# Define the main menu function
def main_menu():
    menu_running = True

    # Define the start button
    start_button = Button(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 - BUTTON_HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT, "Start Game", start_game)

    while menu_running:
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    start_button.check_click(event.pos)

        # Draw the start button
        start_button.draw(screen)

        # Update the display
        pygame.display.update()

# Define the game function
def start_game():
    global start_time, current_time, score, music_started

    # Reset game variables
    start_time = pygame.time.get_ticks()
    current_time = start_time
    score = 0
    music_started = False
    clock = pygame.time.Clock()

    # Game loop
    while True:
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
        for note, time_frame in map_rect[:]:
            if current_time - start_time >= time_frame:
                if not note.dissolving:
                    note.update((speed / 1000) * dt)  # Move the note down
                else:
                    note.dissolve()
                    if note.alpha == 0:
                        map_rect.remove((note, time_frame))

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

# Main loop to start the menu
main_menu()

