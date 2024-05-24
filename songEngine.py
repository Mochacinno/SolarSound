import pygame

#lets get sound 
from pygame import mixer

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

def bpm_for_time(bpm_array, time):
    """
    Get the BPM value at a specific time.
    
    Parameters:
    bpm_array (list of tuples): List of tuples (bpm, time_when_change_occurs).
    time (float): The specific time at which to find the BPM.
    
    Returns:
    float: The BPM value at the specified time.
    """
    bpm = bpm_array[0][0]  # Start with the first BPM value
    
    for bpm_change, change_time in bpm_array:
        if time < change_time:
            break
        bpm = bpm_change
    
    return bpm

def load(map):

    mixer.music.load(map + ".mp3")

    bpms = [(92.0, 0.0), (185.0, 4.16), (62.0, 7.66), (185.0, 22.24), (92.0, 30.53), (185.0, 33.37), (62.0, 33.97), (185.0, 43.24), (92.0, 50.64), (123.0, 56.84), (92.0, 61.81), (185.0, 64.57), (62.0, 72.61), (92.0, 72.86), (185.0, 73.24), (172.0, 74.37), (62.0, 74.49), (172.0, 74.65), (161.0, 74.77), (123.0, 74.86), (161.0, 75.51), (152.0, 75.6), (161.0, 77.21), (152.0, 78.18), (172.0, 78.32), (152.0, 78.41), (92.0, 78.58), (123.0, 78.9), (92.0, 86.4), (123.0, 88.89), (92.0, 97.34), (185.0, 106.0), (92.0, 107.79), (185.0, 108.02), (92.0, 111.76), (258.0, 116.63), (185.0, 116.68), (123.0, 117.73), (185.0, 119.51), (258.0, 121.14), (62.0, 121.25), (92.0, 121.39), (185.0, 121.72), (258.0, 127.13), (92.0, 127.36), (152.0, 129.31), (81.0, 130.47), (92.0, 131.1), (258.0, 131.94), (185.0, 131.96), (92.0, 137.74), (152.0, 139.04), (123.0, 141.48), (129.0, 141.94), (185.0, 142.11), (123.0, 142.9), (129.0, 143.8), (185.0, 144.52), (129.0, 144.82), (92.0, 145.33), (129.0, 147.33), (185.0, 148.28), (258.0, 148.51), (129.0, 148.75), (123.0, 149.44), (129.0, 150.14), (258.0, 150.42), (96.0, 150.65), (123.0, 151.35), (185.0, 151.7), (123.0, 152.6), (96.0, 152.72), (185.0, 152.83), (123.0, 153.0), (78.0, 154.44), (185.0, 154.95), (129.0, 155.13), (92.0, 
155.62), (185.0, 163.19), (92.0, 168.79), (152.0, 170.62), (92.0, 171.62), (185.0, 173.41), (92.0, 178.28), (108.0, 179.4), (185.0, 179.75), (108.0, 183.83), (152.0, 183.95), (92.0, 184.2), (185.0, 184.27), (92.0, 184.37), (185.0, 185.02), (92.0, 185.62), (123.0, 187.48), (92.0, 195.93), (123.0, 196.84), (92.0, 206.56), (185.0, 215.39), (92.0, 219.96), (108.0, 225.19), (185.0, 225.26), (123.0, 225.88), (108.0, 227.37), (123.0, 227.53), (92.0, 227.6), (235.0, 240.3), (123.0, 240.56), (144.0, 240.77), (185.0, 241.19)]

    start_time = 3.67

    beatmap = []
    beats = []
    beats_in_measure = []
    res = []
    with open(map + "3.txt", 'r') as file:
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
    measure_time = (60 / bpm) * 4000

    current_time = (start_time * 1000) - (measure_time / (len(beatmap[0])))

    for beats_per_mesure in beatmap:
        bpm = bpm_for_time(bpms, current_time / 1000)
        measure_time = (60 / bpm) * 4000
        #print(measure_time)
        for i in range(len(beats_per_mesure)):
            # Calculate the time for the current beat by adding the time for the previous beat
            beats_per_mesure[i] = (beats_per_mesure[i], (current_time + ((measure_time / (len(beats_per_mesure))) * (i+1))))
            # Update the previous time for the next iteration
        current_time += measure_time
        res.append(beats_per_mesure)
    
    print(beatmap)
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
    if not music_started and current_time - start_time >= 3400:
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

