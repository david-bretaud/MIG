import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt


#=========================
#     Fonctions amont
#=========================

def dico_voiture(file) :
    dico = {}
    df = pd.read_csv(file, index_col = 'motorisation')
    for c in df['categorie'] :
        dico[c] = {}
    for m in df.index :
        if df.loc[m]['poids'] == 'None' :
            continue
        dico[df.loc[m]['categorie']][m] = {critere: df.loc[m][critere] for critere in df.columns}
    return dico


#=============================
#     Constantes globales 
#============================= 

coutPompeElec = 0.2 #Demander groupe 3 / en €/kWh
coutPompeHydro = 10 #Demander groupe 2 / en €/kg
prixDiesel = 1.26 #€/L
prixEssence = 1.35 #€/L
emissionEssence = 2.3 #kgCO2/L
emissionDiesel = 2.7 #kgCo2/L
prixBattery = 130 #prix de la batterie en €/kWh
prixFC = 160 #prix de la pile à combustible en €/kW


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
Batterie = {2 : ( , ),5 : ( , ), 10 : ( , ), 20 : ( , ), 30 : ( , ), 40 : ( , ), 50 : ( , ), 60 : ( , ), 70 : ( , ), 80 : ( , )} 
FuelCell = {'Puissance' : (cout en euros, emission de CO2 à la conception)}
ICE = {'Puissance' : (cout en euros, emission de CO2 en gCO2/km)}
ElectricMotor = {'Puissance' : (cout en euros, emission de CO2 en gCO2/km)}
DictionnaireVoiture = dico_voiture('Classeur5.csv')


#==================================
#     Classe voiture (à faire) 
#==================================

Attributs :
    modele : str  parmi {'ICEV', 'HEV', 'PHEV', 'BEV', 'BEVH2', 'FECV', 'FCPHE'}
    taille : str parmi{'Petite', 'Berline', 'Citadine', 'Compacte', 'Familiale'}
    occasion : boolean #Achat véhicule d'occasion
    conversion : boolean #si conversion à électrique
    puissance : int #Puissance de moteur en kW
    kilometrage : int #distance parcourue tout au long de la vie du véhicule, en km.
    dQuot : int #distance quotienne. 
    drivingCycle : str

    prixAchat = int #calculé après coup
    emissionCO2km : 0.0 #Emission de gCO2 au km, calculé après coup
    ESS : str parmi ('Batterie', 'ICE', 'FuelCell') #attribué selon le modèle
    ESS2 : str parmi {'Batterie', 'ICE', 'FuelCell', None} #attribué selon le modèle
    ESS_modele = int #donne la clé du dictionnaire associé (ie la puissance), déterminé par un algorithme de dimensionnement
    ESS2_modele = int (0 si None) #donne la clé du dictionnaire associé (ie la puissance), déterminé par un algorithme de dimensionnement
    poids et prix de la carrosserie : prendre les data dans le dictionnaire de voiture en fonction de taille et motorisation
    bonus_malus = 0 #Calculé après coup (besoin de prixAchat, emissionCO2km, puissance, occasion)


#==================
#     Méthodes 
#================== 

def consoEssence(x):
    """
    Renvoie la consommation d'essence en L/100km en fonction de la masse du véhicule
    """
    return 2*10**(-6)*x**2+0.0005*x + 3.3549

def consoDiesel(x):
    """
    Renvoie la consommation de diesel en L/100km en fonction de la masse du véhicule
    """
    return 2*10**(-6)*x**2-0.0008*x + 3.198

def consoHEV(x):
    """
    Renvoie la consommation de carburant d'un HEV en L/100km en fonction de la masse du véhicule
    """
    return  10**(-6)*x**2-0.0008*x + 3.2038

def consoPHEV(x):
    """
    Renvoie la consommation de carburant d'un PHEV en L/100km en fonction de la masse du véhicule
    """
    return 2.57 + (x-780)*0.82/1550

def coutBonusMalus():
    """
    Renvoie la somme des différents malus (>0) et bonus (<0) à l'achat du véhicule:
    [malusCO2, malusAnnuel,  malusOccasion, primeConversion, bonusEcologique]
    """
    prix = self.prixAchat
    # Calcul du malus CO2 :
    if self.emmisionCO2km <= 109 :
        malusCO2 = MalusCO2.get(109)
    elif self.emissionCO2km >= 173 :
        malusCO2 = MalusCO2.get(173)
    else : 
        malusCO2 = MalusCO2.get(self.emissionCO2km)

    # Calcul du malus annuel, à multiplier par le nombre d'années d'utilisation
    malusAnnuel = 0
    if self.emissionCO2km > 190 :
        malusAnnuel = 160

    # Calcul du malus d'occasion
    if self.occasion :
        chevaux = int(self.puissance*1.35962162)
        if 9 < chevaux < 16 :
            malusOccasion = MalusOccasion.get(chevaux)
        elif chevaux <= 9 :
            malusOccasion = 0
        else :
            malusOccasion = 1000

    # Calcul des primes :
    primeConversion = 0
    if conversion :
        primeConversion = 2000 euros

    # Bonus écologique (négatif) :
    bonusEcologique = 0
    if self.modele = 'BEV' :
        if prix <= 450000 :
            bonusEcologique = -min(6000, 0.27*prix)
        elif 45000< prix <= 60000 :
            bonusEcologique = -3000
    elif self.modele = 'FCEV' :
        if prix >= 60000 :
            bonusEcologique = -3000
    elif self.modele = 'HEV' :
        if self.emissionCO2km <50 : 
            bonusEcologique = -2000

    return malusCO2 + malusAnnuel +  malusOccasion + primeConversion + bonusEcologique

def coutEntretien(mod):
    """
    Renvoie le cout d'entretien de la voiture sur 10 000km.
    """
    if mod = 'ICEV'
        prix = np.random.randint(536, 918)
    elif mod = 'HEV' or mod = 'PHEV' :
        prix = np.random.randint(482, 826)
    elif mod = 'BEV' :
        prix = np.random.randint(413, 706)
    elif mod  = 'BEVH2' : 
        prix = np.random.randint(450, 750)
    elif mod = 'FCEV' or mod = 'FCPHE' :
        prix = np.random.randint(413, 706)

def coutEntretienTotal():
    nbre = int(self.kilometrage/10000)
    cost = 0
    mod = self.modele
    for i in range(nbre):
        cost += coutEntretien(mod)
    return cost

def coutMAJ():
    """
    Cout de remplacement des ESS : batterie à partir de 160 000km, pile à combustible à partir de 200 000km
    """
    coutMaj = 0
    if ESS = 'Batterie' :
        if kilometrage >= 160000 :
            coutMaj = Batterie.get(ESS_modele)[0]
    elif ESS = 'FuelCell' :
        if kilometrage >= 200000: 
            coutMaj = FuelCell.get(ESS_modele)[0]
    return coutMaj

def dimensionnementESS() :

def coutAchat():
    
def analyseVehicule(Vehicle) :


#================================================
#     Représentation (juste à titre d'image)
#================================================ 

X = np.linspace(500, 2500, 500)

plt.plot(X, consoEssence(X), label = 'Essence')
plt.plot(X, consoDiesel(X), label = 'Diesel')
plt.plot(X, consoHEV(X), label = 'HEV')
plt.plot(X, consoPHEV(X), label = 'PHEV')
plt.legend()
plt.show()

prixDiesel = 1.26 #€/L
prixEssence = 1.35 #€/L
emissionDiesel = 2.7 #kgCo2/L
emissionEssence = 2.3 #kgCO2/L

plt.plot(X, consoEssence(X)*prixEssence, label = 'Dépenses en euros sur 100 km pour un véhicule essence')
plt.plot(X, consoDiesel(X)*prixDiesel, label = 'Dépenses en euros sur 100 km pour un véhicule diesel')
plt.plot(X, consoEssence(X)*emissionEssence, label = 'Emissions de Co2 en kg sur 100 km pour un véhicule essence')
plt.plot(X, consoDiesel(X)*emissionDiesel, label = 'Emissions de Co2 en kg  sur 100 km pour un véhicule diesel')
plt.legend()
plt.show()


#==================================
#     Représentation graphique
#================================== 


def calculTCO(dico):
    return dico.get('coutBonus')+dico.get('coutAchat')+dico.get('coutEntretien')+dico.get('coutUtilisation')

def update(L1, L2):
    l = len(L1)
    L3 = []
    for i in range(l):
        L3 += [max(0,L1[i])+L2[i]]
    return L3

# Valeurs aléatoires, juste pour avoir une représentation
Voiture1 = {'coutBonus' : -2000 , 'coutAchat' : 20000, 'coutEntretien' : 10000 , 'coutUtilisation' : 12000, 'emissionUtilisation' : 3600, 'emissionConception' : 2500}
Voiture2 = {'coutBonus' : 0, 'coutAchat' : 15000, 'coutEntretien' : 7000, 'coutUtilisation' : 8000, 'emissionUtilisation' : 4500, 'emissionConception' : 3600 }
Voiture3 = {'coutBonus' : -5000, 'coutAchat' : 30000 , 'coutEntretien' : 15000, 'coutUtilisation' : 4000, 'emissionUtilisation' : 2000, 'emissionConception' : 800}
ListeVoiture = [Voiture1, Voiture2, Voiture3]

ycoutBonus = [i.get('coutBonus') for i in ListeVoiture]
ycoutAchat = [i.get('coutAchat') for i in ListeVoiture]
ycoutEntretien = [i.get('coutEntretien') for i in ListeVoiture]
ycoutUtilisation = [i.get('coutUtilisation') for i in ListeVoiture]
xemissionUtilisation = [i.get('emissionUtilisation') for i in ListeVoiture]
xemissionConception = [i.get('emissionConception') for i in ListeVoiture]
TCO = [calculTCO(i) for i in ListeVoiture]

Li1 = update(ycoutBonus, [0 for i in range(len(ListeVoiture))])
Li2 = update(Li1, ycoutAchat)
Li3 = update(Li2, ycoutEntretien)

barWidth = 0.3
r = len(ListeVoiture) # Nombre de groupe de colonnes
r1 = range(r) #placement des colonnes cout
r2 = [x + 0.5 for x in r1] #placement des colonnes emission
r0 = [x + 0.25 for x in r1] # placement des colonnes TCO final
Gender = ["TCO final", "Bonus-Malus", "Cout à l'achat", "Cout d'entretien", "Cout d'utilisation", "Emission de conception", "Emission à l'utilisation"]

plt.bar(r0, TCO, width = 0.1, color = 'darkslategrey', edgecolor = 'black', hatch = '/')
plt.bar(r1, ycoutBonus, width = barWidth, color = 'chartreuse', edgecolor ='black')
plt.bar(r1, ycoutAchat, width = barWidth, color = 'dodgerblue', edgecolor ='black', bottom=Li1)
plt.bar(r1, ycoutEntretien, width = barWidth, color = 'crimson', edgecolor ='black', tick_label = 'Entretien', bottom=Li2)
plt.bar(r1, ycoutUtilisation, width = barWidth, color = 'gold', edgecolor ='black', tick_label = 'Utilisation', bottom=Li3)
plt.bar(r2, xemissionConception, width = barWidth, color = 'lightgrey', edgecolor = 'black')
plt.bar(r2, xemissionUtilisation, width = barWidth, color = 'dimgray', edgecolor = 'black', bottom = xemissionConception)


plt.xlabel('Modèles de voiture', fontsize = 15)
plt.ylabel('TCO (€) _ Emission de Co2 (kg)', fontsize = 12)
plt.title('TCO et émission de CO2 pour chaque véhicule')




""" Commentaires : 
Pour dimensionner la puissance moteur, faire en fonction de la vitesse max. 
pour dimensionner la puissance de la batterie ou de la pile à combustible, utiliser lalgorithme, déterminer lenergie consommée et diviser par le temps
dutilisation pour avoir la capacité nécessaire. 

coutUtilisation = coutPompe*consommation1Cycle*nbreCycleConduite
"""



