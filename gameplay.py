# gameplay.py
import pygame
import sys
from utils import bpm_for_time
from note import Note
from key import Key

# LOADING SONG Function
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

# initialising keys
keys = [
    Key(100, 500, (255, 0, 0), (220, 0, 0), pygame.K_z),
    Key(200, 500, (0, 255, 0), (0, 220, 0), pygame.K_x),
    Key(300, 500, (0, 0, 255), (0, 0, 220), pygame.K_m),
    Key(400, 500, (255, 255, 0), (220, 220, 0), pygame.K_COMMA),
]

class Gameplay:
    def __init__(self, song_path):
        self.beatmap = load(song_path)
        self.note_speed = 1
        self.BPM = 0
        self.notes = []
        self.note_index = 0
        self.run()

    def run(self):
        start_time = pygame.time.get_ticks()
        current_time = start_time
        score = 0
        music_started = False
        clock = pygame.time.Clock()
        speed = 500

        running = True
        while running:
            screen.fill((255, 255, 255))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in key_press_times:
                        key_press_times[event.key].append(current_time - start_time - 1000)
                        print(f"Key {event.key} pressed at {current_time - start_time - 1000}")

            dt = clock.tick(60)
            current_time += dt

            if not music_started and current_time - start_time >= 1000 + 69 - 175:
                pygame.mixer.music.play()
                music_started = True

            k = pygame.key.get_pressed()
            for key in keys:
                if k[key.key]:
                    pygame.draw.rect(screen, key.coloridle, key.rect)
                    key.handled = False
                else:
                    pygame.draw.rect(screen, key.coloractive, key.rect)
                    key.handled = True

            for note, time_frame in self.beatmap[:]:
                if current_time - start_time >= time_frame:
                    if not note.dissolving:
                        note.update((speed / 1000) * dt)
                    else:
                        note.dissolve()
                        if note.alpha == 0:
                            self.beatmap.remove((note, time_frame))

                    note.draw(screen)

                if not note.dissolving:
                    for key in keys:
                        if note.key_index == keys.index(key):
                            texte_score_time = 0
                            for press_time in key_press_times[key.key]:
                                if abs(press_time - time_frame) < 30:
                                    note.dissolving = True
                                    key_press_times[key.key].remove(press_time)
                                    score += 2
                                    texte_score_time = current_time

                                    texte = "Perfect"
                                    image_texte = font2.render(texte, True, GRAY)
                                    rect_texte = image_texte.get_rect()
                                    rect_texte.center = (400, 300)
                                    screen.blit(image_texte, rect_texte)

                                elif abs(press_time - time_frame) < 50:
                                    note.dissolving = True
                                    key_press_times[key.key].remove(press_time)
                                    score += 1
                                    texte_score_time = current_time

                                    texte = "Good"
                                    image_texte = font2.render(texte, True, GRAY)
                                    rect_texte = image_texte.get_rect()
                                    rect_texte.center = (400, 300)
                                    screen.blit(image_texte, rect_texte)

            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            pygame.display.update()

            if not running:
                break
