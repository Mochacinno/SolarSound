import pygame
from pygame import mixer
from utils import bpm_for_time

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