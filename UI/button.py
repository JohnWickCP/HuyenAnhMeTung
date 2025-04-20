# ui/button.py
import pygame
from config import BLACK, screen, small_font

class Button:
    def __init__(self, text, x, y, width, height, action=None, color=None):
        from config import LIGHT_BLUE
        
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = action
        self.color = color if color is not None else LIGHT_BLUE
        self.hover_color = (min(self.color[0] + 50, 255), 
                           min(self.color[1] + 50, 255), 
                           min(self.color[2] + 50, 255))
        self.text_color = BLACK
        self.hover = False
    
    def draw(self):
        """Vẽ nút lên màn hình với góc bo tròn và không viền"""
        mouse_pos = pygame.mouse.get_pos()
        self.hover = (self.x <= mouse_pos[0] <= self.x + self.width and 
                      self.y <= mouse_pos[1] <= self.y + self.height)
        
        color = self.hover_color if self.hover else self.color
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), border_radius=5)
        
        text_surf = small_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        """Kiểm tra xem nút có được nhấn không"""
        if self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height:
            return True
        return False