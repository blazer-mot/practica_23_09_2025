from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np

def is_valid(board, row, col, num):

    if num in board[row]:
        return False

    if num in board[:, col]:
        return False

    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    if num in board[start_row:start_row+3, start_col:start_col+3]:
        return False
    return True

def solve(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve(board):
                            return True
                        board[row][col] = 0
                return False
    return True

driver = webdriver.Chrome()
driver.get("https://absite.ru/sudoku/")

cells = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.sudoku td"))
)

grid = np.zeros((9, 9), dtype=int)

for i, cell in enumerate(cells):
    row = i // 9
    col = i % 9
    value = cell.text.strip()
    if value.isdigit():
        grid[row][col] = int(value)

print("Исходная матрица:")
print(grid)

if solve(grid):
    print("\nРешение:")
    print(grid)
else:
    print("Решения нет")
