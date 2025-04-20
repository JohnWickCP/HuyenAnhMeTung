# Thư viện tiêu chuẩn
import pygame
import time
import os
import pickle
from tkinter import filedialog

# Import từ config
from config import (
    WHITE, BLACK, GRAY, LIGHT_BLUE, BLUE, RED, GREEN, PALE_PINK, GREEN_BUTTON,
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, TILE_MARGIN, AI_BOARD_BG,
    font, small_font, sound_enabled, welcome_music, game_music, victory_sound, lose_sound,
    screen, ButtonConfig, AIConfig, DEFEAT_IMAGE_PATH, SHOW_NUMBERS_WITH_IMAGE,
)

# Import từ models
from Models import Puzzle, Database, BestFirstSearch, HillClimbing

# Import từ ui
from UI import Button, MapManager

class Game:
    def __init__(self):
        self.model_classes = {
            "Puzzle": Puzzle,
            "BestFirstSearch": BestFirstSearch,
            "HillClimbing": HillClimbing
        }
        """Lớp quản lý trò chơi"""
        self.state = "welcome"  # welcome, playing, solving, end, how_to_play, settings
        self.puzzle = None
        self.goal_puzzle = None  # Trạng thái đích
        self.size = 3  # Kích thước mặc định
        self.move_count = 0  # Số bước di chuyển
        self.start_time = None  # Thời gian bắt đầu
        self.end_time = None  # Thời điểm kết thúc
        self.solver = None  # Thuật toán giải
        self.solution = []  # Lời giải
        self.solution_index = 0  # Chỉ số hiện tại trong lời giải
        self.solution_time = 0  # Thời gian giải
        self.last_solution_time = 0  # Thời gian cập nhật lời giải cuối
        self.buttons = []  # Danh sách các nút
        self.delay_time = 1.5  # Thời gian chờ trước khi chuyển sang end
        self.delay_start = None  # Thời điểm bắt đầu delay
        self.volume = 50  # Âm lượng mặc định (0-100)
        self.sound_enabled = sound_enabled  # Trạng thái âm thanh
        self.current_music = None  # Âm nhạc hiện tại
        self.original_image = None  # Hình ảnh gốc
        self.tile_images = []  # Danh sách mảnh hình ảnh
        self.use_image = False  # Sử dụng hình ảnh hay không
        self.image_path = None  # Đường dẫn hình ảnh
        self.db = Database()  # Kết nối cơ sở dữ liệu
        self.selected_map_id = None  # ID của map đang chơi
        self.ai_move_interval = AIConfig.DEFAULT_MOVE_INTERVAL  # Khoảng thời gian di chuyển của AI

        # Thêm quản lý map
        self.map_manager = MapManager(self, self.db)
        self.saving_map = False  # Trạng thái đang lưu map
        self.map_name_input = ""  # Tên map khi lưu
        self.showing_result = False  # Trạng thái hiển thị kết quả

        # Thêm biến cho chế độ đấu với AI
        self.duel_mode = False
        self.ai_puzzle = None
        self.ai_move_count = 0
        self.player_turn_count = 0
        self.ai_solver = None
        self.ai_solving = False
        self.ai_solution = []
        self.ai_solution_index = 0
        self.ai_last_move_time = 0
        self.ai_win_delay_start = None
        self.ai_win_delay_time = AIConfig.AI_WIN_DELAY_TIME

        # Tạo các nút ban đầu
        self.create_buttons()

        # Phát nhạc welcome khi khởi tạo
        if self.sound_enabled:
            self.play_music("welcome")

    def play_music(self, music_type):
        """Phát nhạc nền tương ứng với trạng thái game"""
        if not self.sound_enabled:
            return
        pygame.mixer.stop()
        try:
            if music_type == "welcome":
                welcome_music.play(-1)
                self.current_music = "welcome"
            elif music_type == "game":
                game_music.play(-1)
                self.current_music = "game"
            elif music_type == "victory":
                victory_sound.play()
                self.current_music = "victory"
            elif music_type == "lose":
                lose_sound.play()
                self.current_music = "lose"
        except Exception as e:
            print(f"Lỗi phát nhạc {music_type}: {e}")

    def create_buttons(self):
        """Tạo các nút trong trò chơi"""
        self.buttons = []
        if self.state == "welcome":
            button_width = ButtonConfig.WELCOME_BUTTON_WIDTH
            button_height = ButtonConfig.WELCOME_BUTTON_HEIGHT
            button_spacing = ButtonConfig.WELCOME_BUTTON_SPACING
            start_y = ButtonConfig.WELCOME_START_Y
            center_x = SCREEN_WIDTH // 2

            self.buttons.extend([
                Button("3x3", center_x - button_width//2, start_y, button_width, button_height, self.set_size_3, GREEN_BUTTON),
                Button("4x4", center_x - button_width//2, start_y + button_height + button_spacing, button_width, button_height, self.set_size_4, GREEN_BUTTON),
                Button("5x5", center_x - button_width//2, start_y + 2 * (button_height + button_spacing), button_width, button_height, self.set_size_5, GREEN_BUTTON),
                Button("Duel với AI", center_x - button_width//2, start_y + 3 * (button_height + button_spacing), button_width, button_height, self.start_duel_mode, GREEN_BUTTON),
                Button("How to Play", center_x - button_width//2, start_y + 4 * (button_height + button_spacing), button_width, button_height, self.show_how_to_play, GREEN_BUTTON),
                Button("Settings", center_x - button_width//2, start_y + 5 * (button_height + button_spacing), button_width, button_height, self.show_settings, GREEN_BUTTON)
            ])
        elif self.state in ["playing", "solving"]:
            if self.duel_mode:
                self.buttons.extend([
                    Button("New Game", 50, ButtonConfig.PLAYING_ROW1_Y, ButtonConfig.PLAYING_BUTTON_WIDTH, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.new_game, GREEN_BUTTON),
                    Button("3x3", 160, ButtonConfig.PLAYING_ROW1_Y, 80, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.set_size_3_duel, GREEN_BUTTON),
                    Button("4x4", 250, ButtonConfig.PLAYING_ROW1_Y, 80, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.set_size_4_duel, GREEN_BUTTON),
                    Button("5x5", 340, ButtonConfig.PLAYING_ROW1_Y, 80, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.set_size_5_duel, GREEN_BUTTON),
                    Button("Load Map", 430, ButtonConfig.PLAYING_ROW1_Y, ButtonConfig.PLAYING_BUTTON_WIDTH, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.show_map_manager, GREEN_BUTTON),
                    Button("Load Image", 540, ButtonConfig.PLAYING_ROW1_Y, ButtonConfig.PLAYING_BUTTON_WIDTH, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.load_image, GREEN_BUTTON),
                    Button("Back", SCREEN_WIDTH - 150, ButtonConfig.PLAYING_ROW1_Y, ButtonConfig.PLAYING_BUTTON_WIDTH, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.back_to_welcome, GREEN_BUTTON)
                ])
            else:
                self.buttons.extend([
                    Button("New 3x3", 50, ButtonConfig.PLAYING_ROW1_Y, ButtonConfig.PLAYING_BUTTON_WIDTH, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.new_game_3x3, GREEN_BUTTON),
                    Button("New 4x4", 160, ButtonConfig.PLAYING_ROW1_Y, ButtonConfig.PLAYING_BUTTON_WIDTH, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.new_game_4x4, GREEN_BUTTON),
                    Button("New 5x5", 270, ButtonConfig.PLAYING_ROW1_Y, ButtonConfig.PLAYING_BUTTON_WIDTH, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.new_game_5x5, GREEN_BUTTON),
                    Button("Load Map", 50, ButtonConfig.PLAYING_ROW2_Y, ButtonConfig.PLAYING_BUTTON_WIDTH, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.show_map_manager, GREEN_BUTTON),
                    Button("Save Map", 180, ButtonConfig.PLAYING_ROW2_Y, ButtonConfig.PLAYING_BUTTON_WIDTH, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.show_save_map, GREEN_BUTTON),
                    Button("Load Image", 310, ButtonConfig.PLAYING_ROW2_Y, ButtonConfig.PLAYING_BUTTON_WIDTH, ButtonConfig.PLAYING_BUTTON_HEIGHT, self.load_image, GREEN_BUTTON),
                    Button("Solve BFS", ButtonConfig.RIGHT_COLUMN_X, ButtonConfig.RIGHT_COLUMN_Y_START, ButtonConfig.RIGHT_COLUMN_WIDTH, ButtonConfig.RIGHT_COLUMN_HEIGHT, self.solve_best_first, GREEN_BUTTON),
                    Button("Hill Climbing", ButtonConfig.RIGHT_COLUMN_X, ButtonConfig.RIGHT_COLUMN_Y_START + ButtonConfig.RIGHT_COLUMN_SPACING, ButtonConfig.RIGHT_COLUMN_WIDTH, ButtonConfig.RIGHT_COLUMN_HEIGHT, self.solve_hill_climbing, GREEN_BUTTON),
                    Button("Save Game", ButtonConfig.RIGHT_COLUMN_X, ButtonConfig.RIGHT_COLUMN_Y_START + 2 * ButtonConfig.RIGHT_COLUMN_SPACING, ButtonConfig.RIGHT_COLUMN_WIDTH, ButtonConfig.RIGHT_COLUMN_HEIGHT, self.save_game, GREEN_BUTTON),
                    Button("Load Game", ButtonConfig.RIGHT_COLUMN_X, ButtonConfig.RIGHT_COLUMN_Y_START + 3 * ButtonConfig.RIGHT_COLUMN_SPACING, ButtonConfig.RIGHT_COLUMN_WIDTH, ButtonConfig.RIGHT_COLUMN_HEIGHT, self.load_game, GREEN_BUTTON),
                    Button("Back", ButtonConfig.RIGHT_COLUMN_X, ButtonConfig.RIGHT_COLUMN_Y_START + 4 * ButtonConfig.RIGHT_COLUMN_SPACING, ButtonConfig.RIGHT_COLUMN_WIDTH, ButtonConfig.RIGHT_COLUMN_HEIGHT, self.back_to_welcome, GREEN_BUTTON)
                ])
        elif self.state == "end":
            self.buttons.extend([
                Button("Play Again", SCREEN_WIDTH//2 - ButtonConfig.END_BUTTON_WIDTH//2, ButtonConfig.END_BUTTON_Y, ButtonConfig.END_BUTTON_WIDTH, ButtonConfig.END_BUTTON_HEIGHT, self.new_game, GREEN_BUTTON),
                Button("Menu", SCREEN_WIDTH//2 - ButtonConfig.END_BUTTON_WIDTH//2, ButtonConfig.END_BUTTON_Y + ButtonConfig.END_BUTTON_HEIGHT + ButtonConfig.END_BUTTON_SPACING, ButtonConfig.END_BUTTON_WIDTH, ButtonConfig.END_BUTTON_HEIGHT, self.back_to_welcome, GREEN_BUTTON)
            ])
        elif self.state == "how_to_play":
            self.buttons.extend([
                Button("Back", SCREEN_WIDTH//2 - ButtonConfig.END_BUTTON_WIDTH//2, ButtonConfig.HOW_TO_PLAY_BUTTON_Y, ButtonConfig.END_BUTTON_WIDTH, ButtonConfig.END_BUTTON_HEIGHT, self.back_to_welcome, GREEN_BUTTON)
            ])
        elif self.state == "settings":
            self.buttons.extend([
                Button("Volume +", SCREEN_WIDTH//2 - 200, ButtonConfig.SETTINGS_BAR_Y, 150, 50, self.increase_volume, GREEN_BUTTON),
                Button("Volume -", SCREEN_WIDTH//2 + 50, ButtonConfig.SETTINGS_BAR_Y, 150, 50, self.decrease_volume, GREEN_BUTTON),
                Button("Toggle Sound", SCREEN_WIDTH//2 - 100, ButtonConfig.SETTINGS_BAR_Y + 70, 200, 50, self.toggle_sound, GREEN_BUTTON),
                Button("AI Speed +", SCREEN_WIDTH//2 - 200, ButtonConfig.SETTINGS_AI_SPEED_BUTTON_Y, 150, 50, self.increase_ai_speed, GREEN_BUTTON),
                Button("AI Speed -", SCREEN_WIDTH//2 + 50, ButtonConfig.SETTINGS_AI_SPEED_BUTTON_Y, 150, 50, self.decrease_ai_speed, GREEN_BUTTON),
                Button("Back", SCREEN_WIDTH//2 - 100, ButtonConfig.SETTINGS_BACK_BUTTON_Y, 200, 50, self.back_to_welcome, GREEN_BUTTON)
            ])
        elif self.state == "duel_lost":
            panel_width = ButtonConfig.DUEL_PANEL_WIDTH
            panel_height = ButtonConfig.DUEL_PANEL_HEIGHT
            panel_x = (SCREEN_WIDTH - panel_width) // 2
            panel_y = (SCREEN_HEIGHT - panel_height) // 2

            play_again_x = panel_x + (panel_width // 2) - ButtonConfig.DUEL_BUTTON_WIDTH - (ButtonConfig.DUEL_BUTTON_SPACING // 2)
            play_again_y = panel_y + panel_height - ButtonConfig.DUEL_BUTTON_Y_OFFSET
            menu_x = panel_x + (panel_width // 2) + (ButtonConfig.DUEL_BUTTON_SPACING // 2)
            menu_y = panel_y + panel_height - ButtonConfig.DUEL_BUTTON_Y_OFFSET

            self.buttons.extend([
                Button("Chơi Lại", play_again_x, play_again_y, ButtonConfig.DUEL_BUTTON_WIDTH, ButtonConfig.DUEL_BUTTON_HEIGHT, self.start_duel_mode, GREEN_BUTTON),
                Button("Menu", menu_x, menu_y, ButtonConfig.DUEL_BUTTON_WIDTH, ButtonConfig.DUEL_BUTTON_HEIGHT, self.back_to_welcome, GREEN_BUTTON)
            ])

    def start_duel_mode(self):
        """Bắt đầu chế độ đấu với AI"""
        self.duel_mode = True
        self.state = "playing"

        self.puzzle = Puzzle(self.size)
        self.goal_puzzle = Puzzle(self.size)
        self.goal_puzzle.initialize()

        puzzle_state = self.puzzle.shuffle(100)
        self.ai_puzzle = Puzzle(self.size)
        for i in range(self.size):
            for j in range(self.size):
                value = self.puzzle.get_value(i, j)
                self.ai_puzzle.set_value(i, j, value)

        self.move_count = 0
        self.ai_move_count = 0
        self.player_turn_count = 0
        self.start_time = time.time()
        self.ai_solving = False
        self.ai_solution = []
        self.ai_solution_index = 0

        if self.sound_enabled:
            self.play_music("game")

        if self.use_image and self.original_image:
            self.split_image()

    def show_map_manager(self):
        """Hiển thị giao diện quản lý map"""
        self.map_manager.load_maps()
        self.map_manager.show()

    def show_save_map(self):
        """Hiển thị giao diện lưu map"""
        self.saving_map = True
        self.map_name_input = f"Map_{time.strftime('%Y%m%d_%H%M%S')}"

    def draw_save_map_dialog(self):
        """Vẽ hộp thoại lưu map"""
        if not self.saving_map:
            return

        dialog_width = 500
        dialog_height = 250
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, WHITE, (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(screen, BLACK, (dialog_x, dialog_y, dialog_width, dialog_height), 2)

        title_font = pygame.font.SysFont("segoeui", 32, bold=True)
        title = title_font.render("LƯU MAP", True, BLUE)
        screen.blit(title, (dialog_x + dialog_width // 2 - title.get_width() // 2, dialog_y + 20))

        font = pygame.font.SysFont("segoeui", 24)
        instruction = font.render("Nhập tên cho map:", True, BLACK)
        screen.blit(instruction, (dialog_x + 30, dialog_y + 70))

        input_rect = pygame.Rect(dialog_x + 30, dialog_y + 100, dialog_width - 60, 40)
        pygame.draw.rect(screen, LIGHT_BLUE, input_rect)
        pygame.draw.rect(screen, BLACK, input_rect, 2)
        input_text = font.render(self.map_name_input, True, BLACK)
        screen.blit(input_text, (input_rect.x + 10, input_rect.y + 10))

        save_btn = pygame.Rect(dialog_x + 100, dialog_y + 170, 120, 40)
        pygame.draw.rect(screen, GREEN_BUTTON, save_btn, border_radius=5)
        save_text = font.render("Lưu", True, BLACK)
        screen.blit(save_text, (save_btn.x + save_btn.width // 2 - save_text.get_width() // 2, save_btn.y + 10))

        cancel_btn = pygame.Rect(dialog_x + 280, dialog_y + 170, 120, 40)
        pygame.draw.rect(screen, RED, cancel_btn, border_radius=5)
        cancel_text = font.render("Hủy", True, WHITE)
        screen.blit(cancel_text, (cancel_btn.x + cancel_btn.width // 2 - cancel_text.get_width() // 2, cancel_btn.y + 10))

    def handle_save_map_dialog(self, event):
        """Xử lý sự kiện trong hộp thoại lưu map"""
        if not self.saving_map:
            return False

        dialog_width = 500
        dialog_height = 250
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            save_btn = pygame.Rect(dialog_x + 100, dialog_y + 170, 120, 40)
            if save_btn.collidepoint(mouse_pos):
                self.save_map_to_db()
                self.saving_map = False
                return True
            cancel_btn = pygame.Rect(dialog_x + 280, dialog_y + 170, 120, 40)
            if cancel_btn.collidepoint(mouse_pos):
                self.saving_map = False
                return True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.save_map_to_db()
                self.saving_map = False
                return True
            elif event.key == pygame.K_ESCAPE:
                self.saving_map = False
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.map_name_input = self.map_name_input[:-1]
                return True
            else:
                if len(self.map_name_input) < 30:
                    self.map_name_input += event.unicode
                return True

        return False

    def save_map_to_db(self):
        """Lưu map hiện tại vào cơ sở dữ liệu"""
        if not self.puzzle:
            print("Không có puzzle để lưu!")
            return

        board_state = ",".join(str(self.puzzle.get_value(i, j))
                            for i in range(self.size)
                            for j in range(self.size))

        image_path = self.image_path if self.use_image else None
        map_id = self.db.save_map(self.map_name_input, self.size, board_state, image_path)
        if map_id:
            self.selected_map_id = map_id
            print(f"Đã lưu map: {self.map_name_input}")
        else:
            print("Lỗi khi lưu map!")

    def show_how_to_play(self):
        """Hiển thị màn hình hướng dẫn cách chơi"""
        self.state = "how_to_play"

    def show_settings(self):
        """Hiển thị màn hình cài đặt"""
        self.state = "settings"

    def update_volume(self):
        """Cập nhật âm lượng cho tất cả các âm thanh"""
        if self.sound_enabled:
            volume = self.volume / 100.0
            welcome_music.set_volume(volume)
            game_music.set_volume(volume)
            victory_sound.set_volume(volume)

    def increase_volume(self):
        """Tăng âm lượng"""
        self.volume = min(100, self.volume + 10)
        self.update_volume()
        print(f"Đã tăng âm lượng lên {self.volume}%")

    def decrease_volume(self):
        """Giảm âm lượng"""
        self.volume = max(0, self.volume - 10)
        self.update_volume()
        print(f"Đã giảm âm lượng xuống {self.volume}%")

    def toggle_sound(self):
        """Bật/tắt âm thanh"""
        if self.sound_enabled:
            pygame.mixer.stop()
            self.sound_enabled = False
            print("Đã tắt âm thanh")
        else:
            self.sound_enabled = True
            self.play_music(self.state if self.state in ["welcome", "playing"] else "welcome")
            print("Đã bật âm thanh")

    def increase_ai_speed(self):
        """Giảm khoảng thời gian di chuyển để AI di chuyển nhanh hơn"""
        self.ai_move_interval = max(AIConfig.MIN_MOVE_INTERVAL, self.ai_move_interval - AIConfig.MOVE_INTERVAL_STEP)
        print(f"Tốc độ AI tăng: khoảng thời gian di chuyển {self.ai_move_interval:.2f}s")

    def decrease_ai_speed(self):
        """Tăng khoảng thời gian di chuyển để AI di chuyển chậm hơn"""
        self.ai_move_interval = min(AIConfig.MAX_MOVE_INTERVAL, self.ai_move_interval + AIConfig.MOVE_INTERVAL_STEP)
        print(f"Tốc độ AI giảm: khoảng thời gian di chuyển {self.ai_move_interval:.2f}s")

    def load_image(self):
        """Tải hình ảnh từ máy tính"""
        file_path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if file_path:
            try:
                self.original_image = pygame.image.load(file_path)
                self.original_image = self.original_image.convert_alpha()
                self.image_path = file_path
                self.use_image = True
                if self.state == "playing" and self.puzzle:
                    self.split_image()
                elif self.state == "welcome":
                    self.new_game()
            except Exception as e:
                print(f"Lỗi khi tải hình ảnh: {e}")
                self.use_image = False
                self.original_image = None
                self.image_path = None

    def split_image(self):
        """Chia hình ảnh thành các mảnh nhỏ cho puzzle"""
        if not self.original_image or not self.puzzle:
            return
        tile_size_adjusted = TILE_SIZE - (self.size - 3) * 10
        tile_size_adjusted = max(tile_size_adjusted, 40)
        target_width = self.size * tile_size_adjusted
        target_height = self.size * tile_size_adjusted
        try:
            scaled_image = pygame.transform.scale(self.original_image, (target_width, target_height))
            self.tile_images = []
            for i in range(self.size):
                for j in range(self.size):
                    value = i * self.size + j + 1
                    if value == self.size * self.size:
                        value = 0
                    tile_surface = pygame.Surface((tile_size_adjusted, tile_size_adjusted), pygame.SRCALPHA)
                    tile_surface.blit(
                        scaled_image,
                        (0, 0),
                        (j * tile_size_adjusted, i * tile_size_adjusted, tile_size_adjusted, tile_size_adjusted)
                    )
                    self.tile_images.append((value, tile_surface))
            print(f"Đã chia hình ảnh thành {len(self.tile_images)} mảnh")
        except Exception as e:
            print(f"Lỗi khi chia hình ảnh: {e}")
            self.use_image = False
            self.tile_images = []

    def set_size_3(self):
        """Đặt kích thước puzzle là 3x3"""
        self.size = 3
        self.new_game()

    def set_size_4(self):
        """Đặt kích thước puzzle là 4x4"""
        self.size = 4
        self.new_game()

    def set_size_5(self):
        """Đặt kích thước puzzle là 5x5"""
        self.size = 5
        self.new_game()

    def set_size_3_duel(self):
        """Đặt kích thước puzzle là 3x3 cho chế độ duel"""
        self.size = 3
        self.start_duel_mode()

    def set_size_4_duel(self):
        """Đặt kích thước puzzle là 4x4 cho chế độ duel"""
        self.size = 4
        self.start_duel_mode()

    def set_size_5_duel(self):
        """Đặt kích thước puzzle là 5x5 cho chế độ duel"""
        self.size = 5
        self.start_duel_mode()

    def new_game(self):
        """Tạo trò chơi mới"""
        self.puzzle = Puzzle(self.size)
        self.goal_puzzle = Puzzle(self.size)
        self.goal_puzzle.initialize()
        self.puzzle.shuffle(100)
        self.move_count = 0
        self.start_time = time.time()
        self.state = "playing"
        self.solution = []
        self.solution_index = 0
        self.selected_map_id = None

        if self.duel_mode:
            self.ai_move_count = 0
            self.player_turn_count = 0
            self.ai_solving = False
            self.ai_solution = []
            self.ai_solution_index = 0

            self.ai_puzzle = Puzzle(self.size)
            for i in range(self.size):
                for j in range(self.size):
                    value = self.puzzle.get_value(i, j)
                    self.ai_puzzle.set_value(i, j, value)

        if self.sound_enabled:
            self.play_music("game")
        if self.use_image and self.original_image:
            self.split_image()

    def new_game_3x3(self):
        """Tạo trò chơi mới 3x3"""
        self.size = 3
        self.new_game()

    def new_game_4x4(self):
        """Tạo trò chơi mới 4x4"""
        self.size = 4
        self.new_game()

    def new_game_5x5(self):
        """Tạo trò chơi mới 5x5"""
        self.size = 5
        self.new_game()

    def save_map(self):
        """Lưu map vào cơ sở dữ liệu"""
        if self.state == "playing" and self.puzzle:
            board_state = ",".join(str(self.puzzle.get_value(i, j))
                                  for i in range(self.size)
                                  for j in range(self.size))
            map_name = f"Map_{time.strftime('%Y%m%d_%H%M%S')}"
            image_path = self.image_path if self.use_image else None
            self.selected_map_id = self.db.save_map(map_name, self.size, board_state, image_path)
            print(f"Đã lưu map: {map_name}")

    def load_map(self):
        """Tải map từ cơ sở dữ liệu"""
        maps = self.db.load_maps()
        if not maps:
            print("Không có map nào được lưu!")
            return
        map_id, map_name, size, board_state, image_path = maps[0]
        self.size = size
        self.puzzle = Puzzle(size)
        values = [int(x) for x in board_state.split(",")]
        for i in range(size):
            for j in range(size):
                value = values[i * size + j]
                self.puzzle.set_value(i, j, value)
        self.selected_map_id = map_id
        self.move_count = 0
        self.start_time = time.time()
        self.state = "playing"
        if image_path and os.path.exists(image_path):
            self.image_path = image_path
            self.original_image = pygame.image.load(image_path)
            self.original_image = self.original_image.convert_alpha()
            self.use_image = True
            self.split_image()
        else:
            self.use_image = False
            self.original_image = None
            self.image_path = None
        print(f"Đã tải map: {map_name}")

    def save_game(self):
        """Lưu trạng thái trò chơi"""
        if self.state == "playing":
            game_state = {
                'puzzle': self.puzzle,
                'size': self.size,
                'move_count': self.move_count,
                'start_time': self.start_time,
                'elapsed_time': time.time() - self.start_time,
                'use_image': self.use_image,
                'image_path': self.image_path,
                'selected_map_id': self.selected_map_id
            }
            try:
                with open('puzzle_save.pkl', 'wb') as f:
                    pickle.dump(game_state, f)
                print("Đã lưu trò chơi thành công!")
            except Exception as e:
                print(f"Lỗi khi lưu trò chơi: {e}")

    def load_game(self):
        """Tải trạng thái trò chơi"""
        try:
            if os.path.exists('puzzle_save.pkl'):
                with open('puzzle_save.pkl', 'rb') as f:
                    game_state = pickle.load(f)
                self.puzzle = game_state['puzzle']
                self.size = game_state['size']
                self.move_count = game_state['move_count']
                self.elapsed_time = game_state['elapsed_time']
                self.start_time = time.time() - self.elapsed_time
                self.use_image = game_state.get('use_image', False)
                self.selected_map_id = game_state.get('selected_map_id', None)
                self.state = "playing"
                if self.use_image and 'image_path' in game_state:
                    try:
                        self.image_path = game_state['image_path']
                        if os.path.exists(self.image_path):
                            self.original_image = pygame.image.load(self.image_path)
                            self.original_image = self.original_image.convert_alpha()
                            self.split_image()
                        else:
                            print("Không tìm thấy file hình ảnh!")
                            self.use_image = False
                            self.original_image = None
                            self.image_path = None
                    except Exception as e:
                        print(f"Lỗi khi tải hình ảnh: {e}")
                        self.use_image = False
                        self.original_image = None
                        self.image_path = None
                print("Đã tải trò chơi thành công!")
            else:
                print("Không tìm thấy file lưu!")
        except Exception as e:
            print(f"Lỗi khi tải trò chơi: {e}")

    def solve_best_first(self):
        """Giải puzzle bằng Best-first Search"""
        if self.state == "playing":
            self.solver = BestFirstSearch(self.puzzle)
            success, steps, solve_time = self.solver.solve()
            if success:
                self.solution = self.solver.get_solution()
                self.solution_index = 0
                self.solution_time = solve_time
                self.state = "solving"
                self.last_solution_time = time.time()
            else:
                print("Không tìm thấy lời giải bằng Best-first Search!")

    def solve_hill_climbing(self):
        """Giải puzzle bằng Hill Climbing"""
        if self.state == "playing":
            self.solver = HillClimbing(self.puzzle)
            success, steps, solve_time = self.solver.solve()
            if success:
                self.solution = self.solver.get_solution()
                self.solution_index = 0
                self.solution_time = solve_time
                self.state = "solving"
                self.last_solution_time = time.time()
            else:
                print("Không tìm thấy lời giải tối ưu bằng Hill Climbing!")

    def back_to_welcome(self):
        """Quay lại màn hình welcome"""
        self.state = "welcome"
        self.duel_mode = False
        if self.sound_enabled:
            self.play_music("welcome")

    def handle_events(self, event):
        """Xử lý sự kiện"""
        if event.type == pygame.QUIT:
            print("Received pygame.QUIT event")
            return False

        if self.map_manager.is_visible():
            return self.map_manager.handle_events(event)

        if self.saving_map:
            return self.handle_save_map_dialog(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button.is_clicked(mouse_pos):
                    button.action()
                    return True
            if self.state == "playing" and self.puzzle:
                if hasattr(self, 'last_board_info'):
                    board_x, board_y, tile_size = self.last_board_info
                    if self.puzzle.handle_click(mouse_pos, board_x, board_y, tile_size):
                        self.move_count += 1
                        if self.duel_mode:
                            self.player_turn_count += 1
                        if self.puzzle.is_goal():
                            self.state = "end"
                            self.end_time = time.time()
                            if self.sound_enabled:
                                self.play_music("victory")
                            if self.selected_map_id:
                                elapsed_time = int(self.end_time - self.start_time)
                                self.db.save_result(self.selected_map_id, self.move_count, elapsed_time)
                                print(f"Đã lưu kết quả: {self.move_count} bước, {elapsed_time}s")

        return True

    def update(self):
        """Cập nhật trạng thái trò chơi"""
        if self.state == "solving" and self.solution:
            current_time = time.time()
            if current_time - self.last_solution_time > 0.5:
                if self.solution_index < len(self.solution):
                    self.puzzle.move(self.solution[self.solution_index])
                    self.solution_index += 1
                    self.last_solution_time = current_time
                    self.move_count += 1
                    if self.solution_index >= len(self.solution):
                        if self.puzzle.is_goal():
                            self.delay_start = time.time()
                            if self.sound_enabled:
                                self.play_music("victory")
                            if self.selected_map_id:
                                elapsed_time = int(current_time - self.start_time)
                                self.db.save_result(self.selected_map_id, self.move_count, elapsed_time)
                                print("Đã lưu kết quả vào cơ sở dữ liệu")
                        else:
                            self.state = "playing"

        elif self.state == "playing" and self.duel_mode:
            if self.player_turn_count >= AIConfig.PLAYER_TURN_THRESHOLD and not self.ai_solving and not self.ai_puzzle.is_goal():
                print("AI bắt đầu giải puzzle")
                self.ai_solving = True
                self.ai_solver = BestFirstSearch(self.ai_puzzle)
                success, steps, solve_time = self.ai_solver.solve()
                if success:
                    self.ai_solution = self.ai_solver.get_solution()
                    self.ai_solution_index = 0
                    self.ai_last_move_time = time.time()
                else:
                    print("AI không tìm thấy lời giải!")
                    self.ai_solving = False

            if self.ai_solving and self.ai_solution:
                current_time = time.time()
                if current_time - self.ai_last_move_time > self.ai_move_interval:
                    if self.ai_solution_index < len(self.ai_solution):
                        self.ai_puzzle.move(self.ai_solution[self.ai_solution_index])
                        self.ai_solution_index += 1
                        self.ai_move_count += 1
                        self.ai_last_move_time = current_time

                        if self.ai_puzzle.is_goal() and self.ai_win_delay_start is None:
                            print("AI đã giải xong!")
                            self.ai_win_delay_start = time.time()
                            self.end_time = time.time()
                            if self.sound_enabled:
                                pygame.mixer.stop()
                                if 'lose_sound' in globals():
                                    lose_sound.play()

            if self.ai_win_delay_start is not None:
                current_time = time.time()
                if current_time - self.ai_win_delay_start >= self.ai_win_delay_time:
                    self.state = "duel_lost"
                    self.ai_win_delay_start = None

            if self.puzzle.is_goal():
                self.state = "end"
                self.end_time = time.time()
                if self.sound_enabled:
                    self.play_music("victory")
                if self.selected_map_id:
                    elapsed_time = int(self.end_time - self.start_time)
                    self.db.save_result(self.selected_map_id, self.move_count, elapsed_time)
                    print("Đã lưu kết quả vào cơ sở dữ liệu")

        if self.delay_start is not None:
            current_time = time.time()
            if current_time - self.delay_start >= self.delay_time:
                self.state = "end"
                self.end_time = current_time
                self.delay_start = None

    def draw(self):
        """Vẽ trò chơi"""
        screen.fill(WHITE)
        self.create_buttons()

        if self.state == "welcome":
            self.draw_welcome_screen()
        elif self.state in ["playing", "solving"]:
            if self.duel_mode:
                self.last_board_info = self.draw_duel_mode()
            else:
                self.last_board_info = self.draw_game_board()
        elif self.state == "end":
            self.draw_end_screen()
        elif self.state == "duel_lost":
            self.draw_duel_lost_screen()
        elif self.state == "how_to_play":
            self.draw_how_to_play_screen()
        elif self.state == "settings":
            self.draw_settings_screen()

        for button in self.buttons:
            button.draw()

        if self.map_manager.is_visible():
            self.map_manager.draw()

        if self.saving_map:
            self.draw_save_map_dialog()

        pygame.display.flip()

    def draw_duel_lost_screen(self):
        """Vẽ màn hình thua khi AI giải xong trước"""
        screen.fill(WHITE)

        panel_width = ButtonConfig.DUEL_PANEL_WIDTH
        panel_height = ButtonConfig.DUEL_PANEL_HEIGHT
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        pygame.draw.rect(screen, LIGHT_BLUE, (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(screen, RED, (panel_x, panel_y, panel_width, panel_height), 3, border_radius=10)

        title_font = pygame.font.SysFont("segoeui", 60, bold=True)
        title = title_font.render("NON!", True, RED)
        screen.blit(title, (panel_x + (panel_width - title.get_width()) // 2, panel_y + 30))

        try:
            defeat_image = pygame.image.load(DEFEAT_IMAGE_PATH)
            defeat_image = pygame.transform.scale(defeat_image, (ButtonConfig.DUEL_IMAGE_WIDTH, ButtonConfig.DUEL_IMAGE_HEIGHT))
            screen.blit(defeat_image, (panel_x + (panel_width - ButtonConfig.DUEL_IMAGE_WIDTH) // 2, panel_y + ButtonConfig.DUEL_IMAGE_Y_OFFSET))
        except Exception as e:
            print(f"Không thể tải ảnh thua cuộc: {e}")

        info_font = pygame.font.SysFont("segoeui", 30)
        info_y = panel_y + ButtonConfig.DUEL_SUBTITLE_Y_OFFSET
        subtitle = info_font.render("AI đã giải xong trước bạn", True, BLACK)
        screen.blit(subtitle, (panel_x + (panel_width - subtitle.get_width()) // 2, info_y))

        elapsed_time = int(self.end_time - self.start_time) if self.end_time and self.start_time else 0
        ai_moves = info_font.render(f"Số bước của AI: {self.ai_move_count}", True, BLACK)
        player_moves = info_font.render(f"Số bước của bạn: {self.move_count}", True, BLACK)
        #time_text = info_font.render(f"Thời gian chơi: {elapsed_time}s", True, BLACK)

        screen.blit(ai_moves, (panel_x + (panel_width - ai_moves.get_width()) // 2, info_y + ButtonConfig.DUEL_STAT_SPACING))
        screen.blit(player_moves, (panel_x + (panel_width - player_moves.get_width()) // 2, info_y + 2 * ButtonConfig.DUEL_STAT_SPACING))
        #screen.blit(time_text, (panel_x + (panel_width - time_text.get_width()) // 2, info_y + 3 * ButtonConfig.DUEL_STAT_SPACING))

        message_font = pygame.font.SysFont("segoeui", 32, bold=True, italic=True)
        message = message_font.render(".", True, BLUE)
        screen.blit(message, (panel_x + (panel_width - message.get_width()) // 2, panel_y + panel_height - ButtonConfig.DUEL_MESSAGE_Y_OFFSET))

    def draw_welcome_screen(self):
        """Vẽ màn hình welcome"""
        screen.fill(WHITE)
        panel_width = ButtonConfig.WELCOME_PANEL_WIDTH
        panel_height = ButtonConfig.WELCOME_PANEL_HEIGHT
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = ButtonConfig.WELCOME_PANEL_Y
        pygame.draw.rect(screen, LIGHT_BLUE, (panel_x, panel_y, panel_width, panel_height), border_radius=20)

        title_font = pygame.font.SysFont("segoeui", 60, bold=True)
        title_shadow = title_font.render("Huyễn Ảnh Mê Tung", True, BLACK)
        title = title_font.render("Huyễn Ảnh Mê Tung", True, RED)
        screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + ButtonConfig.WELCOME_TITLE_SHADOW_OFFSET, panel_y + ButtonConfig.WELCOME_TITLE_Y_OFFSET + ButtonConfig.WELCOME_TITLE_SHADOW_OFFSET))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, panel_y + ButtonConfig.WELCOME_TITLE_Y_OFFSET))

    def draw_game_board(self):
        """Vẽ bảng chơi"""
        screen.fill(WHITE)
        board_x, board_y, tile_size = self.draw_puzzle()
        self.draw_goal_puzzle()
        elapsed_time = int(time.time() - self.start_time) if self.start_time else 0
        move_rect = pygame.Rect(ButtonConfig.PLAYING_MOVE_X, ButtonConfig.PLAYING_MOVE_TIME_Y, ButtonConfig.PLAYING_MOVE_WIDTH, ButtonConfig.PLAYING_MOVE_HEIGHT)
        time_rect = pygame.Rect(ButtonConfig.PLAYING_TIME_X, ButtonConfig.PLAYING_MOVE_TIME_Y, ButtonConfig.PLAYING_MOVE_WIDTH, ButtonConfig.PLAYING_MOVE_HEIGHT)
        pygame.draw.rect(screen, PALE_PINK, move_rect, border_radius=5)
        pygame.draw.rect(screen, PALE_PINK, time_rect, border_radius=5)
        move_text = small_font.render(f"Move: {self.move_count}", True, BLACK)
        time_text = small_font.render(f"Time: {elapsed_time}s", True, BLACK)
        screen.blit(move_text, (move_rect.x + 10, move_rect.y + 10))
        screen.blit(time_text, (time_rect.x + 10, time_rect.y + 10))
        if self.solution_time > 0:
            solution_text = small_font.render(f"Time to Solve: {self.solution_time:.2f}s", True, BLACK)
            screen.blit(solution_text, (ButtonConfig.PLAYING_SOLUTION_TEXT_X, ButtonConfig.PLAYING_SOLUTION_TEXT_Y))
        return board_x, board_y, tile_size

    def draw_puzzle(self):
        """Vẽ bảng puzzle"""
        if not self.puzzle:
            return
        tile_size_adjusted = TILE_SIZE - (self.size - 3) * 10
        tile_size_adjusted = max(tile_size_adjusted, 40)
        board_width = self.puzzle.size * (tile_size_adjusted + TILE_MARGIN)
        board_height = self.puzzle.size * (tile_size_adjusted + TILE_MARGIN)
        board_x = (SCREEN_WIDTH - board_width) // 2
        board_y = ButtonConfig.PLAYING_BOARD_Y
        pygame.draw.rect(screen, GRAY, (board_x - 10, board_y - 10, board_width + 20, board_height + 20))
        for row in range(self.puzzle.size):
            for col in range(self.puzzle.size):
                value = self.puzzle.get_value(row, col)
                x = board_x + col * (tile_size_adjusted + TILE_MARGIN)
                y = board_y + row * (tile_size_adjusted + TILE_MARGIN)
                if value != 0:
                    if self.use_image and self.tile_images:
                        for tile_value, tile_img in self.tile_images:
                            if tile_value == value:
                                resized_img = pygame.transform.scale(tile_img, (tile_size_adjusted, tile_size_adjusted))
                                screen.blit(resized_img, (x, y))
                                break
                    else:
                        pygame.draw.rect(screen, LIGHT_BLUE, (x, y, tile_size_adjusted, tile_size_adjusted))
                    pygame.draw.rect(screen, BLACK, (x, y, tile_size_adjusted, tile_size_adjusted), 2)
                    if not self.use_image or SHOW_NUMBERS_WITH_IMAGE:
                        num_font_size = min(36, tile_size_adjusted // 2 + 10)
                        num_font = pygame.font.SysFont(None, num_font_size)
                        text = num_font.render(str(value), True, BLACK)
                        text_rect = text.get_rect(center=(x + tile_size_adjusted // 2, y + tile_size_adjusted // 2))
                        screen.blit(text, text_rect)
        return board_x, board_y, tile_size_adjusted

    def draw_goal_puzzle(self):
        """Vẽ bảng puzzle đích"""
        if not self.goal_puzzle:
            return
        main_tile_size = TILE_SIZE - (self.size - 3) * 10
        main_tile_size = max(main_tile_size, 40)
        small_tile_size = main_tile_size // 2
        small_margin = TILE_MARGIN // 2
        board_width = self.goal_puzzle.size * (small_tile_size + small_margin)
        board_height = self.goal_puzzle.size * (small_tile_size + small_margin)
        board_x = SCREEN_WIDTH - board_width - 50
        board_y = 50
        pygame.draw.rect(screen, GRAY, (board_x - 5, board_y - 5, board_width + 10, board_height + 10))
        goal_title = small_font.render("Target", True, RED)
        screen.blit(goal_title, (board_x + board_width//2 - goal_title.get_width()//2, board_y - 25))
        for row in range(self.goal_puzzle.size):
            for col in range(self.goal_puzzle.size):
                value = self.goal_puzzle.get_value(row, col)
                x = board_x + col * (small_tile_size + small_margin)
                y = board_y + row * (small_tile_size + small_margin)
                if value != 0:
                    if self.use_image and self.tile_images:
                        for tile_value, tile_img in self.tile_images:
                            if tile_value == value:
                                small_img = pygame.transform.scale(tile_img, (small_tile_size, small_tile_size))
                                screen.blit(small_img, (x, y))
                                break
                    else:
                        pygame.draw.rect(screen, LIGHT_BLUE, (x, y, small_tile_size, small_tile_size))
                    pygame.draw.rect(screen, BLACK, (x, y, small_tile_size, small_tile_size), 1)
                    if not self.use_image or SHOW_NUMBERS_WITH_IMAGE:
                        small_num_font = pygame.font.SysFont(None, max(12, small_tile_size // 2 + 5))
                        text = small_num_font.render(str(value), True, BLACK)
                        text_rect = text.get_rect(center=(x + small_tile_size // 2, y + small_tile_size // 2))
                        screen.blit(text, text_rect)

    def draw_duel_mode(self):
        screen.fill(WHITE)

        player_title = font.render("BẠN", True, BLUE)
        ai_title = font.render("AI", True, RED)
        screen.blit(player_title, (ButtonConfig.DUEL_PLAYER_X - player_title.get_width() // 2, ButtonConfig.DUEL_BOARD_Y - ButtonConfig.DUEL_TITLE_Y_OFFSET))
        screen.blit(ai_title, (ButtonConfig.DUEL_AI_X - ai_title.get_width() // 2, ButtonConfig.DUEL_BOARD_Y - ButtonConfig.DUEL_TITLE_Y_OFFSET))

        player_board_x, player_board_y, tile_size = self.draw_player_puzzle()
        self.draw_ai_puzzle(tile_size)
        self.draw_goal_puzzle_duel(tile_size)

        elapsed_time = int(time.time() - self.start_time) if self.start_time else 0
        move_rect = pygame.Rect(ButtonConfig.DUEL_PLAYER_STAT_X, ButtonConfig.DUEL_STAT_Y, 
                            ButtonConfig.DUEL_STAT_WIDTH, ButtonConfig.DUEL_STAT_HEIGHT)
        ai_move_rect = pygame.Rect(ButtonConfig.DUEL_AI_STAT_X, ButtonConfig.DUEL_STAT_Y, 
                                ButtonConfig.DUEL_STAT_WIDTH, ButtonConfig.DUEL_STAT_HEIGHT)
        time_rect = pygame.Rect(ButtonConfig.DUEL_TIME_STAT_X, ButtonConfig.DUEL_STAT_Y, 
                            ButtonConfig.DUEL_STAT_WIDTH, ButtonConfig.DUEL_STAT_HEIGHT)

        pygame.draw.rect(screen, PALE_PINK, move_rect, border_radius=10)
        pygame.draw.rect(screen, PALE_PINK, ai_move_rect, border_radius=10)
        pygame.draw.rect(screen, PALE_PINK, time_rect, border_radius=10)

        move_text = small_font.render(f"Bạn: {self.move_count}", True, BLACK)
        ai_move_text = small_font.render(f"AI: {self.ai_move_count}", True, BLACK)
        time_text = small_font.render(f"Thời gian: {elapsed_time}s", True, BLACK)

        screen.blit(move_text, (move_rect.x + (move_rect.width - move_text.get_width()) // 2, 
                            move_rect.y + (move_rect.height - move_text.get_height()) // 2))
        screen.blit(ai_move_text, (ai_move_rect.x + (ai_move_rect.width - ai_move_text.get_width()) // 2, 
                                ai_move_rect.y + (ai_move_rect.height - ai_move_text.get_height()) // 2))
        screen.blit(time_text, (time_rect.x + (time_rect.width - time_text.get_width()) // 2, 
                            time_rect.y + (time_rect.height - time_text.get_height()) // 2))

        if self.player_turn_count < AIConfig.PLAYER_TURN_THRESHOLD:
            turns_left = AIConfig.PLAYER_TURN_THRESHOLD - self.player_turn_count
            turns_text = font.render(f"AI đang nhường bạn: {turns_left} bước", True, RED)
            screen.blit(turns_text, (SCREEN_WIDTH // 2 - turns_text.get_width() // 2, ButtonConfig.DUEL_STAT_Y - ButtonConfig.DUEL_TURN_TEXT_Y_OFFSET))

        return player_board_x, player_board_y, tile_size

    def draw_goal_puzzle_duel(self, main_tile_size):
        if not self.goal_puzzle:
            return

        small_tile_size = main_tile_size // 2
        small_margin = TILE_MARGIN // 2
        board_width = self.goal_puzzle.size * (small_tile_size + small_margin)
        board_height = self.goal_puzzle.size * (small_tile_size + small_margin)

        board_x = ButtonConfig.DUEL_TARGET_X - board_width // 2
        board_y = ButtonConfig.DUEL_TARGET_Y

        pygame.draw.rect(screen, GRAY, (board_x - 10, board_y - 10, board_width + 20, board_height + 20), border_radius=5)
        goal_title = font.render("", True, RED)
        screen.blit(goal_title, (board_x + board_width // 2 - goal_title.get_width() // 2, board_y - 30))

        for row in range(self.goal_puzzle.size):
            for col in range(self.goal_puzzle.size):
                value = self.goal_puzzle.get_value(row, col)
                x = board_x + col * (small_tile_size + small_margin)
                y = board_y + row * (small_tile_size + small_margin)
                if value != 0:
                    if self.use_image and self.tile_images:
                        for tile_value, tile_img in self.tile_images:
                            if tile_value == value:
                                small_img = pygame.transform.scale(tile_img, (small_tile_size, small_tile_size))
                                screen.blit(small_img, (x, y))
                                break
                    else:
                        pygame.draw.rect(screen, LIGHT_BLUE, (x, y, small_tile_size, small_tile_size))
                    pygame.draw.rect(screen, BLACK, (x, y, small_tile_size, small_tile_size), 1)
                    small_num_font = pygame.font.SysFont(None, max(12, small_tile_size // 2 + 5))
                    text = small_num_font.render(str(value), True, BLACK)
                    text_rect = text.get_rect(center=(x + small_tile_size // 2, y + small_tile_size // 2))
                    screen.blit(text, text_rect)

    def draw_player_puzzle(self):
        if not self.puzzle:
            return 0, 0, 0

        tile_size_adjusted = min(TILE_SIZE, SCREEN_WIDTH // (self.size * 1.5))
        tile_size_adjusted = max(tile_size_adjusted, 40)

        board_width = self.puzzle.size * (tile_size_adjusted + TILE_MARGIN)
        board_height = self.puzzle.size * (tile_size_adjusted + TILE_MARGIN)

        board_x = ButtonConfig.DUEL_PLAYER_X - board_width // 2
        board_y = ButtonConfig.DUEL_BOARD_Y

        pygame.draw.rect(screen, GRAY, (board_x - 15, board_y - 15, board_width + 30, board_height + 30), border_radius=5)

        for row in range(self.puzzle.size):
            for col in range(self.puzzle.size):
                value = self.puzzle.get_value(row, col)
                x = board_x + col * (tile_size_adjusted + TILE_MARGIN)
                y = board_y + row * (tile_size_adjusted + TILE_MARGIN)
                if value != 0:
                    if self.use_image and self.tile_images:
                        for tile_value, tile_img in self.tile_images:
                            if tile_value == value:
                                resized_img = pygame.transform.scale(tile_img, (tile_size_adjusted, tile_size_adjusted))
                                screen.blit(resized_img, (x, y))
                                break
                    else:
                        pygame.draw.rect(screen, LIGHT_BLUE, (x, y, tile_size_adjusted, tile_size_adjusted))
                    pygame.draw.rect(screen, BLACK, (x, y, tile_size_adjusted, tile_size_adjusted), 2)
                    if not self.use_image or SHOW_NUMBERS_WITH_IMAGE:
                        num_font_size = min(36, tile_size_adjusted // 2 + 10)
                        num_font = pygame.font.SysFont(None, num_font_size)
                        text = num_font.render(str(value), True, BLACK)
                        text_rect = text.get_rect(center=(x + tile_size_adjusted // 2, y + tile_size_adjusted // 2))
                        screen.blit(text, text_rect)

        return board_x, board_y, tile_size_adjusted

    def draw_ai_puzzle(self, tile_size):
        if not self.ai_puzzle:
            return

        board_width = self.ai_puzzle.size * (tile_size + TILE_MARGIN)
        board_height = self.ai_puzzle.size * (tile_size + TILE_MARGIN)

        board_x = ButtonConfig.DUEL_AI_X - board_width // 2
        board_y = ButtonConfig.DUEL_BOARD_Y

        pygame.draw.rect(screen, AI_BOARD_BG, (board_x - 15, board_y - 15, board_width + 30, board_height + 30), border_radius=5)

        for row in range(self.ai_puzzle.size):
            for col in range(self.ai_puzzle.size):
                value = self.ai_puzzle.get_value(row, col)
                x = board_x + col * (tile_size + TILE_MARGIN)
                y = board_y + row * (tile_size + TILE_MARGIN)
                if value != 0:
                    if self.use_image and self.tile_images:
                        for tile_value, tile_img in self.tile_images:
                            if tile_value == value:
                                resized_img = pygame.transform.scale(tile_img, (tile_size, tile_size))
                                screen.blit(resized_img, (x, y))
                                break
                    else:
                        pygame.draw.rect(screen, (255, 200, 200), (x, y, tile_size, tile_size))
                    pygame.draw.rect(screen, BLACK, (x, y, tile_size, tile_size), 2)
                    if not self.use_image or SHOW_NUMBERS_WITH_IMAGE:
                        num_font_size = min(36, tile_size // 2 + 10)
                        num_font = pygame.font.SysFont(None, num_font_size)
                        text = num_font.render(str(value), True, BLACK)
                        text_rect = text.get_rect(center=(x + tile_size // 2, y + tile_size // 2))
                        screen.blit(text, text_rect)

    def draw_end_screen(self):
        """Vẽ màn hình kết thúc"""
        screen.fill(WHITE)
        title_font = pygame.font.SysFont("segoeui", 50, bold=True)
        win_text = title_font.render("CHÚC MỪNG!", True, RED)
        screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, ButtonConfig.END_TITLE_Y))
        subtitle = font.render("Bạn đã hoàn thành trò chơi", True, BLACK)
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, ButtonConfig.END_SUBTITLE_Y))

        left_panel_x = ButtonConfig.END_LEFT_PANEL_X
        right_panel_x = ButtonConfig.END_RIGHT_PANEL_X
        panel_y = ButtonConfig.END_PANEL_Y
        panel_width = ButtonConfig.END_PANEL_WIDTH
        panel_height = ButtonConfig.END_PANEL_HEIGHT

        pygame.draw.rect(screen, LIGHT_BLUE, (left_panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, BLUE, (left_panel_x, panel_y, panel_width, panel_height), 2)
        info_title = font.render("THÔNG TIN", True, BLUE)
        screen.blit(info_title, (left_panel_x + panel_width//2 - info_title.get_width()//2, panel_y + 15))
        pygame.draw.line(screen, BLUE, 
                        (left_panel_x + ButtonConfig.END_LINE_OFFSET, panel_y + 50), 
                        (left_panel_x + panel_width - ButtonConfig.END_LINE_OFFSET, panel_y + 50), 2)

        info_x = left_panel_x + ButtonConfig.END_INFO_X_OFFSET
        info_y = ButtonConfig.END_INFO_Y_START
        elapsed_time = int(self.end_time - self.start_time) if self.end_time and self.start_time else 0
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        size_text = small_font.render(f"Kích thước: {self.size}x{self.size}", True, BLACK)
        screen.blit(size_text, (info_x, info_y))
        time_text = small_font.render(f"Thời gian: {minutes:02d}:{seconds:02d}", True, BLACK)
        screen.blit(time_text, (info_x, info_y + ButtonConfig.END_INFO_SPACING))
        moves_text = small_font.render(f"Số bước di chuyển: {self.move_count}", True, BLACK)
        screen.blit(moves_text, (info_x, info_y + 2 * ButtonConfig.END_INFO_SPACING))

        if self.solution_time > 0:
            pygame.draw.line(screen, BLUE, 
                            (left_panel_x + ButtonConfig.END_LINE_OFFSET, info_y + 3 * ButtonConfig.END_INFO_SPACING - 10), 
                            (left_panel_x + panel_width - ButtonConfig.END_LINE_OFFSET, info_y + 3 * ButtonConfig.END_INFO_SPACING - 10), 1)
            ai_title = small_font.render("So sánh với AI:", True, BLACK)
            screen.blit(ai_title, (info_x, info_y + 3 * ButtonConfig.END_INFO_SPACING))
            solution_text = small_font.render(f"Thời gian giải: {self.solution_time:.2f}s", True, BLACK)
            screen.blit(solution_text, (info_x, info_y + 4 * ButtonConfig.END_INFO_SPACING))
            if self.solution and len(self.solution) > 0:
                compare_text = small_font.render(f"Số bước của AI: {len(self.solution)}", True, BLACK)
                screen.blit(compare_text, (info_x, info_y + 5 * ButtonConfig.END_INFO_SPACING))

        pygame.draw.rect(screen, GRAY, (right_panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, BLACK, (right_panel_x, panel_y, panel_width, panel_height), 2)
        result_title = font.render("KẾT QUẢ", True, BLACK)
        screen.blit(result_title, (right_panel_x + panel_width//2 - result_title.get_width()//2, panel_y + 15))
        pygame.draw.line(screen, BLACK, 
                    (right_panel_x + ButtonConfig.END_LINE_OFFSET, panel_y + 50), 
                    (right_panel_x + panel_width - ButtonConfig.END_LINE_OFFSET, panel_y + 50), 2)
        self.draw_result_board(right_panel_x, panel_y)

    def draw_result_board(self, panel_x, panel_y):
        """Vẽ bảng kết quả trong panel kết quả"""
        if not self.puzzle:
            return
        panel_width = ButtonConfig.END_PANEL_WIDTH
        panel_title_height = ButtonConfig.END_PANEL_TITLE_HEIGHT
        margin = 20
        available_space = panel_width - 2 * margin
        result_tile_size = min(30, available_space // self.puzzle.size - 5)
        result_tile_size = max(result_tile_size, ButtonConfig.END_MIN_TILE_SIZE)
        board_width = self.puzzle.size * (result_tile_size + 5)
        board_height = self.puzzle.size * (result_tile_size + 5)
        board_x = panel_x + (panel_width - board_width) // 2
        board_y = panel_y + panel_title_height + ButtonConfig.END_RESULT_BOARD_Y_OFFSET
        for row in range(self.puzzle.size):
            for col in range(self.puzzle.size):
                value = self.puzzle.get_value(row, col)
                x = board_x + col * (result_tile_size + 5)
                y = board_y + row * (result_tile_size + 5)
                if value != 0:
                    if self.use_image and self.tile_images:
                        for tile_value, tile_img in self.tile_images:
                            if tile_value == value:
                                small_img = pygame.transform.scale(tile_img, (result_tile_size, result_tile_size))
                                screen.blit(small_img, (x, y))
                                break
                    else:
                        pygame.draw.rect(screen, LIGHT_BLUE, (x, y, result_tile_size, result_tile_size))
                    pygame.draw.rect(screen, BLACK, (x, y, result_tile_size, result_tile_size), 1)
                    if not self.use_image or SHOW_NUMBERS_WITH_IMAGE:
                        num_font_size = min(24, result_tile_size - 4)
                        num_font = pygame.font.SysFont("segoeui", num_font_size)
                        text = num_font.render(str(value), True, BLACK)
                        text_rect = text.get_rect(center=(x + result_tile_size // 2, y + result_tile_size // 2))
                        screen.blit(text, text_rect)

    def draw_how_to_play_screen(self):
        """Vẽ màn hình hướng dẫn cách chơi"""
        title = font.render("HƯỚNG DẪN CHƠI", True, BLUE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, ButtonConfig.HOW_TO_PLAY_TITLE_Y))
        instructions = [
            "1. Di chuyển các ô để sắp xếp về trạng thái đích hiển thị ở góc phải.",
            "2. Nhấp chuột vào ô cạnh ô trống để di chuyển ô đó vào vị trí ô trống.",
            "3. Bạn có thể sử dụng các thuật toán để tự động giải puzzle.",
            "4. Best First là thuật toán tìm kiếm tốt nhất, luôn tìm được lời giải tối ưu.",
            "5. Hill Climbing là thuật toán leo đồi, nhanh nhưng không luôn tìm được lời giải tối ưu.",
            "6. Bạn có thể điều chỉnh âm lượng trong phần Settings.",
            "7. Bạn có thể tải hình ảnh tùy chỉnh cho puzzle.",
        ]
        y_pos = ButtonConfig.HOW_TO_PLAY_TEXT_Y_START
        for line in instructions:
            text = small_font.render(line, True, BLACK)
            screen.blit(text, (ButtonConfig.HOW_TO_PLAY_TEXT_X_OFFSET, y_pos))
            y_pos += ButtonConfig.HOW_TO_PLAY_TEXT_SPACING

    def draw_settings_screen(self):
        """Vẽ màn hình cài đặt"""
        title = font.render("CÀI ĐẶT", True, BLUE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        volume_text = font.render(f"Âm lượng: {self.volume}%", True, BLACK)
        screen.blit(volume_text, (SCREEN_WIDTH//2 - volume_text.get_width()//2, 150))
        sound_status = "Bật" if self.sound_enabled else "Tắt"
        sound_text = font.render(f"Âm thanh: {sound_status}", True, BLACK)
        screen.blit(sound_text, (SCREEN_WIDTH//2 - sound_text.get_width()//2, 200))
        bar_width = 400
        bar_height = 30
        bar_x = SCREEN_WIDTH//2 - bar_width//2
        bar_y = 250
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * self.volume / 100)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)