# main.py - Điểm khởi đầu của ứng dụng
import pygame
import sys
from game import Game
from config import clock

def main():
    print("Đang khởi động trò chơi...")
    game = Game()
    print("Đã khởi tạo trò chơi")
    running = True
    
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                game.handle_events(event)
            
            game.update()
            game.draw()
            clock.tick(60)
    finally:
        game.db.close()
        print("Đã đóng kết nối cơ sở dữ liệu")
    
    print("Trò chơi đã thoát")
    pygame.quit()
    sys.exit()

# Gọi hàm main khi chạy file trực tiếp
if __name__ == "__main__":
    main()