import pygame

pygame.init()
width = 800
height = 400
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
car_surface = pygame.transform.scale_by(car_surface, 0.10)
car_rect = car_surface.get_rect(midtop = (0, 100))

i = 0
while running :
    #Event loop
    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            running = False

    #All rendering
    score_surface = score_font.render(f"{car_rect.left}", True, "Pink")

    #All filling
    screen.fill((255,255,255))

    #Conditonals
    car_rect.left %= width
    car_rect.bottom %= height
    
    #All screen blits on to display
    screen.blit(track_surface, (0,100))
    screen.blit(score_surface, (0,0))
    #All boundary rendering
    border_rect = pygame.draw.rect(screen, "Blue", (700, 100, 5, track_rect.height))
    collision_rect = pygame.draw.rect(screen, "Black", (0,100, width, 2))
    screen.blit(car_surface, car_rect)

    #Handle player input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] :
        car_rect.top -=4
    if keys[pygame.K_DOWN] :
        car_rect.bottom +=4
    if keys[pygame.K_RIGHT] :
        car_rect.left +=4
    if keys[pygame.K_LEFT] :
        car_rect.right -=4

    #Clean up and frame rate
    pygame.display.update()
    clock.tick(60)

pygame.quit()