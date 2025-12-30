import pygame
import math
import numpy as np

class reward_gate:
    def __init__(self, start: tuple, end: tuple):
        self.start = start
        self.end = end
        self.crossed = False

def cast_ray(track_mask: pygame.mask, car_rect: pygame.Rect, track_rect: pygame.Rect, degrees):

    curr_x, curr_y = car_rect.centerx - track_rect.left, car_rect.centery - track_rect.top
    
    dx =  math.cos(degrees * (math.pi/180))
    dy =  -math.sin(degrees * (math.pi/180))

    while (curr_x >= 0 and curr_x < track_mask.get_size()[0] and
           curr_y >= 0 and curr_y < track_mask.get_size()[1] and
           track_mask.get_at((int(curr_x), int(curr_y))) == 1) :
        curr_x += dx
        curr_y += dy

    distance = math.sqrt((car_rect.centerx - track_rect.left - curr_x)**2 + (car_rect.centery - track_rect.top - curr_y) ** 2)
    return distance, (curr_x, curr_y)

def cast_all_rays(track_mask: pygame.mask, car_rect: pygame.Rect, track_rect: pygame.Rect, degrees, count=4) : 
    step = 0
    ray_points = []
    dists_to_edge = []
    while (step <= 360) :
        dist, (ray_x, ray_y) = cast_ray(track_mask, car_rect, track_rect, degrees + step)
        ray_points.append((ray_x, ray_y))
        dists_to_edge.append(dist)
        step += 360/count
    return dists_to_edge, ray_points

def dist_to_reward_gate(gates: list[reward_gate], car_rect: pygame.Rect) :
    for gate in gates:
        if (not gate.crossed):
            avg = (np.add(gate.start, gate.end)) / 2
            return (car_rect.centerx - avg[0]) ** 2 + (car_rect.centery - avg[1]) **2

def reset_gates(gates : list[reward_gate]):
    for gate in gates:
        gate.crossed = False

def all_crossed(gates : list[reward_gate]) -> bool:
    for gate in gates:
        if not (gate.crossed):
            return False
    return True


pygame.init()
width = 1400
height = 830
screen = pygame.display.set_mode((width, height), flags=pygame.SCALED, vsync=1) #Screen tearing fix

pygame.display.set_caption("Car")
clock = pygame.time.Clock()
running = True

score_font = pygame.font.Font(None, 50)

#Track info
track_surface = pygame.image.load("pics/racetrack.png").convert_alpha()
track_surface = pygame.transform.scale_by(track_surface, 2)
track_rect = track_surface.get_rect(center = (width/2, height/2))
track_mask = pygame.mask.from_surface(track_surface)
mask_image = track_mask.to_surface()

#Car info
car_surface  = pygame.image.load("pics/Car_top.png").convert_alpha()
car_surface = pygame.transform.scale_by(car_surface, 0.04)
car_rect = car_surface.get_rect(midtop = (600, 650))

#Car info original
car_surface_orig = car_surface
degrees = 180
speed = 0
MAX_SPPED = 8
RAY_COUNT = 8


#Making Reward Gates (side_length = 155)
gate_left = reward_gate((205,400), (360, 400))
gate_right = reward_gate((1037,400), (1192, 400))
gate_up = reward_gate((width/2, 100), (width/2, 205))
gate_down = reward_gate((width/2, 625), (width/2, 730))

reward_gates = [gate_left, gate_up, gate_right, gate_down]
curr_gate = 0

#Distances
dists_to_edge = [-1] * RAY_COUNT
dist_to_gate = -1

while running :
    #Event loop
    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            running = False

    #All rendering
    score_surface = score_font.render(f"{degrees}", True, "Pink")
    distance_surface = score_font.render(f"{sum(dists_to_edge)/len(dists_to_edge)}", True, "Pink")
    reward_dist_surface = score_font.render(f"{dist_to_gate}", True, "Pink")
    curr_gate_surface = score_font.render(f"{curr_gate}", True, "Pink")

    #All filling
    screen.fill((0,0,0))

    #Conditionals
    car_rect.left %= width
    car_rect.bottom %= height
    
    #Drawing the track
    screen.blit(track_surface, track_rect)

    #Collison check and restart
    car_mask = pygame.mask.from_surface(car_surface)
    if not track_mask.overlap(car_mask, (car_rect.left - track_rect.left, car_rect.top - track_rect.top)):
        car_surface = pygame.transform.rotate(car_surface_orig, 180)
        car_rect = car_surface.get_rect(midtop = (600, 650))
        degrees = 180
        speed = 0
        reset_gates(reward_gates)
        curr_gate = 0

    #Casting rays
    dists_to_edge, rays = cast_all_rays(track_mask, car_rect, track_rect, degrees, RAY_COUNT)
    for i in range(0,RAY_COUNT): 
        pygame.draw.line(screen, "Blue", 
                        (car_rect.centerx, car_rect.centery), 
                        (rays[i][0] + track_rect.left, rays[i][1] + track_rect.top))

    #Drawing reward gates and calculating distance
    if (all_crossed(reward_gates)):
        reset_gates(reward_gates)
        curr_gate = 0
    for gate in reward_gates:
        pygame.draw.line(screen, "Yellow", gate.start, gate.end)
        if car_rect.clipline(gate.start, gate.end) and reward_gates[curr_gate] == gate:
            gate.crossed = True
            curr_gate +=1
    
    dist_to_gate = dist_to_reward_gate(reward_gates, car_rect)

    #All screen blits on to display
    screen.blit(score_surface, (0,0))
    screen.blit(distance_surface, (700, 0))
    screen.blit(reward_dist_surface, (300,0))
    screen.blit(curr_gate_surface, (500,0))
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
    #pygame.draw.rect(screen,"Orange", car_rect, 2)
    pygame.display.update()
    clock.tick(60)

pygame.quit()



