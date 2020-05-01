#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Interface graphique pour le jeu de bataille navale.
"""

__author__ = 'FIL - IEEA - Univ. Lille1'
__date_creation__ = 'Tue Feb  3 14:20:23 2015'

from tkinter import *
from tkinter.ttk import *
import re
import bataille_navale as BN

class Plateau (Frame):
    """
    """
    def __init__ (self, boss, jeu):
        Frame.__init__(self)
        self.jeu = jeu
        self.nlig = jeu['plateau']['haut']
        self.ncol = jeu['plateau']['larg']
        self.can = Canvas (self, bg = "blue", borderwidth = 0,
                           highlightthickness = 1, highlightbackground = "white")
        self.bind ("<Configure>", self.redim)
        self.can.bind ("<Button-1>", self.clic)
        self.can.pack ()
        self.gagne = False
        self.boss = boss
        self.nbre_tirs = 0
        
    def redim (self, event):
        """
        """
        self.width, self.height = event.width - 4, event.height - 4
        self.tracerGrille ()

    def tracerGrille (self):
        """
        """
        lmax = self.width / self.ncol
        hmax = self.height / self.nlig
        self.cote = min (lmax, hmax)
        larg, haut = self.cote * self.ncol, self.cote * self.nlig
        self.can.configure (width = larg, height = haut)
        self.can.delete (ALL)
        s = self.cote
        for l in range (self.nlig - 1):
            self.can.create_line (0, s, larg, s, fill = "white")
            s += self.cote
        s = self.cote
        for c in range (self.ncol - 1):
            self.can.create_line (s, 0, s, haut, fill = "white")
            s += self.cote
        for coup in self.jeu['coups_joues']:
            i,j = coup
            # les coordonnées d'un coup sont dans un intervalle [1,LARG] et [1,HAUT]
            i -= 1
            j -= 1
            x1 = i * self.cote + 5
            x2 = (i+1) * self.cote - 5
            y1 = j * self.cote + 5
            y2 = (j+1) * self.cote - 5
            if coup in self.jeu['plateau']:
                nav = self.jeu['plateau'][coup]
                if self.jeu['touches']['etats_navires'][nav] == 0:
                    self.can.create_oval (x1,y1,x2,y2,outline="grey",width=1,fill="black")
                else:
                    self.can.create_oval (x1,y1,x2,y2,outline="grey",width=1,fill="red")
            else:
                self.can.create_oval (x1,y1,x2,y2,outline="grey",width=1,fill="blue")
        if self.gagne:
            self.boss.conclure (self.nbre_tirs)
            
    def clic (self, event):
        """
        """
        self.nbre_tirs += 1
        lig, col = 1 + event.y // self.cote, 1 + event.x // self.cote
        BN.analyse_un_tir (self.jeu, (col,lig))
        self.gagne =  BN.tous_coules (self.jeu)
        self.tracerGrille()

class Jeu(Frame):
    """
    """
    def __init__(self, nom, version):
        Frame.__init__(self)
        self.master.geometry ("400x400")
        self.master.title (nom + " joue à la bataille navale")
        jeu = BN.cree_jeu(version)
        self.plateau = Plateau (self, jeu)
        self.plateau.pack (expand = YES, fill=BOTH, padx=8, pady=8)
        self.pack ()
        self.nom = nom
        self.version = version
        
    def conclure (self,nbre_tirs=1000):
        BN.sauver_result (self.nom, self.version, nbre_tirs)
        self.conclusion = Toplevel (self)
        self.conclusion.title ('Score')
        Label (self.conclusion, text = 'Bravo {0} !\nTu as gagné en {1} tirs'.format(self.nom,nbre_tirs)).grid ()
        Button (self.conclusion, text = 'OK', command = self.quit).grid ()
        
        
    def quit(self):
        self.conclusion.destroy()
        self.master.destroy()
  
        
class Nom(Frame):
    """
    """
    def __init__(self):
        Frame.__init__(self)
        self.master.geometry("350x200")
        self.master.title("Informations")
        self.label_nom = Label(self.master, text="Nom : ")
        self.label_nom.place(x=60, y=50)
        var_nom = StringVar()
        entree_nom = Entry(self.master, textvariable=var_nom)
        entree_nom.place(x=160, y=50)
        self.label_version = Label(self.master, text="Version : ")
        self.label_version.place(x=60, y=100)
        liste_versions = Combobox(self.master, values=["Choisir une version : ", "1", "2", "3"])
        liste_versions.place(x=160, y=100)
        liste_versions.current(0)
        button_valider = Button(self.master, text="Valider", command=self.valider)
        button_valider.place(x=170, y=150)
        self.nom = var_nom
        self.versions = liste_versions
        self.pack()
        
    def valider(self):
        nbr = re.compile(r"[0-9]")
        nom = re.compile(r"^$")
        if nbr.search(self.versions.get()) and not nom.search(self.nom.get()):
            jeu = Jeu(self.nom.get(), self.versions.get())
            self.destroy()
        else:
            if nom.search(self.nom.get()):
                self.label_nom["text"] = "Donner un nom svp : "
                self.label_nom["foreground"] = "red"
                self.label_nom.place(x=10, y=50)
            if not nbr.search(self.versions.get()):
                self.label_version["text"] = "Choisissez une version svp : "
                self.label_version["foreground"] = "red"
                self.label_version.place(x=10, y=100)
            
        
if __name__ == '__main__':
    nom = Nom().mainloop()
    
# eof
