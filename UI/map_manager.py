# map_manager.py
import pygame
import time
import os
from tkinter import messagebox

# Import từ config
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, BLUE, RED, GREEN_BUTTON,
    font, small_font, screen
)

class MapManager:
    def __init__(self, game, db):
        self.game = game
        self.db = db
        self.visible = False
        self.maps = []
        self.current_page = 0
        self.maps_per_page = 5
        self.selected_map_index = None
        self.show_results = False
        self.results = []

    def load_maps(self):
        """Tải danh sách các map từ cơ sở dữ liệu"""
        self.maps = self.db.load_maps()
        self.current_page = 0
        self.selected_map_index = None
        self.show_results = False

    def show(self):
        """Hiển thị giao diện quản lý map"""
        self.visible = True
        self.load_maps()

    def hide(self):
        """Ẩn giao diện quản lý map"""
        self.visible = False
        self.show_results = False

    def load_map(self, map_index):
        """Tải một map cụ thể từ danh sách"""
        if 0 <= map_index < len(self.maps):
            map_id, map_name, size, board_state, image_path = self.maps[map_index]
            self.game.size = size
            self.game.puzzle = self.game.model_classes["Puzzle"](size)
            values = [int(x) for x in board_state.split(",")]
            for i in range(size):
                for j in range(size):
                    value = values[i * size + j]
                    self.game.puzzle.set_value(i, j, value)
            self.game.selected_map_id = map_id
            self.game.move_count = 0
            # Sửa lỗi: Thay self.game.time() bằng time.time()
            self.game.start_time = time.time()
            self.game.state = "playing"
            if image_path and os.path.exists(image_path):
                try:
                    self.game.image_path = image_path
                    self.game.original_image = pygame.image.load(image_path)
                    self.game.original_image = self.game.original_image.convert_alpha()
                    self.game.use_image = True
                    self.game.split_image()
                except Exception as e:
                    print(f"Không thể tải hình ảnh: {e}")
                    self.game.use_image = False
                    self.game.original_image = None
                    self.game.image_path = None
            else:
                self.game.use_image = False
                self.game.original_image = None
                self.game.image_path = None
            self.hide()
            print(f"Đã tải map: {map_name}")

    def delete_map(self, map_index):
        """Xóa một map khỏi cơ sở dữ liệu"""
        if 0 <= map_index < len(self.maps):
            map_id = self.maps[map_index][0]
            if self.db.delete_map(map_id):
                print(f"Đã xóa map ID: {map_id}")
                self.load_maps()
            else:
                print(f"Không thể xóa map ID: {map_id}")

    def show_results_for_map(self, map_index):
        """Hiển thị kết quả của một map cụ thể"""
        if 0 <= map_index < len(self.maps):
            map_id = self.maps[map_index][0]
            self.results = self.db.load_results(map_id)
            self.show_results = True
            self.selected_map_index = map_index

    def handle_events(self, event):
        """Xử lý sự kiện trong giao diện quản lý map"""
        if not self.visible:
            return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            start_index = self.current_page * self.maps_per_page
            end_index = min(start_index + self.maps_per_page, len(self.maps))

            # Xử lý nút đóng
            close_btn = pygame.Rect(SCREEN_WIDTH - 70, 110, 50, 50)
            if close_btn.collidepoint(mouse_pos):
                self.hide()
                return True

            # Xử lý các nút trong danh sách map
            for i in range(start_index, end_index):
                map_idx = i - start_index
                map_y = 180 + map_idx * 100
                select_btn = pygame.Rect(SCREEN_WIDTH//2 - 300, map_y + 50, 100, 40)
                delete_btn = pygame.Rect(SCREEN_WIDTH//2 - 150, map_y + 50, 100, 40)
                result_btn = pygame.Rect(SCREEN_WIDTH//2 - 0, map_y + 50, 100, 40)

                if select_btn.collidepoint(mouse_pos):
                    self.load_map(i)
                    return True
                elif delete_btn.collidepoint(mouse_pos):
                    if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa map này?"):
                        self.delete_map(i)
                    return True
                elif result_btn.collidepoint(mouse_pos):
                    self.show_results_for_map(i)
                    return True

            # Xử lý nút phân trang
            prev_btn = pygame.Rect(SCREEN_WIDTH//2 - 150, 680, 100, 40)
            next_btn = pygame.Rect(SCREEN_WIDTH//2 + 50, 680, 100, 40)
            if prev_btn.collidepoint(mouse_pos) and self.current_page > 0:
                self.current_page -= 1
                return True
            elif next_btn.collidepoint(mouse_pos) and (self.current_page + 1) * self.maps_per_page < len(self.maps):
                self.current_page += 1
                return True

            # Xử lý nút đóng kết quả
            if self.show_results:
                close_results_btn = pygame.Rect(SCREEN_WIDTH - 70, 110, 50, 50)
                if close_results_btn.collidepoint(mouse_pos):
                    self.show_results = False
                    return True

        return True

    def draw(self):
        """Vẽ giao diện quản lý map"""
        if not self.visible:
            return

        # Vẽ nền mờ
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Vẽ panel chính
        panel_width = 700
        panel_height = 600
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

        # Vẽ nút đóng
        close_btn = pygame.Rect(SCREEN_WIDTH - 70, 110, 50, 50)
        pygame.draw.rect(screen, RED, close_btn)
        close_text = font.render("X", True, WHITE)
        screen.blit(close_text, (close_btn.x + 15, close_btn.y + 5))

        # Vẽ tiêu đề
        title = font.render("QUẢN LÝ MAP", True, BLUE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 120))

        if not self.show_results:
            # Hiển thị danh sách map
            start_index = self.current_page * self.maps_per_page
            end_index = min(start_index + self.maps_per_page, len(self.maps))

            for i in range(start_index, end_index):
                map_idx = i - start_index
                map_data = self.maps[i]
                map_name = map_data[1]
                size = map_data[2]
                map_y = 180 + map_idx * 100

                # Vẽ thông tin map
                map_info = small_font.render(f"Map: {map_name} - Kích thước: {size}x{size}", True, BLACK)
                screen.blit(map_info, (SCREEN_WIDTH//2 - 300, map_y))

                # Vẽ các nút
                select_btn = pygame.Rect(SCREEN_WIDTH//2 - 300, map_y + 50, 100, 40)
                delete_btn = pygame.Rect(SCREEN_WIDTH//2 - 150, map_y + 50, 100, 40)
                result_btn = pygame.Rect(SCREEN_WIDTH//2 - 0, map_y + 50, 100, 40)

                pygame.draw.rect(screen, GREEN_BUTTON, select_btn)
                pygame.draw.rect(screen, RED, delete_btn)
                pygame.draw.rect(screen, BLUE, result_btn)

                select_text = small_font.render("Chọn", True, BLACK)
                delete_text = small_font.render("Xóa", True, WHITE)
                result_text = small_font.render("", True, WHITE)

                screen.blit(select_text, (select_btn.x + 25, select_btn.y + 10))
                screen.blit(delete_text, (delete_btn.x + 25, delete_btn.y + 10))
                screen.blit(result_text, (result_btn.x + 15, result_btn.y + 10))

            # Vẽ nút phân trang
            if len(self.maps) > self.maps_per_page:
                prev_btn = pygame.Rect(SCREEN_WIDTH//2 - 150, 680, 100, 40)
                next_btn = pygame.Rect(SCREEN_WIDTH//2 + 50, 680, 100, 40)

                pygame.draw.rect(screen, GRAY if self.current_page == 0 else GREEN_BUTTON, prev_btn)
                pygame.draw.rect(screen, GRAY if (self.current_page + 1) * self.maps_per_page >= len(self.maps) else GREEN_BUTTON, next_btn)

                prev_text = small_font.render("Trước", True, BLACK)
                next_text = small_font.render("Sau", True, BLACK)

                screen.blit(prev_text, (prev_btn.x + 15, prev_btn.y + 10))
                screen.blit(next_text, (next_btn.x + 25, next_btn.y + 10))

        else:
            # Hiển thị kết quả của map được chọn
            map_name = self.maps[self.selected_map_index][1]
            result_title = font.render(f"Kết quả của {map_name}", True, BLUE)
            screen.blit(result_title, (SCREEN_WIDTH//2 - result_title.get_width()//2, 120))

            if not self.results:
                no_result = small_font.render("Chưa có kết quả nào!", True, BLACK)
                screen.blit(no_result, (SCREEN_WIDTH//2 - no_result.get_width()//2, 300))
            else:
                y_pos = 180
                for idx, result in enumerate(self.results[:5]):
                    moves = result[1]
                    time_taken = result[2]
                    result_text = small_font.render(f"Kết quả {idx + 1}: {moves} bước, {time_taken}s", True, BLACK)
                    screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, y_pos))
                    y_pos += 50

    def is_visible(self):
        """Kiểm tra xem giao diện quản lý map có đang hiển thị không"""
        return self.visible