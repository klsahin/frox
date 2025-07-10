import pygame
from classes import *
import random

arduino = False  # Set to True to use Arduino, False to use keyboard

if arduino:
    import serial
    import serial.tools.list_ports
    import time
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

def collisionDetection(objectsOnScreen):
    if objectsOnScreen == []: return None
    [lx, ly] = frog.position
    ygap = 50 # offset for frog image
    xgap = 25
    for object in (objectsOnScreen):
        x_overlap = (lx + xgap < object.x + object.width and lx + frog.width  - xgap > object.x)
        y_overlap = (ly + ygap < object.y + object.height and ly + frog.height - ygap> object.y)
        if x_overlap and y_overlap and not isJumping:
            return object
        
isJumping = False

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
            farLeftData = []
            topLeftData = []
            topRightData = []
            farRightData = []
            count = 0
            for data in decoded_bytes.split(","):
                if count < 2:
                    farLeftData.append(data)
                elif count < 4:
                    topLeftData.append(data)
                elif count < 6:
                    topRightData.append(data)
                elif count < 8:
                    farRightData.append(data)
                count += 1
            farLeftTurn = False
            topLeftTurn = False
            topRightTurn = False
            farRightTurn = False
            threshold = 2000
            if int(farLeftData[0]) > threshold and int(farLeftData[1]) > threshold:
                farLeftTurn = True
            if int(topLeftData[0]) > 3000 and int(topLeftData[1]) > threshold:
                topLeftTurn = True
            if int(topRightData[0]) > threshold and int(topRightData[1]) > threshold:
                topRightTurn = True
            if int(farRightData[0]) > threshold and int(farRightData[1]) > threshold:
                farRightTurn = True
            input_tuple = (farLeftTurn, topLeftTurn, topRightTurn, farRightTurn)
        else:
            keys = pygame.key.get_pressed()
            input_tuple = (
                keys[pygame.K_a] or keys[pygame.K_h],  # farLeft
                keys[pygame.K_w] or keys[pygame.K_u],  # topLeft
                keys[pygame.K_s] or keys[pygame.K_i],  # topRight
                keys[pygame.K_d] or keys[pygame.K_l],  # farRight
            )
            isJumping = keys[pygame.K_SPACE]
            
            

        if input_tuple != (False, False, False, False):
            start = False
        if input_tuple != prev_input or start == True:
            frog.set_direction(*input_tuple)
            prev_input = input_tuple
        leaves.draw(screen)
        tree.scroll(screen_speed, isJumping)
        tree.draw(screen)
        score_text = font.render(str(score), True, font_color)
        screen.blit(score_text, (20, 20))
        isJumping = frog.update(screen, leaves, tree, isJumping)

        # Move and draw the single fruit
        #objectsOnScreen = []
        if objectsOnScreen != []:
            for obj in objectsOnScreen:
                obj.y += screen_speed  # Move down with the tree scroll speed
                obj.position[1] = obj.y
                obj.load_image(screen)
                #objectsOnScreen.append(obj)
                # if obj.y > screenHeight:
                #     objectsOnScreen.append(spawn_single_object())
            if objectsOnScreen[-1].y > vertical_spacing:
                    objectsOnScreen.append(spawn_single_object())

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
