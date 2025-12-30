import gymnasium as gym
import numpy as np
from gymnasium import spaces
import pygame
import math


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


class CarEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self):
        super(CarEnv, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(4)
        # Example for using image as input (channel-first; channel-last also works):
        pygame.init()
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(N_CHANNELS, HEIGHT, WIDTH), dtype=np.uint8)

    def step(self, action):
        ...
        return observation, reward, terminated, truncated, info

    def reset(self):
        self.done = False
        self.width = 1400
        self.height = 830
        self.screen = pygame.display.set_mode((self.width, self.height), flags=pygame.SCALED, vsync=1) #Screen tearing fix

        pygame.display.set_caption("Car")
        self.clock = pygame.time.Clock()
        self.running = True

        self.score_font = pygame.font.Font(None, 50)

        #Track info
        track_surface = pygame.image.load("pics/racetrack.png").convert_alpha()
        track_surface = pygame.transform.scale_by(track_surface, 2)
        track_rect = track_surface.get_rect(center = (self.width/2, self.height/2))
        track_mask = pygame.mask.from_surface(track_surface)
        mask_image = track_mask.to_surface()

        #Car info
        self.car_surface  = pygame.image.load("pics/Car_top.png").convert_alpha()
        self.car_surface = pygame.transform.scale_by(self.car_surface, 0.04)
        self.car_rect = self.car_surface.get_rect(midtop = (600, 650))

        #Car info original
        self.car_surface_orig = self.car_surface
        self.degrees = 180
        self.speed = 0
        self.MAX_SPPED = 8
        self.RAY_COUNT = 8

        #Making Reward Gates (side_length = 155)
        self.gate_left = reward_gate((205,400), (360, 400))
        self.gate_right = reward_gate((1037,400), (1192, 400))
        self.gate_up = reward_gate((self.width/2, 100), (self.width/2, 205))
        self.gate_down = reward_gate((self.width/2, 625), (self.width/2, 730))

        self.reward_gates = [self.gate_left, self.gate_up, self.gate_right, self.gate_down]
        self.curr_gate = 0

        #Distances
        self.dists_to_edge = [-1] * self.RAY_COUNT
        self.dist_to_gate = -1

        return self.observation
