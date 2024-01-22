import gym
from gym import spaces
import numpy as np
from force3 import Force3

class Force3Env(gym.Env):
    metadata = {'render.modes': ['console']}

    def __init__(self):
        super(Force3Env, self).__init__()
        # Initialisation de la liste des actions valides
        self.valid_actions = []

        # Définition des actions valides
        # Actions pour le type 0 (Placer)
        for target_pos in range(4):
            self.valid_actions.append((0, None, target_pos, None))
        
        for target_pos in range(5, 9):
            self.valid_actions.append((0, None, target_pos, None))

        # Actions pour le type 1 (Déplacer un pion rond)
        for start_pos in range(9):
            for target_pos in range(9):
                self.valid_actions.append((1, start_pos, target_pos, None))

        # Actions pour le type 2 (Déplacer un carré)
        for start_pos in range(9):
            for target_pos in range(9):
                for move_two in range(2):
                    self.valid_actions.append((2, start_pos, target_pos, move_two))

        # L'espace d'observation (l'état du plateau)
        self.observation_space = spaces.Box(low=-1, high=2, shape=(9, ), dtype=np.int32)

        self.force3 = Force3()  # Instance de la classe de jeu

        self.current_player = self.force3.current_player # Initialiser l'agent

    def reset(self):
        # Réinitialiser le jeu
        initial_state = self.force3.reset()

        # Changer l'agent
        self.current_player = -self.current_player

        return np.array(initial_state).reshape(-1)

    def convert_to_action_tuple(self, action):
        action_type_num, start_pos, target_pos, move_two_decision = action

        action_mapping = {0: 'place_round', 1: 'move_round', 2: 'move_square'}
        action_type = action_mapping[action_type_num]

        if action_type == 'place_round':
            target_row, target_col = divmod(target_pos, 3)
            return action_type, None, None, target_row, target_col, None
        else:
            start_row, start_col = divmod(start_pos, 3)
            target_row, target_col = divmod(target_pos, 3)
            if action_type == 'move_round':
                return action_type, start_row, start_col, target_row, target_col, None
            else:
                return action_type, start_row, start_col, target_row, target_col, move_two_decision

    def step(self, action):
        action_type, start_row, start_col, target_row, target_col, move_two_decision = self.convert_to_action_tuple(action)
        board, game_over, winner, success, _ = self.force3.step((action_type, start_row, start_col, target_row, target_col, move_two_decision))

        reward = self.calculate_reward(board, game_over, winner, success, target_row, target_col)
        done = game_over
        info = {'winner': winner}
        return np.array(board).reshape(-1), reward, done, info


    def calculate_reward(self, board, game_over, winner, success, target_row, target_col):
        # Récompenses et pénalités de base
        WIN_REWARD = 100
        LOSE_PENALTY = -100
        INVALID_MOVE = -20
        NEUTRAL_REWARD = 0
        BLOCK_REWARD = 20
        OPPORTUNITY_FOR_GAIN = 20
        MOVE_TWO_PENALTY = -20  # pénalité pour déplacer deux carrés de manière non judicieuse

        # Récompense pour gagner
        if game_over:
            if winner == self.current_player:
                return WIN_REWARD
            else:
                return LOSE_PENALTY
        
        if self.force3.is_second_move_of_double and self.force3.current_player == self.current_player:
            # Évaluer si le mouvement de deux carrés est stratégiquement judicieux
            if self.is_opportunity(board, target_row, target_col) and self.is_blocking_move(board, target_row, target_col):
                return OPPORTUNITY_FOR_GAIN + BLOCK_REWARD
            if self.is_opportunity(board, target_row, target_col):
                return OPPORTUNITY_FOR_GAIN
            if self.is_blocking_move(board, target_row, target_col):
                return BLOCK_REWARD
            else:
                return MOVE_TWO_PENALTY
        elif self.force3.current_player == self.current_player:
            if self.is_opportunity(board, target_row, target_col) and self.is_blocking_move(board, target_row, target_col):
                return OPPORTUNITY_FOR_GAIN + BLOCK_REWARD
            if self.is_opportunity(board, target_row, target_col):
                return OPPORTUNITY_FOR_GAIN
            if self.is_blocking_move(board, target_row, target_col):
                return BLOCK_REWARD
            
        if not success:
            return INVALID_MOVE
            
        return NEUTRAL_REWARD

    def is_blocking_move(self, board, row, col):
        opponent = -self.current_player

        # Vérifications pour les coins
        if (row == 0 and col == 0) and ((board[1][0] == opponent and board[2][0] == opponent) or 
                                    (board[0][1] == opponent and board[0][2] == opponent) or 
                                    (board[1][1] == opponent and board[2][2] == opponent)):
            return True
        elif (row == 0 and col == 2) and ((board[0][0] == opponent and board[0][1] == opponent) or 
                                        (board[1][2] == opponent and board[2][2] == opponent) or 
                                        (board[1][1] == opponent and board[2][0] == opponent)):
            return True
        elif (row == 2 and col == 0) and ((board[0][0] == opponent and board[1][0] == opponent) or 
                                        (board[2][1] == opponent and board[2][2] == opponent) or 
                                        (board[1][1] == opponent and board[0][2] == opponent)):
            return True
        elif (row == 2 and col == 2) and ((board[0][2] == opponent and board[1][2] == opponent) or 
                                        (board[2][0] == opponent and board[2][1] == opponent) or 
                                        (board[1][1] == opponent and board[0][0] == opponent)):
            return True

        # Vérifications pour les cases centrales des côtés
        elif (row == 0 and col == 1) and ((board[0][0] == opponent and board[0][2] == opponent) or 
                                        (board[1][1] == opponent and board[2][1] == opponent)):
            return True
        elif (row == 1 and col == 0) and ((board[0][0] == opponent and board[2][0] == opponent) or 
                                        (board[1][1] == opponent and board[1][2] == opponent)):
            return True
        elif (row == 1 and col == 2) and ((board[0][2] == opponent and board[2][2] == opponent) or 
                                        (board[1][0] == opponent and board[1][1] == opponent)):
            return True
        elif (row == 2 and col == 1) and ((board[2][0] == opponent and board[2][2] == opponent) or 
                                        (board[0][1] == opponent and board[1][1] == opponent)):
            return True

        # Vérification pour la case centrale
        elif (row == 1 and col == 1) and ((board[0][0] == opponent and board[2][2] == opponent) or 
                                        (board[0][2] == opponent and board[2][0] == opponent) or 
                                        (board[0][1] == opponent and board[2][1] == opponent) or 
                                        (board[1][0] == opponent and board[1][2] == opponent)):
            return True

        return False

    def is_opportunity(self, board, row, col):
        player = self.current_player
        # Si la case est la case centrale, vérifier la ligne, la colonne et les deux diagonales
        if(row == 1 and col == 1):
            if (self.check_line_for_opportunity(board, row, player) or self.check_column_for_opportunity(board, col, player) or self.check_diagonal_for_opportunity(board, True, player) or self.check_diagonal_for_opportunity(board, False, player)):
                return True
            else:
                return False
        # Si la case n'est pas centrale mais qui appartient à la diagonale principale, vérifier la ligne, la colonne et la diagonale principale
        elif ((row == col) and (self.check_line_for_opportunity(board, row, player) or self.check_column_for_opportunity(board, col, player) or self.check_diagonal_for_opportunity(board, True, player))):
            return True
         # Si la case n'est pas centrale mais qui appartient à la diagonale secondaire, vérifier la ligne, la colonne et la diagonale secondaire
        elif ((row + col == 2) and (self.check_line_for_opportunity(board, row, player) or self.check_column_for_opportunity(board, col, player) or self.check_diagonal_for_opportunity(board, False, player))):
            return True
         # Si la case n'est pas centrale et n'appartient ni à la diagonale principale ni à la diagonale secondaire, vérifier uniquement la ligne et la colonne
        elif (self.check_line_for_opportunity(board, row, player) or self.check_column_for_opportunity(board, col, player)):
            return True
        
        else:
            return False


    def check_line_for_opportunity(self, board, row, player):
        # Vérifier une opportunité dans une ligne spécifique
        return self.check_for_opportunity_in_sequence([board[row][i] for i in range(3)], player)

    def check_column_for_opportunity(self, board, col, player):
        # Vérifier une opportunité dans une colonne spécifique
        return self.check_for_opportunity_in_sequence([board[i][col] for i in range(3)], player)

    def check_diagonal_for_opportunity(self, board, is_primary_diagonal, player):
        # Vérifier une opportunité dans une diagonale spécifique
        if is_primary_diagonal:
            sequence = [board[i][i] for i in range(3)]
        else:
            sequence = [board[i][2 - i] for i in range(3)]

        return self.check_for_opportunity_in_sequence(sequence, player)

    def check_for_opportunity_in_sequence(self, sequence, player):
        # Vérifier si une séquence contient exactement deux pions du joueur et une case soit vide soit avec un carré
        player_count = sequence.count(player)
        empty_or_square_count = sequence.count(0) + sequence.count(2)

        return player_count == 2 and empty_or_square_count == 1
