from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from time import sleep
import random

class Node:
    def __init__(self, board, move=None, parent=None):
        self.board = board
        self.move = move
        self.parent = parent
        self.children = []

    def add_child(self, board, move):
        child = Node(board, move, self)
        self.children.append(child)
        return child


class TicTacToe:
    def __init__(self):
        self.root = Tk()
        self.root.title('Tic Tac Toe')
        self.buttons = []
        self.is_x_turn = False
        self.is_training = False
        self.is_auto_play = False
        self.game_tree = None
        self.epoch = 100
        self.total_epoch = 0


        initial_board = [[' ' for _ in range(3)] for _ in range(3)]
        root_Node = Node(initial_board)
        self.build_game_tree(root_Node)
        self.game_tree = root_Node


        self.root.geometry("250x300")
        self.label = Label(self.root, text="Tic Tac Toe", font=('Arial', 8,"bold")).grid(row=0, column=3, columnspan=3)
        self.text = (Label(self.root, text= "", font=('Arial', 8)))
        self.text.place(x = 5, y = 210)
        self.train_button = Button(self.root, text="Train", command=self.train, height=3, width=7).grid(row=2, column=3)
        self.auto_play_button = Button(self.root, text="Auto Play", command=self.auto_play, height=3, width=7).grid(row=1, column=3)
        self.clear_button = Button(self.root, text="Clear", command=self.clear_board, height=3, width=6).place(x = 5, y = 240)
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="determinate", maximum=self.epoch)
        self.progress.place(x = 5, y = 180)
        self.epoch_input = Scale(self.root, from_=50, to=10000, orient=HORIZONTAL, length=180,label="Epoch",resolution=50)
        self.epoch_input.place(x = 60, y = 230)
        self.epoch_input.set(100)
        for i in range(3):
            row = []
            for j in range(3):
                button = Button(self.root, text=" ", command=lambda row=i, col=j: self.click(row, col), height=3, width=6)
                button.grid(row=i, column=j)
                row.append(button)
            self.buttons.append(row)


    def auto_play(self):
        self.is_auto_play = True
        moves = self.play_game(self.game_tree)
        icon = "O"
        for move in moves:
            self.buttons[move.move[0]][move.move[1]]['text'] = icon
            icon = "X" if icon == "O" else "O"
            self.root.update()
            sleep(1)
        self.is_auto_play = False
        who_is_last_move = "O" if len(moves) % 2 else "X"
        result = f"{who_is_last_move} is Win" if self.check_winner(moves[-1].board) else "Draw"
        messagebox.showinfo("Game Over", result)
        self.clear_board()
    def print_moves(self,moves):
        for move in moves:
            for i in range(3):
                print(move.board[i])
            print(f"___________{move.move}______________")
    def train(self):
        self.is_training = True
        self.is_training = True
        self.progress['value'] = 0  # Reset progress bar value
        self.epoch = self.epoch_input.get()
        self.progress['maximum'] = self.epoch
        for i in range(self.epoch):
            moves = self.play_game(self.game_tree)
            last_move = moves[-1]
            o_moves = [moves[i] for i in range(len(moves)) if i % 2 == 0]
            x_moves = [moves[i] for i in range(len(moves)) if i % 2 != 0]
            if self.check_winner(last_move.board) == "X":
                # 0x0x0x
                for j in range(len(o_moves)-1, -1, -1):
                    parent = self.search_board(self.game_tree, o_moves[j].board)
                    reward_node = self.search_board(parent, x_moves[j].board)
                    self.reward(parent, reward_node)
                    if j != 0:
                        parent = self.search_board(self.game_tree, x_moves[j - 1].board)
                        remove_node = self.search_board(parent, o_moves[j].board)
                        self.punish(parent, remove_node)
                remove_node = self.search_board(self.game_tree, o_moves[0].board)
                self.punish(self.game_tree, remove_node)
            if self.check_winner(last_move.board) == "O":
                # 0x0x0
                for j in range(len(x_moves)-1, -1, -1):
                    parent = self.search_board(self.game_tree, x_moves[j].board)
                    reward_node = self.search_board(parent, o_moves[j + 1].board)
                    self.reward(parent, reward_node)
                    parent = self.search_board(self.game_tree, o_moves[j].board)
                    remove_node = self.search_board(parent, x_moves[j].board)
                    self.punish(parent, remove_node)
                reward_node = self.search_board(self.game_tree, o_moves[0].board)
                self.reward(self.game_tree, reward_node)
            self.progress['value'] = i + 1  # Update progress bar value
            self.root.update_idletasks()  # Update the GUI to reflect the change
            self.is_training = False
            self.progress['value'] = 0  # Optionally reset the progress bar after training
        self.is_training = False
        self.total_epoch += self.epoch
        self.text.config(text=f"Training is done :: total_training_epoch = {self.total_epoch}")
        self.root.update()

    def reward(self, parent,reward_node):
        parent.children.extend([reward_node, reward_node])
    def punish(self, parent ,punish_node):
        if parent.children.count(punish_node) > 1:
            parent.children.remove(punish_node)



    def play_game(self, node):
        play_track = []
        if not node.children:
            return play_track
        choosen_move = random.choice(node.children)
        play_track.append(choosen_move)
        if self.check_winner(choosen_move.board) or self.is_draw(choosen_move.board):
            return play_track
        play_track.extend(self.play_game(choosen_move))
        return play_track



    def build_game_tree(self,node, player='O'):
        # Check if the game is over

        if self.check_winner(node.board) or self.is_draw(node.board):
            return

        # Try all possible moves
        for i in range(3):
            for j in range(3):
                if node.board[i][j] == ' ':
                    # Copy the current board and make a new move
                    new_board = [row[:] for row in node.board]
                    new_board[i][j] = player


                    # Add the new game state to the tree
                    child = node.add_child(new_board, (i, j))

                    # Recurse for the other player
                    self.build_game_tree(child, 'X' if player == 'O' else 'O')

    # The function to check the winner and the draw can be implemented as follows:
    def search_board(self, node, board):
        if node.board == board:
            return node

        for child in node.children:
            found = self.search_board(child, board)
            if found:
                return found
        return None
    def check_winner(self,board):
        # Check rows, columns and diagonals for a winner
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != ' ':
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != ' ':
                return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] != ' ':
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != ' ':
            return board[0][2]
        return None

    def is_draw(self,board):
        return all(board[i][j] != ' ' for i in range(3) for j in range(3))


    def auto_click(self, row, col):
        if self.buttons[row][col]['text'] == " ":
            self.buttons[row][col]['text'] = 'X'
            self.is_x_turn = False
            self.check_for_winner()
    def click(self, row, col):
        if self.buttons[row][col]['text'] == " " and not self.is_x_turn and not self.is_training and not self.is_auto_play:
            self.buttons[row][col]['text'] = 'O'
            self.is_x_turn = True
            self.check_for_winner()
        if  self.is_x_turn and not self.is_auto_play and not self.is_training:
            current_board = self.search_board(self.game_tree, [[button['text'] for button in row] for row in self.buttons])
            for i in range(3):
                print(current_board.board[i])
            temp = list(set(current_board.children))
            for child in temp:
                print(f"{child.move} -> {current_board.children.count(child)}")
            choiced_move = random.choice(current_board.children).move
            self.auto_click(choiced_move[0], choiced_move[1])


    def check_for_winner(self):
        is_game_over = False
        for row in self.buttons:
            if row[0]['text'] == row[1]['text'] == row[2]['text'] != " ":
                self.end_game(row[0]['text'])
                is_game_over = True
        for col in range(3):
            if self.buttons[0][col]['text'] == self.buttons[1][col]['text'] == self.buttons[2][col]['text'] != " ":
                self.end_game(self.buttons[0][col]['text'])
                is_game_over = True
        if self.buttons[0][0]['text'] == self.buttons[1][1]['text'] == self.buttons[2][2]['text'] != " ":
            self.end_game(self.buttons[0][0]['text'])
            is_game_over = True
        if self.buttons[0][2]['text'] == self.buttons[1][1]['text'] == self.buttons[2][0]['text'] != " ":
            self.end_game(self.buttons[0][2]['text'])
            is_game_over = True
        if not is_game_over and all(button['text'] != " " for row in self.buttons for button in row):
            self.end_game("It's a draw!")
            is_game_over = True
        return is_game_over
    def clear_board(self):
        for row in self.buttons:
            for button in row:
                button['text'] = " "
        print("#######################################\n#######################################")
    def end_game(self, winner):
        message = f"Game Over {winner} wins!" if winner != "It's a draw!" else "It's a draw!"
        messagebox.showinfo("Game Over", message)
        self.clear_board()
        self.is_x_turn = False


    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = TicTacToe()
    game.run()

