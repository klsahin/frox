import pygame
from classes import *
import random
import time

arduino = True  # Set to True to use Arduino, False to use keyboard

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
frog = Frog(300, 400, 260, 390, 1)  # Example parameters for Frog
frog.load_image()

# Lane positions for fruit (divide crawlable path into 3 lanes)
lane_x = [160 + 15, 300 + 15, 440 + 15]  # Shift all lanes 15 pixels to the right
object_width = 75
object_height = 75
object_spawn_y = -80  # Start just above the screen
fruits = []
num_objects = 5
vertical_spacing = screenHeight // num_objects

# Only one fruit at a time, randomly in one of the three lanes
active_objects = []

def spawn_single_object():
    objectList = ["Fruit"] * 3 + ["Obstacle"] * 1
    object = random.choice(objectList)
    lane = random.choice([0, 1, 2])
    if object == "Fruit":
        fruit_type = random.randint(1, 3)
        return Fruit(lane_x[lane], object_spawn_y, object_width, object_height, fruit_type)
    else:
        return Obstacle(lane_x[lane], object_spawn_y, object_width, object_height)


#active_objects.append(spawn_single_object())

def draw_objects():
    leaves.draw(screen)
    tree.draw(screen)
    # frog drawing is now handled in frog.update()

prev_input = (False, False, False, False)
start = True
score = 0
objectsOnScreen = []
objectsOnScreen.append(spawn_single_object()) #initial object

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

def collisionDetection(objectsOnScreen):
    if objectsOnScreen == []: return None
    if frog.in_air:
        return None
    [lx, ly] = frog.position
    ygap = 50 # offset for frog image (top)
    xgap = 25
    bottom_gap = 350 # reduce hitbox from the bottom by 40 pixels
    for object in (objectsOnScreen):
        x_overlap = (lx + xgap < object.x + object.width and lx + frog.width  - xgap > object.x)
        y_overlap = (ly + ygap < object.y + object.height and ly + frog.height - bottom_gap > object.y)
        if x_overlap and y_overlap:
            return object

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if score > 0:
        screen_speed = int(speed * (1 + score/100))
    else:
        screen_speed = speed

    try:
        if arduino:
            serialCom.reset_input_buffer()  # Clear the input buffer
            s_bytes = serialCom.readline()
            decoded_bytes = s_bytes.decode("utf-8").strip('\r\n')
            print(f"decoded bytes: {decoded_bytes}")
            rightData, leftData = decoded_bytes.split(',')
            leftData = float(leftData)
            rightData = float(rightData)
            leftTurn = rightTurn  = False
            threshold = 1000
            if leftData > threshold: leftTurn = True
            if rightData > threshold: right = True
            if leftTurn and rightTurn and not jump_button_held: 
                jump_button_held = True
                jump_press_time = time.time()
            if not(leftTurn and rightTurn) and jump_button_held:
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
            input_tuple = (leftData, rightData)
        else:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not jump_button_held:
                        jump_button_held = True
                        jump_press_time = time.time()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE and jump_button_held:
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
            keys = pygame.key.get_pressed()
            input_tuple = (keys[pygame.K_LEFT], keys[pygame.K_RIGHT])

        if input_tuple != (False, False):
            start = False
        if input_tuple != prev_input or start == True:
            frog.set_direction(*input_tuple)
            prev_input = input_tuple

        leaves.draw(screen)
        tree.scroll(screen_speed, frog.in_air)
        tree.draw(screen)
        frog.draw_shadow(screen)
        score_text = font.render(str(score), True, font_color)
        screen.blit(score_text, (20, 20))

        # Move and draw the single fruit
        if objectsOnScreen != []:
            for obj in objectsOnScreen:
                obj.y += screen_speed  # Move down with the tree scroll speed
                obj.position[1] = obj.y
                obj.load_image(screen)
            if objectsOnScreen[-1].y > vertical_spacing:
                objectsOnScreen.append(spawn_single_object())

        # Only trigger jump if pending
        if jump_pending:
            frog.start_jump(jump_duration)
            frog.set_direction(*input_tuple)
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
