"""coutPompeElec = 1 #Demander groupe 3
coutPompeHydro = 1 #Demander groupe 2
prixLitreCarburant = 1.3

prixAchat ==> renvoyer par premier algo : fonction des composants  + gabarit (prix de carrosserie)

Attributs dont jai besoin (introduits par self) 
    emissionCO2km : nbre en gCO2/km #Emission de CO2 au km
    occasion : boolean #Achat véhicule d'occasion
    puissance : int en cv #Puissance de moteur
    modele : str  parmi {'ICEV', 'HEV', 'PHEV', 'BEV', 'BEVH2', 'FECV', 'FCPHE'} 
    conversion : boolean #si conversion à électrique
    


Calcul des couts supplémentaires : malusCO2, malusAnnuel, malusOccasion, primeConversion, bonusEcologique

# Dictionnaires
MalusCO2 = {109 : 0, 110 : 50, 111 : 75, 112 : 100, 113 : 125, 114 : 150, 115 : 170, 116 : 190, 117 : 210, 118 : 230, 119 : 240,
 120 : 260, 121 : 280, 122 : 310, 123 : 330, 124 : 360, 125 : 400, 126 : 450, 127 : 540, 128 : 650, 129 : 740, 130 : 818, 131 : 898,
 132 : 983, 133 : 1074, 134 : 1172, 135 : 1276, 136 : 1386, 137 : 1504, 138 : 1629, 139 : 1761, 140 : 1901, 141 : 2049, 142 : 2205,
 143 : 2370, 144 : 2544, 145 : 2726, 146 : 2918, 147 : 3119, 148 : 33331, 149 : 3552, 150 : 3784, 151 : 4026, 152 : 4279, 153 : 4543,
 154 : 4818, 155 : 5105, 156 : 5404, 157 : 5715, 158 : 6039, 159 : 6375, 160 : 6724, 161 : 7086, 162 : 7462, 163 : 7851, 164 : 8254,
 165 : 8671, 166 : 9103, 167 : 9550, 168 : 10011, 169 : 10488, 170 : 10980, 171 : 11488, 172 : 12012, 173 : 12500}    

MalusOccasion = {10 : 100, 11 : 100, 12 : 300, 13 : 300, 14 : 300, 15 : 1000}

    # Calcul du malus CO2 :
    if self.emmisionCO2km <= 109 :
        malusCO2 = MalusCO2.get(109)
    else if self.emissionCO2km >= 173 :
        malusCO2 = MalusCO2.get(173)
    else : 
        malusCO2 = MalusCO2.get(self.emissionCO2km)

    # Calcul du malus annuel, à multiplier par le nombre d'année d'utilisation
    malusAnnuel = 0
    if self.emissionCO2km > 190 :
        malusAnnuel = 160

    # Calcul du malus d'occasion
    if self.occasion :
        if 9 < self.puissance < 16 :
            malusOccasion = MalusOccasion.get(self.puissance)
        else if self.puissance <= 9 :
            malusOccasion = 0
        else :
            malusOccasion = 1000

    # Calcul des primes :
    primeConversion = 0
    if conversion :
        primeConversion = 2000 euros

    # Bonus écologique :
    bonusEcologique = 0
    if modele = 'BEV' :
        if prixAchat <= 450000 :
            bonusEcologique = min(6000, 0.27*prixAchat)
        else if 45000< prixAchat <= 60000 :
            bonusEcologique = 3000
    else if modele = 'FCEV' :
        if prixAchat >= 60000 :
            bonusEcologique = 3000
    else if modele = 'HEV' :
        if self.emissionCO2km <50 : 
            bonusEcologique = 2000



coutEntretien = 0 
if modele = ''

coutUtilisation = coutPompe*consommation1Cycle*nbreCycleConduite
"""



