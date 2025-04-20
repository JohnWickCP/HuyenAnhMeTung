# Hướng dẫn cài đặt và cấu hình cơ sở dữ liệu

Trò chơi "Huyễn Ảnh Mê Tung" sử dụng Microsoft SQL Server để lưu trữ các bản đồ puzzle và kết quả. Tài liệu này hướng dẫn chi tiết cách cài đặt và cấu hình cơ sở dữ liệu cần thiết cho trò chơi.

## Cài đặt SQL Server

### Bước 1: Tải và cài đặt SQL Server

1. Tải xuống SQL Server Express từ trang web chính thức của Microsoft:
   - Truy cập [https://www.microsoft.com/en-us/sql-server/sql-server-downloads](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
   - Chọn "Download for free" dưới phiên bản SQL Server Express

2. Chạy file cài đặt:
   - Chọn "Basic" cho cài đặt cơ bản hoặc "Custom" nếu muốn tùy chỉnh thêm
   - Trong quá trình cài đặt, lưu ý tên instance (mặc định là "SQLEXPRESS")

3. Thiết lập xác thực:
   - Đảm bảo bạn chọn "Mixed Mode Authentication" (cho phép cả Windows Authentication và SQL Server Authentication)
   - Tạo mật khẩu cho tài khoản 'sa' (system administrator)
   - Ghi nhớ tên instance và mật khẩu sa cho các bước tiếp theo

### Bước 2: Cài đặt SQL Server Management Studio (SSMS)

1. Tải SSMS từ trang web Microsoft:
   - Truy cập [https://docs.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms](https://docs.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms)
   - Nhấn vào liên kết tải xuống phiên bản mới nhất

2. Cài đặt SSMS theo hướng dẫn trên màn hình

### Bước 3: Cài đặt ODBC Driver cho SQL Server

1. Tải ODBC Driver 17 cho SQL Server:
   - Truy cập [https://www.microsoft.com/en-us/download/details.aspx?id=56567](https://www.microsoft.com/en-us/download/details.aspx?id=56567)
   - Chọn phiên bản phù hợp với hệ điều hành của bạn (32-bit hoặc 64-bit)

2. Cài đặt driver theo hướng dẫn trên màn hình

## Tạo cơ sở dữ liệu puzzle8

### Sử dụng SQL Server Management Studio

1. Mở SQL Server Management Studio
2. Kết nối đến SQL Server:
   - Server name: `localhost` hoặc `localhost\SQLEXPRESS` (nếu bạn cài đặt instance mặc định)
   - Authentication: Chọn "SQL Server Authentication"
   - Login: sa
   - Password: [mật khẩu bạn đã tạo]

3. Tạo cơ sở dữ liệu mới:
   - Nhấn chuột phải vào "Databases" trong Object Explorer
   - Chọn "New Database"
   - Đặt tên là "puzzle8"
   - Nhấn OK

### Sử dụng T-SQL Script

Nếu bạn muốn sử dụng script để tạo cơ sở dữ liệu, bạn có thể:

1. Mở SQL Server Management Studio và kết nối
2. Nhấn vào nút "New Query"
3. Sao chép và dán đoạn script sau:

```sql
-- Tạo cơ sở dữ liệu
USE master;
GO

-- Kiểm tra và xóa cơ sở dữ liệu cũ nếu tồn tại
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'puzzle_8')
BEGIN
    ALTER DATABASE puzzle_8 SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE puzzle_8;
END
GO

-- Tạo cơ sở dữ liệu mới
CREATE DATABASE puzzle_8;
GO

-- Sử dụng cơ sở dữ liệu
USE puzzle_8;
GO

-- Tạo bảng lưu trữ thông tin map
CREATE TABLE PuzzleMaps (
    MapID INT IDENTITY(1,1) PRIMARY KEY,
    MapName NVARCHAR(100) NOT NULL,
    Size INT NOT NULL, -- Kích thước map (3 cho 3x3, 4 cho 4x4, 5 cho 5x5)
    BoardState NVARCHAR(MAX) NOT NULL, -- Trạng thái bảng (chuỗi các số phân cách bởi dấu phẩy)
    ImagePath NVARCHAR(MAX) NULL, -- Đường dẫn đến hình ảnh (nếu có)
    CreateDate DATETIME DEFAULT GETDATE() -- Ngày tạo map
);
GO

-- Tạo bảng lưu trữ kết quả giải
CREATE TABLE PuzzleResults (
    ResultID INT IDENTITY(1,1) PRIMARY KEY,
    MapID INT NOT NULL,
    MoveCount INT NOT NULL, -- Số bước di chuyển
    ElapsedTime INT NOT NULL, -- Thời gian giải (giây)
    SolveDate DATETIME DEFAULT GETDATE(), -- Ngày giải
    FOREIGN KEY (MapID) REFERENCES PuzzleMaps(MapID) ON DELETE CASCADE -- Khóa ngoại đến bảng Maps
);
GO

-- Tạo index để tăng tốc truy vấn
CREATE INDEX IX_PuzzleResults_MapID ON PuzzleResults(MapID);
GO
CREATE INDEX IX_PuzzleMaps_CreateDate ON PuzzleMaps(CreateDate);
GO

-- Tạo stored procedure để lấy danh sách map
CREATE PROCEDURE GetAllMaps
AS
BEGIN
    SELECT MapID, MapName, Size, BoardState, ImagePath, CreateDate
    FROM PuzzleMaps
    ORDER BY CreateDate DESC;
END
GO

-- Tạo stored procedure để lấy kết quả của một map
CREATE PROCEDURE GetMapResults
    @MapID INT
AS
BEGIN
    SELECT ResultID, MoveCount, ElapsedTime, SolveDate
    FROM PuzzleResults
    WHERE MapID = @MapID
    ORDER BY ElapsedTime ASC;
END
GO

-- Tạo stored procedure để lưu map mới
CREATE PROCEDURE SaveMap
    @MapName NVARCHAR(100),
    @Size INT,
    @BoardState NVARCHAR(MAX),
    @ImagePath NVARCHAR(MAX) = NULL
AS
BEGIN
    INSERT INTO PuzzleMaps (MapName, Size, BoardState, ImagePath)
    VALUES (@MapName, @Size, @BoardState, @ImagePath);
    
    DECLARE @MapID INT = SCOPE_IDENTITY();
    RETURN @MapID;
END
GO

-- Tạo stored procedure để lưu kết quả
CREATE PROCEDURE SaveResult
    @MapID INT,
    @MoveCount INT,
    @ElapsedTime INT
AS
BEGIN
    INSERT INTO PuzzleResults (MapID, MoveCount, ElapsedTime)
    VALUES (@MapID, @MoveCount, @ElapsedTime);
END
GO

-- Tạo stored procedure để xóa map
CREATE PROCEDURE DeleteMap
    @MapID INT
AS
BEGIN
    DELETE FROM PuzzleMaps WHERE MapID = @MapID;
END
GO

-- Tạo stored procedure để lấy 10 kết quả tốt nhất (ít bước nhất)
CREATE PROCEDURE GetTop10Results
AS
BEGIN
    SELECT TOP 10 pr.ResultID, pm.MapName, pm.Size, pr.MoveCount, pr.ElapsedTime, pr.SolveDate
    FROM PuzzleResults pr
    JOIN PuzzleMaps pm ON pr.MapID = pm.MapID
    ORDER BY pr.MoveCount ASC, pr.ElapsedTime ASC;
END
GO

-- Tạo các map mẫu để test
-- Map 3x3 đã giải (trạng thái đích)
INSERT INTO PuzzleMaps (MapName, Size, BoardState)
VALUES ('3x3 Đã giải', 3, '1,2,3,4,5,6,7,8,0');
GO

-- Map 3x3 đã trộn (ví dụ)
INSERT INTO PuzzleMaps (MapName, Size, BoardState)
VALUES ('3x3 Đơn giản', 3, '1,2,3,4,0,6,7,5,8');
GO

-- Map 4x4 đã giải
INSERT INTO PuzzleMaps (MapName, Size, BoardState)
VALUES ('4x4 Đã giải', 4, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0');
GO

-- Map 5x5 đã giải
INSERT INTO PuzzleMaps (MapName, Size, BoardState)
VALUES ('5x5 Đã giải', 5, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,0');
GO

```

4. Nhấn F5 hoặc nút "Execute" để chạy script

## Cấu hình kết nối trong trò chơi

Trò chơi sử dụng chuỗi kết nối trong class `Database` để kết nối đến SQL Server. Nếu bạn cài đặt với các thông số mặc định, phần cấu hình trong mã nguồn có thể hoạt động ngay. Tuy nhiên, nếu bạn thay đổi instance name hoặc mode xác thực, bạn cần điều chỉnh chuỗi kết nối.

Mở file `main.py` và tìm phương thức `__init__` của class `Database`:

```python
def __init__(self):
    try:
        self.conn = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=localhost;'  # Điều chỉnh thành localhost\SQLEXPRESS nếu cần
                'DATABASE=puzzle8;'
                'Trusted_Connection=yes;'  # Windows Authentication
            )
        self.cursor = self.conn.cursor()
        self.create_tables_if_not_exist()
        print("Kết nối cơ sở dữ liệu thành công!")
    except Exception as e:
        print(f"Lỗi kết nối cơ sở dữ liệu: {e}")
        self.conn = None
        self.cursor = None
```

### Điều chỉnh chuỗi kết nối:

#### 1. Sử dụng Windows Authentication (Trusted Connection):

```python
self.conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost\SQLEXPRESS;'  # Thay thế bằng tên instance của bạn
    'DATABASE=puzzle8;'
    'Trusted_Connection=yes;'
)
```

#### 2. Sử dụng SQL Server Authentication:

```python
self.conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost\SQLEXPRESS;'  # Thay thế bằng tên instance của bạn
    'DATABASE=puzzle8;'
    'UID=sa;'  # Tài khoản SQL Server
    'PWD=YourPassword;'  # Thay thế bằng mật khẩu của bạn
)
```

## Kiểm tra kết nối

Để kiểm tra liệu kết nối cơ sở dữ liệu đã được thiết lập đúng:

1. Chạy trò chơi
2. Nếu thấy thông báo "Kết nối cơ sở dữ liệu thành công!" trong console, kết nối đã được thiết lập thành công
3. Thử sử dụng tính năng lưu/tải map để kiểm tra chức năng cơ sở dữ liệu

## Xử lý sự cố

### Lỗi kết nối cơ sở dữ liệu

1. **Lỗi "Server not found"**:
   - Kiểm tra xem SQL Server đã được chạy chưa (kiểm tra trong Services)
   - Xác minh tên instance là chính xác (localhost hoặc localhost\SQLEXPRESS)

2. **Lỗi xác thực**:
   - Kiểm tra tên đăng nhập và mật khẩu khi sử dụng SQL Authentication
   - Đảm bảo tài khoản Windows của bạn có quyền truy cập SQL Server khi sử dụng Windows Authentication

3. **Lỗi "Database 'puzzle8' not found"**:
   - Đảm bảo bạn đã tạo cơ sở dữ liệu puzzle8
   - Thử tạo lại cơ sở dữ liệu bằng script ở trên

4. **Lỗi "ODBC Driver not found"**:
   - Cài đặt lại ODBC Driver 17 cho SQL Server
   - Kiểm tra tên driver trong chuỗi kết nối (phải khớp với tên driver đã cài đặt)

### Lỗi quyền truy cập

Nếu gặp lỗi về quyền truy cập:

1. Mở SQL Server Management Studio
2. Kết nối với tài khoản 'sa'
3. Mở Security > Logins
4. Kiểm tra quyền của tài khoản bạn đang sử dụng
5. Cấp quyền cho cơ sở dữ liệu puzzle8 nếu cần

## Stored Procedures

Script cơ sở dữ liệu đã tạo một số stored procedures để giúp quản lý dữ liệu game dễ dàng hơn. Dưới đây là danh sách các procedures đã được tạo và cách sử dụng:

### GetAllMaps
Lấy danh sách tất cả các map đã lưu, sắp xếp theo thời gian tạo giảm dần.
```sql
EXEC GetAllMaps
```

### GetMapResults
Lấy tất cả kết quả của một map cụ thể, sắp xếp theo thời gian hoàn thành tăng dần.
```sql
EXEC GetMapResults @MapID = 1
```

### SaveMap
Lưu một map mới và trả về ID của map vừa tạo.
```sql
DECLARE @NewMapID INT
EXEC @NewMapID = SaveMap 
    @MapName = N'Map mới 3x3', 
    @Size = 3, 
    @BoardState = N'1,2,3,4,5,6,7,8,0', 
    @ImagePath = N'C:\Images\puzzle.jpg'
PRINT @NewMapID
```

### SaveResult
Lưu kết quả giải puzzle cho một map.
```sql
EXEC SaveResult 
    @MapID = 1, 
    @MoveCount = 42, 
    @ElapsedTime = 75
```

### DeleteMap
Xóa một map và tất cả kết quả của map đó.
```sql
EXEC DeleteMap @MapID = 1
```

### GetTop10Results
Lấy 10 kết quả tốt nhất (ít bước nhất) từ tất cả các map.
```sql
EXEC GetTop10Results
```

## Cách sử dụng Stored Procedures từ code Python

Đoạn code dưới đây giúp bạn hiểu cách sử dụng các stored procedures này từ Python với pyodbc:

```python
def get_all_maps(self):
    """Lấy danh sách tất cả các map sử dụng stored procedure"""
    if not self.conn:
        print("Không có kết nối cơ sở dữ liệu!")
        return []
    
    try:
        self.cursor.execute("EXEC GetAllMaps")
        return self.cursor.fetchall()
    except Exception as e:
        print(f"Lỗi khi tải danh sách map: {e}")
        return []

def save_map(self, map_name, size, board_state, image_path=None):
    """Lưu map mới sử dụng stored procedure"""
    if not self.conn:
        print("Không có kết nối cơ sở dữ liệu!")
        return None
    
    try:
        # Sử dụng stored procedure để lưu map
        params = (map_name, size, board_state, image_path)
        self.cursor.execute("DECLARE @MapID INT; EXEC @MapID = SaveMap ?, ?, ?, ?; SELECT @MapID", params)
        map_id = self.cursor.fetchone()[0]
        self.conn.commit()
        print(f"Đã lưu map có ID: {map_id}")
        return map_id
    except Exception as e:
        print(f"Lỗi khi lưu map: {e}")
        return None
```

## Sử dụng trò chơi không có cơ sở dữ liệu

Trò chơi được thiết kế để hoạt động ngay cả khi không có kết nối cơ sở dữ liệu. Trong trường hợp này:

- Bạn vẫn có thể chơi trò chơi bình thường
- Các tính năng lưu/tải map và xếp hạng sẽ không hoạt động
- Sẽ có thông báo "Không có kết nối cơ sở dữ liệu!" trong console

## Sao lưu và khôi phục cơ sở dữ liệu

### Sao lưu cơ sở dữ liệu

1. Mở SQL Server Management Studio
2. Nhấn chuột phải vào cơ sở dữ liệu puzzle8
3. Chọn Tasks > Back Up...
4. Đặt tên file sao lưu và vị trí lưu
5. Nhấn OK để sao lưu

### Khôi phục cơ sở dữ liệu

1. Mở SQL Server Management Studio
2. Nhấn chuột phải vào Databases
3. Chọn Restore Database...
4. Chọn Device và tìm đến file sao lưu
5. Nhấn OK để khôi phục

## Tham khảo thêm

- [Tài liệu SQL Server](https://docs.microsoft.com/en-us/sql/sql-server/)
- [Tài liệu pyodbc](https://github.com/mkleehammer/pyodbc/wiki)
- [SQL Server Express Download](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)