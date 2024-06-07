import pygame
from threading import Thread
from game_config import *
import song_generation
import sys

class CustomThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.value = None

    def run(self):
        self.value = song_generation.generate_chart(song_path)

def run_loading_screen():

    clock = pygame.time.Clock()

    # Load background image
    background_image = pygame.image.load("assets/background.jpg")
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

    # Text font
    font = pygame.font.SysFont(None, 36)

    # Variables for loading bar
    bar_width = 600
    bar_height = 50
    x_bar = (screen_width - bar_width) // 2
    y_bar = (screen_height - bar_height) // 2
    fill_width = 0

    # Progress bar update interval (in milliseconds)
    update_interval = 2000  # 20 seconds

    # Current step status
    current_step = 0

    # Step texts
    step_texts = [
        "Loading audio file...",
        "Filtering audio...",
        "Detecting onsets...",
        "Finding tempo...",
        "Calculating RMS...",
        "Analyzing musical segments..."
    ]

    # Start the process
    global song_path
    song_path = "Music+Beatmaps/sink.mp3" 
    custom_thread = CustomThread()

    # Start the song generation
    # Create and start the thread
    custom_thread.start()

    # Time of the last progress update
    last_update_time = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Check if it's time to update the progress
        current_time = pygame.time.get_ticks()
        if current_time - last_update_time >= update_interval:
            # Update current step
            current_step += 1
            # Reset last update time
            last_update_time = current_time
        # Update loading bar
        fill_width = min(bar_width * (current_step / 6), fill_width + 1)
        # Display loading screen
        screen.blit(background_image, (0, 0))
        pygame.draw.rect(screen, WHITE, (x_bar, y_bar, bar_width, bar_height))
        pygame.draw.rect(screen, GRAY, (x_bar, y_bar, fill_width, bar_height))
        # Display current step text
        if current_step < len(step_texts):
            current_step_text = step_texts[current_step]
            text_surface = font.render(current_step_text, True, pygame.Color('white'))
            screen.blit(text_surface, (x_bar, y_bar - 40))
        else:
            running = False
        
        pygame.display.flip()
        clock.tick(30)
        

    custom_thread.join() # Ensure the task completes
    value = custom_thread.value 