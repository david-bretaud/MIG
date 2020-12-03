import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from ConsoPuissance import * 
from drivetrain_fast import *

# Ajouter l'abonnement electricite


#=============================
#     Constantes globales 
#============================= 

prixMoteurElectrique = 12 # €/kW
prixMoteurThermique = 25 # €/kW et comprend l'ICE
prixBatterie = 131 # €/kWh
prixPile = 160 # €/kW
prixReservoirH2 = 880 # €/kg
prixAssurance = 700 # €/an
prixPompeHydro = 10 #Demander groupe 2 / en €/kg
prixDiesel = 1.26 #€/L
prixEssence = 1.35 #€/L
emissionEssence = 2.3 #kgCO2/L
emissionDiesel = 2.7 #kgCo2/L
emissionElectricite = 0.056 # en kg/kWh pour le mix français (donnée notebook)
emissionHydrogene = emissionElectricite/0.1*5.6  # en kg de CO2/ kg de H2 ie en kg de CO2/16 kWh (en comptabilisant les 50% de rendement)


#=========================
#     Fonctions amont
#=========================

def dico_voiture(file) :
    dico = {}
    df = pd.read_csv(file, index_col = 'motorisation')
    for m in df.index :
        if df.loc[m]['consommation_WLTP'] == 'None' :
            continue
        dico[m] = {}
        for critere in df.columns :
            if critere == 'categorie' :
                dico[m][critere] = df.loc[m][critere]
            else :
                dico[m][critere] = float(df.loc[m][critere])
    return dico

def prixPompeElec(usage):   
    """
    Renvoie le prix du kWh en euros en fonction de sa borne de recharge : chez soi, bornes autoroutes, bornes de ville
    """ 
    if usage == rural or usage == periurbain:
        #On peut la recharger a la maison
        prix = 0.14 #en €/kWh
        temps = 10 #en heures
        return prix
    elif usage == urbain:
        abonnement = 15 #euros
        prix = 0.25 #Prix moyen (mais on peut descendre a 0)
        temps = 5
        return prix
    elif usage == autoroute:
        prix = (2/3)*0.5 + (1/3)*0.14 #moyenne entre supercharger autoroute et maison
        temps = 1
        return prix
 
def dimensionnementPHEV(dist): 
    def puissanceICE(x) :
        if 15 <= x < 50 :
            return 90
        elif 50<=x < 100 :
            return 90 - (x-50)*7/5
        elif 100<= x :
            return 20
    def puissanceBatterie(x):
        if 15 <= x < 50 :
            return 30
        elif 50<=x < 100 :
            return 30 + (x-50)*6/5
        elif 100<= x :
            return 90
    return puissanceICE(dist), puissanceBatterie(dist)

def autonomie(modele, cycle, dist):
    if cycle == autoroute :
        if modele == "FCEV":
            return min(400, 10*dist)
        elif modele == "BEV":
            return max(350, 2*dist)  
    elif cycle == urbain :
        if modele == "FCEV":
            return min(250, 15*dist)
        elif modele == "BEV":
            return max(150, 2*dist)
    elif cycle == periurbain :
        if modele == "FCEV":
            return min(300, 10*dist)
        elif modele == "BEV":
            return max(200, 2*dist)
    elif cycle == rural :
        if modele == "FCEV":
            return min(300, 10*dist)
        elif modele == "BEV":
            return max(250, 2*dist)

def dimensionnementFCEV(puis, masse):
    ratio = masse/1750
    x = puis*ratio
    if x <13 : 
        return min(2.2, 0.001*(2200 - (x-10)*150))
    elif 13 <= x < 30 :
        return 0.001*(1750-(x-13)*880/17)
    else :
        return 0.001*(870+(x-30)*465/7)

def masseMoteurThermique(puissance) :  
    '''
    renvoie la masse du moteur+réservoir en fonction de la puissance du moteur, puissance en entrée en kW
    '''
    reservoir = 35
    moteur = puissance/0.600  #modele linéaire 600W/kg
    return moteur + reservoir

def masseMoteurElectrique(puissance): 
    """
    renvoie la masse du pack moteur (comprenant moteur electrique, onduleur, etc...)
    """
    return 30

def massePAC(puissance):
    '''
    renvoie la masse de la PAC en fonction de la puissance(modele 10/4 yourik) avec la donnée 56kg pour 113 kW Mirai
    '''
    return 56*(puissance/113)

def masseBatterie(capacite):
    """
    renvoie la masse de la batterie en fonction de la capacité
    """
    if capacite < 20 :
        return capacite/0.120
    elif capacite > 70 :
        return capacite/0.180
    else :
        return capacite/((capacite-20)*0.06/50+0.120)

def calculCoutMoteur(moteur):
    if moteur.get('Nom') == "MoteurElectrique":
        return moteur.get('Puissance')*prixMoteurElectrique
    elif moteur.get('Nom') == "MoteurThermique" :
        return moteur.get('Puissance')*prixMoteurThermique
    else :
        return 0

def calculCoutESS(ess):
    if ess.get('Nom')=="Batterie":
        alpha = 1
        if ess.get('Pack')==True:
            alpha=1.2
        return ess.get('Capacite')*prixBatterie*alpha
    elif ess.get('Nom')=="PileCombustible":
        return ess.get('Puissance')*prixPile + ess.get('Reservoir')*prixReservoirH2
    else :
        return 0
    
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
    else :
        prix = 0
    return prix

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
        self.drivingCycle = param.get('drivingCycle') # variable parmi urbain, periurbain, autoroute, rural ie WLTP
        self.taille = param.get('taille') # str parmi{'petite', 'berline', 'citadine', 'dcompacte', 'familiale'} (le d pour avoir un indice différent)
        self.occasion = param.get('occasion', False) # boolean Achat véhicule d'occasion
        self.conversion = param.get('conversion') # boolean si conversion thermique à électrique/hybride
        self.distQuot = param.get('distQuot') # int distance quotienne moyenne, aller retour boulot par exemple
        self.frequence = param.get('frequence') #nombre de réalisation de la distance quotidienne par semaine 
        self.modele = param.get('modele') # str  parmi {'ICEV', 'HEV', 'PHEV', 'BEV', 'FCEV'} 'FCPHE' et 'BEVH2' on s'en passera
        #==============================
        #   Attributs intermédiaires
        #==============================
        self.kilometrageAnnuel = param.get('distQuot')*param.get('frequence')*52
        self.nombreAnnees = min(8, 150000/(param.get('distQuot')*param.get('frequence')*52))
        self.motorisation = param.get('taille')[0]+'-'+param.get('modele')
        self.prixPompeElec = prixPompeElec(param.get('drivingCycle'))
        self.kilometrage = 0 #distance totale parcourue sur toute la vie du véhicule
        self.masseTotale = 0
        self.coefficientTrainee = 0
        self.dico = None
        self.puissance = 0 #Puissance moteur nécessaire       
        self.moteur1 = None 
        self.moteur2 = None 
        self.ess1 = None 
        self.ess2 = None
        self.consommationNRJ = 0 #consommation d'énergie sur 100km, en kWh/100km pour les véhicules elec, en kgH2/100km pour FCEV
        
        #======================
        #   Attributs finaux
        #======================
        self.prixAchat = 0 # €
        self.coutBonusMalus = 0 # €
        self.coutEntretienTotal = 0 # €
        self.coutUtilisation = 0 # €
        self.TCO = 0 # €
        self.emissionConception = 0 # en kgCO2
        self.emissionUtilisation = 0 # en kgCO2
        self.emissionRecyclage = 0 # en kgCO2
        self.emissionTotale = 0 # en kgCO2
        
    #==============
    #   Méthodes 
    #==============
     
    def __update_automatique__(self):
        self.kilometrage = self.kilometrageAnnuel*self.nombreAnnees
        self.coefficientTrainee = DictionnaireVoiture.get(self.taille[0]+'-'+'ICEV').get('coeffTrainee')
        self.masseTotale = DictionnaireVoiture.get(self.motorisation).get('masseTotale')

    def __update_dico__(self): 
        self.dico = {'masseTotale' : self.masseTotale, 'CoeffTrainee' : self.coefficientTrainee}

    def __update_puissance__(self): 
        self.puissance = puissance_necessaire(self.dico)

    def __update_moteur_ess__(self) : 
        if self.modele == 'ICEV' :
            self.moteur1 = {'Nom' : "MoteurThermique", 'Puissance': self.puissance }
            self.moteur2 = {'Nom' : "None"}
            self.ess1 = {'Nom' : "ReservoirEssence"}
            self.ess2 = {'Nom' : "None"}
        elif self.modele == 'HEV' :
            self.moteur1 = {'Nom' : "MoteurThermique", 'Puissance' : self.puissance}
            self.moteur2 = {'Nom' : "MoteurElectrique", 'Puissance' : DictionnaireVoiture.get(self.motorisation).get('puissanceElectrique')}
            self.ess1 = {'Nom' : "ReservoirEssence"}
            self.ess2 = {'Nom' : "Batterie" , 'Capacite' : int(self.distQuot/25)+1, 'Pack' : False} #En considérant que 5Km ~= 1 kWh et que le freinage régénératif autour de 20% d'éco, soit 1/5 encore
        elif self.modele == 'PHEV' :
            ratio = self.puissance/110
            puissance1, puissance2 = dimensionnementPHEV(self.distQuot)
            self.moteur1 = {'Nom' : "MoteurThermique", 'Puissance' : puissance1*ratio}
            self.moteur2 = {'Nom' : "MoteurElectrique", 'Puissance' : self.puissance}
            self.ess1 = {'Nom' : "ReservoirEssence"}
            self.ess2 = {'Nom' : "Batterie", 'Capacite' : 1.5*self.distQuot/5, 'Pack':True}
        elif self.modele == "BEV" :
	        capacite = autonomie("BEV", self.drivingCycle, self.distQuot)*0.2
	        self.moteur1 = {'Nom' : "MoteurElectrique", 'Puissance' : self.puissance}
	        self.moteur2 = {'Nom' : "None"}
	        self.ess1 = {'Nom' : "Batterie", 'Capacite' : capacite, 'Pack' : True}
	        self.ess2 = {'Nom' : "None"}
        elif self.modele == "FCEV" :
            reservoir = autonomie("FCEV", self.drivingCycle, self.distQuot)/100
            self.moteur1 = {'Nom' : "MoteurElectrique", 'Puissance' : self.puissance }
            self.moteur2 = {'Nom' : "None" }
            self.ess1 = {'Nom' : "PileCombustible", 'Puissance' : self.puissance, 'Reservoir' : reservoir }
            self.ess2 = {'Nom' : "Batterie", 'Capacite' : dimensionnementFCEV(self.puissance, self.masseTotale), 'Pack' : True }
        
    def __update_masseTotale__(self) : 
        poidsESS = 0
        poidsInitial = DictionnaireVoiture.get(self.motorisation).get('masseTotale')
        if self.modele == 'ICEV':
            poidsESS -= masseMoteurThermique(DictionnaireVoiture.get(self.motorisation).get(' puissanceThermique'))
            poidsESS += masseMoteurThermique(self.moteur1.get('Puissance'))
        elif self.modele == 'HEV' or self.modele == 'PHEV':
            poidsESS -=  masseMoteurThermique(DictionnaireVoiture.get(self.motorisation).get(' puissanceThermique'))
            poidsESS += masseMoteurThermique(self.moteur1.get('Puissance'))
            poidsESS -= masseBatterie(DictionnaireVoiture.get(self.motorisation).get('batterie'))
            poidsESS += masseBatterie(self.ess2.get('Capacite'))
        elif self.modele == 'BEV':
            poidsESS -= masseBatterie(DictionnaireVoiture.get(self.motorisation).get('batterie'))
            poidsESS += masseBatterie(self.ess1.get('Capacite'))
        elif self.modele == 'FCEV':
            poidsESS -= masseBatterie(DictionnaireVoiture.get(self.motorisation).get('batterie'))
            poidsESS += masseBatterie(self.ess2.get('Capacite'))
            poidsESS -= DictionnaireVoiture.get(self.motorisation).get('reservoir')* 20
            poidsESS += self.ess1.get('Reservoir')*20 #20kg de réservoir pour 1 kg de H2
            poidsESS += massePAC(self.ess1.get('Puissance') - DictionnaireVoiture.get(self.motorisation).get(' puissanceThermique')) 
        self.masseTotale = poidsInitial - poidsESS 

    def __update_NRJ__(self):
        if self.modele == 'ICEV':
            self.consommationNRJ = consoEssence(self.dico, self.drivingCycle) # en L/100km
        elif self.modele == 'HEV' :
            self.consommationNRJ = consoHEV(self.dico, self.drivingCycle) # en L/100km
        elif self.modele == 'PHEV' :
            self.consommationNRJ = consoPHEV(self.dico, self.drivingCycle) # en [L/100km , kWh/100km] 
        elif self.modele == 'BEV' :
            self.consommationNRJ = consoEV(self.dico, self.drivingCycle) # en kWh/100km
        elif self.modele == 'FCEV' :
            self.consommationNRJ = consoFCEV(self.dico, self.drivingCycle) # en kgH2/100km
        elif self.modele == 'FCPHE' :
            self.consommationNRJ = consoFCPHE(self.dico, self.drivingCycle) # en [kgH2/100km, kWh/100km]
        
    #--------Partie Environnementale--------   
    
    def __update_emissionConception__(self) :
        data = 0
        if self.modele == 'ICEV':
            data += 14.6 #valeur émission de toute la conception à mettre en kgC02/100km
        elif self.modele == 'HEV':
            data += 12.18 #valeur émission de toute la conception sauf batterie
            data += 70 * self.ess2.get('Capacite')/1500
        elif self.modele == 'PHEV':
            data += 5.08 #valeur émission de toute la conception sauf batterie
            data += 70 * self.ess2.get('Capacite')/1500
        elif self.modele == 'BEV':
            data += 9.25 #valeur émission de toute la conception sauf batterie
            data += 70 * self.ess1.get('Capacite')/1500
        elif self.modele == 'FCEV':
            data += 26.92 #valeur émission de toute la conception sauf PAC et reservoir hydrogene
            data += 3.1 * self.ess1.get('Reservoir')/5 + 0.9
            data += 70 * self.ess2.get('Capacite')/1500
        self.emissionConception = data*self.kilometrage/100
 
    def __update_emissionUtilisation__(self) :   
        if self.modele == 'ICEV' or self.modele == 'HEV' :
            self.emissionUtilisation = self.kilometrage/100*self.consommationNRJ*emissionEssence
        elif self.modele == 'PHEV' :
            self.emissionUtilisation = self.kilometrage/100*(self.consommationNRJ[0]*emissionEssence+ self.consommationNRJ[1]*emissionElectricite)
        elif self.modele == 'BEV':
            self.emissionUtilisation = self.kilometrage/100*self.consommationNRJ*emissionElectricite
        elif self.modele == 'FCEV' :
            self.emissionUtilisation = self.kilometrage/100*self.consommationNRJ*emissionHydrogene
        elif self.modele == 'FCPHE' :
            self.emissionUtilisation = self.kilometrage/100*(self.consommationNRJ[0]*emissionHydrogene+ self.consommationNRJ[1]*emissionElectricite)

    def __update_emissionRecyclage__(self) :
        if self.moteur1.get('Nom') == "MoteurElectrique" :
            self.emissionRecyclage = - 2700  #kg de CO2eq
        elif self.moteur1.get('Nom') == "MoteurThermique" and self.moteur2.get('Nom') == "MoteurElectrique" :
            self.emissionRecyclage = - 3000
        elif self.moteur1.get('Nom') == "MoteurThermique" and self.moteur2.get('Nom') == "None" :
            self.emissionRecyclage = -3400

    #--------Partie Economique--------

    def __update_PrixAchat__(self):
        coutCarrosserie = DictionnaireVoiture.get(self.taille[0]+'-'+'ICEV').get('prixCarrosserie')
        coutESS1 = calculCoutESS(self.ess1)
        coutESS2 = calculCoutESS(self.ess2)
        coutMoteur1 = calculCoutMoteur(self.moteur1)
        coutMoteur2 = calculCoutMoteur(self.moteur2)
        coutAssurance = self.nombreAnnees*prixAssurance
        self.prixAchat = coutCarrosserie + coutESS1 + coutESS2 + coutMoteur1 + coutMoteur2 + coutAssurance

    def __update_coutBonusMalus__(self):
        """
        Renvoie la somme des différents malus (>0) et bonus (<0) à l'achat du véhicule:
        [malusCO2, malusAnnuel,  malusOccasion, primeConversion, bonusEcologique]
        Attributs nécessaires : prixAchat, emmissionCO2km, occasion, conversion, puissance, modele
        """
        prix = self.prixAchat
        emissionUnit = int(self.emissionUtilisation*1000/self.kilometrage)
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
            malusAnnuel = 160*self.nombreAnnees

        # Calcul du malus d'occasion
        malusOccasion = 0
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
            primeConversion = -2000 #euros

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
            if emissionUnit <50 : 
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

    def __update_coutUtilisation__(self):
        if self.modele == 'ICEV' or self.modele == 'HEV' :
            self.coutUtilisation = self.kilometrage/100*self.consommationNRJ*prixEssence
        elif self.modele == 'PHEV' :
            self.coutUtilisation = self.kilometrage/100*(self.consommationNRJ[0]*prixEssence+ self.consommationNRJ[1]*self.prixPompeElec)
        elif self.modele == 'BEV':
            self.coutUtilisation = self.kilometrage/100*self.consommationNRJ*self.prixPompeElec
        elif self.modele == 'FCEV' :
            self.coutUtilisation = self.kilometrage/100*self.consommationNRJ*prixPompeHydro
        elif self.modele == 'FCPHE' :
            self.coutUtilisation = self.kilometrage/100*(self.consommationNRJ[0]*prixPompeHydro+ self.consommationNRJ[1]*self.prixPompeElec)

    def __update_TCO__(self) :
        self.TCO = int(self.prixAchat + self.coutBonusMalus + self.coutEntretienTotal + self.coutUtilisation)
        self.emissionTotale = int(self.emissionUtilisation + self.emissionConception + self.emissionRecyclage )

    #--------Partie Finale--------

    def __MAJ__(self):
        print('motorisation : ', self.motorisation)
        self.__update_automatique__()
        print('kilometrage : ', self.kilometrage)
        print('masse totale : ', self.masseTotale)
        print('coefficient de trainee : ', self.coefficientTrainee)
        self.__update_dico__()
        print('dictionnaire : ' ,self.dico)
        self.__update_puissance__()
        print('puissance : ', self.puissance)
        self.__update_moteur_ess__()
        self.__update_masseTotale__()
        print('masse totale : ', self.masseTotale)
        self.__update_dico__()
        print('dico : ', self.dico)
        self.__update_NRJ__()
        print('Consommation energie : ', self.consommationNRJ)
        #Partie Ecologique
        self.__update_emissionConception__()
        print('Emission de conception : ', self.emissionConception)
        self.__update_emissionUtilisation__()
        print('Emission utilisation : ', self.emissionUtilisation)
        self.__update_emissionRecyclage__()
        print('Emission recyclage : ', self.emissionRecyclage)
        # Partie Economique
        self.__update_PrixAchat__()
        print('prix achat : ', self.prixAchat)
        self.__update_coutBonusMalus__()
        print('bonus et malus : ', self.coutBonusMalus)
        self.__update_coutEntretienTotal__()
        print('cout entretien total : ', self.coutEntretienTotal)
        self.__update_coutUtilisation__()
        print('Cout utilisation : ', self.coutUtilisation)
        self.__update_TCO__()
        print('TCO : ', self.TCO)
        print('Emission Totale : ', self.emissionTotale)
        

#==================================
#     Représentation graphique
#================================== 

def creationVoiture(Voitures) :
    Voitures.__MAJ__()
    Voiture = {'coutBonusMalus' : Voitures.coutBonusMalus, 'coutEntretien' : Voitures.coutEntretienTotal, 
    'coutUtilisation' : Voitures.coutUtilisation, 'prixAchat' : Voitures.prixAchat, 'TCO' : Voitures.TCO, 
    'emissionUtilisation' : Voitures.emissionUtilisation, 'emissionRecyclage' : Voitures.emissionRecyclage,
    'emissionConception' : Voitures.emissionConception, 'emissionTotale' : Voitures.emissionTotale}
    return Voiture

def creationListe(param):
    ListeVoiture = []
    taille = param.get('taille')
    if taille == 'petite':
        ListeModele = ['ICEV', 'HEV', 'BEV']
    elif taille == 'citadine':
        ListeModele = ['ICEV', 'HEV', 'BEV']
    elif taille == 'familiale':
        ListeModele = ['ICEV', 'PHEV', 'FCEV']
    elif taille == 'dcompacte':
        ListeModele = ['ICEV', 'HEV', 'PHEV', 'BEV', 'FCEV']
    elif taille == 'berline':
        ListeModele = ['ICEV', 'PHEV', 'BEV', 'FCEV'] 
    for i in ListeModele:
        param['modele']=i
        voiture = Voitures(param)
        ListeVoiture += [creationVoiture(voiture)]
    return ListeVoiture, ListeModele 

def update(L1, L2):
    l = len(L1)
    L3 = []
    for i in range(l):
        L3 += [ max(0,L1[i])+L2[i] ]
    return L3

def representation(ListeVoiture, ListeModele): 
    fig, ax1 = plt.subplots()
    def autolabel(rects, ax):
        """Affiche la valeur finale au dessus du graphique"""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
            
    ycoutBonus = [i.get('coutBonusMalus') for i in ListeVoiture]
    ycoutAchat = [i.get('prixAchat') for i in ListeVoiture]
    ycoutEntretien = [i.get('coutEntretien') for i in ListeVoiture]
    ycoutUtilisation = [i.get('coutUtilisation') for i in ListeVoiture]
    xemissionRecyclage = [i.get('emissionRecyclage') for i in ListeVoiture]
    xemissionConception = [i.get('emissionConception') for i in ListeVoiture]
    xemissionUtilisation = [i.get('emissionUtilisation') for i in ListeVoiture]
    TCO = [i.get('TCO') for i in ListeVoiture]
    emissionTotale = [i.get('emissionTotale') for i in ListeVoiture]

    Li1 = update(ycoutBonus, [0 for i in range(len(ListeVoiture))])
    Li2 = update(Li1, ycoutAchat)
    Li3 = update(Li2, ycoutEntretien)
    Lj1 = update(xemissionRecyclage, [0 for i in range(len(ListeVoiture))])
    Lj2 = update(Lj1,xemissionConception) 

    barWidth = 0.2
    barWidth2 = 0.1
    e = 0.75
    r = len(ListeVoiture) # Nombre de groupe de colonnes
    R = range(r)
    r1 = [x + barWidth for x in R] # placement des colonnes couts
    r2 = [x + 0.45 for x in r1] # placement des colonnes emission
    r0 = [x + 0.2 for x in r1] # placement des colonnes TCO final
    r3 = [x + 0.65 for x in r1] # placement des colonnes Emissions Totales
    r4 = [x + 0.075 for x in r0]
    """Gender = ["Bonus-Malus", "Cout à l'achat", "Cout d'entretien", "Cout d'utilisation",
              "Recyclage", "Emission de conception/entretien", "Emission à l'utilisation", "TCO", "Emissions Totales"]"""
    GenderCout = ["Bonus-Malus", "Cout à l'achat", "Cout d'entretien", "Cout d'utilisation","TCO"]
    GenderCO2 = ["Recyclage", "Emission de conception/entretien", "Emission à l'utilisation", "Emissions Totales"]

    plt.axis([0, r, -10000, max(TCO)+10000])     
    plt.bar(r1, ycoutBonus, width = barWidth, color = 'lime', edgecolor ='black', linewidth = e)
    plt.bar(r1, ycoutAchat, width = barWidth, color = 'yellow', edgecolor ='black', linewidth = e, bottom=Li1)
    plt.bar(r1, ycoutEntretien, width = barWidth, color = 'blue', edgecolor ='black', tick_label = 'Entretien',linewidth = e, bottom=Li2)
    plt.bar(r1, ycoutUtilisation, width = barWidth, color = 'red', edgecolor ='black', tick_label = 'Utilisation',linewidth = e, bottom=Li3)
    tco = plt.bar(r0, TCO, width = barWidth2, color = 'navy', edgecolor = 'black',linewidth = e, hatch = '/')
    autolabel(tco, ax1)
    plt.legend(GenderCout, loc = 'upper left', prop = {'size' : 7}, ncol = 3)
    plt.ylabel('TCO (€)', fontsize = 15)
    plt.gca().yaxis.set_tick_params(labelsize = 7)
    
    ax2 = plt.gca().twinx()
    plt.axis([0, r, -5000, max(emissionTotale)+10000])
    plt.bar(r2, xemissionRecyclage, width = barWidth, color = 'whitesmoke', edgecolor = 'black', linewidth = e)
    plt.bar(r2, xemissionConception, width = barWidth, color = 'silver', edgecolor = 'black', linewidth = e, bottom = Lj1)
    plt.bar(r2, xemissionUtilisation, width = barWidth, color = 'gray', edgecolor = 'black', linewidth = e, bottom = Lj2)
    et = plt.bar(r3, emissionTotale, width = barWidth2, color = 'darkgray', edgecolor = 'black', linewidth = e, hatch = '/')
    autolabel(et, ax2)
    plt.legend(GenderCO2, loc = 'upper right', prop = {'size' : 7}, ncol = 2)
    plt.ylabel('Emission de C02 (kg)', fontsize = 15)
    plt.gca().yaxis.set_tick_params(labelsize = 7)
    
    plt.xlabel('Modèles de voiture', fontsize = 15)    
    plt.title('TCO et émissions de CO2 sur la vie des véhicules', fontsize = 18)
    plt.xticks(r4, ListeModele)
    plt.tick_params(axis = 'x', length = 3)
    fig.tight_layout()
    plt.show()

def TestFinal(param):
    ListeVoiture, ListeModele = creationListe(param)
    representation(ListeVoiture, ListeModele)


#===============
#     Tests
#===============

DrivingCycle = rural           # variable parmi urbain, periurbain, autoroute, rural (sans guillemets !)
Conversion = False                   # boolean : True si conversion thermique à électrique/hybride, False sinon
Occasion = False                    # boolean : True si achat véhicule d'occasion, False sinon                   
DistanceQuotienne = 60              # km pour faire l'aller retour boulot-maison
Frequence = 5                       # Fréquence à la semaine : nombre de journées
Taille = 'berline'                   # Taille du véhicule, parmi {'petite', 'berline', 'citadine', 'dcompacte', 'familiale'} (le d devant compacte est voulu, pour avoir un indice différent)
parametre = {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
TestFinal(parametre)



