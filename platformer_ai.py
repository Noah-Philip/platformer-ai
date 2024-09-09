import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Scrolling Platformer")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Define the player
player_size = 50
player = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 2 * player_size, player_size, player_size)
player_color = BLUE
player_speed = 5
player_y_speed = 0
dash_speed = 100
gravity = 0.5
jump_strength = -10
on_ground = False
dashing = False
dash_direction = 0

# Dash restrictions
last_dash_time = 0
can_dash_in_air = True
dash_cooldown = 1.5  # Cooldown time in seconds

# Define the platforms
platforms = [
    # Horizontal platforms
    pygame.Rect(0, SCREEN_HEIGHT - 50, 1600, 20),  # Base platform
    pygame.Rect(200, SCREEN_HEIGHT - 150, 300, 20),  # Platform 1
    pygame.Rect(600, SCREEN_HEIGHT - 250, 250, 20),  # Platform 2
    pygame.Rect(1000, SCREEN_HEIGHT - 350, 250, 20),  # Platform 3

    # Holes in the floor
    pygame.Rect(500, SCREEN_HEIGHT - 200, 100, 20),  # Hole 1
    pygame.Rect(800, SCREEN_HEIGHT - 300, 100, 20),  # Hole 2

    # Walls
    pygame.Rect(150, SCREEN_HEIGHT - 300, 20, 100),  # Wall 1
    pygame.Rect(450, SCREEN_HEIGHT - 400, 20, 200),  # Wall 2
    pygame.Rect(850, SCREEN_HEIGHT - 500, 20, 300),  # Wall 3

    # Floating platforms
    pygame.Rect(1200, SCREEN_HEIGHT - 250, 200, 20),  # Floating Platform 1
    pygame.Rect(1400, SCREEN_HEIGHT - 350, 200, 20),  # Floating Platform 2

    # Platforms with vertical walls on top
    pygame.Rect(1600, SCREEN_HEIGHT - 150, 20, 100),  # Wall 4 (End of the level, part of flag area)
]

# Define the flag
flag = pygame.Rect(1600 - 50, SCREEN_HEIGHT - 100, 50, 100)  # Flag at the end of the level
flag_color = RED

# Camera position
camera_x = 0

def draw_platforms(camera_x):
    for platform in platforms:
        pygame.draw.rect(screen, BLACK, (platform.x - camera_x, platform.y, platform.width, platform.height))

def draw_flag(camera_x):
    pygame.draw.rect(screen, flag_color, (flag.x - camera_x, flag.y, flag.width, flag.height))

def handle_movement(keys):
    global player_y_speed, on_ground, dashing, dash_direction, last_dash_time, can_dash_in_air

    if keys[pygame.K_LEFT]:
        player.x -= player_speed
        dash_direction = -1
    if keys[pygame.K_RIGHT]:
        player.x += player_speed
        dash_direction = 1

    # Gravity and jumping
    if not on_ground:
        player_y_speed += gravity
    else:
        player_y_speed = 0

    if keys[pygame.K_UP] and on_ground:
        player_y_speed = jump_strength
        on_ground = False

    # Dash
    current_time = time.time()
    if keys[pygame.K_SPACE] and not dashing:
        # Check cooldown
        if (current_time - last_dash_time) >= dash_cooldown:
            # Allow dash if in midair or if dashing is allowed
            if not on_ground and can_dash_in_air:
                dashing = True
                player.x += dash_direction * dash_speed
                last_dash_time = current_time
                can_dash_in_air = False
        dashing = False

def check_collision():
    global on_ground, player_y_speed, can_dash_in_air

    on_ground = False

    # Collision with platforms
    for platform in platforms:
        if player.colliderect(platform):
            # Check collision from above
            if player_y_speed > 0:  # Falling down
                if player.bottom <= platform.top + 0.6 * player.height:  # Within 60% above platform
                    player.bottom = platform.top
                    player_y_speed = 0
                    on_ground = True
                    can_dash_in_air = True
                else:
                    # Collision from sides
                    if player.right > platform.left and player.left < platform.right:
                        player.right = platform.left
                    if player.left < platform.right and player.right > platform.left:
                        player.left = platform.right
            elif player_y_speed < 0:  # Moving up
                if player.top >= platform.bottom and player.bottom <= platform.bottom:
                    player.top = platform.bottom
                    player_y_speed = 0
            else:
                # Handle horizontal collisions
                if player.right > platform.left and player.left < platform.right:
                    player.right = platform.left
                if player.left < platform.right and player.right > platform.left:
                    player.left = platform.right

    # Reset the dash capability when player is on the ground
    if on_ground:
        can_dash_in_air = True


def update_camera():
    global camera_x
    player_center_x = player.x + player.width / 2
    screen_center_x = SCREEN_WIDTH / 2
    camera_x = player_center_x - screen_center_x

    # Make sure the camera doesn't scroll past the level boundaries
    camera_x = max(0, min(camera_x, 1600 - SCREEN_WIDTH))

def game_loop():
    global on_ground, player_y_speed, dashing, dash_direction, last_dash_time, can_dash_in_air
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        keys = pygame.key.get_pressed()
        
        # Handle movement
        handle_movement(keys)
        
        # Update player position
        player.y += player_y_speed
        
        # Check for collisions with platforms
        check_collision()
        
        # Update camera position
        update_camera()
        
        # Clear the screen
        screen.fill(WHITE)
        
        # Draw platforms
        draw_platforms(camera_x)
        
        # Draw player
        pygame.draw.rect(screen, player_color, (player.x - camera_x, player.y, player.width, player.height))
        
        # Draw the flag
        draw_flag(camera_x)
        
        # Check if player has reached the flag
        if player.colliderect(flag):
            print("Level completed!")
            pygame.quit()
            sys.exit()
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)

if __name__ == "__main__":
    game_loop()
