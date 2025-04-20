# Cung cấp truy cập dễ dàng đến các class
from .puzzle import Puzzle
from .database import Database
from .algorithms import BestFirstSearch, HillClimbing, Node

# Cho phép import trực tiếp từ models
__all__ = ['Puzzle', 'Database', 'BestFirstSearch', 'HillClimbing', 'Node']