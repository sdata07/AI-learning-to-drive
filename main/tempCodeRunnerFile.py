import pygame
import math
import numpy as np



pygame.init()
width = 1400
height = 830
screen = pygame.display.set_mode((width, height), flags=pygame.SCALED, vsync=1) #Screen tearing fix

pygame.display.set_caption("Car")
clock = pygame.time.Clock()
running = True

score_font = pygame.font.Font(None, 50)

#Track info
track_surface = pygame.image.load("pics/racetrack.jpg").convert_alpha()
track_surface = pygame.transform.scale(track_surface, (width, 50))
track_rect = track_surface.get_rect()

#Car info
car_surface  = pygame.image.load("pics/Car_top.png").convert_alpha()
car_surface = pygame.transform.scale_by(car_surface, 0.03)
car_rect = car_surface.get_rect(midtop = (0, 100))


#Car info original
car_surface_orig = car_surface
degrees = 0
speed = 0
MAX_SPPED = 8

while running :
    #Event loop
    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            running = False

    #All rendering
    score_surface = score_font.render(f"{degrees}", True, "Pink")

    #All filling
    screen.fill((0,0,0))

    #Conditionals
    car_rect.left %= width
    car_rect.bottom %= height
    
    #Drawing the track
    outer_track = pygame.Rect(width/2,height/2, width - 300, height - 200)
    outer_track.center = (width/2, height/2)
    pygame.draw.rect(screen, "Red", outer_track, 10, 105)

    race_track = pygame.Rect(width/2,height/2, width - 320, height - 220)
    race_track.center = (width/2, height/2)
    pygame.draw.rect(screen, "Gray", race_track, 0, 100)

    inner_track = pygame.Rect(width/2,height/2, width - 600, height - 400)
    inner_track.center = (width/2, height/2)
    pygame.draw.rect(screen, "Red", inner_track, 10, 90)

    

    #All screen blits on to display
    screen.blit(score_surface, (0,0))
    #All boundary rendering
    border_rect = pygame.draw.rect(screen, "Blue", (700, 100, 5, track_rect.height))
    collision_rect = pygame.draw.rect(screen, "Black", (0,100, width, 2))
    screen.blit(car_surface, car_rect)

    #Handle player input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP] :
        speed += 1
        speed = min(MAX_SPPED, speed)
    elif keys[pygame.K_DOWN]:
        speed -= 1
        speed = max(-MAX_SPPED, speed)
    else :
        factor = -1 if speed < 0 else 1
        speed = abs(speed)
        speed -= 0.4 * (speed / 10)
        speed = speed * factor

    if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]:
        orig_x = car_rect.centerx
        orig_y = car_rect.centery

        if keys[pygame.K_RIGHT] :
            degrees -= 2
        else : 
            degrees += 2
        degrees %= 360

        car_surface  = pygame.transform.rotate(car_surface_orig, degrees)
        car_rect = car_surface.get_rect(center = (orig_x , orig_y))

    car_rect.top -= speed * math.sin(degrees * math.pi / 180)
    car_rect.left += speed * math.cos(degrees * math.pi / 180)

    #Clean up and frame rate
    pygame.draw.rect(screen,"Orange", car_rect, 2)
    pygame.display.update()
    clock.tick(60)

pygame.quit()



