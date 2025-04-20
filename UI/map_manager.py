# ui/map_manager.py
import pygame
import os
from config import screen, WHITE, BLACK, BLUE, LIGHT_BLUE, GREEN, RED, GREEN_BUTTON, SCREEN_WIDTH, SCREEN_HEIGHT

class MapManager:
    def __init__(self, game, db):
        self.game = game
        self.db = db
        self.maps = []
        self.current_page = 0
        self.maps_per_page = 5
        self.visible = False
        self.title_font = pygame.font.SysFont("segoeui", 32, bold=True)
        self.font = pygame.font.SysFont("segoeui", 24)
        self.small_font = pygame.font.SysFont("segoeui", 18)
        self.load_maps()
    
    def load_maps(self):
        """Tải danh sách map từ cơ sở dữ liệu"""
        self.maps = self.db.load_maps()
        print(f"Đã tải {len(self.maps)} map từ cơ sở dữ liệu")
    
    def show(self):
        """Hiển thị giao diện quản lý map"""
        self.visible = True
    
    def hide(self):
        """Ẩn giao diện quản lý map"""
        self.visible = False
    
    def is_visible(self):
        """Kiểm tra xem giao diện có đang hiển thị không"""
        return self.visible
    
    def next_page(self):
        """Chuyển đến trang tiếp theo"""
        max_pages = (len(self.maps) - 1) // self.maps_per_page + 1
        if self.current_page < max_pages - 1:
            self.current_page += 1
    
    def prev_page(self):
        """Quay lại trang trước"""
        if self.current_page > 0:
            self.current_page -= 1
    
    def load_map(self, map_index):
        """Tải map được chọn"""
        if 0 <= map_index < len(self.maps):
            map_data = self.maps[map_index]
            map_id, map_name, size, board_state, image_path = map_data
            
            # Cập nhật kích thước puzzle
            self.game.size = size
            
            # Tạo puzzle mới
            self.game.puzzle = self.game.model_classes["Puzzle"](size)
            
            # Tạo puzzle đích
            self.game.goal_puzzle = self.game.model_classes["Puzzle"](size)
            self.game.goal_puzzle.initialize()
            
            # Cập nhật trạng thái từ cơ sở dữ liệu
            values = [int(x) for x in board_state.split(",")]
            for i in range(size):
                for j in range(size):
                    value = values[i * size + j]
                    self.game.puzzle.set_value(i, j, value)
            
            # Cập nhật các biến khác
            self.game.move_count = 0
            self.game.start_time = self.game.time()
            self.game.state = "playing"
            self.game.solution = []
            self.game.solution_index = 0
            self.game.selected_map_id = map_id
            
            # Tải hình ảnh nếu có
            if image_path and os.path.exists(image_path):
                self.game.image_path = image_path
                self.game.original_image = pygame.image.load(image_path)
                self.game.original_image = self.game.original_image.convert_alpha()
                self.game.use_image = True
                self.game.split_image()
            else:
                self.game.use_image = False
                self.game.original_image = None
                self.game.image_path = None
            
            print(f"Đã tải map: {map_name}")
            self.hide()
            
            # Phát nhạc game
            if self.game.sound_enabled:
                self.game.play_music("game")
    
    def draw(self):
        """Vẽ giao diện quản lý map"""
        if not self.visible:
            return
        
        # Vẽ hộp thoại đè lên màn hình chính
        dialog_width = 700
        dialog_height = 500
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        # Vẽ lớp phủ mờ
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # RGBA với alpha = 128 (mờ 50%)
        screen.blit(overlay, (0, 0))
        
        # Vẽ hộp thoại
        pygame.draw.rect(screen, WHITE, (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(screen, BLACK, (dialog_x, dialog_y, dialog_width, dialog_height), 2)
        
        # Vẽ tiêu đề
        title = self.title_font.render("QUẢN LÝ MAP", True, BLUE)
        screen.blit(title, (dialog_x + dialog_width // 2 - title.get_width() // 2, dialog_y + 20))
        
        # Vẽ danh sách map
        if not self.maps:
            no_maps_text = self.font.render("Không có map nào. Hãy tạo map mới!", True, BLACK)
            screen.blit(no_maps_text, (dialog_x + dialog_width // 2 - no_maps_text.get_width() // 2, dialog_y + 200))
        else:
            # Tính số trang
            max_pages = (len(self.maps) - 1) // self.maps_per_page + 1
            
            # Vẽ thông tin trang
            page_info = self.small_font.render(f"Trang {self.current_page + 1}/{max_pages}", True, BLACK)
            screen.blit(page_info, (dialog_x + dialog_width // 2 - page_info.get_width() // 2, dialog_y + 60))
            
            # Vẽ nút Previous/Next
            if self.current_page > 0:
                prev_btn = pygame.Rect(dialog_x + 50, dialog_y + 55, 80, 30)
                pygame.draw.rect(screen, LIGHT_BLUE, prev_btn, border_radius=5)
                prev_text = self.small_font.render("< Trước", True, BLACK)
                screen.blit(prev_text, (prev_btn.x + prev_btn.width // 2 - prev_text.get_width() // 2, prev_btn.y + 5))
            
            if self.current_page < max_pages - 1:
                next_btn = pygame.Rect(dialog_x + dialog_width - 130, dialog_y + 55, 80, 30)
                pygame.draw.rect(screen, LIGHT_BLUE, next_btn, border_radius=5)
                next_text = self.small_font.render("Sau >", True, BLACK)
                screen.blit(next_text, (next_btn.x + next_btn.width // 2 - next_text.get_width() // 2, next_btn.y + 5))
            
            # Vẽ từng map
            start_index = self.current_page * self.maps_per_page
            end_index = min(start_index + self.maps_per_page, len(self.maps))
            
            for i in range(start_index, end_index):
                map_index = i
                map_id, map_name, size, board_state, image_path = self.maps[map_index]
                
                y_offset = 100 + (i - start_index) * 70
                map_rect = pygame.Rect(dialog_x + 50, dialog_y + y_offset, dialog_width - 100, 60)
                
                # Vẽ nền cho mỗi map
                pygame.draw.rect(screen, LIGHT_BLUE, map_rect, border_radius=5)
                
                # Vẽ thông tin map
                map_title = self.font.render(f"{map_name} ({size}x{size})", True, BLACK)
                screen.blit(map_title, (map_rect.x + 10, map_rect.y + 5))
                
                # Hiển thị nếu có hình ảnh
                has_image = "Có hình ảnh" if image_path and os.path.exists(image_path) else "Không có hình ảnh"
                img_text = self.small_font.render(has_image, True, GREEN if image_path else RED)
                screen.blit(img_text, (map_rect.x + 10, map_rect.y + 35))
                
                # Vẽ nút Load và Delete
                load_btn = pygame.Rect(map_rect.x + map_rect.width - 170, map_rect.y + 15, 70, 30)
                pygame.draw.rect(screen, GREEN_BUTTON, load_btn, border_radius=5)
                load_text = self.small_font.render("Tải", True, BLACK)
                screen.blit(load_text, (load_btn.x + load_btn.width // 2 - load_text.get_width() // 2, load_btn.y + 5))
                
                delete_btn = pygame.Rect(map_rect.x + map_rect.width - 90, map_rect.y + 15, 70, 30)
                pygame.draw.rect(screen, RED, delete_btn, border_radius=5)
                delete_text = self.small_font.render("Xóa", True, WHITE)
                screen.blit(delete_text, (delete_btn.x + delete_btn.width // 2 - delete_text.get_width() // 2, delete_btn.y + 5))
        
        # Vẽ nút Đóng
        close_btn = pygame.Rect(dialog_x + dialog_width // 2 - 50, dialog_y + dialog_height - 50, 100, 35)
        pygame.draw.rect(screen, GREEN_BUTTON, close_btn, border_radius=5)
        close_text = self.font.render("Đóng", True, BLACK)
        screen.blit(close_text, (close_btn.x + close_btn.width // 2 - close_text.get_width() // 2, close_btn.y + 7))
    
    def handle_events(self, event):
        """Xử lý sự kiện cho giao diện quản lý map"""
        if not self.visible:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Xử lý nút Đóng
            dialog_width = 700
            dialog_height = 500
            dialog_x = (SCREEN_WIDTH - dialog_width) // 2
            dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
            
            close_btn = pygame.Rect(dialog_x + dialog_width // 2 - 50, dialog_y + dialog_height - 50, 100, 35)
            if close_btn.collidepoint(mouse_pos):
                self.hide()
                return True
            
            # Xử lý nút Previous/Next
            if self.current_page > 0:
                prev_btn = pygame.Rect(dialog_x + 50, dialog_y + 55, 80, 30)
                if prev_btn.collidepoint(mouse_pos):
                    self.prev_page()
                    return True
            
            # Tính số trang
            max_pages = (len(self.maps) - 1) // self.maps_per_page + 1
            if self.current_page < max_pages - 1:
                next_btn = pygame.Rect(dialog_x + dialog_width - 130, dialog_y + 55, 80, 30)
                if next_btn.collidepoint(mouse_pos):
                    self.next_page()
                    return True
            
            # Xử lý nút Load và Delete
            if self.maps:
                start_index = self.current_page * self.maps_per_page
                end_index = min(start_index + self.maps_per_page, len(self.maps))
                
                for i in range(start_index, end_index):
                    map_index = i
                    
                    y_offset = 100 + (i - start_index) * 70
                    map_rect = pygame.Rect(dialog_x + 50, dialog_y + y_offset, dialog_width - 100, 60)
                    
                    # Xử lý nút Load
                    load_btn = pygame.Rect(map_rect.x + map_rect.width - 170, map_rect.y + 15, 70, 30)
                    if load_btn.collidepoint(mouse_pos):
                        self.load_map(map_index)
                        return True
                    
                    # Xử lý nút Delete
                    delete_btn = pygame.Rect(map_rect.x + map_rect.width - 90, map_rect.y + 15, 70, 30)
                    if delete_btn.collidepoint(mouse_pos):
                        map_id = self.maps[map_index][0]
                        if self.db.delete_map(map_id):
                            self.load_maps()  # Tải lại danh sách map
                        return True
        
        return True