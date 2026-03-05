import pygame
import sys
import json
from pathlib import Path
from main_scene import main_game
import uuid

pygame.init()


# Globals
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dress Up Game")
clock = pygame.time.Clock()
start_popup = None  # None, "players", "archive"
SAVE_FILE = Path(__file__).parent / "players.json"
renaming = False
rename_text = ""
archive_selected_index = None
archive_renaming = False
archive_rename_text = ""

# Colors
TEXT = (0, 0, 0)
BTN = (245, 245, 245)
BTN_HOVER = (220, 220, 220)

ASSETS = Path(__file__).parent / "assets"

start_bg = pygame.image.load(ASSETS / "start_bg.png").convert()

# Button Image
button_img_raw = pygame.image.load(ASSETS / "btn.png").convert_alpha()
scale_factor = 0.75 
new_w = int(button_img_raw.get_width() * scale_factor)
new_h = int(button_img_raw.get_height() * scale_factor)
button_img = pygame.transform.smoothscale(button_img_raw, (new_w, new_h))
BTN_W, BTN_H = button_img.get_size()
BTN_GAP = 16
button_small = pygame.transform.smoothscale(
    button_img_raw,
    (int(button_img_raw.get_width() * 0.45),
     int(button_img_raw.get_height() * 0.45))
)

# font = pygame.font.SysFont(None, 28)
font = pygame.font.Font(ASSETS / "IndieFlower-Regular.ttf", 28)
btn_font = pygame.font.Font(ASSETS / "IndieFlower-Regular.ttf", 40)
title_font = pygame.font.Font(ASSETS / "IndieFlower-Regular.ttf", 55)

# Buttons (rectangles)
btn_start = pygame.Rect(120, 240, BTN_W, BTN_H)
btn_archive = pygame.Rect(120, 240 + (BTN_H + BTN_GAP)*1, BTN_W, BTN_H)
btn_player = pygame.Rect(120, 240 + (BTN_H + BTN_GAP)*2, BTN_W, BTN_H)
popup_rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 180, 500, 360)
btn_popup_close = pygame.Rect(popup_rect.right - 45, popup_rect.top + 10, 35, 35)
btn_add_player = pygame.Rect(popup_rect.left + 30, popup_rect.top + 90, 160, 40)
btn_rename_player = pygame.Rect(popup_rect.left + 195, popup_rect.top + 90, 130, 40)
btn_delete_player = pygame.Rect(popup_rect.left + 345, popup_rect.top + 90, 130, 40)
btn_players_done = pygame.Rect(popup_rect.centerx - 70, popup_rect.bottom - 60, 140, 40)
rename_panel = pygame.Rect(popup_rect.left + 20, popup_rect.top + 70, popup_rect.width - 40, 150)
rename_input = pygame.Rect(rename_panel.left + 20, rename_panel.top + 20, rename_panel.width - 40, 45)
btn_rename_save = pygame.Rect(rename_panel.left + 20, rename_panel.bottom - 55, 120, 40)
btn_rename_back = pygame.Rect(rename_panel.right - 140, rename_panel.bottom - 55, 120, 40)
btn_archive_delete = pygame.Rect(popup_rect.right - 160, popup_rect.bottom - 60, 120, 40)
btn_archive_rename = pygame.Rect(popup_rect.left + 40, popup_rect.bottom - 60, 120, 40)
btn_archive_load = pygame.Rect(popup_rect.left + 190, popup_rect.bottom - 60, 120, 40)
archive_rename_panel = pygame.Rect(popup_rect.left + 40, popup_rect.top + 100, popup_rect.width - 80, 140)
archive_rename_input = pygame.Rect(archive_rename_panel.left + 20, archive_rename_panel.top + 45, archive_rename_panel.width - 40, 40)
btn_archive_rename_ok = pygame.Rect(archive_rename_panel.left + 20, archive_rename_panel.bottom - 50, 120, 35)
btn_archive_rename_back = pygame.Rect(archive_rename_panel.right - 140, archive_rename_panel.bottom - 50, 120, 35)

btn_music = pygame.Rect(WIDTH - 110, 20, 40, 40)
btn_exit = pygame.Rect(WIDTH - 160, 20, 40, 40)

def draw_button(rect, label):
    mouse = pygame.mouse.get_pos()
    color = BTN_HOVER if rect.collidepoint(mouse) else BTN
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=8)
    text = font.render(label, True, TEXT)
    screen.blit(text, text.get_rect(center=rect.center))

def draw_paper_button(rect, label):
    mouse = pygame.mouse.get_pos()
    hover = rect.collidepoint(mouse)
    if hover and start_popup is None:
        lift = -4 
    else: 
        lift = 0

    screen.blit(button_img, (rect.x, rect.y + lift))

    txt = btn_font.render(label, True, (60, 61, 60))
    screen.blit(txt, txt.get_rect(center=(rect.centerx, rect.centery + lift)))

def draw_small_paper_button(rect, label):
    global font
    mouse = pygame.mouse.get_pos()
    hover = rect.collidepoint(mouse)
    lift = - 2 if hover else 0
    img_rect = button_small.get_rect(center = rect.center)
    img_rect.y += lift
    screen.blit(button_small, img_rect.topleft)
    txt = font.render(label, True, (60, 61, 60))
    screen.blit(txt, txt.get_rect(center = (img_rect.centerx, img_rect.centery)))

# Player profile persistence
def save_players(players, selected_player):
    data = {
        "players": players,
        "selected_id": selected_player["id"] if selected_player else None
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_players():
    if not SAVE_FILE.exists():
        return [], None
    
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        players = data.get("players", [])
        selected_id = data.get("selected_id")

        # selected_player must be an object from the players list
        selected_player = None
        if selected_id:
            for p in players:
                if p.get("id") == selected_id:
                    selected_player = p
                    break

        # Safety: if there are players but none selected, pick the first one
        if players and selected_player is None:
            selected_player = players[0]

        return players, selected_player
    
    except Exception as e:
        print("Failed to load players.json", e)
        return [], None

players, selected_player = load_players()

# Deleting a player
def delete_selected_player():
    global selected_player
    if selected_player is not None:
        del_index = players.index(selected_player)
        players.remove(selected_player)
        # updating the selection safely
        if players:
            new_index = min(del_index, len(players) - 1)
            selected_player = players[new_index]
        else:
            selected_player = None
        save_players(players, selected_player)

# Deleting an outfit
def delete_selected_outfit():
    global archive_selected_index
    if(
        selected_player is not None and
        archive_selected_index is not None and
        0 <= archive_selected_index < len(selected_player.get("outfits", []))
    ):
        del selected_player["outfits"][archive_selected_index]
        outfits = selected_player.get("outfits", [])
        if outfits:
            archive_selected_index = min(archive_selected_index, len(outfits) - 1)
        else:
            archive_selected_index = None
        save_players(players, selected_player)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse = pygame.mouse.get_pos()
            outfits = selected_player.get("outfits", []) if selected_player else []
            if start_popup is None and not renaming and not archive_renaming:
                # Start button
                if btn_start.collidepoint(mouse):
                    if selected_player is None:
                        if not players: # Starting a game with no players
                            players.append({"id":uuid.uuid4().hex,"name":"Player 1", "outfits":[]})
                        selected_player = players[0]
                    # Loading the main game
                    result = main_game(selected_player)
                    if result == "start menu":
                        players, selected_player = load_players()

                        # Reset archive selection safely
                        outfits = selected_player.get("outfits", []) if selected_player else []
                        archive_selected_index = 0 if outfits else None
                        # UI clean up
                        start_popup = None
                        renaming = False
                        rename_text = ""
                        archive_renaming = False
                        archive_rename_text = ""
                        continue
                    else:
                        running = False
                # Archive button
                elif btn_archive.collidepoint(mouse):
                    start_popup = "archive"
                    outfits = selected_player.get("outfits", []) if selected_player else []
                    archive_selected_index = 0 if outfits else None
                # Players button
                elif btn_player.collidepoint(mouse):
                    start_popup = "players"
                # Music button
                elif btn_music.collidepoint(mouse):
                    print("Music button clicked")
                #Exit button
                elif btn_exit.collidepoint(mouse):
                    print("Exit button clicked")
                    running = False
                continue
            # buttons inside renaming_panel
            if renaming:
                    if btn_rename_save.collidepoint(mouse):
                        new_name = rename_text.strip()
                        if new_name and selected_player is not None:
                            selected_player["name"] = new_name
                            save_players(players, selected_player)
                            renaming = False
                            rename_text = ""
                            continue
                    if btn_rename_back.collidepoint(mouse):
                        renaming = False
                        rename_text = ""
                        continue
            # Start menu logic    
            if start_popup is not None:
                if btn_popup_close.collidepoint(mouse):
                    start_popup = None
                    archive_selected_index = None
                    archive_renaming = False
                    archive_rename_text = ""
                    renaming = False
                    rename_text = ""
                    continue
            
            if start_popup == "archive" and selected_player is not None:
                # Renaming an outfit
                if btn_archive_rename.collidepoint(mouse):
                    if(
                        selected_player is not None and
                        archive_selected_index is not None and
                        0 <= archive_selected_index < len(selected_player.get("outfits", []))
                    ):
                        archive_renaming = True
                        archive_rename_text = selected_player["outfits"][archive_selected_index].get("name","")
                        continue
                if archive_renaming:
                    if btn_archive_rename_ok.collidepoint(mouse):
                        new_name = archive_rename_text.strip()
                        if(
                            new_name and 
                            selected_player is not None and
                            archive_selected_index is not None and
                            0 <= archive_selected_index < len(selected_player.get("outfits", []))
                        ):
                            selected_player["outfits"][archive_selected_index]["name"] = new_name
                            save_players(players, selected_player)
                        archive_renaming = False
                        archive_rename_text = ""
                        continue
                    if btn_archive_rename_back.collidepoint(mouse):
                        archive_renaming = False
                        archive_rename_text = ""
                        continue
                # Deleting an outfit
                if btn_archive_delete.collidepoint(mouse) and not archive_renaming:
                    delete_selected_outfit()
                    continue
                # Loading an outfit
                if btn_archive_load.collidepoint(mouse) and not archive_renaming:
                    if (
                        selected_player is not None and
                        archive_selected_index is not None and
                        0 <= archive_selected_index < len(selected_player.get("outfits", []))
                    ):
                        outfit_to_load = outfits[archive_selected_index]
                        result = main_game(selected_player, outfit_to_load)
                        if result == "start menu":
                            players, selected_player = load_players()
    
                            # Reset archive selection safely
                            outfits = selected_player.get("outfits", []) if selected_player else []
                            archive_selected_index = 0 if outfits else None
                            # UI clean up
                            start_popup = None
                            renaming = False
                            rename_text = ""
                            archive_renaming = False
                            archive_rename_text = ""
                            continue
                        else:
                            running = False
                    continue
                #Selecting an outfit
                if not archive_renaming: 
                    start_y = popup_rect.top + 120
                    row_h = 40

                    for i, outfit in enumerate(outfits):
                        row_rect = pygame.Rect(popup_rect.left + 30, start_y + i * row_h, popup_rect.width - 60, row_h)
                        if row_rect.collidepoint(mouse):
                            archive_selected_index = i
                            break

            if start_popup == "players":
                # Renaming a player
                if btn_rename_player.collidepoint(mouse):
                    if selected_player is not None:
                        renaming = True
                        rename_text = selected_player["name"] #start with the current name.
                        continue
                # Adding a new player
                if btn_add_player.collidepoint(mouse):
                    new_name = f"Player {len(players) + 1}"
                    new_player = {
                        "id": uuid.uuid4().hex,
                        "name": new_name,
                        "outfits": []
                    }
                    players.append(new_player)
                    selected_player = new_player
                    save_players(players, selected_player)
                    continue
                # Deleting a player
                if btn_delete_player.collidepoint(mouse):
                    delete_selected_player()
                    continue
                # Selecting a player
                if btn_players_done.collidepoint(mouse):
                    start_popup = None
                    renaming = False
                    rename_text =""
                    continue
                start_y = popup_rect.top + 150
                row_h = 30

                selected = False
                for i, player in enumerate(players):
                    row_rect = pygame.Rect(
                        popup_rect.left + 30,
                        start_y + i * row_h,
                        popup_rect.width - 60,
                        row_h
                    )
                    if row_rect.collidepoint(mouse):
                        selected_player = player
                        save_players(players, selected_player)
                        selected = True
                        break
                
                if selected:
                    continue

        # Keyboard input
        if event.type == pygame.KEYDOWN:
            # Keyboard input of archive panel
            if start_popup == "archive":
                outfits = selected_player.get("outfits", []) if selected_player else []
                # Arrow key navigation
                if selected_player is not None and not archive_renaming and outfits:
                    if archive_selected_index is None:
                        archive_selected_index = 0

                    if event.key == pygame.K_DOWN:
                        archive_selected_index = min(archive_selected_index + 1, len(outfits) - 1)
                
                    elif event.key == pygame.K_UP:
                        archive_selected_index = max(archive_selected_index - 1, 0)
                # Renaming keyboard input
                if archive_renaming:
                    if event.key == pygame.K_ESCAPE:
                        archive_renaming = False
                        archive_rename_text = ""

                    elif event.key == pygame.K_RETURN:
                        new_name = archive_rename_text.strip()
                        if (
                            new_name and
                            selected_player is not None and
                            archive_selected_index is not None and
                            0 <= archive_selected_index < len(selected_player.get("outfits", []))
                        ):
                            selected_player["outfits"][archive_selected_index]["name"] = new_name
                            save_players(players, selected_player)
                            archive_renaming = False
                            archive_rename_text = ""

                    elif event.key == pygame.K_BACKSPACE:
                        archive_rename_text = archive_rename_text[:-1]

                    else:
                        if len(archive_rename_text) < 20 and event.unicode.isprintable():
                            archive_rename_text += event.unicode
                # Keyboard input when deleting an outfit
                else:
                    if event.key == pygame.K_DELETE:
                        delete_selected_outfit()
                        continue

            # Keyboard input of players panel
            if start_popup == "players":
                # Arrow key navigation
                if players and not renaming:
                    current_index = players.index(selected_player) if selected_player in players else 0

                    if event.key == pygame.K_DOWN:
                        new_index = min(current_index + 1, len(players) - 1)
                        selected_player = players[new_index]
                        save_players(players, selected_player)

                    elif event.key == pygame.K_UP:
                        new_index = max(current_index - 1, 0)
                        selected_player = players[new_index]
                        save_players(players, selected_player)  
                # Keyboard input when renaming
                if renaming:
                    if event.key == pygame.K_ESCAPE:
                        renaming = False
                        rename_text = ""

                    elif event.key == pygame.K_RETURN:
                        new_name = rename_text.strip()
                        if new_name and selected_player is not None:
                            selected_player["name"] = new_name
                            save_players(players, selected_player)
                            renaming = False
                            rename_text = ""

                    elif event.key == pygame.K_BACKSPACE:
                        rename_text = rename_text[:-1]

                    else:
                        if len(rename_text) < 18 and event.unicode.isprintable():
                            rename_text += event.unicode
                # Keyboard input when deleting a player
                else:
                    if event.key == pygame.K_DELETE:
                        delete_selected_player()
                        continue

    # Start menu drawing 
    screen.blit(start_bg, (0,0))

    title = title_font.render("Barbie Dress Up", True, (60, 61, 60))
    shadow = title_font.render("Barbie Dress Up", True, (190, 190, 190))
    column_center_x = btn_start.centerx
    title_rect = title.get_rect(center = (column_center_x, 190))
    screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
    screen.blit(title, title_rect)

    draw_paper_button(btn_start, "Start")
    draw_paper_button(btn_archive, "Archive")
    draw_paper_button(btn_player, "Players")
    draw_button(btn_music, "M")
    draw_button(btn_exit, "X")

    # Popup menu drawing
    if start_popup is not None:
        #dark overlay behind popup
        overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120)) #transparant black
        screen.blit(overlay, (0, 0))

        #popup panel
        pygame.draw.rect(screen, (255, 255, 255), popup_rect, border_radius = 16)
        pygame.draw.rect(screen , (0, 0, 0), popup_rect, 2, border_radius = 16)

        #close button
        draw_button(btn_popup_close, "X")

        #popup title
        if start_popup == "players":
            t = font.render("Players", True, TEXT)
            screen.blit(t, t.get_rect(center = (popup_rect.centerx, popup_rect.top + 50)))

            draw_small_paper_button(btn_add_player, "Add Player")
            draw_small_paper_button(btn_rename_player, "Rename")
            draw_small_paper_button(btn_delete_player, "Delete")
            draw_small_paper_button(btn_players_done, "Done")

            # Draw rename input popup
            if renaming:
                pygame.draw.rect(screen, (255, 255, 255), rename_panel, border_radius=10)
                pygame.draw.rect(screen, (0, 0, 0), rename_panel, 2, border_radius=10)

                label = font.render("Rename Player", True, TEXT)
                screen.blit(label, (rename_panel.left + 20, rename_panel.top -30))

                pygame.draw.rect(screen, (255, 255, 255), rename_input, border_radius=10)
                pygame.draw.rect(screen, (0, 0, 0), rename_input, 2, border_radius=10)

                txt = font.render(rename_text, True, TEXT)
                screen.blit(txt, (rename_input.x + 10, rename_input.y + 8))

                draw_small_paper_button(btn_rename_save, "Save")
                draw_small_paper_button(btn_rename_back, "Back")
            
            else:
                # Draw player list
                start_y = popup_rect.top + 150
                for i, player in enumerate(players):
                    line = player["name"]
                    if player is selected_player:
                        line = "> " + line #simple selection marker
                    
                    txt = font.render(line, True, TEXT)
                    screen.blit(txt, (popup_rect.left + 40, start_y + i*30)) 

        elif start_popup == "archive":
            t = font.render("Archive", True, TEXT)
            screen.blit(t, t.get_rect(center = (popup_rect.centerx, popup_rect.top + 50)))
            
            draw_small_paper_button(btn_archive_delete, "Delete")
            draw_small_paper_button(btn_archive_rename, "Rename")
            draw_small_paper_button(btn_archive_load, "Load")

            # Draw archive list
            if selected_player is None:
                msg = font.render("No Player selected.", True, TEXT)
                screen.blit(msg, (popup_rect.left + 40, popup_rect.top + 120))
            else:
                # Header
                header_font = pygame.font.Font(ASSETS / "IndieFlower-Regular.ttf", 24)
                header_text = f"{selected_player['name']}'s Outfits"
                header = header_font.render(header_text, True, (60, 60, 60))
                screen.blit(header, (popup_rect.left + 40, popup_rect.top + 95))
                # Divider line
                pygame.draw.line(
                    screen,
                    (180, 180, 180),
                    (popup_rect.left + 40, popup_rect.top + 120),
                    (popup_rect.right - 40, popup_rect.top + 120),
                    1
                    )

                if not outfits:
                    msg = font.render("No outfits saved.", True, TEXT)
                    screen.blit(msg, (popup_rect.left + 40, popup_rect.top + 130))
                else:
                    start_y = popup_rect.top + 135
                    for i, outfit in enumerate(outfits):
                        name = outfit.get("name", f"Outfit {i + 1}")

                        # Highlight selected row
                        row_rect = pygame.Rect(popup_rect.left + 30, start_y + i*30, popup_rect.width - 60, 30)
                        if archive_selected_index == i:
                            pygame.draw.rect(screen, (220, 240, 255), row_rect, border_radius = 6)
                        
                        line = name if archive_selected_index != i else ">" + name
                        txt = font.render(line, True, TEXT)
                        screen.blit(txt, (popup_rect.left + 40, start_y + i*30))

            # Draw archive rename panel
            if archive_renaming:
                pygame.draw.rect(screen, (255, 255, 255), archive_rename_panel, border_radius = 10)
                pygame.draw.rect(screen, (0, 0, 0), archive_rename_panel, 2, border_radius = 10)

                label = font.render("Rename outfit", True, TEXT)
                screen.blit(label, (archive_rename_panel.left + 20, archive_rename_panel.top + 10))

                pygame.draw.rect(screen, (255, 255, 255), archive_rename_input, border_radius = 8)
                pygame.draw.rect(screen, (0, 0, 0), archive_rename_input, 2, border_radius = 8)

                txt = font.render(archive_rename_text, True, TEXT)
                screen.blit(txt, (archive_rename_input.x + 10, archive_rename_input.y + 8))

                draw_small_paper_button(btn_archive_rename_ok, "Save")
                draw_small_paper_button(btn_archive_rename_back, "Back")
            
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
