import random

class Force3:

    def __init__(self):
        # Initialisation de l'état du jeu
        self.reset()
        self.move_history = []  # Liste pour stocker l'historique des mouvements
        self.is_second_move_of_double = False
        self.dones = []

    def reset(self):
        # La carte est représentée par une grille 3x3
        # 0 représente un carré vide  
        # 1 et -1 représentent les jetons de tour des deux joueurs
        # 2 représente un jeton carré
        self.board = [
            [2, 2, 2],
            [2, 0, 2],
            [2, 2, 2]
        ]
        # Le joueur 1 ou 2 commence le jeu
        self.current_player = 1
        # Garder une trace du nombre de jetons ronds placés par chaque joueur
        self.round_tokens_placed = {1: 0, -1: 0}
        # Etat du jeu - si le jeu est terminé ou non
        self.game_over = False
        # Gagnant du jeu, None si aucun gagnant n'est encore gagnant
        self.winner = None
        # Mémoriser le dernier mouvement
        self.last_move = None
        # Liste pour stocker l'historique des mouvements
        self.move_history = []

        # Renvoie l'état initial de la carte
        return self.board
    
    def render(self):
        # Définition des symboles pour chaque type de pion
        symbols = {0: '.', 1: 'X', -1: 'O', 2: '#'}

        # Afficher chaque ligne du plateau
        for row in self.board:
            print(' '.join(symbols[piece] for piece in row))
            
        print()
    
    def step(self, action):
        if self.game_over:
            return self.board, self.game_over, self.winner, False, "Game is over. Please reset."

        action_type, row, col, target_row, target_col, move_two_decision = action

        # Vérifier si l'action est valide
        if not self.is_valid_move(action_type, row, col, target_row, target_col):
            return self.board, self.game_over, self.winner, False, "Invalid move."

        if action_type == 'place_round':
            self.board[target_row][target_col] = self.current_player
            self.round_tokens_placed[self.current_player] += 1
            self.is_second_move_of_double = False  # Réinitialiser pour le prochain tour
        elif action_type == 'move_square':
            self._move_square(row, col, target_row, target_col, move_two_decision)
            if move_two_decision and not self.is_second_move_of_double and (target_row in [0, 2] or target_col in [0, 2]):
                self.is_second_move_of_double = True  # Marquer que le prochain mouvement est le second du double mouvement
            else:
                self.is_second_move_of_double = False  # Réinitialiser pour le prochain tour
        elif action_type == 'move_round':
            self._move_round(row, col, target_row, target_col)
            self.is_second_move_of_double = False  # Réinitialiser pour le prochain tour

        # Rechercher un gagnant
        self.game_over, self.winner = self.check_winner()

        self.dones.append(self.game_over)

        # Changer le joueur actuel
        if not self.game_over and not self.is_second_move_of_double:
            self.current_player = -self.current_player

        return self.board, self.game_over, self.winner, True, None  # Aucune erreur

    def _move_square(self, row, col, target_row, target_col, move_two):
        
        if self.board[row][col] in [-1, 1, 2] and self.board[target_row][target_col] == 0:
            if move_two and self.is_second_move_of_double:
                if self.board[row][col] == 2:
                    # Déplacer un seul carré
                    self.board[row][col], self.board[target_row][target_col] = 0, 2
                elif self.board[row][col] == 1:
                    # Déplacer un seul carré
                    self.board[row][col], self.board[target_row][target_col] = 0, 1
                else:
                    # Déplacer un seul carré
                    self.board[row][col], self.board[target_row][target_col] = 0, -1
                # Mémoriser ce mouvement pour empêcher le mouvement inverse
                self.last_move = ((row, col), (target_row, target_col), self.current_player)
                self.move_history.append(self.last_move)
            else:
                if self.board[row][col] == 2:
                    # Déplacer un seul carré
                    self.board[row][col], self.board[target_row][target_col] = 0, 2
                elif self.board[row][col] == 1:
                    # Déplacer un seul carré
                    self.board[row][col], self.board[target_row][target_col] = 0, 1
                else:
                    # Déplacer un seul carré
                    self.board[row][col], self.board[target_row][target_col] = 0, -1 

    def _move_round(self, row, col, target_row, target_col):
        # Déplacer un jeton rond de (row, col) vers (target_row, target_col)
        if self.board[row][col] == self.current_player and self.board[target_row][target_col] == 2 and ((row == target_row and col - target_col in [1, -1]) or (col == target_col and row - target_row in [1, -1]) or (row == target_row - 1 and col == target_col - 1) or (row == target_row + 1 and col == target_col + 1) or (row == target_row + 1 and col == target_col - 1) or (row == target_row - 1 and col == target_col + 1)):
            self.board[row][col], self.board[target_row][target_col] = 2, self.current_player

    def is_valid_move(self, action_type, row, col, target_row, target_col):
        if self.is_second_move_of_double and action_type in ['place_round', 'move_round'] and not self.dones[-1]:
            return False
        # Vérification pour empêcher le mouvement inverse
        if len(self.move_history) > 0:
            case_depart, case_arrivee, player = self.move_history[-1]
            if (row == case_arrivee[0] and col == case_arrivee[1] and target_row == case_depart[0] and target_col == case_depart[1]) and self.current_player != player:
                return False

        if action_type == 'place_round':
            # Vérifier si la cellule cible est carrée et si le joueur actuel n'a pas placé tous ses jetons tour
            return self.board[target_row][target_col] == 2 and self.round_tokens_placed[self.current_player] < 3
        elif action_type == 'move_square':
            # Vérifier si les indices sont dans les limites du tableau
            if not (0 <= row < 3 and 0 <= col < 3 and 0 <= target_row < 3 and 0 <= target_col < 3):
                return False
            else:
                if self.is_second_move_of_double:
                    return (self.board[row][col] == 2 or self.board[row][col] == self.current_player or self.board[row][col] == -self.current_player) and self.board[target_row][target_col] == 0 and ((row == target_row and col - target_col in [1, -1]) or (col == target_col and row - target_row in [1, -1])) and self.round_tokens_placed[self.current_player] == 3 and self.round_tokens_placed[-self.current_player] == 3
                # Vérifier si la cellule source a un jeton carré ou rond et que la cellule cible est vide
                return (self.board[row][col] == 2 or self.board[row][col] == self.current_player) and self.board[target_row][target_col] == 0 and ((row == target_row and col - target_col in [1, -1]) or (col == target_col and row - target_row in [1, -1])) and self.round_tokens_placed[self.current_player] == 3 and self.round_tokens_placed[-self.current_player] == 3
        elif action_type == 'move_round':
            # Vérifier si les indices sont dans les limites du tableau
            if not (0 <= row < 3 and 0 <= col < 3 and 0 <= target_row < 3 and 0 <= target_col < 3):
                return False
            else:
                # Vérifier si la cellule source contient le jeton de tour du joueur actuel et si la cellule cible est carrée
                return self.board[row][col] == self.current_player and self.board[target_row][target_col] == 2 and ((row == target_row and col - target_col in [1, -1]) or (col == target_col and row - target_row in [1, -1]) or (row == target_row - 1 and col == target_col - 1) or (row == target_row + 1 and col == target_col + 1) or (row == target_row + 1 and col == target_col - 1) or (row == target_row - 1 and col == target_col + 1)) and self.round_tokens_placed[self.current_player] == 3 and self.round_tokens_placed[-self.current_player] == 3
        else:
            # Type d'action invalide
            return False
        
    def check_winner(self):
        # Vérifier les lignes horizontales, verticales et diagonales pour gagner
        for row in range(3):
            if (self.board[row][0] == self.board[row][1] == self.board[row][2] != 0) and (self.board[row][0] == self.board[row][1] == self.board[row][2] != 2):
                return True, self.board[row][0]
        for col in range(3):
            if (self.board[0][col] == self.board[1][col] == self.board[2][col] != 0) and (self.board[0][col] == self.board[1][col] == self.board[2][col] != 2):
                return True, self.board[0][col]
        if (self.board[0][0] == self.board[1][1] == self.board[2][2] != 0) and (self.board[0][0] == self.board[1][1] == self.board[2][2] != 2):
            return True, self.board[0][0]
        if (self.board[0][2] == self.board[1][1] == self.board[2][0] != 0) and (self.board[0][2] == self.board[1][1] == self.board[2][0] != 2):
            return True, self.board[0][2]

        # Aucun gagnant encore
        return False, None