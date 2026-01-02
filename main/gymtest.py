
import pygame
import carEnv 

pygame.init()
env = carEnv.CarEnv()

# It will check your custom environment and output additional warnings if needed
episodes = 50
for episode in range(episodes):
	done = False
	obs = env.reset()
	while True:#not done:
		random_action = env.action_space.sample()
		print("action",random_action)
		obs, reward, done, _, _ = env.step(random_action)
		if (done) :
			env.reset()
		env.render()
		print('reward',reward)
		


