import pygame
import sys
import random
import re
from pathlib import Path
import json
import uuid

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


#=============================================================
# Saving the outfit
#=============================================================
SAVE_FILE = Path(__file__).parent / "players.json"

def save_outfit_to_file(player_id: str, outfit: dict):
    data = {"players": [], "selected_id": None}

    if SAVE_FILE.exists():
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    data.update(loaded)
        except: 
            pass

    players = data.get("players", [])
    target = None
    for p in players:
        if p.get("id") == player_id:
            target = p
            break

    if target is None:
        target = {"id": player_id, "name":"Unknown","outfits":[]}
        players.append(target)

    outfits = target.setdefault("outfits",[])
    incoming_id = outfit.get("outfit_id")

    if incoming_id:
        existing = next((o for o in outfits if o.get("outfit_id") == incoming_id), None)
        if existing:
            keep_name = existing.get("name")
            existing.clear()
            existing.update(outfit)
            existing["name"] = keep_name
        else:
            outfits.append(outfit)
    else:
        outfits.append(outfit)

    data["players"] = players
    
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



# ============================================================
# MAIN GAME
# ============================================================
def main_game(player, preset_outfit=None):
    body = pygame.image.load(ASSETS / "body.png").convert_alpha()

    # Auto-load base lists (used for rendering safety)
    hairs = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("hair*.png"))]
    dresses = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("dress*.png"))]
    tops = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("top*.png"))]
    pants = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("pants*.png"))]
    shoes = [pygame.image.load(p).convert_alpha() for p in sorted(ASSETS.glob("shoes*.png"))]
    backgrounds = [pygame.image.load(p).convert() for p in sorted(ASSETS.glob("background*.png"))]

    # Save feature
    save_popup = False
    overwrite_popup = False
    outfit_name_text = ""
    save_panel = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 120, 440, 240)
    save_input = pygame.Rect(save_panel.left + 30, save_panel.top + 70, save_panel.width - 60, 45)
    btn_save = pygame.Rect(WIDTH - 140, HEIGHT - 60, 120, 40)
    btn_save_ok = pygame.Rect(save_panel.left + 30, save_panel.bottom - 60, 140, 40)
    btn_save_cancel = pygame.Rect(save_panel.right - 170, save_panel.bottom - 60, 140, 40)
    overwrite_panel = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 110, 440, 220)
    btn_overwrite = pygame.Rect(overwrite_panel.left + 30, overwrite_panel.bottom - 60, 120, 40)
    btn_save_as_new = pygame.Rect(overwrite_panel.centerx - 70, overwrite_panel.bottom - 60, 140, 40)
    btn_overwrite_cancel = pygame.Rect(overwrite_panel.right - 150, overwrite_panel.bottom - 60, 120, 40)

    # Pause menu
    paused = False
    btn_pause = pygame.Rect(15, 15, 55, 45)
    pause_panel = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)
    btn_resume = pygame.Rect(pause_panel.left + 40, pause_panel.top + 90, 320, 45)
    btn_main_menu = pygame.Rect(pause_panel.left + 40, pause_panel.top + 150, 320, 45)
    btn_exit_game = pygame.Rect(pause_panel.left + 40, pause_panel.top + 210, 320, 45)

    # Character position
    x = (WIDTH - 100) // 2
    y = 0

    hairs_index = None
    dresses_index = None
    tops_index = None
    pants_index = None
    shoes_index = None
    bg_index = 0

    # Tracking loaded outfit
    current_outfit_id = None
    current_outfit_name = None

    # Tracking unsaved changes
    unsaved_popup = False
    pending_exit_action = None
    
    unsaved_panel = pygame.Rect(WIDTH//2 - 230, HEIGHT//2 - 130, 460, 260)
    btn_unsaved_save = pygame.Rect(unsaved_panel.left + 30, unsaved_panel.bottom - 70, 120, 45)
    btn_unsaved_no = pygame.Rect(unsaved_panel.left + 155, unsaved_panel.bottom - 70, 150, 45)
    btn_unsaved_cancel = pygame.Rect(unsaved_panel.right - 150, unsaved_panel.bottom - 70, 120, 45)

    def current_state():
        return{
            "hair": hairs_index,
            "dress": dresses_index,
            "top": tops_index,
            "pants": pants_index,
            "shoes": shoes_index,
            "background": bg_index,
        }
    
    last_saved_state = current_state()
    dirty = False

    if preset_outfit:
        hairs_index = preset_outfit.get("hair")
        dresses_index = preset_outfit.get("dress")
        tops_index = preset_outfit.get("top")
        pants_index = preset_outfit.get("pants")
        shoes_index = preset_outfit.get("shoes")
        bg_index = preset_outfit.get("background", 0)
        # Safety: clamp invalid indices to None/ 0
        if hairs_index is not None and not (0 <= hairs_index < len(hairs)): hairs_index = None
        if dresses_index is not None and not (0 <= dresses_index < len(dresses)): dresses_index = None
        if tops_index is not None and not (0 <= tops_index < len(tops)): tops_index = None
        if pants_index is not None and not (0 <= pants_index < len(pants)): pants_index = None
        if shoes_index is not None and not (0 <= shoes_index < len(shoes)): shoes_index = None
        if not (0 <= bg_index < len(backgrounds)): bg_index = 0

        current_outfit_id = preset_outfit.get("outfit_id")
        current_outfit_name = preset_outfit.get("name")

        last_saved_state = current_state()
        dirty = False

    def request_exit(action):
        nonlocal unsaved_popup, pending_exit_action
        if dirty:
            unsaved_popup = True
            pending_exit_action = action
            return None
        else:
            return action
        


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
    view_rect = pygame.Rect(20, 80, 350, 450)

    # closet background
    def draw_closet():
        rect = view_rect
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
        nonlocal dirty

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
                    dirty = (current_state() != last_saved_state)
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
                dirty = (current_state() != last_saved_state)
                return

    # create buttons
    create_category_buttons()
    cloth_buttons = create_cloth_buttons(current_category)

    # main running
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                res = request_exit("quit")
                if res:
                    return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Unsaved_popup buttons
                if unsaved_popup:
                    if btn_unsaved_save.collidepoint(event.pos):
                        if current_outfit_id is not None:
                            overwrite_popup = True
                        else:
                            save_popup = True
                            outfit_name_text = ""
                        unsaved_popup = False
                        continue
                    if btn_unsaved_no.collidepoint(event.pos):
                        if pending_exit_action == "start menu":
                            return "start menu"
                        if pending_exit_action == "quit":
                            return "quit"
                    if btn_unsaved_cancel.collidepoint(event.pos):
                        unsaved_popup = False
                        pending_exit_action = None
                        continue
                    continue
                # Save_poup buttons
                if save_popup:
                    if btn_save_ok.collidepoint(event.pos):
                        outfit_name = outfit_name_text.strip()

                        if outfit_name != "":
                            # Build a outfit dictionary
                            outfit = {
                                "outfit_id": current_outfit_id or uuid.uuid4().hex,
                                "name": outfit_name,
                                "hair": hairs_index,
                                "dress": dresses_index,
                                "top": tops_index,
                                "pants": pants_index,
                                "shoes": shoes_index,
                                "background": bg_index
                            }
                            save_outfit_to_file(player["id"], outfit)
                            last_saved_state = current_state()
                            dirty =False
                        if pending_exit_action == "start menu":
                            return "start menu"
                        elif pending_exit_action == "quit":
                            return "quit"
                        current_outfit_id = outfit["outfit_id"]
                        current_outfit_name = outfit["name"]
                        save_popup = False
                        outfit_name_text = ""
                    elif btn_save_cancel.collidepoint(event.pos):
                        save_popup = False
                        outfit_name_text = ""
                    continue
                # Overwrite_popup
                if overwrite_popup:
                    if btn_overwrite.collidepoint(event.pos):
                        outfit = {
                            "outfit_id": current_outfit_id,
                            "name": current_outfit_name,
                            "hair": hairs_index,
                            "dress": dresses_index,
                            "top": tops_index,
                            "pants": pants_index,
                            "shoes": shoes_index,
                            "background": bg_index
                        }
                        save_outfit_to_file(player["id"], outfit)
                        last_saved_state = current_state()
                        dirty = False
                        overwrite_popup = False
                        if pending_exit_action == "start menu":
                            return "start menu"
                        elif pending_exit_action == "quit":
                            return "quit"
                        current_outfit_id = outfit["outfit_id"]
                        current_outfit_name = outfit["name"]
                    elif btn_save_as_new.collidepoint(event.pos):
                        overwrite_popup = False
                        current_outfit_id = None
                        current_outfit_name = None
                        save_popup = True
                        outfit_name_text = ""
                    elif btn_overwrite_cancel.collidepoint(event.pos):
                        overwrite_popup = False
                    continue
                # Pause menu buttons
                if paused:
                    if btn_resume.collidepoint(event.pos):
                        paused = False
                        continue
                    if btn_main_menu.collidepoint(event.pos):
                        res = request_exit("start menu")
                        if res: 
                            return "start menu"
                    if btn_exit_game.collidepoint(event.pos):
                        res = request_exit("quit")
                        if res:
                            return "quit"
                    continue
                # Pause menu
                if btn_pause.collidepoint(event.pos) and not save_popup:
                    paused = True
                    continue
                # Save_popup
                if btn_save.collidepoint(event.pos):
                    if current_outfit_id is not None:
                        overwrite_popup = True
                    else:
                        save_popup = True
                        outfit_name_text = ""
                    continue

                handle_click(event.pos)

            # Keyboard navigations
            if event.type == pygame.KEYDOWN:
                # Unsaved_popup
                if unsaved_popup:
                    if event.key == pygame.K_ESCAPE:
                        unsaved_popup = False
                        pending_exit_action = None
                    continue
                # Save popup
                if save_popup:
                    if event.key == pygame.K_BACKSPACE:
                        outfit_name_text = outfit_name_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        outfit_name = outfit_name_text.strip()

                        if outfit_name != "":
                            # Build a outfit dictionary
                            outfit = {
                                "outfit_id": current_outfit_id or uuid.uuid4().hex,
                                "name": outfit_name,
                                "hair": hairs_index,
                                "dress": dresses_index,
                                "top": tops_index,
                                "pants": pants_index,
                                "shoes": shoes_index,
                                "background": bg_index
                            }
                            save_outfit_to_file(player["id"], outfit)
                            last_saved_state = current_state()
                            dirty =False
                        if pending_exit_action == "start menu":
                            return "start menu"
                        elif pending_exit_action == "quit":
                            return "quit"
                        current_outfit_id = outfit["outfit_id"]
                        current_outfit_name = outfit["name"]
                        save_popup = False
                        outfit_name_text = ""
                    else:
                        if len(outfit_name_text) < 20 and event.unicode.isprintable():
                            outfit_name_text += event.unicode
                    continue
                #Escape key
                if event.key == pygame.K_ESCAPE:
                    if save_popup:
                        save_popup = False
                        outfit_name_text = ""
                    elif paused:
                        paused = False
                    else:
                        paused = True
                    continue

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
            message = f"Now I am ready to party, {player['name']}!"
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

        # Darw save button
        draw_button(btn_save, "Save")

        # Darw overwrite_popup
        if overwrite_popup:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0,0))

            pygame.draw.rect(screen, (255, 255, 255), overwrite_panel, border_radius = 12)
            pygame.draw.rect(screen, (0, 0, 0), overwrite_panel, 2, border_radius = 12)

            label = ui_font.render("Overwrite this saved outfit?", True, (0, 0, 0))
            screen.blit(label, label.get_rect(center = (overwrite_panel.centerx, overwrite_panel.top + 75)))

            draw_button(btn_overwrite, "Overwrite")
            draw_button(btn_save_as_new, "Save as New")
            draw_button(btn_overwrite_cancel, "Cancel")

        # Darw save_popup
        if save_popup:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay,(0,0))

            pygame.draw.rect(screen, (255, 255, 255), save_panel, border_radius = 12)
            pygame.draw.rect(screen, (0, 0, 0), save_panel, 2, border_radius = 12)
            label = ui_font.render("Name your outfit:", True, (0, 0, 0))
            screen.blit(label, (save_panel.left + 30, save_panel.top + 30))

            pygame.draw.rect(screen, (255, 255, 255), save_input, border_radius = 10)
            pygame.draw.rect(screen, (0, 0, 0), save_input, 2, border_radius = 10)

            typed = ui_font.render(outfit_name_text, True, (0, 0, 0))
            screen.blit(typed, (save_input.x + 10, save_input.y + 10))

            draw_button(btn_save_ok, "OK")
            draw_button(btn_save_cancel, "Cancel")

        # Darw pause menu button
        draw_button(btn_pause, "Menu")

        # Draw pause menu panel
        if paused and not save_popup and not overwrite_popup:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay,(0,0))

            pygame.draw.rect(screen, (255, 255, 255), pause_panel, border_radius = 14)
            pygame.draw.rect(screen, (0, 0, 0), pause_panel, 2, border_radius = 14)

            title = title_font.render("Menu", True, (0, 0, 0))
            screen.blit(title, title.get_rect(center = (pause_panel.centerx, pause_panel.top + 45)))

            draw_button(btn_resume, "Resume")
            draw_button(btn_main_menu, "Main Menu")
            draw_button(btn_exit_game, "Exit Game")
        
        # Draw save check in panel
        if unsaved_popup:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            pygame.draw.rect(screen, (255, 255, 255), unsaved_panel, border_radius = 14)
            pygame.draw.rect(screen, (0, 0, 0), unsaved_panel, 2, border_radius = 14)

            msg = ui_font.render("Save before leaving?", True, (0, 0, 0))
            screen.blit(msg, msg.get_rect(center = (unsaved_panel.centerx, unsaved_panel.top + 95)))

            draw_button(btn_unsaved_save, "Save")
            draw_button(btn_unsaved_no, "Don't Save")
            draw_button(btn_unsaved_cancel, "Cancel")

        pygame.display.flip()
        clock.tick(60)
    return "quit"
