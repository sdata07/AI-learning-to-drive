import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import carEnv 
from stable_baselines3 import PPO

pygame.init()

env = carEnv.CarEnv()
# Load model
model = PPO.load('model/a2c_180000', env=env)

# Run a test
obs = env.reset()[0]
terminated = False
while True:
    action, _ = model.predict(observation=obs, deterministic=False) # Turn on deterministic, so predict always returns the same behavior
    obs, _, terminated, _, _ = env.step(action)
    env.render()
    if terminated:
        env.reset()