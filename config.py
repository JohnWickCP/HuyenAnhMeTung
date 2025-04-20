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
TILE_MARGIN = 4
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
LIGHT_BLUE = (135, 206, 250)  # Sky blue, tươi sáng hơn
PALE_PINK = (255, 204, 204)   # Hồng nhạt dịu hơn
GREEN_BUTTON = (50, 205, 50)  # Xanh lá cây nổi bật hơn
AI_BOARD_BG = (255, 245, 238) # Màu nền nhẹ cho bảng AI

# Cấu hình hiển thị số trên ô khi sử dụng hình ảnh
SHOW_NUMBERS_WITH_IMAGE = False  # False: ẩn số khi dùng hình ảnh, True: hiển thị số

# Đường dẫn
ASSETS_DIR = "HuyenAnhMeTung/Assets" # Bạn nên xóa "HuyenAnhMeTung" nếu bạn đang chạy từ thư mục gốc của dự án
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SAVES_DIR = "saves"

FONT_PATH = os.path.join(FONTS_DIR, "segoeui.ttf")
SAVE_FILE_PATH = os.path.join(SAVES_DIR, 'puzzle_save.pkl')
DEFEAT_IMAGE_PATH = os.path.join("HuyenAnhMeTung/Assets/images", "thua.jpg")  # Đường dẫn ảnh thua cuộc

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
    welcome_music = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "a.mp3"))
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

# Cấu hình vị trí nút và các thông số giao diện
class ButtonConfig:
    # Welcome screen
    WELCOME_BUTTON_WIDTH = 250
    WELCOME_BUTTON_HEIGHT = 50
    WELCOME_BUTTON_SPACING = 20
    WELCOME_START_Y = 180
    WELCOME_PANEL_WIDTH = 700
    WELCOME_PANEL_HEIGHT = 550
    WELCOME_PANEL_Y = 70
    WELCOME_TITLE_Y_OFFSET = 30
    WELCOME_TITLE_SHADOW_OFFSET = 3

    # Playing screen
    PLAYING_ROW1_Y = 20
    PLAYING_ROW2_Y = 70
    PLAYING_BUTTON_WIDTH = 120
    PLAYING_BUTTON_HEIGHT = 40
    PLAYING_BUTTON_SPACING = 10
    PLAYING_BOARD_Y = 150
    PLAYING_MOVE_TIME_Y = 550
    PLAYING_MOVE_WIDTH = 100
    PLAYING_MOVE_HEIGHT = 40
    PLAYING_MOVE_X = 570
    PLAYING_TIME_X = 680
    PLAYING_SOLUTION_TEXT_X = 50
    PLAYING_SOLUTION_TEXT_Y = 130

    # Right column
    RIGHT_COLUMN_X = SCREEN_WIDTH - 180
    RIGHT_COLUMN_Y_START = 250
    RIGHT_COLUMN_SPACING = 70
    RIGHT_COLUMN_WIDTH = 150
    RIGHT_COLUMN_HEIGHT = 40

    # End screen
    END_BUTTON_WIDTH = 200
    END_BUTTON_HEIGHT = 50
    END_BUTTON_Y = 500
    END_BUTTON_SPACING = 70
    END_TITLE_Y = 70
    END_SUBTITLE_Y = 130
    END_LEFT_PANEL_X = 150
    END_RIGHT_PANEL_X = SCREEN_WIDTH - 150 - 350
    END_PANEL_Y = 180
    END_PANEL_WIDTH = 350
    END_PANEL_HEIGHT = 320
    END_PANEL_TITLE_HEIGHT = 60
    END_INFO_X_OFFSET = 30
    END_INFO_Y_START = END_PANEL_Y + 70
    END_INFO_SPACING = 40
    END_LINE_OFFSET = 20
    END_RESULT_BOARD_Y_OFFSET = 20
    END_MIN_TILE_SIZE = 20

    # Duel lost allocate
    DUEL_BUTTON_WIDTH = 200
    DUEL_BUTTON_HEIGHT = 50
    DUEL_PANEL_WIDTH = 700
    DUEL_PANEL_HEIGHT = 550
    DUEL_BUTTON_SPACING = 100
    DUEL_BUTTON_Y_OFFSET = 70
    DUEL_TITLE_Y_OFFSET = -50
    DUEL_IMAGE_WIDTH = 240
    DUEL_IMAGE_HEIGHT = 240
    DUEL_IMAGE_Y_OFFSET = 100
    DUEL_SUBTITLE_Y_OFFSET = 350
    DUEL_STAT_SPACING = 40
    DUEL_MESSAGE_Y_OFFSET = 120

    # Duel vs AI screen
    DUEL_PLAYER_X = SCREEN_WIDTH // 3  # Trung tâm bảng người chơi
    DUEL_AI_X = 2 * SCREEN_WIDTH // 3  # Trung tâm bảng AI
    DUEL_BOARD_Y = 160  # Vị trí Y của cả hai bảng
    DUEL_TITLE_Y_OFFSET = 90
    DUEL_TARGET_X = SCREEN_WIDTH - 100  # Trung tâm bảng mục tiêu
    DUEL_TARGET_Y = 120  # Vị trí Y của bảng mục tiêu
    DUEL_STAT_WIDTH = 200  # Chiều rộng ô thống kê
    DUEL_STAT_HEIGHT = 50  # Chiều cao ô thống kê
    DUEL_STAT_Y = 650  # Vị trí Y của các ô thống kê
    DUEL_PLAYER_STAT_X = 50  # Vị trí X của thống kê người chơi
    DUEL_AI_STAT_X = SCREEN_WIDTH - 250  # Vị trí X của thống kê AI
    DUEL_TIME_STAT_X = SCREEN_WIDTH // 2 - 100  # Vị trí X của thời gian
    DUEL_TURN_TEXT_Y_OFFSET = 50

    # How to play screen
    HOW_TO_PLAY_TITLE_Y = 50
    HOW_TO_PLAY_TEXT_X_OFFSET = SCREEN_WIDTH // 2 - 300
    HOW_TO_PLAY_TEXT_Y_START = 120
    HOW_TO_PLAY_TEXT_SPACING = 40
    HOW_TO_PLAY_BUTTON_Y = 600

    # Settings screen
    SETTINGS_TITLE_Y = 50
    SETTINGS_VOLUME_TEXT_Y = 150
    SETTINGS_SOUND_TEXT_Y = 200
    SETTINGS_AI_SPEED_TEXT_Y = 250
    SETTINGS_BAR_Y = 300
    SETTINGS_BAR_WIDTH = 400
    SETTINGS_BAR_HEIGHT = 30
    SETTINGS_AI_SPEED_BUTTON_Y = 440
    SETTINGS_BACK_BUTTON_Y = 500

# Cấu hình AI
class AIConfig:
    DEFAULT_MOVE_INTERVAL = 0.3  # Khoảng thời gian mặc định giữa các bước di chuyển của AI (giây)
    MIN_MOVE_INTERVAL = 0.05     # Khoảng thời gian tối thiểu giữa các bước
    MAX_MOVE_INTERVAL = 1.0      # Khoảng thời gian tối đa giữa các bước
    MOVE_INTERVAL_STEP = 0.05    # Bước thay đổi khi tăng/giảm tốc độ AI
    PLAYER_TURN_THRESHOLD = 3    # Số lượt người chơi trước khi AI bắt đầu giải
    AI_WIN_DELAY_TIME = 2.0      # Thời gian chờ sau khi AI thắng

# Cấu hình Database
DB_CONFIG = {
    'DRIVER': '{ODBC Driver 17 for SQL Server}',
    'SERVER': 'localhost',
    'DATABASE': 'puzzle8',
    'Trusted_Connection': 'yes'
}