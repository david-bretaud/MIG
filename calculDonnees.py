import numpy as np

# Constantes globales :
coutPompeElec = 1 #Demander groupe 3
coutPompeHydro = 1 #Demander groupe 2
prixLitreCarburant = 1.3 #en €/L
prixBattery = 225 #prix de la batterie en €/kWh
prixFC = 300 #prix de la pile à combustible en €/kW

# Dictionnaires
MalusCO2 = {109 : 0, 110 : 50, 111 : 75, 112 : 100, 113 : 125, 114 : 150, 115 : 170, 116 : 190, 117 : 210, 118 : 230, 119 : 240,
 120 : 260, 121 : 280, 122 : 310, 123 : 330, 124 : 360, 125 : 400, 126 : 450, 127 : 540, 128 : 650, 129 : 740, 130 : 818, 131 : 898,
 132 : 983, 133 : 1074, 134 : 1172, 135 : 1276, 136 : 1386, 137 : 1504, 138 : 1629, 139 : 1761, 140 : 1901, 141 : 2049, 142 : 2205,
 143 : 2370, 144 : 2544, 145 : 2726, 146 : 2918, 147 : 3119, 148 : 33331, 149 : 3552, 150 : 3784, 151 : 4026, 152 : 4279, 153 : 4543,
 154 : 4818, 155 : 5105, 156 : 5404, 157 : 5715, 158 : 6039, 159 : 6375, 160 : 6724, 161 : 7086, 162 : 7462, 163 : 7851, 164 : 8254,
 165 : 8671, 166 : 9103, 167 : 9550, 168 : 10011, 169 : 10488, 170 : 10980, 171 : 11488, 172 : 12012, 173 : 12500}    
MalusOccasion = {10 : 100, 11 : 100, 12 : 300, 13 : 300, 14 : 300, 15 : 1000}
Batterie = {2 : ( , ),5 : ( , ), 10 : ( , ), 20 : ( , ), 30 : ( , ), 40 : ( , ), 50 : ( , ), 60 : ( , ), 70 : ( , ), 80 : ( , )} 
FuelCell = {'Puissance' : (cout en euros, emission de CO2 en gCO2/km)}
ICE = {'Puissance' : (cout en euros, emission de CO2 en gCO2/km)}
ElectricMotor = {'Puissance' : (cout en euros, emission de CO2 en gCO2/km)}

Attributs :
    emissionCO2km : int #Emission de gCO2 au km
    occasion : boolean #Achat véhicule d'occasion
    puissance : int #Puissance de moteur en kW
    modele : str  parmi {'ICEV', 'HEV', 'PHEV', 'BEV', 'BEVH2', 'FECV', 'FCPHE'} 
    conversion : boolean #si conversion à électrique
    gabarit : str parmi{'Berline', 'Familiale', 'Citadine'}
    kilometrage : int #distance parcourue tout au long de la vie du véhicule, en km.
    dQuot : int #distance quotienne. 
    drivingCycle :
    ESS : str parmi ('Batterie', 'ICE', 'FuelCell') 
    ESS2 : str parmi {'Batterie', 'ICE', 'FuelCell', None}
    ESS_modele = int #donne la clé du dictionnaire associé
    ESS2_modele = int (0 si None) #donne la clé du dictionnaire associé

    


def coutBonusMalus():
    """
    Renvoie les différents malus (>0) et bonus (<0) à l'achat du véhicule:
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

    # Calcul du malus annuel, à multiplier par le nombre d'année d'utilisation
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

    return [malusCO2, malusAnnuel,  malusOccasion, primeConversion, bonusEcologique]

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

def coutAchat():
           




coutUtilisation = coutPompe*consommation1Cycle*nbreCycleConduite




