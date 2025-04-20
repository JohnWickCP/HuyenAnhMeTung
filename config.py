# config.py
import pygame
import os
import tkinter as tk

# Khởi tạo tkinter và ẩn cửa sổ
root = tk.Tk()
root.withdraw()

# Khởi tạo pygame
pygame.init()
pygame.mixer.init()

# Các hằng số
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750
TILE_SIZE = 80
TILE_MARGIN = 5
ANIMATION_SPEED = 10

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PALE_PINK = (255, 182, 193)
GREEN_BUTTON = (124, 252, 0)

# Đường dẫn
ASSETS_DIR = "HuyenAnhMeTung/Assets"
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SAVES_DIR = "saves"

FONT_PATH = os.path.join(FONTS_DIR, "segoeui.ttf")
SAVE_FILE_PATH = os.path.join(SAVES_DIR, 'puzzle_save.pkl')

# Tạo các thư mục nếu chưa tồn tại
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(SAVES_DIR, exist_ok=True)

# Khởi tạo màn hình
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Huyễn Ảnh mê tung")
clock = pygame.time.Clock()

# Tải font
try:
    font = pygame.font.Font(FONT_PATH, 36)
    small_font = pygame.font.Font(FONT_PATH, 24)
except:
    font = pygame.font.SysFont("segoeui", 36)
    small_font = pygame.font.SysFont("segoeui", 24)

# Trong config.py, phần tải âm thanh
try:
    welcome_music = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "welcome_music.mp3"))
    game_music = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "game_music.mp3"))
    victory_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "victory.wav"))
    lose_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "victory.wav"))

    # Thiết lập âm lượng
    welcome_music.set_volume(0.5)
    game_music.set_volume(0.5)
    victory_sound.set_volume(0.5)
    lose_sound.set_volume(0.5)
    
    sound_enabled = True
except Exception as e:
    print(f"Không thể tải file âm thanh: {e}. Game sẽ chạy mà không có âm thanh.")
    # Tạo đối tượng giả để tránh lỗi
    class DummySound:
        def play(self, loops=0): pass
        def stop(self): pass
        def set_volume(self, volume): pass

# Cấu hình vị trí nút
class ButtonConfig:
    # Welcome screen
    WELCOME_BUTTON_WIDTH = 250
    WELCOME_BUTTON_HEIGHT = 50
    WELCOME_BUTTON_SPACING = 20
    WELCOME_START_Y = 180
    
    # Playing screen
    PLAYING_ROW1_Y = 20
    PLAYING_ROW2_Y = 70
    PLAYING_BUTTON_WIDTH = 120
    PLAYING_BUTTON_HEIGHT = 40
    PLAYING_BUTTON_SPACING = 10
    
    # Right column
    RIGHT_COLUMN_X = SCREEN_WIDTH - 180
    RIGHT_COLUMN_Y_START = 200
    RIGHT_COLUMN_SPACING = 50
    RIGHT_COLUMN_WIDTH = 150
    RIGHT_COLUMN_HEIGHT = 40
    
    # End screen
    END_BUTTON_WIDTH = 200
    END_BUTTON_HEIGHT = 50
    END_BUTTON_Y = 500
    END_BUTTON_SPACING = 70
    
    # Duel lost screen
    DUEL_BUTTON_WIDTH = 200
    DUEL_BUTTON_HEIGHT = 50
    DUEL_PANEL_WIDTH = 700
    DUEL_PANEL_HEIGHT = 550
    DUEL_BUTTON_SPACING = 100

# Cấu hình Database
DB_CONFIG = {
    'DRIVER': '{ODBC Driver 17 for SQL Server}',
    'SERVER': 'localhost',
    'DATABASE': 'puzzle8',
    'Trusted_Connection': 'yes'
}