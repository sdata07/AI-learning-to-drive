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
            reward -= 80

        #Casting rays
        self.dists_to_edge, self.rays = cast_all_rays(self.track_mask, self.car_rect, self.track_rect, self.degrees, self.RAY_COUNT)

        if (self.dists_to_edge[0] == 0 ) and len(set(self.dists_to_edge)) == 1: 
            terminated = True