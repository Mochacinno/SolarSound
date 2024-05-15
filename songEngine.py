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

def load(map):

    mixer.music.load(map + ".mp3")

    rects = []
    beatmap = []
    beats = []
    
    with open(map + ".txt", 'r') as file:
        for line in file:
            if line.strip():
                if line.strip() == ",":
                    beatmap.append(beats)
                    beats = []
                else:
                    beat = []
                    blocks = line.strip().split(',')
                    for block in blocks:
                        beat.append([int(char) for char in block if char.isdigit()])
                    beats.append(beat[0])

    previous_time = 0  # Initialize previous time to 0
    for beats in beatmap:
        for i in range(len(beats)):
            # Calculate the time for the current beat by adding the time for the previous beat
            beats[i] = (beats[i], (previous_time + (1000 / (len(beats)-1)) * i))
            # Update the previous time for the next iteration
        previous_time += 1000
    
    #print(beatmap)
    # [[([1, 0, 0, 0], 250.0), ([0, 0, 0, 0], 500.0), ([0, 0, 0, 0], 750.0), ([0, 0, 0, 0], 1000.0)], [([0, 1, 0, 0], 1333.3333333333333), ([0, 0, 0, 1], 1666.6666666666665), ([1, 0, 0, 0], 1999.9999999999998)], [([0, 0, 0, 0], 2250.0), ([1, 0, 0, 0], 2500.0), ([0, 0, 0, 0], 2750.0), ([0, 0, 0, 0], 3000.0)]]
    
    for beats in beatmap:
        for beat, time in beats:
            for key_index in range(len(beat)):
                if beat[key_index] == 1:
                    rects.append((pygame.Rect(keys[key_index].rect.centerx - 25,0,50,25), time))
    return rects
    
# Loading a certain map
map_rect = load("nATALIE")

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
    if not music_started and current_time - start_time >= 800:
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

