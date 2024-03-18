 # -*- coding: utf-8 -*-

# Nicolas, 2024-02-09
from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys
from itertools import chain


import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme

# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    name = _boardname if _boardname is not None else 'grid-chifoumi-map'
    game = Game('./Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    player = game.player
    
def main():
    nbMatches = 10

    #for arg in sys.argv:
    iterations = 100 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
    
    nbLignes = game.spriteBuilder.rowsize
    nbCols = game.spriteBuilder.colsize
    assert nbLignes == nbCols # a priori on souhaite un plateau carre
    lMin=2  # les limites du plateau de jeu (2 premieres lignes utilisees pour stocker les objets)
    lMax=nbLignes-2 
    cMin=2
    cMax=nbCols-2

    
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)

    playerPoints = [0,0]
    
   
    
    # on definit les types d'items sur la carte
    items_types = {0:"flamme",1:"potion",2:"pumpkin"}

    def zone(k,pos,placed):
        (x,y) = pos
        if placed:
            if k==0: 
                return (x>2 and x<9 and y>2 and y<10) # zone des flammes
            elif k==1:
                return (x>12 and x<19 and y>2 and y<10) # zone des potions
            elif k==2:
                return (x>12 and x<19 and y>12 and y<19) # zone des citrouilles
        else: 
            if k==0: 
                return (x==0 or x==1) # zone des flammes
            elif k==1:
                return (y==0 or y==1) # zone des potions
            elif k==2:
                return (x==lMax or x==lMax+1) # zone des citrouilles
                
    
    nb_types = len(items_types)
    
    # on localise tous les objets a allouer au hasard
    # sur le layer ramassable
    # ceux deja places, et ceux a placer
    
    items_to_place = [[],[],[]]
    items_to_place[0] = [o for o in game.layers['ramassable'] if zone(0,o.get_rowcol(),False)]
    items_to_place[1] = [o for o in game.layers['ramassable'] if zone(1,o.get_rowcol(),False)]
    items_to_place[2] = [o for o in game.layers['ramassable'] if zone(2,o.get_rowcol(),False)]

    items_placed = [[],[],[]]
    items_placed[0] = [o for o in game.layers['ramassable'] if zone(0,o.get_rowcol(),True)]
    items_placed[1] = [o for o in game.layers['ramassable'] if zone(1,o.get_rowcol(),True)]   
    items_placed[2] = [o for o in game.layers['ramassable'] if zone(2,o.get_rowcol(),True)] 
    nbItems = len(items_to_place[0]+items_to_place[1]+items_to_place[2]),len(items_placed[0]+items_placed[1]+items_placed[2])
    picked_items = [[0,0,0],[0,0,0]] # compteur des items de chaque type pour chaque joueur
    
    #-------------------------------
    # Fonctions permettant de récupérer les listes des coordonnées
    # d'un ensemble d'objets ou de joueurs
    #-------------------------------
    
    def itemStates(items): 
        # donne la liste des coordonnees des items
        return [o.get_rowcol() for o in items]
    
    def playerStates(players):
        # donne la liste des coordonnees dez joueurs
        return [p.get_rowcol() for p in players]
    
   
    #-------------------------------
    # Rapport de ce qui est trouve sut la carte
    #-------------------------------
    print("lecture carte")
    print("-------------------------------------------")
    print('joueurs', nbPlayers)
    print("lignes", nbLignes)
    print("colonnes", nbCols)
    print("objets",nbItems)
    print("-------------------------------------------")

    #-------------------------------
    # Carte demo 
    # 2 joueurs 
    # Joueur 0: random walk
    # Joueur 1: A*
    #-------------------------------
    
        
    #-------------------------------

    #-------------------------------
    # Fonctions definissant les positions legales et placement de mur aléatoire
    #-------------------------------
    
    def legal_move_position(pos):
        row,col = pos
        # une position legale de deplacement est dans la carte 
        return (row>lMin and row<lMax-1 and col>=cMin and col<cMax)
    
    
    def legal_position(pos):
        row,col = pos
        all_items_placed = items_placed[0] + items_placed[1] + items_placed[2]
        # une position legale est dans la carte et pas sur un objet deja pose ni sur un joueur
        return ((pos not in itemStates(all_items_placed)) and (pos not in playerStates(players)) and row>lMin and row<lMax-1 and col>=cMin and col<cMax)
    
    def draw_random_location():
        # tire au hasard un couple de position permettant de placer un item
        while True:
            random_loc = (random.randint(lMin,lMax),random.randint(cMin,cMax))
            if legal_position(random_loc):
                return(random_loc)

    #-------------------------------
    # On place tous les items du bord au hasard
    #-------------------------------
                    
    for k in range(nb_types):                 
        for i in range(0,len(items_to_place[k])): 
            o = items_to_place[k][i]
            (x1,y1) = draw_random_location()
            o.set_rowcol(x1,y1)
            items_placed[k].append(o)
            game.mainiteration()
        
    print("Objets places:", len(items_placed[0]),len(items_placed[1]),len(items_placed[2]))

    #-------------------------------
    # On place tous les joueurs au hasard
    #-------------------------------
     
    for i in range(0,len(players)): 
        (x1,y1) = draw_random_location()
        players[i].set_rowcol(x1,y1)
        game.mainiteration()
    
    
        #-------------------------------
    # Fonctions chifumi 
    #-------------------------------
    def chifumi():
        nonlocal nbMatches
        nonlocal iterations
        nbObjectPlayer1 = sum(picked_items[0])

        nbObjectPlayer2 = sum(picked_items[1])
        if(nbObjectPlayer1 == 0):
            player1 = random.choice(["potion","flamme","pumpkin"])
        else:
            probaFlamme = picked_items[0][0]/nbObjectPlayer1
            probaPotion = picked_items[0][1]/nbObjectPlayer1
            probaPumpkin = picked_items[0][2]/nbObjectPlayer1
            player1 = random.choices(["potion","flamme","pumpkin"],[probaPotion,probaFlamme,probaPumpkin])[0]
            
        if(nbObjectPlayer2 == 0):
            player2 = random.choice(["potion","flamme","pumpkin"])
        else:
            probaFlamme = picked_items[1][0]/nbObjectPlayer2
            probaPotion = picked_items[1][1]/nbObjectPlayer2
            probaPumpkin = picked_items[1][2]/nbObjectPlayer2
            player2 = random.choices(["potion","flamme","pumpkin"],[probaPotion,probaFlamme,probaPumpkin])[0]
        print("Chifoumi!, Joueur 1 a choisi:",player1,"Joueur 2 a choisi:",player2)
        if(player1 == player2):
            print("Egalité")
            gagnant = -1
        if player1 == "potion":
            if player2 == "flamme":
                playerPoints[0]+=1
                gagnant = 0
            else:
                playerPoints[1]+=1
                gagnant = 1
        if player1 == "flamme":
            if player2 == "pumpkin":
                playerPoints[0]+=1
                gagnant = 0
            else:
                playerPoints[1]+=1
                gagnant = 1
        if player1 == "pumpkin":
            if player2 == "potion":
                playerPoints[0]+=1
                gagnant = 0
            else:
                playerPoints[1]+=1
                gagnant = 1
        #le joueur perdant réinitialise son sac 
        if(gagnant == 0):
           #On replace aléatoirement les items de l'inventaire du joueur perdant sur la map
            for i in range(0,len(picked_items[1])):
                for j in range(0,picked_items[1][i]):
                    o = players[1].depose(game.layers,lambda x:True)
                    (x1,y1) = draw_random_location()
                    o.set_rowcol(x1,y1)
                    items_placed[i].append(o)
            picked_items[1] = [0,0,0]
        else:
            if (gagnant == 1):
                for i in range(0,len(picked_items[0])):
                    for j in range(0,picked_items[0][i]):
                        o = players[0].depose(game.layers,lambda x:True)
                        (x1,y1) = draw_random_location()
                        o.set_rowcol(x1,y1)
                        items_placed[i].append(o)
                picked_items[0] = [0,0,0]
        #replacer le joueur 1 et 2
        for i in range(0,len(players)):
            (x1,y1) = draw_random_location()
            players[i].set_rowcol(x1,y1)
        #reduire le nombre de match
        nbMatches-=1
        iterations = 100






    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
            
    posPlayers = playerStates(players)
    row,col = posPlayers[0]
    row1,col1 = posPlayers[1]
    path = []
    
    while(True):
        iterations-=1
        if(iterations == 0):
            print("Fin d'un match")
            nbMatches-=1
            if(nbMatches == 0):
                break
            else:
                print("Nouveau match en cours")
                iterations = 100
                #on replace les joueurs
                print("replacement des joueurs")
                for i in range(0,len(players)):
                    (x1,y1) = draw_random_location()
                    players[i].set_rowcol(x1,y1)
                    


        
        #-------------------------------
        # on fait bouger le joueur 0 au hasard
        #-------------------------------

        
        while True: # tant que pas legal on retire une position
            x_inc,y_inc = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
            next_row = row+x_inc
            next_col = col+y_inc
            if legal_move_position((next_row,next_col)):
                break
        players[0].set_rowcol(next_row,next_col)
        print ("pos 0:", next_row,next_col)
    
        col=next_col
        row=next_row
        posPlayers[0]=(row,col)
        
        if(posPlayers[0] == posPlayers[1]):
            chifumi()

        for k in range(nb_types):
            if posPlayers[0] in itemStates(items_placed[k]):
                print("Trouvé ",items_types[k])
                picked_items[0][k]+=1
                o=players[0].ramasse(game.layers) # on recupere l'objet 
                items_placed[k].remove(o)         # on l'enleve de la liste des objets de ce type
                break
       
        # mise à jour du pleateau de jeu
        #game.mainiteration()

    
    #-------------------------------
    # calcul A* pour le joueur 1
    # le joueur va rejoindre le joueur 0 en évitant tous les items
    #-------------------------------
                
        potion_et_citrouille = items_placed[1] + items_placed[2]
        tmpFlamme = []
        champsDeVision = 3
        g =np.zeros((nbLignes,nbCols),dtype=bool)    # une matrice remplie par defaut a True  

        for i in range(posPlayers[1][0]-champsDeVision,posPlayers[1][0]+champsDeVision):
            for j in range(posPlayers[1][1]-champsDeVision,posPlayers[1][1]+champsDeVision):
                g[max(min(i,nbLignes-1),0)][max(min(j,nbCols-1),0)]=True

        #met a false les case de g qui sont des items_placed[1] ou des items_placed[2]
        for i in range(len(potion_et_citrouille)):
            g[potion_et_citrouille[i].get_rowcol()[0]][potion_et_citrouille[i].get_rowcol()[1]]=False

        #parcour items_placed[0]et verifie que la case g est true pour chaque item
        for i in range(len(items_placed[0])):
            if g[items_placed[0][i].get_rowcol()[0]][items_placed[0][i].get_rowcol()[1]]==True:
                tmpFlamme.append(items_placed[0][i].get_rowcol())


        if(tmpFlamme!=[]):
            p = ProblemeGrid2D(posPlayers[1],tmpFlamme[0] ,g,'manhattan')
            if path == []:
                path = probleme.astar(p, verbose=False)
                print("Chemin trouvé:", path)
                
            if len(path)>0:
                print(path)
                next_row,next_col=path[0]
                players[1].set_rowcol(next_row,next_col)
                posPlayers[1]=(next_row,next_col)
                print ("pos joueur 1:", next_row,next_col)
                if posPlayers[1] == posPlayers[0]:
                   chifumi()
                   
                elif posPlayers[1] in itemStates(items_placed[0]):
                    print(posPlayers[1])
                    picked_items[1][0]+=1
                    o=players[1].ramasse(game.layers)
                    items_placed[0].remove(o)
                elif posPlayers[1] in itemStates(items_placed[1]):
                    print(posPlayers[1])
                    picked_items[1][1]+=1
                    o=players[1].ramasse(game.layers)
                    items_placed[1].remove(o)
                elif posPlayers[1] in itemStates(items_placed[2]):
                    print(posPlayers[1])
                    picked_items[1][2]+=1
                    o=players[1].ramasse(game.layers)
                    items_placed[2].remove(o)
                path=path[1:]
        else:
            row1,col1 = posPlayers[1]
            #se deplace aléatoirement si il n'y a plus de flamme
            while True: 
                x_inc,y_inc = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
                next_row = row1+x_inc
                next_col = col1+y_inc
                if legal_move_position((next_row,next_col)):
                    break
            players[1].set_rowcol(next_row,next_col)
            print ("pos 1:", next_row,next_col)
            if(next_row,next_col) == posPlayers[0]:
                chifumi()
            elif(next_row,next_col) in itemStates(items_placed[0]):
                print("Trouvé flamme")
                picked_items[1][0]+=1
                o=players[1].ramasse(game.layers)
                items_placed[0].remove(o)
            elif(next_row,next_col) in itemStates(items_placed[1]):
                print("Trouvé potion")
                picked_items[1][1]+=1
                o=players[1].ramasse(game.layers)
                items_placed[1].remove(o)
            elif(next_row,next_col) in itemStates(items_placed[2]):
                print("Trouvé citrouille")
                picked_items[1][2]+=1
                o=players[1].ramasse(game.layers)
                items_placed[2].remove(o)
            col1=next_col
            row1=next_row
            posPlayers[1]=(row1,col1)

        game.mainiteration()


            



    print("Point joueur 1:",playerPoints[0], "Point joueur 2:",playerPoints[1])
    if(playerPoints[0]>playerPoints[1]):
        print("Joueur 1 a gagné")
    if(playerPoints[0]<playerPoints[1]):
        print("Joueur 2 a gagné")
    if(playerPoints[0]==playerPoints[1]):
        print("Egalité")





    pygame.quit()
    
    
    
    
    #-------------------------------
    
        
    
    
   

if __name__ == '__main__':
    main()