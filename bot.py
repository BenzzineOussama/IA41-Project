import copy
import time

import pygame
from force3 import Force3 
from math import inf
class Force3AI:
    def __init__(self,jeu):
        self.jeu= jeu
        self.last_move=0
    def get_valid_moves(self,board):
        valid_moves= []
        action_types=['place_round','move_square','move_round']
        for action_type in action_types:
            for row in range (len(board)):
                for col in range(len(board)):
                    for target_row in range(len(board)):
                        for target_col in range(len(board)):
                            if self.jeu.is_valid_move(action_type,row, col, target_row, target_col) and (action_type,row, col, target_row, target_col) not in valid_moves:
                                valid_moves.append((action_type,row, col, target_row, target_col,False))
        return valid_moves
    def minimax(self,board,depth,current_player):
        best_move = ("place_round",0,0,0,0,False)
        if depth == 0 or self.jeu.game_over:
            best_score,best_move = self.evaluate(best_move)
            return best_score,best_move
        if current_player==-1:
            best_score= - inf
            
        else:
            best_score = + inf
        for valid_move in self.get_valid_moves(board):
            if self.last_move!=0:
                if valid_move[1]!=self.last_move[3] and valid_move[2]!=self.last_move[4]:
                    copied = copy.deepcopy(board)
                    board = self.generate_board_state(board,valid_move,current_player)
                    score,_= self.minimax(board,depth-1,-current_player)
                    board[valid_move[1]][valid_move[2]],board[valid_move[3]][valid_move[4]]=copied[valid_move[1]][valid_move[2]],copied[valid_move[3]][valid_move[4]]
                    if current_player == -1:
                        if score>best_score:
                            best_score=score
                            best_move=valid_move
                    else:
                        if score<best_score:
                            best_score=score
                            best_move=valid_move
            elif self.last_move==0:
                copied = copy.deepcopy(board)
                board = self.generate_board_state(board,valid_move,current_player)
                score,_= self.minimax(board,depth-1,-current_player)
                board[valid_move[1]][valid_move[2]],board[valid_move[3]][valid_move[4]]=copied[valid_move[1]][valid_move[2]],copied[valid_move[3]][valid_move[4]]
                if current_player == -1:
                    if score>best_score:
                        best_score=score
                        best_move=valid_move
                else:
                    if score<best_score:
                        best_score=score
                        best_move=valid_move
        
        return best_score,best_move
    def evaluate(self,best_move):
        game_win, winner = self.jeu.check_winner()
        if winner == 1:
            return -100, best_move
        elif winner == -1:
            return 100, best_move
        else: 
            return 0, best_move
    def generate_board_state(self,board,action,current_player):
        action_type, row, col, target_row, target_col, move_two_decision = action
        if action_type == 'place_round':
            board[target_row][target_col] = current_player
        elif action_type == 'move_square':
            if board[row][col] in [-1, 1, 2] and board[target_row][target_col] == 0:
                if board[row][col] == 2:
                    # Déplacer un seul carré
                    board[row][col], board[target_row][target_col] = 0, 2
                elif board[row][col] == 1:
                    # Déplacer un seul carré
                    board[row][col], board[target_row][target_col] = 0, 1
                else:
                    # Déplacer un seul carré
                    board[row][col], board[target_row][target_col] = 0, -1 
        elif action_type == 'move_round':
            if board[row][col] == -1 and board[target_row][target_col] == 2 and ((row == target_row and col - target_col in [1, -1]) or (col == target_col and row - target_row in [1, -1]) or (row == target_row - 1 and col == target_col - 1) or (row == target_row + 1 and col == target_col + 1) or (row == target_row + 1 and col == target_col - 1) or (row == target_row - 1 and col == target_col + 1)):
                board[row][col], board[target_row][target_col] = 2, current_player
        return board
    