# models/algorithms.py
import heapq
import time

class Node:
    """Lớp đại diện cho một nút trong quá trình tìm kiếm"""
    def __init__(self, puzzle, parent=None, action=None):
        self.puzzle = puzzle
        self.parent = parent
        self.action = action
        self.g = 0  # Số bước đi từ trạng thái ban đầu
        self.h = puzzle.manhattan_distance()  # Giá trị heuristic
        self.f = self.g + self.h  # Tổng giá trị đánh giá
    
    def __lt__(self, other):
        """So sánh để sử dụng trong hàng đợi ưu tiên"""
        return self.f < other.f

class BestFirstSearch:
    """Thuật toán Best-first Search sử dụng Manhattan distance"""
    def __init__(self, puzzle):
        self.initial_puzzle = puzzle.clone()
        self.solution = []
        self.explored = set()
        self.step_count = 0
    
    def solve(self):
        """Tìm lời giải cho puzzle sử dụng Best-first Search"""
        start_time = time.time()
        
        # Tạo nút gốc
        start_node = Node(self.initial_puzzle)
        
        # Hàng đợi ưu tiên
        frontier = []
        heapq.heappush(frontier, start_node)
        frontier_set = {self._get_state_tuple(start_node.puzzle)}
        
        while frontier:
            # Lấy nút có giá trị f nhỏ nhất
            current = heapq.heappop(frontier)
            frontier_set.remove(self._get_state_tuple(current.puzzle))
            
            # Kiểm tra nếu đã đạt mục tiêu
            if current.puzzle.is_goal():
                # Lưu lời giải
                path = []
                while current.parent:
                    path.append(current.action)
                    current = current.parent
                self.solution = list(reversed(path))
                self.step_count = len(self.solution)
                end_time = time.time()
                return True, self.step_count, end_time - start_time
            
            # Thêm trạng thái hiện tại vào tập đã khám phá
            self.explored.add(self._get_state_tuple(current.puzzle))
            
            # Khám phá các trạng thái kề
            for action in current.puzzle.get_possible_moves():
                child_puzzle = current.puzzle.clone()
                child_puzzle.move(action)
                child_state = self._get_state_tuple(child_puzzle)
                
                # Kiểm tra nếu trạng thái đã được khám phá
                if child_state in self.explored or child_state in frontier_set:
                    continue
                
                # Tạo nút con
                child = Node(
                    puzzle=child_puzzle,
                    parent=current,
                    action=action
                )
                child.g = current.g + 1
                child.f = child.g + child.h
                
                # Thêm vào hàng đợi ưu tiên
                heapq.heappush(frontier, child)
                frontier_set.add(child_state)
        
        # Không tìm thấy lời giải
        end_time = time.time()
        return False, 0, end_time - start_time
    
    def _get_state_tuple(self, puzzle):
        """Chuyển đổi trạng thái puzzle thành tuple để có thể sử dụng làm khóa trong set"""
        return tuple(tuple(row) for row in puzzle.board)
    
    def get_solution(self):
        """Trả về lời giải"""
        return self.solution
    
    def get_step_count(self):
        """Trả về số bước của lời giải"""
        return self.step_count

class HillClimbing:
    """Thuật toán Hill Climbing sử dụng Manhattan distance"""
    def __init__(self, puzzle):
        self.initial_puzzle = puzzle.clone()
        self.solution = []
        self.step_count = 0
    
    def solve(self):
        """Tìm lời giải cho puzzle sử dụng Hill Climbing"""
        start_time = time.time()
        
        current_puzzle = self.initial_puzzle.clone()
        path = []
        
        max_iterations = 1000  # Giới hạn số lần lặp để tránh vòng lặp vô hạn
        iterations = 0
        
        while not current_puzzle.is_goal() and iterations < max_iterations:
            iterations += 1
            
            # Tính toán giá trị heuristic hiện tại
            current_h = current_puzzle.manhattan_distance()
            
            # Khởi tạo biến để lưu nước đi tốt nhất
            best_move = None
            best_h = float('inf')
            
            # Thử mọi nước đi có thể
            for move in current_puzzle.get_possible_moves():
                # Tạo trạng thái mới sau khi di chuyển
                new_puzzle = current_puzzle.clone()
                new_puzzle.move(move)
                
                # Tính toán giá trị heuristic mới
                new_h = new_puzzle.manhattan_distance()
                
                # Nếu tìm thấy nước đi tốt hơn
                if new_h < best_h:
                    best_h = new_h
                    best_move = move
            
            # Nếu không tìm thấy nước đi tốt hơn, thoát vòng lặp
            if best_h >= current_h:
                break
            
            # Thực hiện nước đi tốt nhất
            current_puzzle.move(best_move)
            path.append(best_move)
        
        # Lưu lời giải
        self.solution = path
        self.step_count = len(path)
        
        end_time = time.time()
        if current_puzzle.is_goal():
            return True, self.step_count, end_time - start_time
        else:
            return False, self.step_count, end_time - start_time
    
    def get_solution(self):
        """Trả về lời giải"""
        return self.solution
    
    def get_step_count(self):
        """Trả về số bước của lời giải"""
        return self.step_count