# models/database.py
import pyodbc
from config import DB_CONFIG

class Database:
    def __init__(self):
        try:
            connection_string = (
                f'DRIVER={DB_CONFIG["DRIVER"]};'
                f'SERVER={DB_CONFIG["SERVER"]};'
                f'DATABASE={DB_CONFIG["DATABASE"]};'
                f'Trusted_Connection={DB_CONFIG["Trusted_Connection"]};'
            )
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
            self.create_tables_if_not_exist()
            print("Kết nối cơ sở dữ liệu thành công!")
        except Exception as e:
            print(f"Lỗi kết nối cơ sở dữ liệu: {e}")
            self.conn = None
            self.cursor = None
    
    def create_tables_if_not_exist(self):
        """Tạo các bảng nếu chưa tồn tại"""
        try:
            # Kiểm tra bảng PuzzleMaps có tồn tại không
            self.cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PuzzleMaps' AND xtype='U')
            CREATE TABLE PuzzleMaps (
                MapID INT IDENTITY(1,1) PRIMARY KEY,
                MapName NVARCHAR(100) NOT NULL,
                Size INT NOT NULL,
                BoardState NVARCHAR(MAX) NOT NULL,
                ImagePath NVARCHAR(MAX) NULL,
                CreateDate DATETIME DEFAULT GETDATE()
            )
            """)
            
            # Kiểm tra bảng PuzzleResults có tồn tại không
            self.cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PuzzleResults' AND xtype='U')
            CREATE TABLE PuzzleResults (
                ResultID INT IDENTITY(1,1) PRIMARY KEY,
                MapID INT NOT NULL,
                MoveCount INT NOT NULL,
                ElapsedTime INT NOT NULL,
                SolveDate DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (MapID) REFERENCES PuzzleMaps(MapID)
            )
            """)
            
            self.conn.commit()
            print("Đã tạo bảng thành công nếu chưa tồn tại!")
        except Exception as e:
            print(f"Lỗi khi tạo bảng: {e}")
    
    def save_map(self, map_name, size, board_state, image_path=None):
        """Lưu map vào cơ sở dữ liệu"""
        if not self.conn:
            print("Không có kết nối cơ sở dữ liệu!")
            return None
        
        try:
            query = """
            INSERT INTO PuzzleMaps (MapName, Size, BoardState, ImagePath)
            VALUES (?, ?, ?, ?)
            """
            self.cursor.execute(query, (map_name, size, board_state, image_path))
            self.conn.commit()
            map_id = self.cursor.execute("SELECT @@IDENTITY").fetchone()[0]
            print(f"Đã lưu map có ID: {map_id}")
            return map_id
        except Exception as e:
            print(f"Lỗi khi lưu map: {e}")
            return None
    
    def load_maps(self):
        """Lấy danh sách tất cả các map"""
        if not self.conn:
            print("Không có kết nối cơ sở dữ liệu!")
            return []
        
        try:
            self.cursor.execute("""
            SELECT MapID, MapName, Size, BoardState, ImagePath 
            FROM PuzzleMaps 
            ORDER BY CreateDate DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi khi tải danh sách map: {e}")
            return []
    
    def get_map_by_id(self, map_id):
        """Lấy thông tin map theo ID"""
        if not self.conn:
            print("Không có kết nối cơ sở dữ liệu!")
            return None
        
        try:
            self.cursor.execute("""
            SELECT MapID, MapName, Size, BoardState, ImagePath 
            FROM PuzzleMaps 
            WHERE MapID = ?
            """, map_id)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Lỗi khi tải map theo ID: {e}")
            return None
    
    def delete_map(self, map_id):
        """Xóa map theo ID"""
        if not self.conn:
            print("Không có kết nối cơ sở dữ liệu!")
            return False
        
        try:
            # Trước tiên xóa các kết quả liên quan
            self.cursor.execute("DELETE FROM PuzzleResults WHERE MapID = ?", map_id)
            # Sau đó xóa map
            self.cursor.execute("DELETE FROM PuzzleMaps WHERE MapID = ?", map_id)
            self.conn.commit()
            print(f"Đã xóa map có ID: {map_id}")
            return True
        except Exception as e:
            print(f"Lỗi khi xóa map: {e}")
            return False
    
    def save_result(self, map_id, move_count, elapsed_time):
        """Lưu kết quả vào cơ sở dữ liệu"""
        if not self.conn:
            print("Không có kết nối cơ sở dữ liệu!")
            return False
        
        try:
            query = """
            INSERT INTO PuzzleResults (MapID, MoveCount, ElapsedTime)
            VALUES (?, ?, ?)
            """
            self.cursor.execute(query, (map_id, move_count, elapsed_time))
            self.conn.commit()
            print(f"Đã lưu kết quả cho map có ID: {map_id}")
            return True
        except Exception as e:
            print(f"Lỗi khi lưu kết quả: {e}")
            return False
    
    def get_results_by_map_id(self, map_id):
        """Lấy danh sách kết quả theo map ID"""
        if not self.conn:
            print("Không có kết nối cơ sở dữ liệu!")
            return []
        
        try:
            self.cursor.execute("""
            SELECT ResultID, MoveCount, ElapsedTime, SolveDate
            FROM PuzzleResults 
            WHERE MapID = ?
            ORDER BY ElapsedTime ASC
            """, map_id)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi khi tải kết quả theo map ID: {e}")
            return []
    
    def close(self):
        """Đóng kết nối cơ sở dữ liệu"""
        if self.conn:
            self.conn.close()
            print("Đã đóng kết nối cơ sở dữ liệu!")