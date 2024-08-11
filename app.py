from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

class BingoGame:
    def __init__(self):
        self.selected = np.zeros((5, 5), dtype=np.int32)
        self.selections = 0
        self.remaining_turns = 8
        self.game_over = False

    def calculate_weight_for_position(self, i, j):
        temp_selected = self.selected.copy()
        temp_selected[i, j] = 1

        score_multiplier = (32 - self.selections) / 16

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
        if self.game_over:
            return np.zeros((5, 5))
        weights = np.zeros((5, 5))
        for i in range(5):
            for j in range(5):
                if self.selected[i, j] == 0:
                    weights[i, j] = self.calculate_weight_for_position(i, j)
        return weights

    def update_weights(self):
        weights = self.calculate_weights()
        max_weight = np.max(weights)
        highlighted = []
        for i in range(5):
            for j in range(5):
                if self.selected[i, j] == 0:
                    if self.selections % 2 == 0 and not self.game_over:
                        if weights[i, j] == max_weight:
                            highlighted.append((i, j))
        return highlighted

    def select_square(self, i, j):
        if self.game_over:
            return None
        if self.selected[i, j] == 0:
            self.selected[i, j] = 1
            self.selections += 1
            if self.selections % 2 == 1:  # Player's turn
                self.remaining_turns -= 1
            if self.selections >= 16:
                self.game_over = True
                return self.calculate_score()
        return None

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

game = BingoGame()

@app.route('/')
def index():
    return render_template('index.html', game=game)

@app.route('/select/<int:i>/<int:j>', methods=['POST'])
def select(i, j):
    if game.game_over:
        return jsonify({"status": "game_over", "score": None})
    score = game.select_square(i, j)
    return jsonify({"status": "game_over" if game.game_over else "continue", "score": score})

@app.route('/restart', methods=['POST'])
def restart():
    global game
    game = BingoGame()
    return jsonify({"status": "restarted"})

if __name__ == '__main__':
    app.run(debug=True)
