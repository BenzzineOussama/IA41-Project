import time
import pygame
import sys
from force3 import Force3
from bot import Force3AI
# Initialisation de Pygame et des polices
pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 36)

LARGEUR, HAUTEUR = 400, 500   # La hauteur totale de la fenêtre
HAUTEUR_PLATEAU = 400  # La hauteur utilisée pour le plateau de jeu
TAILLE_CASE = LARGEUR // 3
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Force 3")
def choix_mode_jeu():
    dialog_rect= pygame.Rect(LARGEUR // 8 , HAUTEUR // 4, 3* LARGEUR // 4, HAUTEUR // 2)
    pygame.draw.rect(ecran,(200,200,200),dialog_rect)
    question_text = font.render("Choisir le mode", True, (0, 0, 0))
    text_x = dialog_rect.x + (dialog_rect.width - question_text.get_width()) // 2  # Centrer le texte
    text_y = dialog_rect.y + 20
    ecran.blit(question_text, (text_x, text_y))
    bouton_largeur = dialog_rect.width // 2 +20 
    human_rect = pygame.Rect(dialog_rect.x + 65, dialog_rect.y + 80, bouton_largeur, 50)
    ia_rect = pygame.Rect(dialog_rect.x + 65, dialog_rect.y + 150, bouton_largeur, 50)
    pygame.draw.rect(ecran, (0, 255, 0), human_rect)
    pygame.draw.rect(ecran, (0, 0, 255), ia_rect)
    human_text = font.render("Joueur vs IA", True, (255, 255, 255))
    ia_text = font.render("IA vs IA", True, (255, 255, 255))
    ecran.blit(human_text, (human_rect.x + 7, human_rect.y + 12))
    ecran.blit(ia_text, (ia_rect.x + 40, ia_rect.y + 12))

    pygame.display.update()
    while True:
        for event in pygame.event.get():
            mode = None
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if human_rect.collidepoint(event.pos):
                    mode= "Joueur"
                elif ia_rect.collidepoint(event.pos):
                    mode= "IA"
                
                return mode
def choix_couleur():
    dialog_rect= pygame.Rect(LARGEUR // 8 , HAUTEUR // 4, 3* LARGEUR // 4, HAUTEUR // 2)
    pygame.draw.rect(ecran,(200,200,200),dialog_rect)
    question_text = font.render("Choisir votre couleur", True, (0, 0, 0))
    text_x = dialog_rect.x + (dialog_rect.width - question_text.get_width()) // 2  # Centrer le texte
    text_y = dialog_rect.y + 20
    ecran.blit(question_text, (text_x, text_y))
    bouton_largeur = dialog_rect.width // 2 - 40
    red_rect = pygame.Rect(dialog_rect.x + 20, dialog_rect.y + 80, bouton_largeur, 50)
    blue_rect = pygame.Rect(dialog_rect.x + dialog_rect.width // 2 + 20, dialog_rect.y + 80, bouton_largeur, 50)
    pygame.draw.rect(ecran, (255, 0, 0), red_rect)
    pygame.draw.rect(ecran, (0, 0, 255), blue_rect)
    red_text = font.render("Rouge", True, (255, 255, 255))
    blue_text = font.render("Blue", True, (255, 255, 255))
    ecran.blit(red_text, (red_rect.x + 20, red_rect.y + 10))
    ecran.blit(blue_text, (blue_rect.x + 25, blue_rect.y + 10))

    pygame.display.update()
    while True:
        for event in pygame.event.get():
            couleur = None
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if red_rect.collidepoint(event.pos):
                    couleur= (255,0,0)
                elif blue_rect.collidepoint(event.pos):
                    couleur= (0,0,255)
                
                return couleur


# Création d'une instance du jeu
jeu = Force3()
mode=choix_mode_jeu()
couleur = None
if mode == "Joueur":
    couleur = choix_couleur()
else:
    couleur=(255,0,0)

def dessiner_plateau():
    ecran.fill((255, 255, 255))  # Blanc
    # Dessiner seulement jusqu'à HAUTEUR_PLATEAU
    for x in range(1, 3):
        pygame.draw.line(ecran, (0, 0, 0), (x * TAILLE_CASE, 0), (x * TAILLE_CASE, HAUTEUR_PLATEAU))
        pygame.draw.line(ecran, (0, 0, 0), (0, x * TAILLE_CASE), (LARGEUR, x * TAILLE_CASE))

def dessiner_jetons():
    symbols = None
    if couleur == (255,0,0):
        symbols = {0: (255, 255, 255), 1: (255, 0, 0), -1: (0, 0, 255), 2: (0, 255, 0)}  # Couleurs pour chaque type de jeton
    else:
        symbols = {0: (255, 255, 255), -1: (255, 0, 0), 1: (0, 0, 255), 2: (0, 255, 0)}

    for row in range(3):
        for col in range(3):
            center = (col * TAILLE_CASE + TAILLE_CASE // 2, row * TAILLE_CASE + TAILLE_CASE // 2)
            color = symbols[jeu.board[row][col]]
            if jeu.board[row][col] in [1, -1]:  # Jetons ronds pour les joueurs
                pygame.draw.circle(ecran, color, center, TAILLE_CASE // 3)
            elif jeu.board[row][col] == 2:  # Jeton carré
                pygame.draw.rect(ecran, color, (center[0] - TAILLE_CASE // 4, center[1] - TAILLE_CASE // 4, TAILLE_CASE // 2, TAILLE_CASE // 2))

def get_grid_position(x, y):
    row = y // TAILLE_CASE
    col = x // TAILLE_CASE
    return row, col

def dessiner_texte_joueur_actuel():
    if couleur == (255,0,0):
        text = f"Joueur Actuel: {'Rouge' if jeu.current_player == 1 else 'Bleu'}"
        text_surface = font.render(text, True, (0, 0, 0))
        # Positionner le texte en dessous du plateau de jeu
        ecran.blit(text_surface, (10, HAUTEUR_PLATEAU + 10))
    else:
        text = f"Joueur Actuel: {'Bleu' if jeu.current_player == 1 else 'Rouge'}"
        text_surface = font.render(text, True, (0, 0, 0))
        # Positionner le texte en dessous du plateau de jeu
        ecran.blit(text_surface, (10, HAUTEUR_PLATEAU + 10))

def dessiner_texte_gagnant():
    if jeu.game_over and jeu.winner is not None:
        if couleur == (255,0,0):
            text = f"Gagnant: {'Rouge' if jeu.winner == 1 else 'Bleu'}"
            text_surface = font.render(text, True, (0, 0, 0))
            # Positionner le texte en dessous du texte du joueur actuel
            ecran.blit(text_surface, (10, HAUTEUR_PLATEAU + 40))
        else:
            text = f"Gagnant: {'Bleu' if jeu.winner == 1 else 'Rouge'}"
            text_surface = font.render(text, True, (0, 0, 0))
            # Positionner le texte en dessous du texte du joueur actuel
            ecran.blit(text_surface, (10, HAUTEUR_PLATEAU + 40))

def demander_deplacement_deux_carres():
    # Agrandir la largeur du rectangle pour la boîte de dialogue
    dialogue_rect = pygame.Rect(LARGEUR // 8, HAUTEUR // 4, 3 * LARGEUR // 4, HAUTEUR // 4)
    pygame.draw.rect(ecran, (200, 200, 200), dialogue_rect)
    

    # Ajuster le texte et les positions des boutons
    question_text = font.render("Déplacer deux carrés ?", True, (0, 0, 0))
    text_x = dialogue_rect.x + (dialogue_rect.width - question_text.get_width()) // 2  # Centrer le texte
    text_y = dialogue_rect.y + 20
    ecran.blit(question_text, (text_x, text_y))

    bouton_largeur = dialogue_rect.width // 2 - 40
    oui_rect = pygame.Rect(dialogue_rect.x + 20, dialogue_rect.y + 80, bouton_largeur, 50)
    non_rect = pygame.Rect(dialogue_rect.x + dialogue_rect.width // 2 + 20, dialogue_rect.y + 80, bouton_largeur, 50)
    pygame.draw.rect(ecran, (0, 255, 0), oui_rect)
    pygame.draw.rect(ecran, (255, 0, 0), non_rect)

    oui_text = font.render("Oui", True, (255, 255, 255))
    non_text = font.render("Non", True, (255, 255, 255))
    ecran.blit(oui_text, (oui_rect.x + 10, oui_rect.y + 10))
    ecran.blit(non_text, (non_rect.x + 10, non_rect.y + 10))

    pygame.display.update()
    
    # Attendre une réponse de l'utilisateur
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if oui_rect.collidepoint(event.pos):
                    return True
                elif non_rect.collidepoint(event.pos):
                    return False

# Variables pour suivre la sélection et l'action
selectionnee = None
action_type = None
move_two = False
bot = Force3AI(jeu)
# Boucle principale du jeu
while True:
    if mode == "IA":
            if jeu.current_player==-1:
                score,move= bot.minimax(jeu.board,1,-1)
                bot.last_move=move
                jeu.step(move)
                
                time.sleep(1)
            else:
                score,move= bot.minimax(jeu.board,1,1)
                bot.last_move=move
                jeu.step(move)
                
                time.sleep(1)
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        else:

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                row, col = get_grid_position(mouse_x, mouse_y)

                if jeu.game_over:
                    jeu.reset()
                    selectionnee = None
                    action_type = None
                    continue
                
                current_content = jeu.board[row][col]

                if jeu.round_tokens_placed[jeu.current_player] < 3 and current_content == 2:
                    move_two = False
                    # Phase de placement des pions
                    action = ('place_round', None, None, row, col, move_two)
                elif selectionnee is None:
                    # Premier clic : sélectionner l'élément
                    selectionnee = (row, col)
                    if current_content == 2:
                        action_type = 'move_square'
                    elif current_content == jeu.current_player:
                        action_type = ('move_round', 'move_square')
                    continue

                # Deuxième clic : effectuer l'action
                target_row, target_col = row, col
                if action_type == ('move_round', 'move_square'):
                    if jeu.board[target_row][target_col] == 0:
                        # Si la case cible est vide et sur le bord, demander s'il veut déplacer deux carrés
                        if target_row in [0, 2] or target_col in [0, 2]:
                            action = ('move_square', selectionnee[0], selectionnee[1], target_row, target_col, move_two)
                            valid_move = jeu.is_valid_move(action[0], action[1], action[2], action[3], action[4])
                            if valid_move:
                                move_two = demander_deplacement_deux_carres()
                                action = ('move_square', selectionnee[0], selectionnee[1], target_row, target_col, move_two)
                            else:
                                move_two = False
                        else:
                            move_two = False
                            action = (action_type[1], selectionnee[0], selectionnee[1], target_row, target_col, move_two)
                    else:
                        move_two = False
                        # Déplacer un pion
                        action = (action_type[0], selectionnee[0], selectionnee[1], target_row, target_col, move_two)
                elif action_type == 'move_square':
                    if jeu.board[target_row][target_col] == 0:
                        # Si la case cible est vide et sur le bord, demander s'il veut déplacer deux carrés
                        if target_row in [0, 2] or target_col in [0, 2]:
                            action = ('move_square', selectionnee[0], selectionnee[1], target_row, target_col, move_two)
                            valid_move = jeu.is_valid_move(action[0], action[1], action[2], action[3], action[4])
                            if valid_move:
                                move_two = demander_deplacement_deux_carres()
                                action = ('move_square', selectionnee[0], selectionnee[1], target_row, target_col, move_two)
                            else:
                                move_two = False

                        else:
                            move_two = False
                            action = ('move_square', selectionnee[0], selectionnee[1], target_row, target_col, move_two)

                if move_two:
                    _, game_over, winner, valid_move, error_message = jeu.step(action)
                    if not jeu.game_over:
                        dessiner_plateau()
                        dessiner_jetons()
                        dessiner_texte_joueur_actuel()
                        dessiner_texte_gagnant()
                        pygame.display.update()
                        # Attendez que l'utilisateur sélectionne le deuxième carré à déplacer
                        print("Sélectionnez le deuxième carré à déplacer")  # Ou afficher à l'écran
                        second_selectionnee = False
                        while not second_selectionnee:
                            for inner_event in pygame.event.get():
                                if inner_event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                elif inner_event.type == pygame.MOUSEBUTTONDOWN:
                                    second_mouse_x, second_mouse_y = inner_event.pos
                                    second_row, second_col = get_grid_position(second_mouse_x, second_mouse_y)
                                    if jeu.board[second_row][second_col] in [2, 1, -1]:
                                        # L'utilisateur a sélectionné le deuxième carré à déplacer
                                        # Attendez maintenant la sélection de la nouvelle case cible pour ce deuxième carré
                                        second_target_selected = False
                                        while not second_target_selected:
                                            for second_inner_event in pygame.event.get():
                                                if second_inner_event.type == pygame.QUIT:
                                                    pygame.quit()
                                                    sys.exit()
                                                elif second_inner_event.type == pygame.MOUSEBUTTONDOWN:
                                                    second_target_x, second_target_y = second_inner_event.pos
                                                    second_target_row, second_target_col = get_grid_position(second_target_x, second_target_y)
                                                    if jeu.board[second_target_row][second_target_col] == 0:
                                                        # Exécuter le déplacement du deuxième carré
                                                        action2 = ('move_square', second_row, second_col, second_target_row, second_target_col, move_two)
                                                        _, game_over, winner, valid_move, error_message = jeu.step(action2)
                                                        if not valid_move:
                                                            print(error_message) # Afficher l'erreur
                                                            second_target_selected = True
                                                        else:
                                                            second_target_selected = True
                                                            second_selectionnee = True
                                                            

                else:
                    # Exécuter l'action après vérification de la validité
                    _, game_over, winner, valid_move, error_message = jeu.step(action)
                    if not valid_move:
                        print(error_message)  # Afficher l'erreur

                selectionnee = None
                action_type = None
                move_two = False

                if game_over:
                    print(f"Le gagnant est : {winner}")  # Afficher le gagnant
                if jeu.current_player == -1:
                        
                        time.sleep(1)
                        score,move= bot.minimax(jeu.board,1,-1)
                        print(score,move)
                        jeu.step(move)
                        pygame.display.update()
    dessiner_plateau()
    dessiner_jetons()
    dessiner_texte_joueur_actuel()
    dessiner_texte_gagnant()

    pygame.display.update()
