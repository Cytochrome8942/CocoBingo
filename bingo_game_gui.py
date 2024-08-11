import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageTk, ImageEnhance, ImageOps

class BingoGame:
    def __init__(self, root):
        self.root = root
        self.root.title("5x5 Bingo Game")
        self.buttons = [[None for _ in range(5)] for _ in range(5)]
        self.selected = np.zeros((5, 5), dtype=np.int32)
        self.selections = 0
        self.remaining_turns = 8
        self.images = {}
        self.highlight_images = {}
        self.load_images()
        self.initialize_board()
        
        self.turn_label = tk.Label(self.root, text=f"남은 뒤집기 횟수: {self.remaining_turns}")
        self.turn_label.grid(row=0, column=0, columnspan=3, sticky="w")
        
        self.selection_label = tk.Label(self.root, text="수동 선택")
        self.selection_label.grid(row=0, column=3, columnspan=2, sticky="e")

        self.restart_button = tk.Button(self.root, text='다시하기', command=self.restart_game)
        self.restart_button.grid(row=6, columnspan=5)
        
        self.update_weights()  # Initialize weights

    def load_images(self):
        for i in range(1, 26):
            img = Image.open(f'button_{i:02d}.jpg').resize((80, 80))  # Adjust size to 80x80
            self.images[f'button_{i:02d}'] = ImageTk.PhotoImage(img)
            highlight_img = img.copy().convert("RGB")
            enhancer = ImageEnhance.Color(highlight_img)
            highlight_img = enhancer.enhance(5.0)  # Increase color saturation
            self.highlight_images[f'button_{i:02d}'] = ImageTk.PhotoImage(highlight_img)
        self.images['choosed'] = ImageTk.PhotoImage(Image.open('choosed.jpg').resize((80, 80)))

    def initialize_board(self):
        for i in range(5):
            for j in range(5):
                button = tk.Button(self.root, image=self.images[f'button_{i*5 + j + 1:02d}'],
                                   command=lambda i=i, j=j: self.select_square(i, j))
                button.grid(row=i+1, column=j)  # Shift rows down by 1 for labels
                self.buttons[i][j] = button

    def select_square(self, i, j):
        if self.selected[i, j] == 0:
            self.buttons[i][j].config(image=self.images['choosed'])
            self.selected[i, j] = 1
            self.selections += 1
            if self.selections % 2 == 1:  # Player's turn
                self.remaining_turns -= 1
                self.turn_label.config(text=f"남은 뒤집기 횟수: {self.remaining_turns}")
            if self.selections < 16:
                self.update_weights()
            else:
                self.end_game()

    def calculate_weight_for_position(self, i, j):
        temp_selected = self.selected.copy()
        temp_selected[i, j] = 1

        score_multiplier = (16 - self.selections) / 16

        score_for_5 = 100 * np.exp(score_multiplier)
        score_for_4 = 2.7 * np.exp(score_multiplier)
        score_for_3 = 0.9 * np.exp(score_multiplier)
        score_for_2 = 0.3 * score_multiplier
        score_for_1 = 0.1 * score_multiplier

        row_count = np.sum(temp_selected[i, :])
        col_count = np.sum(temp_selected[:, j])
        main_diag_count = np.sum([temp_selected[x, x] for x in range(5)]) if i == j else 0
        anti_diag_count = np.sum([temp_selected[x, 4-x] for x in range(5)]) if i + j == 4 else 0

        score = 0
        if row_count == 5:
            score += score_for_5
        if col_count == 5:
            score += score_for_5
        if main_diag_count == 5:
            score += score_for_5
        if anti_diag_count == 5:
            score += score_for_5

        if row_count == 4:
            score += score_for_4
        if col_count == 4:
            score += score_for_4
        if main_diag_count == 4:
            score += score_for_4
        if anti_diag_count == 4:
            score += score_for_4

        if row_count == 3:
            score += score_for_3
        if col_count == 3:
            score += score_for_3
        if main_diag_count == 3:
            score += score_for_3
        if anti_diag_count == 3:
            score += score_for_3

        if row_count == 2:
            score += score_for_2
        if col_count == 2:
            score += score_for_2
        if main_diag_count == 2:
            score += score_for_2
        if anti_diag_count == 2:
            score += score_for_2

        if row_count == 1:
            score += score_for_1
        if col_count == 1:
            score += score_for_1
        if main_diag_count == 1:
            score += score_for_1
        if anti_diag_count == 1:
            score += score_for_1

        return score

    def calculate_weights(self):
        weights = np.zeros((5, 5))
        for i in range(5):
            for j in range(5):
                if self.selected[i, j] == 0:
                    weights[i, j] = self.calculate_weight_for_position(i, j)
        return weights

    def update_weights(self):
        weights = self.calculate_weights()
        max_weight = np.max(weights)
        for i in range(5):
            for j in range(5):
                if self.selected[i, j] == 0:
                    if self.selections % 2 == 0:
                        self.selection_label.config(text="수동 선택")
                        if weights[i, j] == max_weight:
                            self.buttons[i][j].config(image=self.highlight_images[f'button_{i*5 + j + 1:02d}'])
                        else:
                            self.buttons[i][j].config(image=self.images[f'button_{i*5 + j + 1:02d}'])
                    else:
                        self.selection_label.config(text="자동 선택")
                        self.buttons[i][j].config(image=self.images[f'button_{i*5 + j + 1:02d}'], text='랜덤', bg='SystemButtonFace')
                else:
                    self.buttons[i][j].config(image=self.images['choosed'])

    def end_game(self):
        score = self.calculate_score()
        messagebox.showinfo("Game Over", f"모든 선택을 완료했습니다. 점수: {score}")

    def restart_game(self):
        self.selected = np.zeros((5, 5), dtype=np.int32)
        self.selections = 0
        self.remaining_turns = 8
        self.turn_label.config(text=f"남은 뒤집기 횟수: {self.remaining_turns}")
        for i in range(5):
            for j in range(5):
                self.buttons[i][j].config(image=self.images[f'button_{i*5 + j + 1:02d}'])
        self.update_weights()

    def calculate_score(self):
        score = 0
        for i in range(5):
            if np.sum(self.selected[i, :]) == 5:
                score += 1
        for j in range(5):
            if np.sum(self.selected[:, j]) == 5:
                score += 1
        if np.sum([self.selected[i, i] for i in range(5)]) == 5:
            score += 1
        if np.sum([self.selected[i, 4-i] for i in range(5)]) == 5:
            score += 1
        return score

if __name__ == "__main__":
    root = tk.Tk()
    game = BingoGame(root)
    root.mainloop()
