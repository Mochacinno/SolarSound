import pygame

clock = pygame.time.Clock()

time = 0
while True: 
    time += clock.tick(60)
    print(time)
