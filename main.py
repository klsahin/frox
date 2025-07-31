import pygame
from classes import *
import random
import time


arduino = False  # Set to True to use Arduino, False to use keyboard

if arduino:
    import serial
    import serial.tools.list_ports
    import csv

    # Identify the correct port
    ports = serial.tools.list_ports.comports()
    for port in ports: print(port.device, port.name)

    # Create CSV file
    f = open("data.csv","w",newline='')
    f.truncate()

    # Open the serial com
    serialCom = serial.Serial('/dev/cu.usbserial-110',115200)

    # Toggle DTR to reset the Arduino
    serialCom.dtr = False
    time.sleep(1)
    serialCom.reset_input_buffer()
    serialCom.dtr = True

    # How many data points to record (if stopping)
    kmax = 150
    # Loop through and collect data as it is available
    dataVariable = 0

screenWidth = 700
screenHeight = 800

pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))
running = True

# Load Object
leaves = Leaves(screenWidth, screenHeight)
tree = Tree(screenWidth,screenHeight)
tree.load_image()
frog = Frog(300, 450, 200, 290, 1)  
frog.load_image()

# Lane positions for fruit (divide crawlable path into 3 lanes)
lane_x = [160 + 15, 300 + 15, 440 + 15]  # Shift all lanes 15 pixels to the right
fruit_clump = [0, -40, 40]
obstacle_clump = [0, -75, 75]
object_width = 75
object_height = 75
object_spawn_y = -80  # Start just above the screen
fruits = []
num_objects = 5
vertical_spacing = screenHeight // num_objects


# Only one fruit at a time, randomly in one of the three lanes
active_objects = []

def spawn_single_object():
    objectsToAdd = []
    objectList = ["Fruit"] * 3 + ["Obstacle"] * 1
    object = random.choice(objectList)
    lane = random.choice([0, 1, 2])
    if object == "Fruit":
        if random.random() < 0.60: 
            num = 1   # 60% chance of 1 fruit
        elif random.random() < 0.80:
            num = 2   # 20 % chance of 2 fruits
        else:
            num = 3   # 20 % chance of 3 fruits
        
        fruit_type = random.randint(1, 3)
        for i in range(num):   
            objectsToAdd.append(Fruit(lane_x[lane] + fruit_clump[i], object_spawn_y, object_width, object_height, fruit_type))
    else:
        if objectsOnScreen[-1] == Obstacle: # less chance of many obstacles if last object was an obstacle
            chance = 0.80
        else:
            chance = 0.40

        if random.random() < chance: 
            num = 1
        else:
            num = 3        
        
        for i in range(num):
            objectsToAdd.append(Obstacle(lane_x[lane] + obstacle_clump[i], object_spawn_y, object_width, object_height))

    return objectsToAdd

def spawn_initial_objects(numObjects):
    objectsToAdd = []
    for i in range(1, numObjects + 1):
        objectList = ["Fruit"] * 3 + ["Obstacle"] * 1
        object = random.choice(objectList)
        lane = random.choice([0, 1, 2])
        if object == "Fruit":
            fruit_type = random.randint(1, 3)
            objectsToAdd.append(Fruit(lane_x[lane], object_spawn_y + i * vertical_spacing, object_width, object_height, fruit_type))
        else:
            objectsToAdd.append(Obstacle(lane_x[lane], object_spawn_y + i * vertical_spacing, object_width, object_height))
    return objectsToAdd



def draw_objects():
    leaves.draw(screen)
    tree.draw(screen)
    # frog drawing is now handled in frog.update()

prev_input = (False, False)
start = True
score = 0
objectsOnScreen = []
#objectsOnScreen.append(spawn_single_object()) #initial object
objectsOnScreen.extend(spawn_initial_objects(2))

font_path = 'assets/SuperBubble.ttf'
try:
    font = pygame.font.Font(font_path, 64)  # Adjust size as needed
except FileNotFoundError:
    font = pygame.font.SysFont(None, 64)
font_color = (187, 220, 5)  # #bbdc05 green

speed = 11

floating_texts = []  # List to store active floating texts

jump_button_held = False
jump_press_time = None
jump_release_time = None
jump_pending = False
jump_duration = 0
max_jump_time = 5.0  # seconds for full jump

# Add this variable to track space bar state for keyboard mode
space_was_pressed = False

direction_list = []

def collisionDetection(objectsOnScreen):
    if not objectsOnScreen or frog.in_air:
        return None

    frog_rect = frog.get_hitbox()

    for object in objectsOnScreen:
        object_rect = pygame.Rect(
            object.x - object.width // 2,
            object.y - object.height // 2,
            object.width,
            object.height
        )

        if frog_rect.colliderect(object_rect):
            return object

    return None  # No collisions found


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if score > 0:
        screen_speed = int(speed * (1 + score/100))
    else:
        screen_speed = speed

    # Make background and objects scroll faster when frog is in the air
    if frog.in_air:
        scroll_speed = screen_speed * 2.5
    else:
        scroll_speed = screen_speed

    try:
        if arduino:
            serialCom.reset_input_buffer()  # Clear the input buffer
            s_bytes = serialCom.readline()
            decoded_bytes = s_bytes.decode("utf-8").strip('\r\n')
            #print(f"decoded bytes: {decoded_bytes}")
            leftData, rightData = decoded_bytes.split(',')
            print(f"decoded bytes:         {leftData}, {rightData}")
            leftData = float(leftData)
            rightData = float(rightData)
            leftTurn = rightTurn  = False
            threshold = 500
            if leftData > threshold: leftTurn = True
            if rightData > threshold: rightTurn = True

            averaged_direction = (False, False)

            # when NOT both (turning):
            if not (leftTurn and rightTurn):
                # Record direction: -1 for left, 1 for right, 0 for straight
                if leftTurn and not rightTurn:
                    frog.set_facing(6, False, False)
                    direction_list.append(-1)
                elif rightTurn and not leftTurn:
                    frog.set_facing(-6, False, False)
                    direction_list.append(1)
                else:
                    direction_list.append(0)

                averaged_direction = (leftTurn, rightTurn)

            # When both are pressed (jump initiation)

            if (leftTurn and rightTurn) and not jump_button_held:
                jump_button_held = True
                jump_press_time = time.time()

                # Compute average direction
                if direction_list:
                    avg = sum(direction_list) / len(direction_list)
                    if avg < -0.33:
                        averaged_direction = (True, False)   # left
                    elif avg > 0.33:
                        averaged_direction = (False, True)   # right
                    else:
                        averaged_direction = (leftTurn, rightTurn)  # straight
                else:
                    averaged_direction = (leftTurn, rightTurn)      # default to straight
                print(f"averaged_direction: {averaged_direction}")
                direction_list = []

            # When jump released
            if not leftTurn and not rightTurn and jump_button_held:
                jump_button_held = False
                jump_release_time = time.time()
                if jump_press_time is not None:
                    raw_duration = jump_release_time - jump_press_time
                    print(f"Raw duration: {raw_duration:.2f} seconds")
                    jump_duration = raw_duration
                    if jump_duration > max_jump_time:
                        jump_duration = max_jump_time
                    print(f"Capped jump_duration: {jump_duration:.2f} seconds")
                else:
                    jump_duration = 0
                jump_pending = True

        else:
            keys = pygame.key.get_pressed()
            leftTurn = keys[pygame.K_a]
            rightTurn = keys[pygame.K_d]
            averaged_direction = (leftTurn, rightTurn)

            # when turning:
            if leftTurn and not rightTurn:
                frog.set_facing(6, False, False)
            elif rightTurn and not leftTurn:
                frog.set_facing(-6, False, False)

            # --- Improved jump logic for keyboard ---
            space_pressed = keys[pygame.K_SPACE] or keys[pygame.K_w]
            if space_pressed and not space_was_pressed:
                # Space just pressed
                jump_button_held = True
                jump_press_time = time.time()
            elif not space_pressed and space_was_pressed and jump_button_held:
                # Space just released
                jump_button_held = False
                jump_release_time = time.time()
                if jump_press_time is not None:
                    raw_duration = jump_release_time - jump_press_time
                    print(f"Raw duration: {raw_duration:.2f} seconds")
                    jump_duration = raw_duration
                    if jump_duration > max_jump_time:
                        jump_duration = max_jump_time
                    print(f"Capped jump_duration: {jump_duration:.2f} seconds")
                else:
                    jump_duration = 0
                jump_pending = True
            # Update space_was_pressed for next frame
            space_was_pressed = space_pressed

        # New frog control logic:
        # If only one leg is pressed, set facing (rotate, no jump)
        if averaged_direction[0] and not averaged_direction[1]:
            frog.set_facing(0, *averaged_direction)  # Left turn
        elif averaged_direction[1] and not averaged_direction[0]:
            frog.set_facing(0, *averaged_direction)  # Right turn
        #prev_input = averaged_direction

        leaves.draw(screen)
        tree.scroll(scroll_speed, frog.in_air)
        tree.draw(screen)
        frog.draw_shadow(screen)
        score_text = font.render(str(score), True, font_color)
        screen.blit(score_text, (20, 20))

        # Move and draw the single fruit
        if objectsOnScreen != []:
            for obj in objectsOnScreen:
                if frog.in_air:
                    obj.y += scroll_speed  # Only move down when frog is in the air
                obj.position[1] = obj.y
                obj.load_image(screen)
            if objectsOnScreen[-1].y > vertical_spacing:
                objectsOnScreen.extend(spawn_single_object())

        # Only trigger jump if pending
        if jump_pending:
            frog.start_jump(jump_duration)
            jump_pending = False
            jump_duration = 0

        # Draw the frog on top of all objects
        frog.update(screen, leaves, tree)

        # Draw and update floating texts
        for text in floating_texts[:]:
            text.update()
            text.draw(screen)
            if text.is_dead():
                floating_texts.remove(text)

        pygame.display.flip()

        # Collision detection
        collided = collisionDetection(objectsOnScreen)
        if collided is not None:
            # Check if the collided object is a fruit
            if isinstance(collided, Fruit):
                score += 5
                if collided in objectsOnScreen: objectsOnScreen.remove(collided)
                # Add floating +5 text
                floating_texts.append(FloatingText(
                    collided.x + collided.width // 2,
                    collided.y - 20,
                    "+5",
                    (187, 220, 5),  # green
                    font_path,
                    60,
                    12
                ))
            elif isinstance(collided, Obstacle):
                score -= 10
                if collided in objectsOnScreen: objectsOnScreen.remove(collided)
                # Add floating -10 text
                floating_texts.append(FloatingText(
                    collided.x + collided.width // 2,
                    collided.y - 20,
                    "-10",
                    (220, 30, 30),  # red
                    font_path,
                    60,
                    12
                ))
            # If you add obstacles, handle them here

    except Exception as e:
        print("Error:", e)
        farLeftTurn = topLeftTurn = topRightTurn = farRightTurn = False

if arduino:
    f.close()  # Close the CSV file
pygame.quit()
