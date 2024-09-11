import pygame  # Imports the pygame library for creating games
from pygame.locals import *  # Imports all constants and functions from pygame.locals
import random  # Imports the random library for generating random numbers
import sys  # Imports the sys library for system-specific parameters and functions
import time  # Imports the time library for time-related functions
import json  # Imports the json library for parsing JSON data
from moviepy.editor import *

# Initialize pygame and its mixer module
pygame.init()
pygame.mixer.init()

# Set screen dimensions
screenWidth, screenHeight = 500, 700
size = (screenWidth, screenHeight)
# Create a game window with specified size
game = pygame.display.set_mode(size)
# Set the window title
pygame.display.set_caption("Leap Of Faith")

# Define colors using RGB tuples
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Load background music and sound effects
Bg_Audio = pygame.mixer.Sound('Audio/Background theme.mp3')
# Set the volume for the background music
Bg_Audio.set_volume(0.3)
# Load sound effects for player death and level up
death_sound = pygame.mixer.Sound('Audio/Die sound effect.mp3')
LevelUp_sound = pygame.mixer.Sound('Audio/LevelUp.mp3')

# Set up fonts for displaying text
font = pygame.font.Font(None, 36)

# Define the levels with background images and obstacles
Level_1 = {
    "Background": "Level 1/Space.png",
    "Obstacles": ["Level 1/Asteroid.png"]
}

Level_2 = {
    "Background": "Level 2/Sky.png",
    "Obstacles": ["Level 2/bird_1.png", "Level 2/bird_2.png", "Level 2/bird_3.png"],
    "Sun": "Level 2/sun.png"
}

Level_3 = {
    "Background": "Level 3/Background v1.jpg",
    "Obstacles": ["Level 3/ballon v1.png"]
}

# Load and scale the sun image for Level 2
sun_img = pygame.image.load(Level_2["Sun"]).convert_alpha()
sun_img = pygame.transform.scale(sun_img, (100, 100))

# Load the cloud image for Level 2
cloud_img = pygame.image.load('Level 2/clouds.png').convert_alpha()

# Load and scale the heart image for UI
heart_img = pygame.image.load('UI/heart icon.png').convert_alpha()
heart_img = pygame.transform.scale(heart_img, (30, 30))
# Load the background image for Level 1
background_img = pygame.image.load(Level_1["Background"]).convert_alpha()
# Load and scale the astronaut images for player character
astro_left_img = pygame.image.load("Player/Astro left.png").convert_alpha()
astro_left_img = pygame.transform.scale(astro_left_img, (35, 65))
astro_right_img = pygame.image.load("Player/Astro right.png").convert_alpha()
astro_right_img = pygame.transform.scale(astro_right_img, (35, 65))

# Load and scale the obstacle images for Level 1
obstacle_imgs = [pygame.image.load(obstacle).convert_alpha() for obstacle in Level_1["Obstacles"]]
obstacle_size = (50, 80)
obstacle_imgs = [pygame.transform.scale(obstacle_img, obstacle_size) for obstacle_img in obstacle_imgs]

# Load the menu background image
menu_background_img = pygame.image.load("UI/menu background.png")

# Define the speed variables for the game
speed = 4  # Speed of obstacles
player_speed = 5  # Speed of the player character

obsticle_limit = 1
obsticle_start_limit = 0
obsticle_space = 0

clip = VideoFileClip("UI/Cut Scence.mp4").without_audio()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()  # Initialize the parent class (pygame.sprite.Sprite)
        self.facing = "Left"  # Initial direction the player is facing
        self.health = 3  # Initial health of the player

        self.image = astro_left_img  # Set the initial player image
        self.rect = self.image.get_rect()  # Get the rectangular area of the image
        self.rect.midtop = (screenWidth / 2, 100)  # Set the initial position of the player
        self.blink_timer = 0  # Timer for blinking effect
        self.blinking = False  # Blinking state of the player

    def update(self):
        global player_speed  # Access the global player speed variable
        keys = pygame.key.get_pressed()  # Get the current state of all keyboard keys
        if keys[K_LEFT]:
            self.facing = "Left"  # Update the direction the player is facing
            self.image = astro_left_img  # Set the player image to face left
            self.rect.x -= player_speed  # Move the player left by player_speed
        elif keys[K_RIGHT]:
            self.facing = "Right"  # Update the direction the player is facing
            self.image = astro_right_img  # Set the player image to face right
            self.rect.x += player_speed  # Move the player right by player_speed

        # Ensure the player stays within the screen bounds
        if self.rect.left < 0:
            self.rect.left = 0  # Prevent the player from moving off the left side of the screen
        if self.rect.right > screenWidth:
            self.rect.right = screenWidth  # Prevent the player from moving off the right side of the screen

        # Handle blinking effect
        if self.blinking:
            if pygame.time.get_ticks() - self.blink_timer > 500:
                self.blinking = False  # Stop blinking after 500 milliseconds
                self.image.set_alpha(255)  # Set the image to fully visible
            else:
                # Toggle visibility every 100 milliseconds
                if (pygame.time.get_ticks() // 100) % 2 == 0:
                    self.image.set_alpha(0)  # Make the image invisible
                else:
                    self.image.set_alpha(255)  # Make the image visible
        else:
            self.image.set_alpha(255)  # Ensure the image is fully visible when not blinking

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacles):
        super().__init__()  # Initialize the parent class (pygame.sprite.Sprite)
        global speed, obsticle_limit, obsticle_space, obsticle_start_limit  # Access the global speed variable and obsticle limit variable
        self.image = random.choice(obstacles)  # Randomly select an obstacle image from the list
        self.rect = self.image.get_rect()  # Get the rectangular area of the image
        self.rect.x = random.randint(0, screenWidth - self.rect.width)  # Set a random x position within screen width
        self.rect.y = random.randint(screenHeight, screenHeight + obsticle_space)  # Set a random y position off the bottom of the screen

    def update(self):
        global speed  # Access the global speed variable
        self.rect.y -= speed  # Move the obstacle upward by the speed amount
        if self.rect.bottom < 0:  # If the obstacle moves off the top of the screen
            self.kill()  # Remove the obstacle from all sprite groups

    @staticmethod
    def spawn_obstacles(obstacles, all_sprites, obstacle_spawn_timer, obstacle_spawn_delay, obstacle_group):
        obstacle_spawn_timer += 1  # Increment the obstacle spawn timer
        if obstacle_spawn_timer >= obstacle_spawn_delay:  # If it's time to spawn new obstacles
            num_obstacles = random.randint(obsticle_start_limit, obsticle_limit)  # Randomly determine the number of obstacles to spawn
            for _ in range(num_obstacles):  # Loop to create the determined number of obstacles
                obstacle_instance = Obstacle(obstacles)  # Create a new obstacle instance
                all_sprites.add(obstacle_instance)  # Add the obstacle to the all_sprites group
                obstacle_group.add(obstacle_instance)  # Add the obstacle to the obstacle group
            obstacle_spawn_timer = 0  # Reset the spawn timer
        return obstacle_spawn_timer  # Return the updated spawn timer value

# Button class for creating interactive buttons
class Button:
    def __init__(self, text, pos, size, font, bg_color, text_color):
        self.text = text  # Text to be displayed on the button
        self.pos = pos  # Position of the button (top-left corner)
        self.size = size  # Size of the button (width, height)
        self.font = font  # Font used for the button text
        self.bg_color = bg_color  # Background color of the button
        self.text_color = text_color  # Text color of the button
        self.rect = pygame.Rect(pos, size)  # Create a rectangular area for the button
        self.render_text()  # Render the button text

    def render_text(self):
        self.text_surf = self.font.render(self.text, True, self.text_color)  # Create a surface with the rendered text
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)  # Center the text within the button rectangle

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)  # Draw the button rectangle on the surface
        surface.blit(self.text_surf, self.text_rect)  # Draw the text surface on the button rectangle

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)  # Check if the mouse position is within the button rectangle

# Function to draw the current score on the surface
def draw_score(surface, score):
    score_surf = font.render(f'Score: {score}', True, WHITE)  # Render the score text with the font and color
    score_rect = score_surf.get_rect(topright=(screenWidth - 10, 10))  # Position the score text at the top-right corner
    surface.blit(score_surf, score_rect)  # Draw the rendered score text on the surface

# Function to draw the game title
def draw_title(y, font="Algerian", text="Leap of Faith", font_size=50):
    title_font = pygame.font.SysFont(font, font_size)  # Load the specified font and size
    title_text = title_font.render(text, True, WHITE)  # Render the title text with the font and color
    game.blit(title_text, ((screenWidth - title_text.get_width()) // 2, y))  # Position the title text centered horizontally at y position

# Function to display a message on the screen
def display_message(screen, message, Level, font, duration, BG_img):
    BG = pygame.image.load(BG_img).convert_alpha()  # Load and convert the background image
    screen.blit(BG, (0, 0))  # Draw the background image on the screen
    font = pygame.font.SysFont("Algerian", 100)  # Load the font for the main message
    font2 = pygame.font.SysFont("Algerian", 50)  # Load the font for the level
    text = font.render(message, True, (255, 255, 255))  # Render the main message text with the font and color
    text_rect = text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 50))  # Center the main message text
    text2 = font2.render(Level, True, (255, 255, 255))  # Render the level text with the font and color
    text_rect2 = text2.get_rect(center=(screen.get_width() / 2, 400))  # Position the level text
    screen.blit(text, text_rect)  # Draw the main message text on the screen
    screen.blit(text2, text_rect2)  # Draw the level text on the screen
    pygame.display.update()  # Update the display
    time.sleep(duration)  # Pause for the specified duration

# Function to draw hearts representing player health
def draw_hearts(surface, health):
    if health > 0:
        spacing = 10  # Spacing between heart icons
        total_width = health * (30 + spacing)  # Total width needed to draw all hearts

        # Create a surface to draw multiple heart images
        multi_image_surface = pygame.Surface((total_width, 30), pygame.SRCALPHA)

        # Draw the heart images onto the multi_image_surface
        for i in range(health):
            x_offset = i * (30 + spacing)  # Calculate x offset for each heart
            multi_image_surface.blit(heart_img, (x_offset, 0))  # Draw the heart image at the calculated position

        surface.blit(multi_image_surface, (10, 10))  # Draw the multi_image_surface on the main surface

# Function to draw a final score or other text at a specified position
def draw_final_score(surface, final_score, text, y):
    final_score_surf = font.render(f'{text}: {final_score}', True, WHITE)  # Render the final score text with the font and color
    final_score_rect = final_score_surf.get_rect(center=(screenWidth / 2, y))  # Center the final score text horizontally at y position
    surface.blit(final_score_surf, final_score_rect)  # Draw the final score text on the surface

# Function to load high scores from a JSON file
def load_high_scores(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)  # Load JSON data from the file
            return data.get("high_scores", [0, 0, 0])  # Return high scores from the data, defaulting to [0, 0, 0] if not found
    except (FileNotFoundError, json.JSONDecodeError):
        return [0, 0, 0]  # Return default high scores if there's an error loading the file

# Function to save high scores to a JSON file
def save_high_scores(file_path, high_scores):
    with open(file_path, 'w') as file:
        json.dump({"high_scores": high_scores}, file)  # Write high scores to the JSON file

# Define the file path for the high score
high_scores_file = 'Script/high_score.json'  # File path to store high scores
high_scores = load_high_scores(high_scores_file)  # Load existing high scores from the file

cloud_group = pygame.sprite.Group()  # Create a sprite group for clouds

def play_video(clip):
    clip.preview()

def main(game, level, score=0):
    global high_scores, speed, player_speed, obsticle_limit , obsticle_start_limit, obsticle_space # Declare global variables
    speed = 4
    clock = pygame.time.Clock()  # Initialize Pygame clock for controlling frame rate
    fps = 90  # Frames per second
    run = True  # Flag to control the main game loop
    game_over = False  # Flag to indicate if the game is over
    pause = False  # Flag to indicate if the game is paused

    player = Player()  # Create an instance of the Player class
    all_sprites = pygame.sprite.Group()  # Group for all game sprites
    all_sprites.add(player)  # Add the player sprite to the sprite group

    obstacles = pygame.sprite.Group()  # Group for obstacles

    scroll_y = 0  # Vertical scroll position for the background
    scroll_speed = 5  # Speed at which the background scrolls

    obstacle_spawn_delay = 100  # Delay in frames before spawning a new obstacle
    obstacle_spawn_timer = 0  # Timer for tracking obstacle spawn delay

    obstacle_respawn_timer = 0  # Timer for respawning obstacles after collision
    obstacle_removed = False  # Flag indicating if obstacles have been removed after collision

    start_time = pygame.time.get_ticks()  # Start time in milliseconds

    score = score  # Initialize score (redundant with the function parameter)

    settings = False  # Flag to indicate if the settings menu is open

    # Load level-specific assets
    background_img = pygame.image.load(level["Background"]).convert_alpha()  # Load background image
    obstacle_imgs = [pygame.image.load(obstacle).convert_alpha() for obstacle in level["Obstacles"]]  # Load obstacle images
    obstacle_imgs = [pygame.transform.scale(obstacle_img, obstacle_size) for obstacle_img in obstacle_imgs]  # Scale obstacle images

    settings_buttons = [
            Button("Low", (150, 200), (200, 50), font, WHITE, BLACK),  # Create "Low" difficulty button
            Button("Mid", (150, 270), (200, 50), font, WHITE, BLACK),  # Create "Mid" difficulty button
            Button("High", (150, 340), (200, 50), font, WHITE, BLACK),  # Create "High" difficulty button
            Button("Back", (150, 450), (200, 50), font, 'gray', BLACK)  # Create "Back" button
        ]

    difficulty_text = "Mid"  # Default difficulty text

    while run:  # Main game loop
        clock.tick(fps)  # Cap the frame rate at 90 frames per second
        for event in pygame.event.get():  # Check all events in the event queue
            if event.type == QUIT:  # If the user closes the window
                run = False  # Exit the main game loop
                pygame.quit()  # Quit pygame
                sys.exit()  # Exit the Python program

            if event.type == MOUSEBUTTONDOWN:  # If the user clicks the mouse
                mouse_pos = event.pos  # Get the mouse position
                if game_over:  # If the game is over
                    for button in buttons:  # Check each button in the buttons list
                        if button.is_hovered(mouse_pos):  # If the mouse is hovering over the button
                            if button.text == "Restart":  # If the Restart button is clicked
                                main(game, Level_1, 0)  # Restart the game with Level 1
                            elif button.text == "Main Menu":  # If the Main Menu button is clicked
                                main_menu(game)  # Go back to the main menu

                if pause:  # If the game is paused
                    for button in pause_button:  # Check each button in the pause_button list
                        if button.is_hovered(mouse_pos):  # If the mouse is hovering over the button
                            if button.text == 'Resume':  # If the Resume button is clicked
                                pause = False  # Resume the game
                                print("Resuming with score:", score)  # Print resuming message
                                main(game, level, score)  # Continue the game from the current level
                            elif button.text == "Restart":  # If the Restart button is clicked
                                main(game, Level_1, 0)  # Restart the game with Level 1
                            elif button.text == "Settings":  # If the Settings button is clicked
                                settings = True  # Open the settings menu
                            elif button.text == "Main Menu":  # If the Main Menu button is clicked
                                main_menu(game)  # Go back to the main menu

                if settings:  # If the settings menu is open
                    for buttons in settings_buttons:  # Check each button in the settings_buttons list
                        if buttons.is_hovered(mouse_pos):  # If the mouse is hovering over the button
                            if settings:  # If still in settings menu (redundant check)
                                if buttons.text == "Low":  # If the Low button is clicked
                                    print('Low')  # Print "Low" message
                                    player_speed = 3  # Set player speed to low
                                    difficulty_text = "Low"  # Update difficulty text
                                elif buttons.text == "Mid":  # If the Mid button is clicked
                                    print('Mid')  # Print "Mid" message
                                    player_speed = 5  # Set player speed to medium
                                    difficulty_text = "Mid"  # Update difficulty text
                                elif buttons.text == "High":  # If the High button is clicked
                                    print('High')  # Print "High" message
                                    player_speed = 8  # Set player speed to high
                                    difficulty_text = "high"  # Update difficulty text
                                elif buttons.text == "Back":  # If the Back button is clicked
                                    print('back')  # Print "Back" message
                                    settings = False  # Close the settings menu
                                    pause = True  # Reopen the pause menu
                
            if event.type == KEYDOWN:  # If a key is pressed down
                if event.key == K_ESCAPE or event.key == K_p or event.key == K_m:  # If ESC, P, or M is pressed
                    pause = True  # Pause the game

        if game_over:  # If the game is over
            speed = 4  # Reset speed to default (4)
            game.blit(menu_background_img, (0, 0))  # Draw the menu background
            draw_title(50, "Game Over", font_size=50)  # Draw the "Game Over" title
            buttons = [Button("Restart", (150, 330), (200, 50), font, WHITE, BLACK),  # Create Restart button
                       Button("Main Menu", (150, 400), (200, 50), font, WHITE, BLACK)]  # Create Main Menu button

            for button in buttons:  # Draw each button
                button.draw(game)

            # Draw final score
            draw_final_score(game, score, 'Final Score',(screenHeight / 2) - 50)

            # Update high score if current score is higher
            if score > high_scores[0]:  # If current score is higher than the highest high score
                high_scores[2] = high_scores[1]  # Shift other high scores down
                high_scores[1] = high_scores[0]
                high_scores[0] = score  # Set new high score
                save_high_scores(high_scores_file, high_scores)  # Save high scores to file

            if score > high_scores[1] and score < high_scores[0]:  # If current score is higher than the second high score
                high_scores[2] = high_scores[1]  # Shift third high score down
                high_scores[1] = score  # Set new second high score
                save_high_scores(high_scores_file, high_scores)  # Save high scores to file

            if score > high_scores[2] and score < high_scores[1]:  # If current score is higher than the third high score
                high_scores[2] = score  # Set new third high score
                save_high_scores(high_scores_file, high_scores)  # Save high scores to file

        elif settings:  # If the settings menu is open
            game.blit(menu_background_img, (0, 0))  # Draw the menu background
            draw_title(50, "Paused", font_size=50)  # Draw the "Paused" title
            for button in settings_buttons:  # Draw each button in the settings menu
                button.draw(game)
            draw_title(550, None, f'Sensitivity : {difficulty_text}', 60)  # Draw the sensitivity text

            pause = False

        elif pause and not settings:  # If the game is paused and settings menu is closed
            game.blit(menu_background_img, (0, 0))  # Draw the menu background
            draw_title(50, "Paused", font_size=50)  # Draw the "Paused" title
            pause_button = [Button("Resume", (150, 260), (200, 50), font, WHITE, BLACK),  # Create Resume button
                            Button("Restart", (150, 330), (200, 50), font, WHITE, BLACK),  # Create Restart button                
                            Button("Settings", (150, 400), (200, 50), font, WHITE, BLACK),  # Create Settings button
                Button("Main Menu", (150, 470), (200, 50), font, WHITE, BLACK)]  # Create Main Menu button

            for button in pause_button:  # Iterate through each button in pause_button list
                button.draw(game)  # Draw each button on the game screen

            # Draw final score
            draw_final_score(game, score, 'Score', (screenHeight / 2) - 150)  # Draw the score at the specified position

        else:  # If neither game over, nor settings, nor pause
            all_sprites.update()  # Update all sprites (player and obstacles)

            if player.health == 0:  # If player's health is zero
                game_over = True  # Set game_over flag to True
                death_sound.play()  # Play the death sound effect

            if score == 0:  # If score is zero
                play_video(clip)
                display_message(game, "Level 1", "SPACE", font, 2, "UI/level transition background for level 1.png")  # Display level 1 message

            if score == 3000:  # If score reaches 300
                if level == Level_1:  # If current level is Level 1
                    obsticle_limit = 2
                    speed = 5  # Set speed to 5
                    LevelUp_sound.play()  # Play level up sound effect
                    display_message(game, "Level 2", "SKY", font, 2, "UI/level transition background for level 2.png")  # Display level 2 message
                    main(game, Level_2, 3000)  # Start Level 2 with a score of 3000

            if score == 6000:  # If score reaches 6000
                if level == Level_2:  # If current level is Level 2
                    obsticle_space = 700
                    obsticle_limit = 4
                    speed = 4  # Set speed to 4
                    LevelUp_sound.play()  # Play level up sound effect
                    display_message(game, "Level 3", "CITY", font, 2, "UI/level transition background for level 3.jpg")  # Display level 3 message
                    main(game, Level_3, 6000)  # Start Level 3 with a score of 6000

            # Adjust speed and obsticles spawn based on score thresholds
            if score == 7000:
                speed = 5
            if score == 8000:
                obsticle_start_limit = 1
                speed = 6
            if score == 9000:
                obsticle_start_limit = 2
                speed = 7
            if score == 10000:
                obsticle_start_limit = 3
                speed = 8
            if score == 11000:
                speed = 9
            if score == 12000:
                obsticle_start_limit = 4
                speed = 10

            if not game_over:  # If the game is not over
                if not obstacle_removed:  # If obstacles are not currently being removed
                    # Spawn obstacles
                    obstacle_spawn_timer = Obstacle.spawn_obstacles(obstacle_imgs, all_sprites, obstacle_spawn_timer, obstacle_spawn_delay, obstacles)

                # Update obstacles
                obstacles.update()

                # Check for collisions between player and obstacles
                if pygame.sprite.spritecollide(player, obstacles, True, pygame.sprite.collide_mask):
                    player.health -= 1  # Decrease player's health by 1
                    player.blinking = True  # Set player to blink
                    player.blink_timer = pygame.time.get_ticks()  # Start blink timer

                    obstacle_respawn_timer = pygame.time.get_ticks()  # Set obstacle respawn timer
                    obstacle_removed = True  # Set obstacle removed flag to True
                    for obstacle in obstacles:
                        obstacle.kill()  # Remove obstacle from the sprite group

                # Delay before respawning obstacles after collision
                if obstacle_removed and pygame.time.get_ticks() - obstacle_respawn_timer > 1000:
                    obstacle_removed = False  # Reset obstacle removed flag

                # Update the scrolling background position
                scroll_y -= speed
                if scroll_y <= -screenHeight:
                    scroll_y = 0

                # Draw the scrolling background
                game.blit(background_img, (0, scroll_y))
                game.blit(background_img, (0, scroll_y + screenHeight))

                # Draw specific elements for Level 2
                if level == Level_2:
                    sun_position = (screenWidth - 150, 50)
                    game.blit(sun_img, sun_position)
                    game.blit(cloud_img, (0, scroll_y))
                    game.blit(cloud_img, (0, scroll_y + screenHeight))

                all_sprites.draw(game)  # Draw all sprites on the game screen

                if not pause:  # If the game is not paused
                    score += 1  # Increase the score by 1
                draw_score(game, score)  # Draw the current score
                draw_hearts(game, player.health)  # Draw player's health

        pygame.display.update()  # Update the display to show changes


class Menu:
    def __init__(self, screen):
        global speed, player_speed, high_scores  # Global variables used in the game
        self.font2 = pygame.font.SysFont("Algerian", 40)  # Font for high score display
        self.screen = screen  # Initialize the screen surface
        self.font = pygame.font.Font(None, 50)  # Font for menu buttons
        # Define the buttons for the main menu
        self.buttons = [
            Button("Play", (150, 220), (200, 50), self.font, WHITE, BLACK),
            Button("Settings", (150, 290), (200, 50), self.font, WHITE, BLACK),
            Button("HighScore", (150, 360), (200, 50), self.font, WHITE, BLACK),
            Button("Quit", (150, 500), (200, 50), self.font, 'gray', BLACK)
        ]
        # Define the buttons for the settings menu
        self.settings_buttons = [
            Button("Low", (150, 200), (200, 50), self.font, WHITE, BLACK),
            Button("Mid", (150, 270), (200, 50), self.font, WHITE, BLACK),
            Button("High", (150, 340), (200, 50), self.font, WHITE, BLACK),
            Button("Back", (150, 450), (200, 50), self.font, 'gray', BLACK)
        ]
        # Initialize flags for displaying high scores and settings menu
        self.high_score_display = False
        self.settings = False
        # Default difficulty text
        self.difficulty_text = "Mid"
        # Back button for settings and high score display
        self.Back_btn = Button("Back", (150, 500), (200, 50), self.font, 'gray', BLACK)

    def run(self):
        global player_speed, speed, high_scores  # Global variables used in the game
        running = True
        while running:
            for event in pygame.event.get():  # Iterate through all pygame events
                if event.type == QUIT:  # If the user quits the game
                    pygame.quit()  # Quit pygame
                    sys.exit()  # Exit the program

                if event.type == MOUSEBUTTONDOWN:  # If a mouse button is pressed
                    mouse_pos = event.pos  # Get the position of the mouse click
                    if not self.high_score_display and not self.settings:  # If neither high score nor settings are open
                        for button in self.buttons:  # Check each button in the main menu
                            if button.is_hovered(mouse_pos):  # If the mouse hovers over a button
                                if button.text == "Play":  # If the Play button is clicked
                                    main(game, Level_1)  # Start the game with Level 1
                                elif button.text == "HighScore":  # If the HighScore button is clicked
                                    self.high_score_display = True  # Display the high scores
                                elif button.text == "Settings":  # If the Settings button is clicked
                                    self.settings = True  # Open the settings menu
                                elif button.text == "Quit":  # If the Quit button is clicked
                                    pygame.quit()  # Quit pygame
                                    sys.exit()  # Exit the program

                    for buttons in self.settings_buttons:  # Check each button in the settings menu
                        if buttons.is_hovered(mouse_pos):  # If the mouse hovers over a button
                            if self.settings:  # If the settings menu is open
                                if buttons.text == "Low":  # If the Low button is clicked
                                    print('Low')  # Debug message
                                    player_speed = 3  # Set player speed to 3
                                    self.difficulty_text = "Low"  # Update difficulty text
                                elif buttons.text == "Mid":  # If the Mid button is clicked
                                    print('Mid')  # Debug message
                                    player_speed = 5  # Set player speed to 5
                                    self.difficulty_text = "Mid"  # Update difficulty text
                                elif buttons.text == "High":  # If the High button is clicked
                                    print('High')  # Debug message
                                    player_speed = 8  # Set player speed to 8
                                    self.difficulty_text = "High"  # Update difficulty text
                                elif buttons.text == "Back":  # If the Back button is clicked
                                    print('back')  # Debug message
                                    self.settings = False  # Close the settings menu

                    if self.Back_btn.is_hovered(mouse_pos):  # If the mouse hovers over the Back button
                        if self.high_score_display:  # If high scores are being displayed
                            self.high_score_display = False  # Close the high score display

                if event.type == KEYDOWN:  # If a key is pressed
                    if event.key == K_ESCAPE:  # If the Escape key is pressed
                        self.high_score_display = False  # Close the high score display
                        self.settings = False  # Close the settings menu

            self.screen.blit(menu_background_img, (0, 0))  # Draw the menu background
            for button in self.buttons:  # Draw each button in the main menu
                button.draw(self.screen)

            draw_title(50)  # Draw the game title

            if self.high_score_display:  # If high scores are being displayed
                self.screen.fill(BLACK)  # Fill the screen with black
                high_score_text = self.font2.render("Top 3 High Scores", True, WHITE)  # Render high score text
                self.screen.blit(high_score_text, (screenWidth // 2 - high_score_text.get_width() // 2, 150))  # Display high score text
                for i, score in enumerate(high_scores):  # Iterate through high scores
                    score_text = self.font.render(f"{i + 1}. {score}", True, WHITE)  # Render each high score
                    self.screen.blit(score_text, (screenWidth // 2 - score_text.get_width() // 2, 260 + i * 70))  # Display each high score
                self.Back_btn.draw(self.screen)  # Draw the Back button

            if self.settings:  # If the settings menu is open
                self.screen.blit(menu_background_img, (0, 0))  # Draw the menu background
                for button in self.settings_buttons:  # Draw each button in the settings menu
                    button.draw(self.screen)
                    draw_title(50)  # Draw the game title
                    draw_title(550, None, f'Sensitivity : {self.difficulty_text}', 60)  # Display sensitivity text

            pygame.display.update()  # Update the display

# Main function to run the menu
def main_menu(game):
      # Play background audio indefinitely
    menu = Menu(game)  # Create a Menu instance
    menu.run()  # Run the menu

# Call the main function with the initial level
if __name__ == "__main__":
    Bg_Audio.play(-1)
    main_menu(game)  # Start the main menu
