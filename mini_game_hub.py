import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Game")

# Load images (replace with your image file names)
player_img = pygame.image.load("spaceship.png")  # Spaceship image
asteroid_img = pygame.image.load("asteroid.png")  # Asteroid image
powerup_img = pygame.image.load("battery.png")  # Power-up (battery) image
shield_img = pygame.image.load("shield.png")  # Shield power-up image
bullet_img = pygame.image.load("bullet.png")  # Bullet image
boss_img = pygame.image.load("boss.png")  # Boss image

# Resize images (optional)
player_img = pygame.transform.scale(player_img, (50, 50))
asteroid_img = pygame.transform.scale(asteroid_img, (40, 40))
powerup_img = pygame.transform.scale(powerup_img, (30, 30))
shield_img = pygame.transform.scale(shield_img, (50, 50))
bullet_img = pygame.transform.scale(bullet_img, (5, 15))
boss_img = pygame.transform.scale(boss_img, (150, 150))

# Player settings
player_width, player_height = 50, 50
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - 100
player_speed = 8

# Bullet settings
bullet_width, bullet_height = 5, 15
bullet_speed = 10
bullets = []

# Asteroid settings
asteroid_width, asteroid_height = 40, 40
asteroid_speed = 4
asteroids = []

# Power-up settings
powerup_width, powerup_height = 30, 30
powerup_speed = 3
powerups = []

# Shield settings
shield_active = False
shield_duration = 500  # Shield lasts for 500 frames
shield_timer = 0

# Boss settings
boss_width, boss_height = 150, 150
boss_x = WIDTH // 2 - boss_width // 2
boss_y = -boss_height
boss_speed = 5  # Increased boss speed
boss_health = 10
boss_active = False
boss_spawn_cooldown = 0  # Cooldown timer for boss spawn

# Score & lives
score = 0
lives = 3
font = pygame.font.Font(None, 36)

# Max score
def save_max_score(score):
    with open("max_score.txt", "w") as f:
        f.write(str(score))

def load_max_score():
    try:
        with open("max_score.txt", "r") as f:
            return int(f.read())
    except FileNotFoundError:
        return 0

max_score = load_max_score()

# Pause menu
paused = False

# Game over flag
game_over = False

def draw_text(text, position, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def spawn_asteroid():
    asteroid_x = random.randint(0, WIDTH - asteroid_width)
    asteroid_y = -asteroid_height
    asteroids.append(pygame.Rect(asteroid_x, asteroid_y, asteroid_width, asteroid_height))

def spawn_powerup():
    powerup_x = random.randint(0, WIDTH - powerup_width)
    powerup_y = -powerup_height
    powerups.append({"rect": pygame.Rect(powerup_x, powerup_y, powerup_width, powerup_height), "type": "battery"})

def spawn_shield():
    shield_x = random.randint(0, WIDTH - powerup_width)
    shield_y = -powerup_height
    powerups.append({"rect": pygame.Rect(shield_x, shield_y, powerup_width, powerup_height), "type": "shield"})

def show_game_over():
    global max_score
    screen.fill((0, 0, 0))
    draw_text("Game Over! 😭", (WIDTH // 2 - 100, HEIGHT // 2), (255, 0, 0))
    draw_text(f"Final Score: {score}", (WIDTH // 2 - 80, HEIGHT // 2 + 40), (255, 255, 255))
    if score > max_score:
        max_score = score
        save_max_score(max_score)
    draw_text(f"Max Score: {max_score}", (WIDTH // 2 - 80, HEIGHT // 2 + 80), (255, 255, 255))
    pygame.display.flip()
    pygame.time.delay(3000)
    pygame.quit()
    sys.exit()

def show_pause_menu():
    screen.fill((0, 0, 0))
    draw_text("Paused", (WIDTH // 2 - 50, HEIGHT // 2 - 50), (255, 255, 255))
    draw_text("Press P to Resume", (WIDTH // 2 - 100, HEIGHT // 2), (255, 255, 255))
    pygame.display.flip()

# Game loop
running = True
while running:
    screen.fill((0, 0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Pause/resume the game
                paused = not paused
    
    if paused:
        show_pause_menu()
        continue
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed
    if keys[pygame.K_SPACE]:
        bullets.append(pygame.Rect(player_x + player_width // 2 - bullet_width // 2, player_y, bullet_width, bullet_height))
    
    # Move bullets
    for bullet in bullets:
        bullet.y -= bullet_speed
        if bullet.y < 0:
            bullets.remove(bullet)
    
    # Spawn asteroids and power-ups
    if random.randint(1, 50) == 1:
        spawn_asteroid()
    if random.randint(1, 300) == 1:  # Reduced battery spawn rate (1 in 300)
        spawn_powerup()
    if random.randint(1, 500) == 1:  # Reduced shield spawn rate (1 in 500)
        spawn_shield()
    
    # Move asteroids and power-ups
    for asteroid in asteroids:
        asteroid.y += asteroid_speed
        if asteroid.y > HEIGHT:
            asteroids.remove(asteroid)  # Remove asteroid if it reaches the bottom (no life lost)
    
    for powerup in powerups:
        powerup["rect"].y += powerup_speed
        if powerup["rect"].y > HEIGHT:
            powerups.remove(powerup)
    
    # Check for collisions
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    
    for asteroid in asteroids:
        if player_rect.colliderect(asteroid):  # Check if asteroid hits player
            if shield_active:
                shield_active = False  # Deactivate shield
            else:
                lives -= 1
                if lives == 0:
                    game_over = True
            asteroids.remove(asteroid)
    
    for bullet in bullets:
        for asteroid in asteroids:
            if bullet.colliderect(asteroid):  # Check if bullet hits asteroid
                bullets.remove(bullet)
                asteroids.remove(asteroid)
                score += 1
    
    for powerup in powerups:
        if player_rect.colliderect(powerup["rect"]):  # Check if player collects power-up
            if powerup["type"] == "battery":  # Battery power-up
                lives += 1
            elif powerup["type"] == "shield":  # Shield power-up
                shield_active = True
                shield_timer = shield_duration
            powerups.remove(powerup)
    
    # Update shield timer
    if shield_active:
        shield_timer -= 1
        if shield_timer <= 0:
            shield_active = False
    
    # Boss fight
    if score >= 50 and not boss_active and boss_spawn_cooldown <= 0 and random.randint(1, 10) == 1:  # Boss spawn condition
        boss_active = True
        boss_y = -boss_height  # Reset boss position
        boss_spawn_cooldown = 500  # Set cooldown to 500 frames (~8 seconds)

    if boss_active:
        boss_y += boss_speed
        if boss_y > HEIGHT:  # Boss reaches the bottom
            game_over = True  # Game ends if boss isn't defeated
        else:
            # Check for collisions with boss
            boss_rect = pygame.Rect(boss_x, boss_y, boss_width, boss_height)
            if player_rect.colliderect(boss_rect):  # Player hits boss
                lives -= 5  # Reduce lives by 5
                if lives <= 0:  # If lives are less than or equal to 0, end the game
                    game_over = True
            for bullet in bullets:
                if bullet.colliderect(boss_rect):  # Bullet hits boss
                    bullets.remove(bullet)
                    boss_health -= 1
                    if boss_health <= 0:
                        boss_active = False
                        score += 10  # Reduced bonus points for defeating the boss
    
    # Update boss spawn cooldown
    if boss_spawn_cooldown > 0:
        boss_spawn_cooldown -= 1
    
    # Draw player
    screen.blit(player_img, (player_x, player_y))
    
    # Draw shield if active
    if shield_active:
        screen.blit(shield_img, (player_x - 10, player_y - 10))
    
    # Draw bullets
    for bullet in bullets:
        screen.blit(bullet_img, bullet)
    
    # Draw asteroids
    for asteroid in asteroids:
        screen.blit(asteroid_img, asteroid)
    
    # Draw power-ups
    for powerup in powerups:
        if powerup["type"] == "battery":
            screen.blit(powerup_img, powerup["rect"])
        elif powerup["type"] == "shield":
            screen.blit(shield_img, powerup["rect"])
    
    # Draw boss
    if boss_active:
        screen.blit(boss_img, (boss_x, boss_y))
    
    # Draw score, lives, and max score
    draw_text(f"Score: {score}", (10, 10))
    draw_text(f"Lives: {lives}", (WIDTH - 120, 10))
    draw_text(f"Max Score: {max_score}", (WIDTH // 2 - 60, 10))
    
    pygame.display.flip()
    pygame.time.delay(30)
    
    if game_over:
        show_game_over()

pygame.quit()
sys.exit()