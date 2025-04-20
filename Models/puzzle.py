# models/puzzle.py
import random
from config import TILE_MARGIN, TILE_SIZE

class Puzzle:
    """
    Lớp đại diện cho trạng thái của puzzle N×N.
    Với puzzle 8 truyền thống, N = 3.
    """
    def __init__(self, size=3):
        """Khởi tạo một puzzle với kích thước size×size."""
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.blank_pos = (size-1, size-1)
        self.initialize()
    
    def initialize(self):
        """Khởi tạo puzzle ở trạng thái giải (1,2,3,...,0)"""
        counter = 1
        for i in range(self.size):
            for j in range(self.size):
                if counter < self.size * self.size:
                    self.board[i][j] = counter
                else:
                    self.board[i][j] = 0  # Ô trống
                counter += 1
        self.blank_pos = (self.size-1, self.size-1)
    
    def shuffle(self, moves=100):
        """Trộn puzzle bằng cách thực hiện các nước đi ngẫu nhiên hợp lệ"""
        for _ in range(moves):
            possible_moves = self.get_possible_moves()
            direction = random.choice(possible_moves)
            self.move(direction)
        return self
    
    def get_blank_pos(self):
        """Trả về vị trí (row, col) của ô trống"""
        return self.blank_pos
    
    def get_possible_moves(self):
        """Trả về danh sách các hướng có thể di chuyển ô trống"""
        row, col = self.blank_pos
        moves = []
        
        # Kiểm tra 4 hướng: lên, xuống, trái, phải
        if row > 0:  # Có thể di chuyển lên
            moves.append('UP')
        if row < self.size - 1:  # Có thể di chuyển xuống
            moves.append('DOWN')
        if col > 0:  # Có thể di chuyển sang trái
            moves.append('LEFT')
        if col < self.size - 1:  # Có thể di chuyển sang phải
            moves.append('RIGHT')
            
        return moves
    
    def move(self, direction):
        """
        Di chuyển ô trống theo hướng đã cho
        direction: 'UP', 'DOWN', 'LEFT', 'RIGHT'
        Trả về True nếu di chuyển thành công, False nếu không
        """
        row, col = self.blank_pos
        new_row, new_col = row, col
        
        if direction == 'UP':
            new_row = row - 1
        elif direction == 'DOWN':
            new_row = row + 1
        elif direction == 'LEFT':
            new_col = col - 1
        elif direction == 'RIGHT':
            new_col = col + 1
        else:
            return False
        
        # Kiểm tra nếu vị trí mới nằm ngoài bảng
        if new_row < 0 or new_row >= self.size or new_col < 0 or new_col >= self.size:
            return False
        
        # Hoán đổi ô trống với ô được chọn
        self.board[row][col] = self.board[new_row][new_col]
        self.board[new_row][new_col] = 0
        self.blank_pos = (new_row, new_col)
        
        return True
    
    def is_goal(self):
        """Kiểm tra xem trạng thái hiện tại có phải là đích không"""
        counter = 1
        for i in range(self.size):
            for j in range(self.size):
                if i == self.size - 1 and j == self.size - 1:
                    if self.board[i][j] != 0:
                        return False
                elif self.board[i][j] != counter:
                    return False
                counter += 1
        return True
    
    def manhattan_distance(self):
        """Tính tổng khoảng cách Manhattan từ mỗi ô đến vị trí đích"""
        distance = 0
        for i in range(self.size):
            for j in range(self.size):
                value = self.board[i][j]
                if value != 0:
                    # Vị trí đích của giá trị
                    goal_row = (value - 1) // self.size
                    goal_col = (value - 1) % self.size
                    # Tính khoảng cách Manhattan
                    distance += abs(i - goal_row) + abs(j - goal_col)
        return distance
    
    def clone(self):
        """Tạo một bản sao của puzzle hiện tại"""
        new_puzzle = Puzzle(self.size)
        new_puzzle.board = [row[:] for row in self.board]
        new_puzzle.blank_pos = self.blank_pos
        return new_puzzle
    
    def get_value(self, row, col):
        """Lấy giá trị tại vị trí (row, col)"""
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.board[row][col]
        return None
    
    def set_value(self, row, col, value):
        """Đặt giá trị tại vị trí (row, col)"""
        if 0 <= row < self.size and 0 <= col < self.size:
            self.board[row][col] = value
            if value == 0:
                self.blank_pos = (row, col)
            return True
        return False
    
    def handle_click(self, pos, board_x, board_y, tile_size=TILE_SIZE):
        """Xử lý sự kiện khi người dùng nhấn chuột vào ô"""
        # Tính toán vị trí của ô được nhấn với kích thước ô được điều chỉnh
        col = (pos[0] - board_x) // (tile_size + TILE_MARGIN)
        row = (pos[1] - board_y) // (tile_size + TILE_MARGIN)
        
        # Kiểm tra xem vị trí có hợp lệ và cạnh ô trống không
        if 0 <= row < self.size and 0 <= col < self.size:
            blank_row, blank_col = self.blank_pos
            
            # Kiểm tra xem ô được nhấn có cạnh ô trống không
            if (row == blank_row and abs(col - blank_col) == 1) or \
            (col == blank_col and abs(row - blank_row) == 1):
                
                # Xác định hướng di chuyển của ô trống
                if row < blank_row:
                    return self.move('UP')
                elif row > blank_row:
                    return self.move('DOWN')
                elif col < blank_col:
                    return self.move('LEFT')
                elif col > blank_col:
                    return self.move('RIGHT')
        
        return False