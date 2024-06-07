import pygame
from threading import Thread
from config import *
import song_generation

class CustomThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.value = None

    def run(self):
        self.value = song_generation.generate_chart(song_path)

def run_loading_screen():
    clock = pygame.time.Clock()
    background_image = pygame.image.load("assets/background.jpg")
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

    font = pygame.font.SysFont(None, 36)
    bar_width = 600
    bar_height = 50
    x_bar = (screen_width - bar_width) // 2
    y_bar = (screen_height - bar_height) // 2
    fill_width = 0

    update_interval = 2000
    current_step = 0

    step_texts = [
        "Loading audio file...",
        "Filtering audio...",
        "Detecting onsets...",
        "Finding tempo...",
        "Calculating RMS...",
        "Analyzing musical segments..."
    ]

    global song_path
    song_path = "Music+Beatmaps/sink.mp3"
    custom_thread = CustomThread()
    custom_thread.start()

    last_update_time = pygame.time.get_ticks()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_time = pygame.time.get_ticks()
        if current_time - last_update_time >= update_interval:
            current_step += 1
            last_update_time = current_time
        fill_width = min(bar_width * (current_step / 6), fill_width + 1)

        screen.blit(background_image, (0, 0))
        pygame.draw.rect(screen, WHITE, (x_bar, y_bar, bar_width,
