from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import time

def is_valid(board, row, col, num):
    if num in board[row]:
        return False
    if num in board[:, col]:
        return False
    sr, sc = 3 * (row // 3), 3 * (col // 3)
    if num in board[sr:sr+3, sc:sc+3]:
        return False
    return True

def solve(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                for num in range(1, 10):
                    if is_valid(board, r, c, num):
                        board[r][c] = num
                        if solve(board):
                            return True
                        board[r][c] = 0
                return False
    return True

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
driver.get("https://absite.ru/sudoku/")

cells = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.sudoku td"))
)

grid = np.zeros((9, 9), dtype=int)
original = np.zeros((9, 9), dtype=int)

for i, cell in enumerate(cells):
    r, c = i // 9, i % 9
    val = cell.text.strip()
    if val.isdigit():
        grid[r][c] = int(val)
        original[r][c] = int(val)

print("Исходная матрица:")
print(grid)

solve(grid)
print("\nРешение:")
print(grid)

cells[0].click()  
time.sleep(0.5)

for r in range(9):
    for c in range(9):
        if original[r][c] == 0: 
            driver.switch_to.active_element.send_keys(str(grid[r][c]))

        if c < 8:
            driver.switch_to.active_element.send_keys(Keys.ARROW_RIGHT)

    if r < 8:
        driver.switch_to.active_element.send_keys(Keys.ARROW_DOWN)
        for _ in range(8):
            driver.switch_to.active_element.send_keys(Keys.ARROW_LEFT)
