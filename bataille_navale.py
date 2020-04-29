#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
TP AP1
Licence SESI 1ère année
Univ. Lille 1

bataille_navale.py

Module pour le jeu de bataille navale.

Pour une description générale du jeu voir
http://fr.wikipedia.org/wiki/Bataille_navale_%28jeu%29

"""

__author__ = 'Bina BADIANE'
__date_creation__ = '20/04/2020'


###############################################
# Modules utilisés
###############################################

# Pour la disposition aléatoire des navires
import random as r

# Pour le fichier des scores
from datetime import datetime 

import re

###############################################
# Constantes nommées utilisées
###############################################

# les deux dispositions possibles pour un navire
#  sur le plateau :
# - H : horizontale
# - V : verticale
DISPOSITIONS="HV"


# codes réponses d'analyse de tirs
RATE = 0
TOUCHE = 1
COULE = 2

# nom du fichier contenant les scores réalisés
FICHIER_RESULT = 'bataille_navale_scores.txt'

###############################################
# Procédure principale du jeu
###############################################

def jouer (nom,descr):
    """
    str, str -> ()
    procédure de jeu complet de bataille navale,
    le nom du joueur est donné par le paramètre nom, 
    et le jeu est décrit dans le fichier descr.

    CU : le fichier jeu doit exister et être conforme
    à un fichier de description.
    """
    jeu = cree_jeu(descr)
    decrire_le_jeu(jeu)
    nbre_tirs = 0
    while not tous_coules(jeu):
        tir = lire_un_tir (nom)
        nbre_tirs += 1
        nav,res = analyse_un_tir (jeu,tir)
        if res == RATE:
            print ("raté.")
        elif res == TOUCHE:
            print (nav + " touché.")
        else:
            print (nav + " coulé.")
    sauver_result (nom,descr,nbre_tirs)
    print ("Terminé en {0} tirs".format(nbre_tirs))

###############################################
# Opérations sur les fichiers
###############################################

def lire_donnees(num_descr):
    """
    str -> tuple
    renvoie un triplet dont les deux premières composantes sont 
    et la troisième une liste de couples (nature, taille) où
    nature est une chaîne de caractères décrivant la nature du navire
    et taille un entier désignant le nombre de cases occupées par ce navire.
    Toutes ces données sont lues dans un fichier nommé 'jeu'+num_descr+'.txt'.

    CU : le fichier 'jeu'+num_descr+'.txt' doit exister et être au bon format, 
    ie un  fichier texte contenant :
    larg : haut
    nature1 : taille1
    nature2 : taille2
    ...
    """
    nom_fichier = "jeu" + num_descr + ".txt"
    format_fichier = re.compile(r"""[0-9]+ : [0-9]+\n([-a-zA-Z]+ : [0-9]+\n)+[-a-zA-Z]+ : [0-9]+""")
    largeur = re.compile(r"[0-9]+")
    hauteur = re.compile(r": [0-9]+")
    nom_nav = re.compile(r"[-a-zA-Z]+")
    taille_nav = re.compile(r"[0-9]+")
    with open(nom_fichier, "r") as fichier:
        contenu = fichier.read()
        if(format_fichier.search(contenu)):
            lignes = contenu.split("\n")
            navires = []
            for ligne in lignes[1:]:
                nav_match = nom_nav.search(ligne)
                taille_match = taille_nav.search(ligne)
                navires.append((nav_match.group(), int(taille_match.group())))
            largeur_match = largeur.search(lignes[0])
            hauteur_match = hauteur.search(lignes[0])
            resultat = (int(largeur_match.group()), int(hauteur_match.group()[2:]), navires)
            return resultat
        else:
            raise TypeError("Le fichier n'est pas au bon format\n")


def sauver_result (nom, jeu, nbre):
    """
    str, str, int -> NoneType
    ajoute une ligne dans le fichier FICHIER_RESULT
    contenant le nom, le numéro du jeu joué et le nombre de tirs effectués 
    dans la partie.

    CU : aucune
    """
    nouvelle_ligne = nom + ':' + jeu + ':' + str(nbre) + ':' + str(datetime.today()) + '\n'
    with open(FICHIER_RESULT, "a") as fichier:
        fichier.write(nouvelle_ligne)


###############################################
# Procédures de construction du jeu
###############################################
    
def cree_jeu (descr):
    """
    str -> dict
    renvoie un nouveau jeu de bataille navale construit à partir des données 
    lues dans le fichier descr.


    Le jeu est représenté par un dictionnaire à quatre clés :
    - 'plateau' pour représenter le plateau de jeu (l'espace maritime) avec ses navires
    - 'nb_cases_occupees' dont la valeur associée est le nombre de cases du plateau
                          occupées par les navires
    - 'touches' dictionnaire contenant deux champs :
                * l'un nomme 'nb_touches' contenant un entier 
                * l'autre nomme 'etats_navires' qui contient un dictionnaire
                  donnant pour chaque navire le nombre de tirs 
                  qu'ils peuvent encore recevoir avant d'être coulés
    - 'coups_joues' ensemble des coups joués depuis le début de la partie.

    CU : le fichier doit contenir une description correcte du jeu (cf lire_donnees)
    """
    donnees = lire_donnees(descr)
    return cree_plateau(donnees[0], donnees[1], donnees[2])

def cree_plateau (l, h, l_nav):
    """
    int, int, list -> dict
    renvoie un plateau de largeur l et de hauteur h occupé par les navires 
    de l_nav.
    La disposition est aléatoire.

    CU : les dimensions doivent permettre le placement de tous les navires
    """
    esp = dict()
    esp["plateau"] = {"larg" : l, "haut" : h}
    esp["nb_cases_occupees"] = 0
    esp["touches"] = {"nb_touches" : 0, "etats_navires" : {}}
    esp["coups_joues"] = set()
    for nav in l_nav:
        placer(esp, nav)
    return esp
    
def est_placable (esp, nav, pos, disp):
    """
    dict, tuple, tuple, str -> bool
    
    CU : disp = 'H' ou 'V'
    """
    if disp == 'V':
        if pos[1] + nav[1] - 1 > esp["plateau"]["haut"]:
            placable = False
        else:
            case_pas_occupee = True
            i = pos[1]
            while i <= pos[1] + nav[1] - 1 and case_pas_occupee:
                if (pos[0], i) in list(esp['plateau'].keys())[2:]:
                    case_pas_occupee = False
                i += 1
            placable = case_pas_occupee
    else:
        if pos[0] + nav[1] - 1 > esp['plateau']['larg']:
            placable = False
        else:
            case_pas_occupee = True
            i = pos[0]
            while i <= pos[0] + nav[1] - 1 and case_pas_occupee:
                if (i, pos[1]) in list(esp['plateau'].keys())[2:]:
                    case_pas_occupee = False
                i += 1
            placable = case_pas_occupee
    return placable

def placer (esp, nav):
    """
    dict, tuple -> NoneType
    place le navire nav dans l'espace maritime esp.
    Choix de l'emplacement aléatoire.

    CU : il doit rester de la place
    """
    largeur = esp["plateau"]["larg"]
    hauteur = esp["plateau"]["haut"]
    disp = r.choice(DISPOSITIONS)        
    pos = (r.randint(1, largeur), r.randint(1, hauteur))
    while not est_placable(esp, nav, pos, disp):
        disp = r.choice(DISPOSITIONS)        
        pos = (r.randint(1, largeur), r.randint(1, hauteur))
    if disp == "H":
        for i in range(pos[0], pos[0] + nav[1]):
            esp["plateau"][(i, pos[1])] = nav[0]
    if disp == "V":
        for i in range(pos[1], pos[1] + nav[1]):
            esp["plateau"][(pos[0], i)] = nav[0]
    esp["nb_cases_occupees"] += nav[1]
    esp["touches"]["etats_navires"][nav[0]] = nav[1]

###############################################
# Procédures de déroulement du jeu
###############################################
    
def decrire_le_jeu (jeu):
    """
    dict -> ()
    imprime une description du jeu.
    
    CU : aucune
    """
    print("Dimensions du plateau du jeu : ")
    print("- largeur :", jeu["plateau"]["larg"])
    print("- hauteur :", jeu["plateau"]["haut"])
    print("Navires : ")
    for cle, valeur in jeu["touches"]["etats_navires"].items():
        print("-", cle, ":", valeur, "case(s)")
    print("À vous de jouer en répondant à l'invite ?- par deux nombres séparés par une virgule.")

def lire_un_tir (nom):
    """
    str -> tuple
    renvoie un couple d'entiers lus sur l'entrée standard

    CU : l'entrée doit être de la forme xxx,yyy avec xxx et yyy
         une représentation décimale de deux nombres entiers
    """
    nbrs = re.compile(r"^[0-9]+,[0-9]+$")
    entree_std = input()
    if not nbrs.search(entree_std):
        raise ValueError("L'entrée doit être de la forme xxx,yyy avec xxx et yyy des entiers")
    else:
        entrees = entree_std.split(",")
        return (int(entrees[0]), int(entrees[1]))

def analyse_un_tir (jeu,tir):
    """
    dict, tuple -> str,int
    renvoie 
      - ("",RATE) si tir raté
      - (nav,TOUCHE) si nav touché
      - (nav,COULE) si nav coulé
    et modifie l'état du jeu en conséquence.

    CU : aucune 
    """
    jeu["coups_joues"].add(tir)
    pas_touche = True
    i = 2
    while i < len(jeu["plateau"]) and pas_touche:
        if tir == list(jeu["plateau"].keys())[i]:
            pas_touche = False
        i += 1
    if pas_touche:
        return ("", RATE)
    else:
        jeu["touches"]["nb_touches"] += 1
        nav = list(jeu["plateau"].values())[i-1]
        jeu["touches"]["etats_navires"][nav] -= 1
        if jeu["touches"]["etats_navires"][nav] == 0:
            return (nav, COULE)
        else:
            return (nav, TOUCHE)

def tous_coules (jeu):
    """
    dict -> bool
    renvoie True si tous les navires du plateau de jeu ont été coulés
            et False dans le cas contraire.

    CU : aucune
    """
    coules = True
    i = 0
    while i < len(jeu["touches"]["etats_navires"]) and coules:
        if list(jeu["touches"]["etats_navires"].values())[i] != 0:
            coules = False
        i += 1
    return coules
    
###############################################
# Pour une utilisation du module depuis un terminal
###############################################    

if __name__ == '__main__':
    import sys

    if len (sys.argv) != 3:
        jouer ('Jean Bart','1')
    else:
        jouer (sys.argv[1],sys.argv[2])


# import sys
# import math

# # Auto-generated code below aims at helping you parse
# # the standard input according to the problem statement.

# l = int(input())
# h = int(input())
# a = [[0 for _ in range(l)] for x in range(h)]
# for i in range(l):
#     for j, v in enumerate(input().split()):
#         a[j][i] = int(v)
        
# for l in a:
#     print(*l[::-1])

# import sys
# import math

# # Auto-generated code below aims at helping you parse
# # the standard input according to the problem statement.

# n = int(input())
# l={}
# for i in range(n):
#     emoji, code = input().split()
#     l[''.join(sorted(set(emoji)))]=code
# s = input().split()
# for i in l:
#     for w in range(len(s)):
#         if i==''.join(sorted(set(s[w]))):s[w]=l[i]

# print(' '.join(s))

