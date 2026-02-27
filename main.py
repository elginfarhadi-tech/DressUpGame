import pygame
import sys
import random
import re
from pathlib import Path

pygame.init()

#testelgin
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
    dresses = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("dress*.png"))]
    tops = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("top*.png"))]
    pants = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("pants*.png"))]
    shoes = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("shoes*.png"))]
    backgrounds = [pygame.image.load(p).convert() for p in sorted(ASSETS.glob("background*.png"))]

    # Character position
    x = (WIDTH - 100) // 2
    y = 0

    hairs_index = None
    dresses_index = None
    tops_index = None
    pants_index = None
    shoes_index = None
    bg_index = 0

    ''''
    # Clothing mode:
    # "outfit" => draw clothes only
    # "separates" => draw pants + top only
    clothing_mode = "outfit" if len(clothes) > 0 else "separates"
    '''

    last_special = None

    # Closet categories (ADD Tops + Pants)
    categories = ["Hairs", "Dresses", "Tops", "Pants", "Shoes"]
    category_buttons = []

    # Tip variables 
    tip_text = ""
    tip_timer = 0
    tip_color = (255, 100, 100)

    def show_message(text, color=(255, 0, 0), duration=120):
        nonlocal tip_text, tip_timer, tip_color
        tip_text = text
        tip_color = color
        tip_timer = duration  


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
            "Dresses": [],
            "Tops": [],
            "Pants": [],
            "Shoes": [],
        }

        for file_path in ASSETS.glob("*.png"):
            filename = file_path.stem.lower()

            if filename.startswith("hair"):
                categories_dict["Hairs"].append(file_path)
            elif filename.startswith("dress"):
                categories_dict["Dresses"].append(file_path)
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
    current_category = all_categories[0] if all_categories else "Hairs"

    cloth_buttons = []
    max_scroll = 0
    view_reat = pygame.Rect(20, 80, 350, 450)

    # closet background
    def draw_closet():
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
        button_width = 60
        button_height = 30

        for i, category in enumerate(categories):
            x_btn = 35 + i * (button_width + 5)

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

        start_x = 55
        base_y = 165
        button_width = 80
        button_height = 80
        margin_x = 20
        margin_y = 20

        for i, item in enumerate(items):
            w, h = item["image"].get_size()

            # shoes thumbnails: crop bottom area
            if category == "Shoes":

                start_x_crop = (w - button_width) // 2  
                start_y_crop = h - button_height       
            
                thumb = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                thumb.fill((0, 0, 0, 0)) 
                thumb.blit(item['image'], (0, 0), (start_x_crop, start_y_crop, button_width, button_height))
            
            elif category == "Tops":
                zoom_factor_tops = 0.3
                
                enlarged = pygame.transform.scale(item['image'], 
                    (int(w * zoom_factor_tops), int(h * zoom_factor_tops)))
                
                ew, eh = enlarged.get_size()
                
                start_x_crop = (ew - button_width) // 2   
                start_y_crop = (eh - button_height) // 2  
                
                
                thumb = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                thumb.fill((0, 0, 0, 0))  
                thumb.blit(enlarged, (0, 0), (start_x_crop, start_y_crop, button_width, button_height))
            
            elif category == "Pants":
                
                zoom_factor_pants = 0.3
                enlarged = pygame.transform.scale(item['image'], 
                    (int(w * zoom_factor_pants), int(h * zoom_factor_pants)))
                
                ew, eh = enlarged.get_size()
                
                start_x_crop = max(0, (ew - button_width) // 2)
                start_y_crop = max(0, eh - button_height)
                
                
                thumb = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                thumb.fill((0, 0, 0, 0))  
                thumb.blit(enlarged, (0, 0), (start_x_crop, start_y_crop, button_width, button_height))
            
            else:
                thumb = item["thumb"]


            row = i // 3
            col = i % 3

            x_btn = start_x + col * (button_width + margin_x)
            y_btn = base_y + row * (button_height + margin_y)

            is_selected = False
            if category == "Hairs" and hairs_index is not None and i == hairs_index:
                is_selected = True
            elif category == "Dresses" and dresses_index is not None and i == dresses_index:
                is_selected = True
            elif category == "Shoes"  and shoes_index is not None and i == shoes_index:
                is_selected = True
            elif category == "Tops"  and tops_index is not None and i == tops_index:
                is_selected = True
            elif category == "Pants"  and pants_index is not None and i == pants_index:
                is_selected = True

            cloth_buttons.append(
                {
                    "rect": pygame.Rect(x_btn, y_btn, button_width, button_height),
                    "index": i,
                    "selected": is_selected,
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

            font = pygame.font.Font(None, 22)
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
        nonlocal dresses_index, hairs_index, shoes_index, tops_index, pants_index
        nonlocal tip_text, tip_timer

        # category buttons
        for btn in category_buttons:
            if btn["rect"].collidepoint(pos):
                if btn["category"] != current_category:
                    current_category = btn["category"]
                    
                    for b in category_buttons:
                        b["selected"] = (b["category"] == current_category)
                    
                    cloth_buttons = create_cloth_buttons(current_category)
                return

        # cloth buttons
        for btn in cloth_buttons:
            if btn["rect"].collidepoint(pos):
                
                #conflict logic
                clicked_category = btn['category']
                clicked_index = btn['index']
                print(f"now state - dresses:{dresses_index}, tops:{tops_index}, pants:{pants_index}")
                
                
                # take off logic
                is_already_selected = False
                if clicked_category == "Hairs" and hairs_index is not None and clicked_index == hairs_index:
                    is_already_selected = True
                elif clicked_category == "Dresses" and dresses_index is not None and clicked_index == dresses_index:
                    is_already_selected = True
                elif clicked_category == "Tops" and tops_index is not None and clicked_index == tops_index:
                    is_already_selected = True
                elif clicked_category == "Pants" and pants_index is not None and clicked_index == pants_index:
                    is_already_selected = True
                elif clicked_category == "Shoes" and shoes_index is not None and clicked_index == shoes_index:
                    is_already_selected = True


                if is_already_selected:
                    if clicked_category == "Hairs":
                        hairs_index = None
                    elif clicked_category == "Shoes":
                        shoes_index = None
                    elif clicked_category == "Tops":
                        tops_index = None
                    elif clicked_category == "Pants":
                        pants_index = None
                    elif clicked_category == "Dresses":
                        dresses_index = None

                    cloth_buttons = create_cloth_buttons(current_category)
                    
                    tip_text = f"take off {clicked_category}"
                    tip_timer = 60
                    tip_color = (255, 255, 255)
                    return
                
                conflict = False
                wearing_tops = tops_index is not None
                wearing_pants = pants_index is not None
                wearing_dresses = dresses_index is not None


                if clicked_category == "Tops" and wearing_dresses:
                    tip_text = "not seamtime"
                    tip_timer = 120
                    tip_color = (255, 100, 100)
                    conflict = True
                    print(f"stop: {tip_text}")

                if clicked_category == "Pants" and wearing_dresses:
                    tip_text = "not seamtime"
                    tip_timer = 120
                    tip_color = (255, 100, 100)
                    conflict = True
                    print(f"stop: {tip_text}")
                
                if clicked_category == "Dresses" and (wearing_tops or wearing_pants):
                    tip_text = "not seamtime"
                    tip_timer = 120
                    tip_color = (255, 100, 100)
                    conflict = True
                    print(f"stop: {tip_text}")
                    
                if conflict:
                    return



                if clicked_category  == "Hairs":
                    hairs_index = clicked_index

                elif clicked_category  == "Dresses":
                    dresses_index = clicked_index

                elif clicked_category  == "Tops":
                    tops_index = clicked_index

                elif clicked_category  == "Pants":
                    pants_index = clicked_index

                elif clicked_category  == "Shoes":
                    shoes_index = clicked_index
                
                cloth_buttons = create_cloth_buttons(current_category)

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
        draw_closet()
        draw_category_buttons()
        draw_cloth_buttons()

        # Draw character layers
        screen.blit(body, (x, y))
        if hairs_index is not None and hairs and 0 <= hairs_index < len(hairs):
            screen.blit(hairs[hairs_index], (x, y))
        if dresses_index is not None and dresses and 0 <= dresses_index < len(dresses):
            screen.blit(dresses[dresses_index], (x, y))
        if tops_index is not None and tops and 0 <= tops_index < len(tops):
            screen.blit(tops[tops_index], (x, y))
        if pants_index is not None and pants and 0 <= pants_index < len(pants):
            screen.blit(pants[pants_index], (x, y))
        if shoes_index is not None and shoes and 0 <= shoes_index < len(shoes):
            screen.blit(shoes[shoes_index], (x, y))

        # Special messages
        special = None
        if hairs_index == 1:
            draw_glow_text_topright("Awesome ✨")
            special = "h2"
        elif hairs_index == 3:
            message = f"Now I am ready to party, {player_name}!"
            draw_glow_text_topright(message)
            special = "h4"

        if special != last_special and special is not None:
            play(sparkle_sound)
        last_special = special

        if tip_timer > 0:
            
            tip_bg = pygame.Surface((400, 50))
            tip_bg.set_alpha(200)
            tip_bg.fill((40, 40, 40))
            screen.blit(tip_bg, (WIDTH//2 - 200, 100))

            if tip_text.startswith("take off"):
                color = (255, 255, 255)  
            else:
                color = tip_color  
        
            pygame.draw.rect(screen, color, (WIDTH//2 - 200, 100, 400, 50), 3, border_radius=10)
            
            font = pygame.font.Font(None, 32)
            tip_surface = font.render(tip_text, True, color)
            tip_rect = tip_surface.get_rect(center=(WIDTH//2, 125))
            screen.blit(tip_surface, tip_rect)
            
            tip_timer -= 1
        
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