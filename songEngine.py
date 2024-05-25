import pygame
from pygame import mixer
from utils import bpm_for_time

mixer.init()

font = pygame.font.init()
clock = pygame.time.Clock()

# now we will create a map by making a txt file

screen = pygame.display.set_mode((800, 600))

# CLASSES

class Key():
    def __init__(self,x,y,coloridle,coloractive,key):
        self.x = x
        self.y = y
        self.coloridle = coloridle
        self.coloractive = coloractive
        self.key = key
        self.rect = pygame.Rect(self.x,self.y,100,40)
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

    mixer.music.load(map + "click.mp3")

    bpms = [(92, 0), (184, 4156), (61, 7662), (184, 22244), (92, 30534), (184, 33367), (61, 33970), (184, 43235), (92, 50642), (123, 56842), (92, 61811), (184, 64574), (61, 72608), (92, 72864), (184, 73235), (172, 74373), (61, 74489), (172, 74652), (161, 74768), (123, 74861), (161, 75511), (151, 75604), (161, 77206), (151, 78181), (172, 78320), (151, 78413), (92, 78576), (123, 78901), (92, 86401), (123, 88885), (92, 97338), (184, 105999), (92, 107787), (184, 108019), (92, 111757), (258, 116633), (184, 116680), (123, 117725), (184, 119513), (258, 121138), (61, 121254), (92, 121393), (184, 121719), (258, 127129), (92, 127361), (151, 129311), (80, 130472), (92, 131099), (258, 131935), (184, 131959), (92, 137740), (151, 139041), (123, 141479), (129, 141943), (184, 142106), (123, 142895), (129, 143801), (184, 144520), (129, 144822), (92, 145333), (129, 147330), (184, 148282), (258, 148514), (129, 148747), (123, 149443), (129, 150140), (258, 150418), (95, 150651), (123, 151347), (184, 151695), (123, 152601), (95, 152717), (184, 152833), (123, 152996), (78, 154435), (184, 154946), (129, 155132), (92, 155620), (184, 163189), (92, 168785), (151, 170620), (92, 171618), (184, 173406), (92, 178282), (107, 179397), (184, 179745), (107, 183832), (151, 183948), (92, 184203), (184, 184273), (92, 184366), (184, 185016), (92, 185620), (123, 187477), (92, 195929), (123, 196835), (92, 206564), (184, 215388), (92, 219962), (107, 225187), (184, 225256), (123, 225883), (107, 227369), (123, 227532), (92, 227601), (234, 240303), (123, 240558), (143, 240767), (184, 241185)]
    
    start_time = 3668
    beatmap = []
    beats = []
    beats_in_measure = []
    res = []
    with open(map + "2.txt", 'r') as file:
            for line in file:
                if line.strip():
                    if "," in line.strip():
                        beatmap.append(beats_in_measure)
                        beats_in_measure = []
                    else:
                        beat = []
                        blocks = line.strip()
                        for block in blocks:
                            beat.append(int(block))
                        beats_in_measure.append(beat)
    #print(len(beatmap))
    bpm = bpm_for_time(bpms, start_time)
    measure_time = int(240000 / bpm)
    current_time = start_time

    for beats_per_mesure in beatmap:
        #print(measure_time)
        for i in range(len(beats_per_mesure)):
            # Calculate the time for the current beat by adding the time for the previous beat
            beats_per_mesure[i] = (beats_per_mesure[i], (current_time + ((measure_time // (len(beats_per_mesure))) * (i))))
            # Update the previous time for the next iteration
        current_time += measure_time
        print(current_time)
        bpm = bpm_for_time(bpms, current_time)
        measure_time = int(240000 / bpm)
        res.append(beats_per_mesure)
    
    # print(beatmap)
    # [[([1, 0, 0, 0], 250.0), ([0, 0, 0, 0], 500.0), ([0, 0, 0, 0], 750.0), ([0, 0, 0, 0], 1000.0)], [([0, 1, 0, 0], 1333.3333333333333), ([0, 0, 0, 1], 1666.6666666666665), ([1, 0, 0, 0], 1999.9999999999998)], [([0, 0, 0, 0], 2250.0), ([1, 0, 0, 0], 2500.0), ([0, 0, 0, 0], 2750.0), ([0, 0, 0, 0], 3000.0)]]
    notes = []
    for beats in res:
        for beat, time in beats:
            for key_index in range(len(beat)):
                if beat[key_index] == 1:
                    notes.append((pygame.Rect(keys[key_index].rect.centerx - 25,0,50,25), time))
    return notes
    
# Loading a certain map
map_rect = load("sink")

# Main loop
current_time = 0

score = 0  # Initialize the score

#speed in pixels per second. If the coloured boxes are at 500y and it spawns at 0y, at 500 pps, 1 second is the time the boxes will reach the player.
speed = 500

start_time = pygame.time.get_ticks()
music_started = False  # Flag to track whether music has started

while True:
    screen.fill((0, 0, 0))
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

     # Update the current time
    dt = clock.tick(60)  # Get the time passed since the last frame in milliseconds
    current_time += dt  # Update current time
    elapsed_time = current_time - start_time

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
    for rect, time_frame in map_rect:
        # Check if it's time to spawn the note
        #print(current_time)
        if current_time >= time_frame:
            pygame.draw.rect(screen, (200, 0, 0), rect)
            rect.y += (speed/1000) * dt # Move the note down
            
        # Check collision with keys and handle accordingly
        for key in keys:
            if key.rect.colliderect(rect) and not key.handled:
                map_rect.remove((rect, time_frame))  # Remove the rectangle from map_rect
                key.handled = True
                # Increment the score when a note is hit
                score += 1
                #break

    # Display the score on the screen
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Update the display
    pygame.display.update()

