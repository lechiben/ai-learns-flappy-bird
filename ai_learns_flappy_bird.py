# Uncomment these lines to install required packages
#pip install pygame
#pip install neat-python

# Import necessary libraries
import pygame
import neat
import time
import os
import random

# Set window dimensions
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Load and scale images for the game
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

# Bird class definition
class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        # Initialize bird properties
        self.x = x
        self.y = y 
        self.tilt = 0 
        self.tick_count = 0
        self.vel = 0 
        self.height = self.y
        self.img_count = 0 
        self.img = self.IMGS[0]

    def jump(self):
        # Set jump velocity and reset tick count
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        # Calculate displacement and update bird position
        self.tick_count += 1
        d = self.vel * self.tick_count + 1.5*self.tick_count**2

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2
        
        self.y = self.y + d

        # Update bird tilt
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        # Animate bird and draw it on the window
        self.img_count += 1

        # Choose image based on animation time
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[0]
            self.img_count = 0

        # Set image for steep fall
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
        
        # Rotate image around its center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        # Get collision mask for the bird
        return pygame.mask.from_surface(self.img)

# Pipe class definition
class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        # Initialize pipe properties
        self.x = x 
        self.height = 0
        self.gap = 100

        self.top = 0 
        self.bottom = 0 
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False 
        self.set_height()

    def set_height(self):
        # Set random height for the pipe
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height = self.GAP

    def move(self):
        # Move the pipe
        self.x -= self.VEL

    def draw(self, win):
        # Draw the pipe on the window
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        # Check for collision with bird
        bird_mask = bird.get_mask()
        top_mask = pygame.mas.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mas.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        return False
    
# Base class definition
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        # Initialize base properties
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        # Move the base
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # Reset base positions for continuous scrolling
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        # Draw the base on the window
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, bird, pipes, base):
    # Draw game elements on the window
    win.blit(BG_IMG, (0,0))   
    for pipe in pipes:
        pipe.draw(win)

    bird.draw(win)
    pygame.display.update()

def main():
    # Main game loop
    bird = Bird(230,350)
    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    run = True

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        # Uncomment to enable bird movement
        #bird.move()

        draw_window(win, bird, pipes, base)

    pygame.quit()
    quit()

# Run the main function
main()