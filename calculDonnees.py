import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from drivetrain_fast import *


#=============================
#     Constantes globales 
#============================= 

mix_elec = 1 # A DEFINIR

prixMoteurElectrique = 12 # €/kW
prixMoteurThermique = 25 # €/kW et comprend l'ICE
prixBatterie = 131 # €/kWh
prixPile = 160 # €/kW
prixReservoirH2 = 880 # €/kg
prixAssurance = 700 # €/an
prixPompeElec = 0.2 #Demander groupe 3 / en €/kWh
prixPompeHydro = 10 #Demander groupe 2 / en €/kg
prixDiesel = 1.26 #€/L
prixEssence = 1.35 #€/L
emissionEssence = 2.3 #kgCO2/L
emissionDiesel = 2.7 #kgCo2/L
emissionElectricite = 0.056 # en kg/kWh pour le mix français (donnée notebook)
emissionHydrogene = mix_elec/100*5.6  # en kg de CO2/ kg de H2 ie en kg de CO2/16 kWh (en comptabilisant les 50% de rendement)


#=========================
#     Fonctions amont
#=========================

def dico_voiture(file) :
    dico = {}
    df = pd.read_csv(file, index_col = 'motorisation')
    for m in df.index :
        if df.loc[m]['poids'] == 'None' :
            continue
        dico[m] = {}
        for critere in df.columns :
            if critere == 'categorie' :
                dico[m][critere] = df.loc[m][critere]
            else :
                dico[m][critere] = float(df.loc[m][critere])
    return dico

def consoEssence(x):
    """
    Renvoie la consommation de carburant d'un ICEV-essence en L/100km en fonction de la masse du véhicule
    """
    return 2*10**(-6)*x**2+0.0005*x + 3.3549

def consoDiesel(x):
    """
    Renvoie la consommation de carburant d'un ICEV-diesel en L/100km en fonction de la masse du véhicule
    """
    return 2*10**(-6)*x**2-0.0008*x + 3.198

def consoHEV(x):
    """
    Renvoie la consommation d'essence d'un HEV en L/100km en fonction de la masse du véhicule
    """
    return  10**(-6)*x**2-0.0008*x + 3.2038

def consoPHEV(x):
    """
    Renvoie la consommation d'essence d'un PHEV en L/100km en fonction de la masse du véhicule
    """
    return 2.57 + (x-780)*0.82/1550

def consoEV() : # A DEFINIR
    """
    Renvoie la consommation d'énergie électrique en kWh/100km
    """
    pass

def consoFCEV() : # A DEFINIR 
    pass

def calculEmissionCO2(moteur, ess, modele, motorisation, consoNRJ, masseTot, gamma) :
    """
    Calcul les émissions de CO2 en kg/100km à l'utilisation d'un moteur thermique ou électrique en kgC02/100km en fonction des paramètres rentrés 
    """
    if gamma : 
        if moteur.get('Nom') == "MoteurElectrique" :
            if ess.get('Nom') == "Batterie" :
                return consoNRJ*emissionElectricite*moteur.get('Ratio')
            elif ess.get('Nom') == "PileCombustible" :
                return consoNRJ*emissionHydrogene*moteur.get('Ratio')
        elif moteur.get('Nom') == "MoteurThermique":
            if moteur.get('Carac') : #Si c'est un moteur essence
                if modele == "ICEV" :
                    return consoEssence(masseTot)*emissionEssence
                elif modele == "HEV" :
                    return consoHEV(masseTot)*emissionEssence
                elif modele == "PHEV" :
                    return consoPHEV(masseTot)*emissionEssence
            else : #C'est un moteur diesel, et on considère donc nécessairement que c'est un ICE
                return consoDiesel(masseTot)*emissionDiesel
    else : # !!!!!!!!!!!!!A FINALISER !!!!!!!!!!!!
        return DictionnaireVoiture.get(motorisation).get('consommation_WLTP')*28386829267

def coutEntretien(mod):
    """
    Renvoie le cout d'entretien de la voiture sur 10 000km en fonction du modèle
    """
    if mod == 'ICEV' :
        prix = np.random.randint(536, 918)
    elif mod == 'HEV' or mod == 'PHEV' :
        prix = np.random.randint(482, 826)
    elif mod == 'BEV' :
        prix = np.random.randint(413, 706)
    elif mod == 'BEVH2' : 
        prix = np.random.randint(450, 750)
    elif mod == 'FCEV' or mod == 'FCPHE' :
        prix = np.random.randint(413, 706)

def calculCoutMoteur(moteur):
    if moteur.get('Nom') == "MoteurElectrique":
        if moteur.get('Carac')==True :
            alpha = 1.2
        else :
            alpha = 1
        return moteur.get('Puissance')*prixMoteurElectrique*alpha
    elif moteur.get('Nom') == "MoteurThermique" :
        return moteur.get('Puissance')*prixMoteurThermique
    else :
        return 0

def calculCoutESS(ess) :
	if ess.get('Nom') == "Batterie" :
		return ess.get('Puissance')*prixBatterie
	elif ess.get('Nom') == "PileCombustible" :
		return ess.get('Puissance')*prixPile + ess.get('Reservoir')*prixReservoirH2
	return 0

def massePAC(puissance):
    '''
    renvoie masse de la PAC en fonction de la puissance(modele 10/4 yourik) avec la donnée 56kg pour 113 kW Mirai
    '''
    return 56*(puissance/113)

def masseMoteurThermique(puissance) :  
    '''
    renvoie la masse du moteur+réservoir en fonction de la puissance du moteur, puissance en entrée en kW
    '''
    reservoir = 35
    moteur = puissance/0.600  #modele linéaire 600W/kg
    return moteur + reservoir

#=======================
#     Dictionnaires 
#=======================

MalusCO2 = {109 : 0, 110 : 50, 111 : 75, 112 : 100, 113 : 125, 114 : 150, 115 : 170, 116 : 190, 117 : 210, 118 : 230, 119 : 240,
 120 : 260, 121 : 280, 122 : 310, 123 : 330, 124 : 360, 125 : 400, 126 : 450, 127 : 540, 128 : 650, 129 : 740, 130 : 818, 131 : 898,
 132 : 983, 133 : 1074, 134 : 1172, 135 : 1276, 136 : 1386, 137 : 1504, 138 : 1629, 139 : 1761, 140 : 1901, 141 : 2049, 142 : 2205,
 143 : 2370, 144 : 2544, 145 : 2726, 146 : 2918, 147 : 3119, 148 : 33331, 149 : 3552, 150 : 3784, 151 : 4026, 152 : 4279, 153 : 4543,
 154 : 4818, 155 : 5105, 156 : 5404, 157 : 5715, 158 : 6039, 159 : 6375, 160 : 6724, 161 : 7086, 162 : 7462, 163 : 7851, 164 : 8254,
 165 : 8671, 166 : 9103, 167 : 9550, 168 : 10011, 169 : 10488, 170 : 10980, 171 : 11488, 172 : 12012, 173 : 12500}    
MalusOccasion = {10 : 100, 11 : 100, 12 : 300, 13 : 300, 14 : 300, 15 : 1000}
DictionnaireVoiture = dico_voiture('base_voiture.csv')

#========================
#     Classe voiture 
#========================

class Voitures :
    
    def __init__(self, param = {}):
        #===========
        #   Input
        #===========
        self.drivingCycle = param.get('drivingCycle') # str
        self.taille = param.get('taille') # str parmi{'petite', 'berline', 'citadine', 'dcompacte', 'familiale'} (le d pour avoir un indice différent)
        self.occasion = param.get('occasion', False) # boolean Achat véhicule d'occasion, 
        self.conversion = param.get('conversion') # boolean si conversion thermique à électrique/hybride
        self.distQuot = param.get('distQuot') # int distance quotienne moyenne, aller retour boulot par exemple
        self.frequence = param.get('frequence') #nombre de réalisation de la distance quotidienne par semaine 
        self.modele = param.get('modele') # str  parmi {'ICEV', 'HEV', 'PHEV', 'BEV'} #'BEVH2' on s'en passera, et 'FCEV' et 'FCPHE' manques d'infos pour le moment, il faut compléter le .csv
        #==============================
        #   Attributs intermédiaires
        #==============================
        self.kilometrageAnnuel = param.get('distQuot')*param.get('frequence')*52
        self.nombreAnnees = min(8, 150000/(param.get('distQuot')*param.get('frequence')*52))
        self.kilometrage = 0 #distance totale parcourue sur toute la vie du véhicule
        self.motorisation = self.taille[0]+'-'+self.modele
        self.puissance = 0 #Puissance moteur nécessaire -----> ALGORITHME 
        self.consommationNRJ = 0 #consommation d'énergie sur 100km, en kWh/100km -------> ALGORITHME
        self.masseCarosse = DictionnaireVoiture.get(motorisation).get('masseTotale')
        self.masseTotale = DictionnaireVoiture.get(motorisation).get('masseTotale')
        self.coefficientTrainee = DictionnaireVoiture.get(motorisation).get('CoeffTrainee')
        self.moteur1 = None #[str parmi {"MoteurElectrique", "MoteurThermique"} , int Puissance en kW, boolean True ou False, ratio entr 0 et 1 donnant le ratio d'énergie fourni par cette source, ..., masse] 
            #avec True pour MoteurElectrique == BMS en plus, True pour MoteurThermique == Essence (False si diesel)
        self.moteur2 = None #[str parmi {"MoteurElectrique", "MoteurThermique", "None"} , int Puissance en kW (0 si None), boolean True ou False, ratio entre 0 et 1, ..., masse]
        self.ess1 = None # Liste type ["Batterie", Capacité (en kWh), ...] / ["PileCombustible", Puissance en kW, ..., réservoir hydrogène en kg de H2]
        self.ess2 = None# Si pas d'Ess2, ["None"]
        
        #======================
        #   Attributs finaux
        #======================
        self.prixAchat = 0 # €
        self.coutBonusMalus = 0 # €
        self.coutEntretienTotal = 0 # €
        self.coutUtilisation = 0 # €
        self.TCO = 0 # €
        self.emissionCO2 = 0 #Emission de kgCO2 sur 100 km à l'utilisation
        self.emissionConception = 0 # kgCO2/100km
        self.emissionEntretien = 0 # kgCO2
        
    #==============
    #   Méthodes 
    #============== 
    def __update_kilometrage__(self):
        self.kilometrage = self.kilometrageAnnuel*self.nombreAnnees

    def __dimensionnementESS__(self) : # A DEFINIR !
        pass

    def __update_puissance_NRJ__(self): #A DEFINIR !
        #self.puissance, self.consommationNRJ = drivetrain_fast(self.masseTotale, self.coefficientTrainee)
        pass 

    def __update_moteur_ess__(self) :
        self.moteur1, self.moteur2, self.ess1, self.ess2 = dimensionnementESS(self.distQuot, self.modele, self.puissance, self.consommationNRJ, self.drivingCycle)

    def __update_emissionCO2__(self) :   
        self.emissionC02 = calculEmissionCO2(self.moteur1, self.ess1, self.modele, self.motorisation, self.consommationNRJ, self.masseTotale, True)
        + calculEmissionCO2(self.moteur2, self.ess2, self.modele, self.motorisation, self.consommationNRJ, self.masseTotale, True)

    def __update_masseTotale__(self) : 
        poidsESS = 0
        for ess in [self.ess1, self.ess2]:
            if ess.get('Nom') == "Batterie" :
                poidsESS += ess.get('Puissance')/0.120 # 1 kg de batterie = 120 Wh
            elif ess.get('Nom') == "PileCombustible" :
                poidsESS += ess.get('Reservoir')*20 #20kg de réservoir pour 1 kg de H2
                poidsESS += ess.get('Puissance')*massePAC(ess.get('Puissance'))
        for mot in [self.moteur1, self.moteur2] :
            poidsESS += mot.get('Masse')
        self.masseTotale = self.masseCarosse + poidsESS

    def __update_PrixAchat__(self):
        coutCarrosserie = DictionnaireVoiture.get(self.motorisation).get('prix')
        coutESS1 = calculCoutESS(self.ess1)
        coutESS2 = calculCoutESS(self.ess2)
        coutMoteur1 = calculCoutMoteur(self.moteur1)
        coutMoteur2 = calculCoutMoteur(self.moteur2)
        coutAssurance = self.nombreAnnees*prixAssurance
        self.prixAchat = coutCarrosserie + coutESS1 + coutESS2 + coutMoteur1 + coutMoteur2

    def __update_coutBonusMalus__(self):
        """
        Renvoie la somme des différents malus (>0) et bonus (<0) à l'achat du véhicule:
        [malusCO2, malusAnnuel,  malusOccasion, primeConversion, bonusEcologique]
        Attributs nécessaires : prixAchat, emmissionCO2km, occasion, conversion, puissance, modele
        """
        prix = self.prixAchat
        emissionUnit = self.emissionCO2km*10
        # Calcul du malus CO2 :
        if emissionUnit <= 109 :
            malusCO2 = MalusCO2.get(109)
        elif emissionUnit >= 173 :
            malusCO2 = MalusCO2.get(173)
        else : 
            malusCO2 = MalusCO2.get(emissionUnit)

        # Calcul du malus annuel, à multiplier par le nombre d'années d'utilisation
        malusAnnuel = 0
        if emissionUnit > 190 :
            malusAnnuel = 160

        # Calcul du malus d'occasion
        if self.occasion :
            chevauxFiscaux = int(emissionUnit/45 +self.puissance/40*1.6)
            if 9 < chevaux < 16 :
                malusOccasion = MalusOccasion.get(chevauxFiscaux)
            elif chevaux <= 9 :
                malusOccasion = 0
            else :
                malusOccasion = 1000

        # Calcul des primes :
        primeConversion = 0
        if self.conversion :
            primeConversion = 2000 #euros

        # Bonus écologique (négatif) :
        bonusEcologique = 0
        if self.modele == 'BEV' :
            if prix <= 450000 :
                bonusEcologique = -min(6000, 0.27*prix)
            elif 45000< prix <= 60000 :
                bonusEcologique = -3000
        elif self.modele == 'FCEV' :
            if prix >= 60000 :
                bonusEcologique = -3000
        elif self.modele == 'HEV' or self.modele == 'PHEV' :
            if self.emissionUnit <50 : 
                bonusEcologique = -2000

        self.coutBonusMalus = malusCO2 + malusAnnuel +  malusOccasion + primeConversion + bonusEcologique

    def __update_coutEntretienTotal__(self):
        nbre = int(self.kilometrage/10000)
        cost = 0
        mod = self.modele
        for i in range(nbre):
            cost += coutEntretien(mod)
        
        #Eventuel changement de batterie ou de pile à combustible
        coutMaj = 0
        if self.ess1.get('Nom') == "Batterie" :
            if self.kilometrage >= 160000 :
                coutMaj = calculCoutESS(self.ess1)
        elif self.ess1.get('Nom') == "PileCombustible" :
            if self.kilometrage >= 200000: 
                coutMaj = calculCoutESS(self.ess1)
        self.coutEntretienTotal = cost + coutMaj

    def __update_coutUtilisation__(self): # A COMPLETER : RENSEIGNER LES ARGUMENTS DES FONCTIONS consoEV et consoFCEV
        if self.moteur1.get('Nom')== "MoteurElectrique" and self.moteur2.get('Nom') == "None" : 
            if self.ess1.get('Nom')== "Batterie":
                self.coutUtilisation += self.kilometrage*consoEV(self)/100*prixPompeElec    #facteur1/100 car conso donnée en energie/100km
            else : 
                self.coutUtilisation += self.kilometrage*consoFCEV(self)/100*prixPompeHydro
        elif self.moteur1.get('Nom') == "MoteurThermique" and self.moteur2.get('Nom') == "None" :
            if self.moteur1.get('Carac') :
                self.coutUtilisation += self.kilometrage*consoEssence(self.masseTotale)/100*prixEssence
            else :
                self.coutUtilisation += self.kilometrage*consoDiesel(self.masseTotale)/100*prixDiesel
        elif self.moteur1.get('Nom') == "MoteurThermique" and self.moteur2.get('Nom') == "MoteurElectrique" : 
            if self.ess2.get('Nom') == "Batterie":
                if self.moteur1.get('Carac'):
                    self.coutUtilisation += self.kilometrage*(
                    consoEV(self)/100*prixPompeElec*self.moteur2.get('Ratio') + consoEssence(self)/100*prixEssence*self.moteur1.get('Ratio'))
                else : 
                    self.coutUtilisation += self.kilometrage*(
                    consoEV(self)/100*prixPompeElec*self.moteur2.get('Ratio') + consoDiesel(self)/100*prixDiesel*self.moteur1.get('Ratio'))
            elif self.ess2.get('Nom') == "PileCombustible" : 
                if self.moteur1.get('Carac'):
                    self.coutUtilisation += self.kilometrage*(
                    consoFCEV(self)/100*prixPompeHydro*self.moteur2.get('Ratio') + consoEssence(self)/100*prixEssence*self.moteur1.get('Ratio'))
                else : 
                    self.coutUtilisation += self.kilometrage*(
                    consoFCEV(self)/100*prixPompeHydro*self.moteur2.get('Ratio') + consoDiesel(self)/100*prixDiesel*self.moteur1.get('Ratio'))
        elif self.moteur1.get('Nom') == "MoteurElectrique" and self.moteur2.get('Nom') == "MoteurElectrique" : 
            if self.ess1[0] == 'Batterie':
                self.coutUtilisation += self.kilometrage*(
                consoEV(self)/100*prixPompeElec*self.moteur1.get('Ratio') + consoFCEV(self)/100*prixPompeHydro*self.moteur2.get('Ratio'))
            else : 
                self.coutUtilisation += self.kilometrage*(
                consoFCEV(self)/100*prixPompeHydro*self.moteur1.get('Ratio') + consoEV(self)/100*prixPompeElec*self.moteur2.get('Ratio'))
    
    def __update_TCO__(self) :
        self.TCO = self.prixAchat + self.coutBonusMalus + self.coutEntretienTotal + self.coutUtilisation

    def __update_emissionConception__(self) : # A DEFINIR !
        pass

    def __update_emissionEntretien__(self): # A DEFINIR !
        pass

    def __MAJ__(self):
        self.__update_kilometrage__()
        self.__update_puissance_NRJ__()
        self.__update_moteur_ess__()
        self.__update_emissionCO2__()
        self.__update_masseTotale__()
        self.__update_PrixAchat__()
        self.__update_coutBonusMalus__()
        self.__update_coutEntretienTotal__()
        self.__update_coutUtilisation__()
        self.__update_TCO__()
        self.__update_emissionConception__()
        self.__update_emissionEntretien__()


#==================================
#     Représentation graphique
#================================== 

""" Idee :
Les parametres Voiture qu'on peut choisir sont les attributs input. 
Dans le notebook, il suffit de créer un dictionnaire avec ces paramètres, et d'importer ce fichier comme une librairie.
Par exemple, il pourrait être bien de voir l'attribut 'modele' comme la variable qu'on fait varier. 
En outre, l'idée est de se ramener à comparer, pour les exigences fixées, les différents modeles (TCO et emissions) et de voir quel est le meilleur.
Ainsi, dans le notebook il suffit juste de créer un dictionnaire avec 
{'drivingCycle': ... , 'conversion' ... : , 'taille' : ..., 'distQuot' : ..., 'nombreAnnees' : ..., 'modele' : 'variable'}
Ensuite, pour mod in ['ICEV', 'HEV', 'PHEV', 'BEV', 'FCEV'], on créé la dite voiture avec tous les paramètres, et on ajoute le dictionnaire dans la Liste suivante:
ListeVoiture += [creationVoitures(Voitures)]
Enfin, on finalise en appelant une fonction qui plot le graphique, en prenannt en argument justement ListeVoiture
"""


def creationVoiture(Voitures) :
    Voitures.__MAJ__
    Voiture = {'coutBonusMalus' : Voitures.coutBonusMalus, 'coutEntretien' : Voitures.coutEntretienTotal, 
    'coutUtilisation' : Voitures.coutUtilisation, 'emissionUtilisation' : Voitures.emissionCO2, 
    'emissionConception' : Voitures.emissionConception, 'emissionEntretien' : Voitures.emissionEntretien}
    return Voiture

def update(L1, L2):
    l = len(L1)
    L3 = []
    for i in range(l):
        L3 += [max(0,L1[i])+L2[i]]
    return L3

# Valeurs aléatoires, juste pour avoir une représentation
Voiture1 = {'coutBonus' : -2000 , 'coutAchat' : 20000, 'coutEntretien' : 10000 , 'coutUtilisation' : 12000, 'emissionUtilisation' : 3600, 'emissionConception' : 2500, 'emissionEntretien' : 1100}
Voiture2 = {'coutBonus' : 0, 'coutAchat' : 15000, 'coutEntretien' : 7000, 'coutUtilisation' : 8000, 'emissionUtilisation' : 4500, 'emissionConception' : 3600, 'emissionEntretien' : 900 }
Voiture3 = {'coutBonus' : -5000, 'coutAchat' : 30000 , 'coutEntretien' : 15000, 'coutUtilisation' : 4000, 'emissionUtilisation' : 2000, 'emissionConception' : 800, 'emissionEntretien' : 700}
ListeVoiture = [Voiture1, Voiture2, Voiture3]

ycoutBonus = [i.get('coutBonus') for i in ListeVoiture]
ycoutAchat = [i.get('coutAchat') for i in ListeVoiture]
ycoutEntretien = [i.get('coutEntretien') for i in ListeVoiture]
ycoutUtilisation = [i.get('coutUtilisation') for i in ListeVoiture]
xemissionUtilisation = [i.get('emissionUtilisation') for i in ListeVoiture]
xemissionConception = [i.get('emissionConception') for i in ListeVoiture]
xemissionEntretien = [i.get('emissionEntretien') for i in ListeVoiture]
newTCO = [i.get('TCO') for i in ListeVoiture]

def calculTCO(dico):
    return dico.get('coutBonus')+dico.get('coutAchat')+dico.get('coutEntretien')+dico.get('coutUtilisation')
TCO = [calculTCO(i) for i in ListeVoiture]

Li1 = update(ycoutBonus, [0 for i in range(len(ListeVoiture))])
Li2 = update(Li1, ycoutAchat)
Li3 = update(Li2, ycoutEntretien)
Lj1 = update(xemissionConception,xemissionEntretien) 

barWidth = 0.3
r = len(ListeVoiture) # Nombre de groupe de colonnes
r1 = range(r) #placement des colonnes cout
r2 = [x + 0.5 for x in r1] #placement des colonnes emission
r0 = [x + 0.25 for x in r1] # placement des colonnes TCO final
Gender = ["TCO final", "Bonus-Malus", "Cout à l'achat", "Cout d'entretien", "Cout d'utilisation", "Emission de conception", "Emision d'entretien", "Emission à l'utilisation"]

plt.bar(r0, TCO, width = 0.1, color = 'darkslategrey', edgecolor = 'black', hatch = '/')
plt.bar(r1, ycoutBonus, width = barWidth, color = 'chartreuse', edgecolor ='black')
plt.bar(r1, ycoutAchat, width = barWidth, color = 'dodgerblue', edgecolor ='black', bottom=Li1)
plt.bar(r1, ycoutEntretien, width = barWidth, color = 'crimson', edgecolor ='black', tick_label = 'Entretien', bottom=Li2)
plt.bar(r1, ycoutUtilisation, width = barWidth, color = 'gold', edgecolor ='black', tick_label = 'Utilisation', bottom=Li3)
plt.bar(r2, xemissionConception, width = barWidth, color = 'lightgrey', edgecolor = 'black')
plt.bar(r2, xemissionEntretien, width = barWidth, color = 'grey', edgecolor = 'black', bottom = xemissionConception)
plt.bar(r2, xemissionUtilisation, width = barWidth, color = 'dimgray', edgecolor = 'black', bottom = Lj1)

plt.xlabel('Modèles de voiture', fontsize = 15)
plt.ylabel('TCO (€) _ Emission de Co2 (kg)', fontsize = 12)
plt.title('TCO et émission de CO2 pour chaque véhicule')
plt.xticks(r1, ['Voiture1', 'Voiture2', 'Voiture3'])
plt.legend(Gender)
plt.show()
# Rajouter une deuxième légende pour le CO2



""" Commentaires : 
Pour dimensionner la puissance moteur, faire en fonction de la vitesse max. 
pour dimensionner la puissance de la batterie ou de la pile à combustible, utiliser lalgorithme, déterminer lenergie consommée et diviser par le temps
dutilisation pour avoir la capacité nécessaire. 

coutUtilisation = coutPompe*consommation1Cycle*nbreCycleConduite
"""



