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



class Frog:
    def __init__(self, x, y, width, height, index):
        self.width = width
        self.height = height
        # Treat position as the center
        self.position = [x + width // 2, y + height // 2]
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
        self.in_air = False
        self.jumping = False
        self.jump_duration = 0
        self.jump_frames = 0 # Initialize jump_frames
        # New for facing logic
        self.facing_angle = 0  # 0 = forward, -60 = left, 60 = right
        self.last_facing = 0   # Track last facing for jump direction
        self.facing_set = False  # Track if a single leg was pressed before jump

    def load_image(self):
        self.image = pygame.image.load(self.path).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)
        self.image = pygame.transform.flip(self.image, self.flip, False)
        # Use center-based position
        orig_center = (int(self.position[0]), int(self.position[1]))
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=orig_center)

    def set_facing(self, angle, left, right):
        """
        Set frog's facing direction based on single leg input.
        Only rotates, does not jump.
        """
        # Define step angle (now 45 deg)
        
        max_angle = 75
        
        # Increment angle by 6 degrees (3 steps of 2)
        for i in range(3):
            if angle != 0:  
                self.angle += angle // 3
                if self.angle > max_angle:
                    self.angle = max_angle
                elif self.angle < -max_angle:
                    self.angle = -max_angle

            # Cycle through frames: 0 -> 1 -> 0
            if i == 0:
                self.frame = 0
            elif i == 1:
                self.frame = 1
            else:  # i == 2
                self.frame = 0
                
            self.path = f'assets/frog{self.frame}.png'
            self.load_image()

        self.facing_angle = self.angle
        if (left and not right) or (right and not left):
            self.facing_set = True
        else:
            self.facing_set = False
        

    def start_jump(self, jump_duration):
        print(f"Jump triggered! Duration: {jump_duration:.2f} seconds")
        self.jumping = True
        self.jump_duration = jump_duration
        self.frame = 0
        self.in_air = True
        # Determine jump animation length
        if jump_duration <= 1.0:
            self.jump_frames = 3  # frog0 to frog2
        elif jump_duration <= 3.0:
            self.jump_frames = 5  # frog0 to frog4
        else:
            self.jump_frames = 7  # frog0 to frog6 (full jump)

        # Set jump direction based on facing
        min_scale = 0.5
        max_scale = 1.0
        min_time = 1.0
        max_time = 5.0
        t = max(self.jump_duration, 0)
        if t <= min_time:
            scale = min_scale
        elif t >= max_time:
            scale = max_scale
        else:
            scale = min_scale + (max_scale - min_scale) * ((t - min_time) / (max_time - min_time))
        max_dx = 80
        max_dy = 10

        # Use the current facing angle to determine direction
        if self.facing_set:
            if self.facing_angle > 0:  # left
                self.dx = -max_dx * scale
                self.angle = self.facing_angle
            elif self.facing_angle < 0:  # right
                self.dx = max_dx * scale
                self.angle = self.facing_angle
            else:  # forward
                self.dx = 0
                self.angle = 0
        else:
            self.dx = 0
            self.angle = 0
        self.dy = max_dy * scale
        self.animating = True
        self.load_image()

    # def set_direction(self, left, right):
    #     # Use jump_duration to scale jump distance
    #     min_scale = 0.5
    #     max_scale = 1.0
    #     min_time = 1.0
    #     max_time = 5.0
    #     t = max(self.jump_duration, 0)
    #     if t <= min_time:
    #         scale = min_scale
    #     elif t >= max_time:
    #         scale = max_scale
    #     else:
    #         scale = min_scale + (max_scale - min_scale) * ((t - min_time) / (max_time - min_time))
    #     max_dx = 100
    #     max_dy = 10
    #     max_angle = 60
    #     if left and not right:
    #         self.dx = -max_dx * scale
    #         self.dy = 5 * scale
    #         self.angle = max_angle * scale
    #         self.animating = True
    #     elif right and not left:
    #         self.dx = max_dx * scale
    #         self.dy = 5 * scale
    #         self.angle = -max_angle * scale  #
    #         self.animating = True
    #     elif not left and not right: # straight and not jumping
    #         self.dx = 0
    #         self.dy = max_dy * scale
    #         self.angle = 0
    #         self.animating = True  # Always animate when straight
    def get_hitbox(self):
        angle = self.facing_angle  # This is -45, 0, or 45

        # Shrinking effect: more angle → smaller width
        shrink_factor = abs(angle) / 45  # 0 to 1
        xgap = 50 + 20 * shrink_factor   # 30 → 50
        ygap = 35
        bottom_gap = 225

        # Horizontal shift: frog tilts left → hitbox nudges left
        offset_x = -45 * (angle / 45)  # -15 if left, 0 if center, +15 if right

        center_x = self.position[0] + offset_x
        center_y = self.position[1]

        left = center_x - self.width // 2 + xgap
        right = center_x + self.width // 2 - xgap
        top = center_y - self.height // 2 + ygap
        bottom = center_y + self.height // 2 - bottom_gap

        return pygame.Rect(left, top, right - left, bottom - top)



    def draw_shadow(self, screen):
        show_shadow = self.in_air and self.frame >= 2
        if show_shadow:
            shadow_img = pygame.image.load('assets/shadow.png').convert_alpha()
            shadow_width = int(self.width)
            shadow_height = int(self.height)
            shadow_img = pygame.transform.scale(shadow_img, (shadow_width, shadow_height))
            # Rotate the shadow by the frog's angle
            shadow_img = pygame.transform.rotate(shadow_img, self.angle)
            # Place the shadow's midbottom at the frog's bottom center
            shadow_rect = shadow_img.get_rect()
            anchor_x = int(self.position[0])
            anchor_y = int(self.position[1] + self.height // 2)
            shadow_rect.midbottom = (anchor_x, anchor_y)
            # Draw debug circle at anchor point
            # pygame.draw.circle(screen, (255,0,0), (anchor_x, anchor_y), 10)
            screen.blit(shadow_img, shadow_rect.topleft)

    def update(self, screen, leaves, tree):
        now = pygame.time.get_ticks()
        if self.jumping and now - self.last_update > self.animation_speed:
            self.last_update = now
            # Clamp movement to screen bounds (center-based)
            if (self.position[0] - self.width // 2 < 40 and self.dx < 0) or (self.position[0] + self.width // 2 > 700 and self.dx > 0):
                self.dx = 0
                self.dy = 5
                self.flip = False
            self.path = f'assets/frog{self.frame}.png'
            self.position[0] += self.dx
            # self.position[1] += self.dy  # Uncomment if vertical movement is needed
            self.load_image()
            self.frame += 1
            if self.frame >= self.jump_frames:
                self.frame = 0
                self.jumping = False
                self.in_air = False
                # Reset facing to forward after jump
                self.facing_angle = 0
                self.last_facing = 0
                self.facing_set = False
                self.angle = 0
                self.load_image()
            print("jumping")
        elif not self.jumping:
            self.frame = 0
            self.path = 'assets/frog0.png'
            self.load_image()
            self.in_air = False
            #print("not jumping, reset")
        screen.blit(self.image, self.rect.topleft)
        # DEBUG: Draw hitbox rectangle
        debug_hitbox = self.get_hitbox()
        #pygame.draw.rect(screen, (255, 0, 0), self.get_hitbox(), 2)











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
