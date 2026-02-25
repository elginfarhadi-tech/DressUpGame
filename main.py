import pygame
import sys
import random
from pathlib import Path

pygame.init()

# -----------------------------
# Window
# -----------------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dress Up Game")
clock = pygame.time.Clock()

# -----------------------------
# Colors
# -----------------------------
TEXT = (0, 0, 0)
BTN = (245, 245, 245)
BTN_HOVER = (220, 220, 220)

# -----------------------------
# Assets
# -----------------------------
ASSETS = Path(__file__).parent / "assets"

# -----------------------------
# Sound setup
# -----------------------------
sound_enabled = True
try:
    pygame.mixer.init()
except:
    sound_enabled = False

def load_sound(name):
    if not sound_enabled:
        return None
    try:
        return pygame.mixer.Sound(ASSETS / name)
    except:
        return None

click_sound = load_sound("click.wav")
sparkle_sound = load_sound("sparkle.wav")

def play(sound):
    if sound:
        sound.play()

# -----------------------------
# Fonts
# -----------------------------
title_font = pygame.font.SysFont("arial", 48, bold=True)
ui_font = pygame.font.SysFont("arial", 22)
info_font = pygame.font.SysFont("arial", 20)

# -----------------------------
# Glow function
# -----------------------------
def draw_glow_text_topright(message):
    font = pygame.font.SysFont("arial", 28, bold=True)

    text_color = (255, 240, 250)
    glow_color = (255, 105, 180)

    text_surface = font.render(message, True, text_color)
    text_rect = text_surface.get_rect()
    text_rect.topright = (WIDTH - 20, 20)

    glow_surface = pygame.Surface((text_rect.width + 40, text_rect.height + 40), pygame.SRCALPHA)

    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx == 0 and dy == 0:
                continue
            glow = font.render(message, True, glow_color)
            glow.set_alpha(35)
            glow_surface.blit(glow, (20 + dx, 20 + dy))

    screen.blit(glow_surface, (text_rect.left - 20, text_rect.top - 20))
    screen.blit(text_surface, text_rect)

# -----------------------------
# Button drawing
# -----------------------------
def draw_button(rect, label):
    mouse = pygame.mouse.get_pos()
    color = BTN_HOVER if rect.collidepoint(mouse) else BTN
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=8)
    text = ui_font.render(label, True, TEXT)
    screen.blit(text, text.get_rect(center=rect.center))

# ============================================================
# NAME INPUT SCREEN
# ============================================================
def get_player_name():
    name = ""
    input_box = pygame.Rect(220, 260, 360, 44)
    start_btn = pygame.Rect(330, 330, 140, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name if name else "Player"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 16 and event.unicode.isprintable():
                        name += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_btn.collidepoint(event.pos):
                    return name if name else "Player"

        screen.fill((180, 200, 255))

        title = title_font.render("Enter Your Name", True, TEXT)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))

        pygame.draw.rect(screen, (255, 255, 255), input_box, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), input_box, 2, border_radius=10)

        name_text = ui_font.render(name, True, TEXT)
        screen.blit(name_text, (input_box.x + 10, input_box.y + 10))

        draw_button(start_btn, "Start")

        pygame.display.flip()
        clock.tick(60)

# ============================================================
# MAIN GAME
# ============================================================
def main_game(player_name):

    body = pygame.image.load(ASSETS / "body.png").convert_alpha()

    hairs = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("hair*.png"))]
    clothes = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("clothes*.png"))]
    shoes = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("shoes*.png"))]
    backgrounds = [pygame.image.load(p).convert() for p in sorted(ASSETS.glob("background*.png"))]

    x = (WIDTH - body.get_width()) // 2
    y = 0

    hair_index = 0
    clothes_index = 0
    shoes_index = 0
    bg_index = 0

    btn_hair = pygame.Rect(20, 120, 130, 30)
    btn_clothes = pygame.Rect(20, 160, 130, 30)
    btn_shoes = pygame.Rect(20, 200, 130, 30)
    btn_bg = pygame.Rect(20, 240, 130, 30)
    btn_random = pygame.Rect(20, 280, 130, 30)
    btn_reset = pygame.Rect(20, 320, 130, 30)

    last_special = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = event.pos

                if btn_hair.collidepoint(mouse):
                    play(click_sound)
                    hair_index = (hair_index + 1) % len(hairs)

                elif btn_clothes.collidepoint(mouse):
                    play(click_sound)
                    clothes_index = (clothes_index + 1) % len(clothes)

                elif btn_shoes.collidepoint(mouse):
                    play(click_sound)
                    if shoes:
                        shoes_index = (shoes_index + 1) % len(shoes)

                elif btn_bg.collidepoint(mouse):
                    play(click_sound)
                    bg_index = (bg_index + 1) % len(backgrounds)

                elif btn_random.collidepoint(mouse):
                    play(click_sound)
                    hair_index = random.randrange(len(hairs))
                    clothes_index = random.randrange(len(clothes))
                    bg_index = random.randrange(len(backgrounds))
                    if shoes:
                        shoes_index = random.randrange(len(shoes))

                elif btn_reset.collidepoint(mouse):
                    play(click_sound)
                    hair_index = clothes_index = shoes_index = bg_index = 0

        screen.blit(backgrounds[bg_index], (0, 0))
        screen.blit(body, (x, y))
        screen.blit(clothes[clothes_index], (x, y))
        if shoes:
            screen.blit(shoes[shoes_index], (x, y))
        screen.blit(hairs[hair_index], (x, y))

        special = None
        if hair_index == 1:
            draw_glow_text_topright("Awesome ✨")
            special = "h2"

        elif hair_index == 3:
            message = f"Now I am ready to party, {player_name}!"
            draw_glow_text_topright(message)
            special = "h4"

        if special != last_special and special is not None:
            play(sparkle_sound)

        last_special = special

        draw_button(btn_hair, "Hair")
        draw_button(btn_clothes, "Clothes")
        draw_button(btn_shoes, "Shoes")
        draw_button(btn_bg, "BG")
        draw_button(btn_random, "Random")
        draw_button(btn_reset, "Reset")

        pygame.display.flip()
        clock.tick(60)

# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    name = get_player_name()
    main_game(name)
    pygame.quit()
    sys.exit()