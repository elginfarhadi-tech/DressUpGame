import pygame
import sys
import random
import re
from pathlib import Path

pygame.init()

#test20260225
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
ui_font = pygame.font.SysFont("arial", 22, bold=True)
info_font = pygame.font.SysFont("arial", 20, bold=True)


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

    # Auto-load base lists (used for rendering safety)
    hairs = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("hair*.png"))]
    clothes = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("clothes*.png"))]
    tops = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("top*.png"))]
    pants = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("pants*.png"))]
    shoes = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("shoes*.png"))]
    backgrounds = [pygame.image.load(p).convert() for p in sorted(ASSETS.glob("background*.png"))]

    # Character position
    x = (WIDTH - 100) // 2
    y = 0

    hair_index = 0
    clothes_index = 0
    top_index = 0
    pants_index = 0
    shoes_index = 0
    bg_index = 0

    # Clothing mode:
    # "outfit" => draw clothes only
    # "separates" => draw pants + top only
    clothing_mode = "outfit" if len(clothes) > 0 else "separates"

    last_special = None

    # Closet categories (ADD Tops + Pants)
    categories = ["Hairs", "Cloth", "Tops", "Pants", "Shoes"]
    category_buttons = []

    # reach all assets
    def extract_number(path):
        filename = path.stem
        numbers = re.findall(r"\d+", filename)
        if numbers:
            return int(numbers[0])
        return 0

    def scan_and_classify():
        categories_dict = {
            "Hairs": [],
            "Cloth": [],
            "Tops": [],
            "Pants": [],
            "Shoes": [],
        }

        for file_path in ASSETS.glob("*.png"):
            filename = file_path.stem.lower()

            if filename.startswith("hair"):
                categories_dict["Hairs"].append(file_path)
            elif filename.startswith("clothes"):
                categories_dict["Cloth"].append(file_path)
            elif filename.startswith("top"):
                categories_dict["Tops"].append(file_path)
            elif filename.startswith("pants"):
                categories_dict["Pants"].append(file_path)
            elif filename.startswith("shoes"):
                categories_dict["Shoes"].append(file_path)
            # ignore body/background etc.

        for cat in categories_dict:
            categories_dict[cat].sort(key=extract_number)
            print(f"{cat}: {len(categories_dict[cat])} files")

        return categories_dict

    def load_images(categories_dict):
        clothes_data = {}
        THUMB_SIZE = (80, 80)

        for category, paths in categories_dict.items():
            clothes_data[category] = []

            for path in paths:
                try:
                    img = pygame.image.load(path).convert_alpha()
                    thumb = pygame.transform.scale(img, THUMB_SIZE)
                    name = path.stem

                    clothes_data[category].append(
                        {
                            "path": path,
                            "image": img,
                            "thumb": thumb,
                            "name": name,
                            "index": len(clothes_data[category]),
                        }
                    )
                    print(f"loaded: {category} - {name}")
                except pygame.error as e:
                    print(f"failed loading {path}: {e}")

        return clothes_data

    print("loading asset")
    categories_dict = scan_and_classify()
    clothes_data = load_images(categories_dict)

    all_categories = [c for c in categories if c in clothes_data]
    current_category = all_categories[0] if all_categories else "Cloth"

    cloth_buttons = []
    max_scroll = 0
    view_reat = pygame.Rect(20, 80, 300, 450)

    # closet background
    def draw_wardrobe():
        rect = view_reat
        bg_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        transparency = 100
        bg_color = (245, 245, 250, transparency)
        pygame.draw.rect(bg_surface, bg_color, bg_surface.get_rect(), border_radius=15)
        screen.blit(bg_surface, rect)
        pygame.draw.rect(screen, (100, 100, 120), rect, 3, border_radius=15)

        title = info_font.render("CLOSET", True, (50, 60, 80))
        screen.blit(title, (rect.centerx - 35, rect.y + 12))

    # define closet&buttons
    def create_category_buttons():
        nonlocal category_buttons
        category_buttons = []

        start_y = 130
        button_width = 70
        button_height = 30

        for i, category in enumerate(categories):
            x_btn = 60 + i * (button_width + 5)

            category_buttons.append(
                {
                    "rect": pygame.Rect(x_btn, start_y, button_width, button_height),
                    "category": category,
                    "selected": (category == current_category),
                }
            )

    def create_cloth_buttons(category):
        nonlocal cloth_buttons, max_scroll
        cloth_buttons = []

        if category not in clothes_data:
            return cloth_buttons

        items = clothes_data[category]

        start_x = 40
        base_y = 165
        button_width = 80
        button_height = 80
        margin_x = 10
        margin_y = 10

        for i, item in enumerate(items):
            w, h = item["image"].get_size()

            # shoes thumbnails: crop bottom area
            if category == "Shoes":
                start_x_crop = max(0, (w - button_width) // 2)
                start_y_crop = max(0, h - button_height)

                thumb = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                thumb.fill((0, 0, 0, 0))
                thumb.blit(item["image"], (0, 0), (start_x_crop, start_y_crop, button_width, button_height))
            else:
                thumb = item["thumb"]

            row = i // 3
            col = i % 3

            x_btn = start_x + col * (button_width + margin_x)
            y_btn = base_y + row * (button_height + margin_y)

            cloth_buttons.append(
                {
                    "rect": pygame.Rect(x_btn, y_btn, button_width, button_height),
                    "index": i,
                    "selected": False,
                    "category": category,
                    "thumb": thumb,
                    "name": item["name"],
                }
            )

        # FIX: correct rows calc
        rows = (len(items) + 2) // 3
        total_height = rows * (button_height + margin_y)
        max_scroll = max(0, total_height - 160)

        return cloth_buttons

    def draw_category_buttons():
        for btn in category_buttons:
            if btn["selected"]:
                color = (144, 238, 144)
                border_width = 3
            else:
                color = (200, 200, 200)
                border_width = 1

            pygame.draw.rect(screen, color, btn["rect"])
            pygame.draw.rect(screen, (0, 0, 0), btn["rect"], border_width)

            font = pygame.font.Font(None, 24)
            text = font.render(btn["category"], True, (0, 0, 0))
            text_rect = text.get_rect(center=btn["rect"].center)
            screen.blit(text, text_rect)

    def draw_cloth_buttons():
        for btn in cloth_buttons:
            screen.blit(btn["thumb"], btn["rect"])
            if btn["selected"]:
                pygame.draw.rect(screen, (255, 255, 0), btn["rect"], 4)
            else:
                pygame.draw.rect(screen, (0, 0, 0), btn["rect"], 2)

    def handle_click(pos):
        nonlocal current_category, cloth_buttons
        nonlocal clothes_index, hair_index, shoes_index, top_index, pants_index
        nonlocal clothing_mode

        # category buttons
        for btn in category_buttons:
            if btn["rect"].collidepoint(pos):
                if btn["category"] != current_category:
                    current_category = btn["category"]
                    for b in category_buttons:
                        b["selected"] = (b["category"] == current_category)
                    cloth_buttons = create_cloth_buttons(current_category)
                return

        # item buttons
        for btn in cloth_buttons:
            if btn["rect"].collidepoint(pos):
                for b in cloth_buttons:
                    b["selected"] = False
                btn["selected"] = True

                # IMPORTANT: switching logic
                if current_category == "Hairs":
                    hair_index = btn["index"]

                elif current_category == "Cloth":
                    clothes_index = btn["index"]
                    clothing_mode = "outfit"      # outfits ON, top/pants OFF

                elif current_category == "Tops":
                    top_index = btn["index"]
                    clothing_mode = "separates"   # top/pants ON, outfit OFF

                elif current_category == "Pants":
                    pants_index = btn["index"]
                    clothing_mode = "separates"   # top/pants ON, outfit OFF

                elif current_category == "Shoes":
                    shoes_index = btn["index"]

                return

    # create buttons
    create_category_buttons()
    cloth_buttons = create_cloth_buttons(current_category)

    # main running
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_click(event.pos)

        # Draw background
        if backgrounds:
            screen.blit(backgrounds[bg_index], (0, 0))
        else:
            screen.fill((180, 200, 255))

        # Draw closet & buttons
        draw_wardrobe()
        draw_category_buttons()
        draw_cloth_buttons()

        # Clamp indices safely
        hair_index = min(hair_index, len(hairs) - 1) if hairs else 0
        clothes_index = min(clothes_index, len(clothes) - 1) if clothes else 0
        top_index = min(top_index, len(tops) - 1) if tops else 0
        pants_index = min(pants_index, len(pants) - 1) if pants else 0
        shoes_index = min(shoes_index, len(shoes) - 1) if shoes else 0

        # Draw character layers
        screen.blit(body, (x, y))

        # ✅ KEY CHANGE: draw EITHER clothes OR top+pants (never both)
        if clothing_mode == "outfit":
            if clothes:
                screen.blit(clothes[clothes_index], (x, y))
        else:  # separates
            if pants:
                screen.blit(pants[pants_index], (x, y))
            if tops:
                screen.blit(tops[top_index], (x, y))

        if shoes:
            screen.blit(shoes[shoes_index], (x, y))

        if hairs:
            screen.blit(hairs[hair_index], (x, y))

        # Special messages
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