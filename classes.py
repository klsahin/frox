import pygame
import random

class Leaves:
    def __init__(self, width, height, path = "assets/leaves.png"):
        self.position = [0,0]
        self.size = [width, height]
        self.imagePath = path

    def draw(self, screen):
        self.image = pygame.image.load(self.imagePath).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)
        screen.blit(self.image, self.position)

class Tree:
    def __init__(self, width, height, path1 = "assets/tree.png"):
        self.position = [0, 0]
        self.size = [width, height]
        self.imagePath1 = path1
        self.image1 = None
        self.y_offset = 0

    def load_image(self):
        self.image1 = pygame.image.load(self.imagePath1).convert_alpha()
        self.image1 = pygame.transform.scale(self.image1, self.size)

    def draw(self, screen):
        # Draw the background twice for endless effect using only one image
        w = self.size[1]
        y = self.y_offset % w
        screen.blit(self.image1, (0, y - w))
        screen.blit(self.image1, (0, y))

    def scroll(self, dy, isJumping):
        if isJumping:
            self.y_offset += dy
        else:
            self.y_offset = 0


class Frog:
    def __init__(self, x, y, width, height, index):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.position = [self.x, self.y]
        self.size = [width, height]
        self.index = index
        self.flip = False # left
        self.path = f'assets/frog0.png' #based on numbering system
        self.image = None  # Placeholder for the image, to be loaded later
        # Animation state
        self.frame = 0
        self.frame_count = 6
        self.animating = False
        self.dx = 0
        self.dy = 0
        self.animation_timer = 0
        self.animation_speed = 200  # ms per frame (slower)
        self.last_update = pygame.time.get_ticks()
        
        self.angle = 0

    def load_image(self):
        self.image = pygame.image.load(self.path).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)
        self.image = pygame.transform.flip(self.image, self.flip, False)
        self.image = pygame.transform.rotate(self.image, self.angle)

    def set_direction(self, farLeft, topLeft, topRight, farRight):
        # Set direction and movement based on input, start animation
        # farLeft: A or H key
        # topLeft: W or U key
        # topRight: S or I key
        # farRight: D or L key
        if farLeft and topLeft:
            # Far left: Hold both A (or H) and W (or U)
            self.dx = -30
            self.dy = 5
            self.angle = 60
            self.animating = True
        elif farLeft or topLeft:
            # Top left: Hold A (or H) OR W (or U), but not both
            self.dx = -15
            self.dy = 7
            self.angle = 30
            self.animating = True
        elif topRight and farRight:
            # Far right: Hold both S (or I) and D (or L)
            self.dx = 30
            self.dy = 5
            self.angle = - 60
            self.animating = True
        elif topRight or farRight:
            # Top right: Hold S (or I) OR D (or L), but not both
            self.dx = 15
            self.dy = 7
            self.angle = -30
            self.animating = True
        else:
            self.dx = 0
            self.dy = 10
            self.angle = 0
            self.animating = True  # Always animate when straight

    def update(self, screen, leaves, tree, isJumping):
        # Advance animation if animating
        now = pygame.time.get_ticks()
        if isJumping and now - self.last_update > self.animation_speed:
            self.last_update = now
            # Move Frog
            if (self.position[0] < 40 and self.dx < 0) or (self.position[0] > 450 and self.dx > 0):
                self.dx = 0
                self.dy = 5
                self.flip = False

            '''if not self.jump: # switching btwn 0, 1 frame for regular jumping 
                self.frame %= 2 '''

            self.path = f'assets/frog{self.frame}.png'
            self.position[0] += self.dx
            
            self.load_image()
            self.frame += 1
            if self.frame > self.frame_count:
                self.frame = 0
                self.load_image()
                return False
                # Always keep animating as long as a direction is held
            print("jumping")
        elif not isJumping:
            self.frame = 0
            self.load_image()  
            print("not jumping, reset")
        # Draw Frog
        screen.blit(self.image, self.position)

    
    






class Fruit:
    def __init__(self, x, y, width, height, index = random.randint(1,3)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.position = [self.x, self.y]
        self.size = [width, height]
        self.index = index
        self.image = None
        self.path = f"assets/fruits/f{self.index}.png"

    def load_image(self, screen):
        self.image = pygame.image.load(self.path).convert_alpha()
        if self.size[0] is not None and self.size[1] is not None:
            self.image = pygame.transform.scale(self.image, self.size)
        screen.blit(self.image, self.position)

class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.position = [self.x, self.y]
        self.size = [width, height]
        self.image = None
        self.path = f"assets/bomb.png"

    def load_image(self, screen):
        self.image = pygame.image.load(self.path).convert_alpha()
        if self.size[0] is not None and self.size[1] is not None:
            self.image = pygame.transform.scale(self.image, self.size)
        screen.blit(self.image, self.position)

class FloatingText:
    def __init__(self, x, y, text, color, font_path, font_size=48, fade_speed=8):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.alpha = 255
        self.fade_speed = fade_speed
        self.font = pygame.font.Font(font_path, font_size)
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.y -= 2  # Move up
        self.alpha -= self.fade_speed  # Fade out
        if self.alpha < 0:
            self.alpha = 0
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_dead(self):
        return self.alpha == 0
