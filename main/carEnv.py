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
    for i in range(count):
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
    return np.inf

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
        pygame.init()
        self.width = 1400
        self.height = 830
        self.screen = None
        # Define action and observation space
        pygame.display.set_caption("Car")
        self.clock = pygame.time.Clock()
        self.score_font = pygame.font.Font(None, 50)
        pygame.display.set_mode((1, 1)) 


        #Track info
        self.track_surface = pygame.image.load("pics/racetrack.png").convert_alpha()
        self.track_surface = pygame.transform.scale_by(self.track_surface, 2)
        self.track_rect = self.track_surface.get_rect(center = (self.width/2, self.height/2))
        self.track_mask = pygame.mask.from_surface(self.track_surface)

        #Car info
        self.car_surface  = pygame.image.load("pics/Car_top.png").convert_alpha()
        self.car_surface = pygame.transform.scale_by(self.car_surface, 0.04)

        self.MAX_SPPED = 8
        self.RAY_COUNT = 8
        self.car_surface_orig = self.car_surface
        self.car_surface_orig_rotated = pygame.transform.rotate(self.car_surface_orig, 180)

        #Reward gates
        self.gate_left = reward_gate((205,400), (360, 400))
        self.gate_right = reward_gate((1037,400), (1192, 400))
        self.gate_up = reward_gate((self.width/2, 100), (self.width/2, 205))
        self.gate_down = reward_gate((self.width/2, 625), (self.width/2, 730))

        self.reward_gates = [self.gate_left, self.gate_up, self.gate_right, self.gate_down]

        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(5)
        # Example for using image as input (channel-first; channel-last also works):
        obs_dim = 4 + self.RAY_COUNT
        self.observation_space = spaces.Box(low = -np.inf, high = np.inf, shape=(obs_dim, ), dtype = np.float32)

    def step(self, action):
        terminated = False
        reward = 0
        #Conditionals
        self.car_rect.left %= self.width
        self.car_rect.bottom %= self.height

        #Collison check and restart
        car_mask = pygame.mask.from_surface(self.car_surface)
        if not self.track_mask.overlap(car_mask, (self.car_rect.left - self.track_rect.left, self.car_rect.top - self.track_rect.top)):
            terminated = True
            reward -= 10


        #Casting rays
        self.dists_to_edge, self.rays = cast_all_rays(self.track_mask, self.car_rect, self.track_rect, self.degrees, self.RAY_COUNT)

        if (self.dists_to_edge[0] == 0 ) and len(set(self.dists_to_edge)) == 1: 
            terminated = True
            reward = -10

        #Drawing reward gates and calculating distance
        if (all_crossed(self.reward_gates)):
            reset_gates(self.reward_gates)
            self.curr_gate = 0
        for gate in self.reward_gates:
            if self.car_rect.clipline(gate.start, gate.end) and self.reward_gates[self.curr_gate] == gate:
                gate.crossed = True
                self.curr_gate +=1
                reward += 10.0
        
        self.dist_to_gate = dist_to_reward_gate(self.reward_gates, self.car_rect)

        # progress reward
        reward -= math.sqrt(self.dist_to_gate) * 0.01

        #Handle player input

        if action == 1 :
            self.speed += 1
            self.speed = min(self.MAX_SPPED, self.speed)
        elif action == 2:
            self.speed -= 1
            self.speed = max(-self.MAX_SPPED, self.speed)
        else :
            factor = -1 if self.speed < 0 else 1
            s = abs(self.speed)
            s -= 0.4 * (s / 10)
            self.speed = s * factor

        if action == 3 or action == 4:
            orig_x = self.car_rect.centerx
            orig_y = self.car_rect.centery

            if action == 4 :
                self.degrees -= 2
            else : 
                self.degrees += 2
            self.degrees %= 360

            self.car_surface  = pygame.transform.rotate(self.car_surface_orig, self.degrees)
            self.car_rect = self.car_surface.get_rect(center = (orig_x , orig_y))

        self.car_rect.top -= self.speed * math.sin(self.degrees * math.pi / 180)
        self.car_rect.left += self.speed * math.cos(self.degrees * math.pi / 180)

        observation = np.array([self.dist_to_gate, self.curr_gate, self.degrees, self.speed] + self.dists_to_edge, 
                               dtype=np.float32)
        return observation, reward, terminated, False, {}

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.done = False

        
        self.car_rect = self.car_surface.get_rect(midtop = (600, 650))

        #Car info original
        self.degrees = 180
        self.speed = 0
        
        #Making Reward Gates (side_length = 155)
        self.curr_gate = 0
        reset_gates(self.reward_gates)

        #Distances
        self.dists_to_edge = [-1] * self.RAY_COUNT
        self.dist_to_gate = -1

        self.car_surface = self.car_surface_orig_rotated

        observation = np.array([self.dist_to_gate, self.curr_gate, self.degrees, self.speed] + self.dists_to_edge, 
                               dtype=np.float32)

        return observation, {}
    
    def render(self):
        if self.screen is None:
            self.screen = pygame.display.set_mode((self.width, self.height))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.track_surface, self.track_rect)

        for i in range(0, self.RAY_COUNT): 
            pygame.draw.line(self.screen, "Blue", 
                            (self.car_rect.centerx, self.car_rect.centery), 
                            (self.rays[i][0] + self.track_rect.left, self.rays[i][1] + self.track_rect.top))
        for gate in self.reward_gates:
            pygame.draw.line(self.screen, "Yellow", gate.start, gate.end)

        reward_dist_surface = self.score_font.render(f"{self.dist_to_gate}", True, "Pink")
        curr_gate_surface = self.score_font.render(f"{self.curr_gate}", True, "Pink")

        self.screen.blit(reward_dist_surface, (300,0))
        self.screen.blit(curr_gate_surface, (500,0))
        self.screen.blit(self.car_surface, self.car_rect)

        pygame.display.update()
        self.clock.tick(60)
