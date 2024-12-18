# Uncomment these lines to install required packages
#pip install pygame
#pip install neat-python

# Import necessary libraries
import pygame
import neat
import time
import os
import random

# Initialize pygame
pygame.init()
pygame.font.init()

# Set window dimensions
WIN_WIDTH = 500
WIN_HEIGHT = 800
GEN = 0 
# Load and scale images for the game
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

# Bird class definition
class Bird:
     # Constants for bird behavior and animation
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # Maximum tilt of the bird
    ROT_VEL = 20  # Rotation speed when tilting down
    ANIMATION_TIME = 5  # Time each bird frame is displayed

    def __init__(self, x, y):
        # Initialize bird properties
        self.x = x
        self.y = y 
        self.tilt = 0 # Bird's angle of rotation
        self.tick_count = 0  # Time since last jump
        self.vel = 0  # Vertical velocity
        self.height = self.y  # Height at the last jump
        self.img_count = 0 # Current animation frame count
        self.img = self.IMGS[0] # Current image for rendering

    def jump(self):
        # Set jump velocity and reset tick count
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        # Calculate displacement and update bird position
        self.tick_count += 1
        d = self.vel * self.tick_count + 1.5*self.tick_count**2

        # Limit downward displacement to avoid excessive falling speed
        if d >= 16:
            d = 16

        if d < 0:
            d -= 2 # Extra upward boost when moving upwards

        
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
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
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
        self.bottom = self.height + self.GAP

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
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

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

def draw_window(win, birds, pipes, base, score, gen):
    # Draw game elements on the window
    win.blit(BG_IMG, (0,0))   
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255))
    win.blit(text, (10, 10))

    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    # Main game loop
    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0 

    run = True 

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.time.delay(1500)
                pygame.quit()

        pipe_ind = 0 
        
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x  + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1     

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()      
    
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x in reversed(range(len(birds))):
                if pipes[0].collide(birds[x]):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            pipe.move()
       
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y < 0 or bird.y + bird.img.get_height() >= 730:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()

        draw_window(win, birds, pipes, base, score, GEN)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)