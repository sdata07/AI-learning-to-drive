import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import os
import carEnv 
import shutil

from stable_baselines3 import PPO

model_dir = "model"
log_dir = "logs"



if os.path.exists(model_dir):
     shutil.rmtree(model_dir)
if os.path.exists(log_dir):
    shutil.rmtree(log_dir)

os.makedirs(model_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

env = carEnv.CarEnv()

model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=log_dir)

# This loop will keep training until you stop it with Ctr-C.
# Start another cmd prompt and launch Tensorboard: tensorboard --logdir logs
# Once Tensorboard is loaded, it will print a URL. Follow the URL to see the status of the training.
# Stop the training when you're satisfied with the status.
TIMESTEPS = 1000
iters = 0
while True:
    iters += 1

    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False) # train
    model.save(f"{model_dir}/a2c_{TIMESTEPS*iters}") # Save a trained model every TIMESTEPS
    env.render()