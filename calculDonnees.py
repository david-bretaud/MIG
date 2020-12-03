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
        return moteur.get('Puissance')*prixMoteurElectrique*alpha
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
        self.emissionConception = 0 # kgCO2/100km
        self.emissionEntretien = 0 # kgCO2/100km
        self.emissionUtilisation = 0 #Emission de kgCO2 sur 100 km à l'utilisation
        self.emissionRecyclage = 0 #kgCO2/100km
        
    #==============
    #   Méthodes 
    #==============
     
    def __update_automatique__(self):
        self.kilometrage = self.kilometrageAnnuel*self.nombreAnnees
        self.coefficientTrainee = DictionnaireVoiture.get(self.taille[0]+'-'+'ICEV').get('CoeffTrainee')
        self.masseTotale = DictionnaireVoiture.get(self.motorisation).get('masseTotale')

    def __update_dico__(self): 
        self.dico = {'masseTotale' : self.masseTotale, 'coeffTrainee' : self.coefficientTrainee}

    def __update_puissance__(self): 
        self.puissance = puissanceNecessaire(self.dico)

    def __update_moteur_ess__(self) : 
        if self.modele == 'ICEV' :
            moteur1 = {'Nom' : "MoteurThermique", 'Puissance': self.puissance }
            moteur2 = {'Nom' : "None"}
            ess1 = {'Nom' : "ReservoirEssence"}
            ess2 = {'Nom' : "None"}
        elif self.modele == 'HEV' :
            moteur1 = {'Nom' : "MoteurThermique", 'Puissance' : self.puissance}
            moteur2 = {'Nom' : "MoteurElectrique", 'Puissance' : DictionnaireVoiture.get(motorisation).get('puissanceElectrique')}
            ess1 = {'Nom' : "ReservoirEssence"}
            ess2 = {'Nom' : "Batterie" , 'Capacite' : int(self.distQuot/25)+1, 'Pack' : False} #En considérant que 5Km ~= 1 kWh et que le freinage régénératif autour de 20% d'éco, soit 1/5 encore
        elif self.modele == 'PHEV' :
            ratio = self.puissance/110
            puissance1, puissance2 = ratio*dimensionnementPHEV(self.distQuot)
            moteur1 = {'Nom' : "MoteurThermique", 'Puissance' : puissance1}
            moteur2 = {'Nom' : "MoteurElectrique", 'Puissance' : self.puissance}
            ess1 = {'Nom' : "ReservoirEssence"}
            ess2 = {'Nom' : "Batterie", 'Capacite' : 1.5*self.distQuot/5, 'Pack':True}
        elif self.modele == "BEV" :
	        capacite = autonomie("BEV", self.drivingCycle)*0.2
	        moteur1 = {'Nom' : "MoteurElectrique", 'Puissance' : self.puissance}
	        moteur2 = {'Nom' : "None"}
	        ess1 = {'Nom' : "Batterie", 'Capacite' : capacite, 'Pack' : True}
	        ess2 = {'Nom' : "None"}
        elif self.modele == "FCEV" :
            reservoir = autonomie("FCEV", self.drivingCycle)/100
            moteur1 = {'Nom' : "MoteurElectrique", 'Puissance' : self.puissance }
            moteur2 = {'Nom' : "None" }
            ess1 = {'Nom' : "PileCombustible", 'Puissance' : self.puissance, 'Reservoir' : reservoir }
            ess2 = {'Nom' : "Batterie", 'Capacite' : dimensionnementFCEV(self.puissance, self.masseTotale), 'Pack' : True }
        
    def __update_masseTotale__(self) : 
        poidsESS = 0
        poidsInitial = self.masseTotale
        for ess in [self.ess1, self.ess2]:
            if ess.get('Nom') == "Batterie" :
                poidsInitial -= masseBatterie(DictionnaireVoiture.get(self.motorisation).get('batterie'))
                poidsESS += masseBatterie(ess.get('Capacite'))
            elif ess.get('Nom') == "PileCombustible" :
                poidsInitial -= DictionnaireVoiture.get(self.motorisation).get('reservoir')* 20       #en mettant dans le dico la quanité d'hydrogène stockée dans réservoir
                poidsESS += ess.get('Reservoir')*20 #20kg de réservoir pour 1 kg de H2
                poidsESS += massePAC(ess.get('Puissance') - DictionnaireVoiture.get(self.motorisation).get('puissanceThermique'))       
        for mot in [self.moteur1, self.moteur2] :
            if mot.get('Nom') == "MoteurThermique" :
                poidsESS -= masseMoteurThermique(DictionnaireVoiture.get(self.motorisation).get('puissanceThermique'))
                poidsESS += masseMoteurThermique(mot.get('Puissance'))
            if mot.get('Nom') == "MoteurElectrique":
                poidsESS -= masseMoteurElectrique(DictionnaireVoiture.get(self.motorisation).get('puissanceElectrique'))
                poidsESS += masseMoteurElectrique(mot.get('Puissance'))
        self.masseTotale = poidsInitial + poidsESS

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
    """
    def __update_emissionConception__(self) : # A DEFINIR !
        if modele == 'ICEV':
            data =  
        elif modele == 'HEV':
            data =  
        elif modele == 'PHEV':
            data =  
        elif modele == 'BEV':
            data =  
        elif modele == 'FCEV':
            data = 4
        self.emissionEntretien = data*self.kilometrage/100

    def __update_emissionEntretien__(self): # A DEFINIR !
        if modele == 'ICEV':
            data =  
        elif modele == 'HEV':
            data =  
        elif modele == 'PHEV':
            data =  
        elif modele == 'BEV':
            data =  
        elif modele == 'FCEV':
            data = 0.85 
        self.emissionEntretien = data*self.kilometrage/100
    """
    def __update_emissionUtilisation__(self) :   
        if self.modele == 'ICEV' or self.modele == 'HEV' :
            self.coutUtilisation = self.kilometrage/100*self.consommationNRJ*emissionEssence
        elif self.modele == 'PHEV' :
            self.coutUtilisation = self.kilometrage/100*(self.consommationNRJ[0]*emissionEssence+ self.consommationNRJ[1]*emissionElectricite)
        elif self.modele == 'BEV':
            self.coutUtilisation = self.kilometrage/100*self.consommationNRJ*emissionElectricite
        elif self.modele == 'FCEV' :
            self.coutUtilisation = self.kilometrage/100*self.consommationNRJ*emissionHydrogene
        elif self.modele == 'FCPHE' :
            self.coutUtilisation = self.kilometrage/100*(self.consommationNRJ[0]*emissionHydrogene+ self.consommationNRJ[1]*emissionElectricite)

    def __update_emissionRecyclage__(self) :
        if self.moteur1.get('Nom') == "MoteurElectrique" :
            self.emissionRecyclage = - 2700  #kg de CO2eq
        elif self.moteur1.get('Nom') == "MoteurThermique" and self.moteur2.get('Nom') == "MoteurElectrique" :
            self.emissionRecyclage = - 3000
        elif self.moteur1.get('Nom') == "MoteurThermique" and self.moteur2.get('Nom') == "None" :
            self.emissionRecyclage = -3400

    #--------Partie Economique--------

    def __update_PrixAchat__(self):
        coutCarrosserie = DictionnaireVoiture.get(self.taille[0]+'-'+'ICEV').get('prix')
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
        self.TCO = self.prixAchat + self.coutBonusMalus + self.coutEntretienTotal + self.coutUtilisation
        self.emissionTotale = self.emissionUtilisation + self.emissionConception + self.emissionEntretien + self.emissionRecyclage #définir la bonne untié !

    #--------Partie Finale--------

    def __MAJ__(self):
        self.__update_automatique__()
        self.__update_dico__()
        self.__update_puissance__()
        self.__update_moteur_ess__()
        self.__update_masseTotale__()
        self.__update_dico__()
        self.__update_NRJ__()
        #Partie Ecologique
        self.__update_emissionConception__()
        self.__update_emissionEntretien__()
        self.__update_emissionUtilisation__()
        self.__update_emissionRecyclage__()
        # Partie Economique
        self.__update_PrixAchat__()
        self.__update_coutBonusMalus__()
        self.__update_coutEntretienTotal__()
        self.__update_coutUtilisation__()
        self.__update_TCO__()
        

#==================================
#     Représentation graphique
#================================== 

def creationVoiture(Voitures) :
    Voitures.__MAJ__
    Voiture = {'coutBonusMalus' : Voitures.coutBonusMalus, 'coutEntretien' : Voitures.coutEntretienTotal, 
    'coutUtilisation' : Voitures.coutUtilisation, 'prixAchat' : Voitures.prixAchat, 'TCO' : Voitures.TCO, 
    'emissionUtilisation' : Voitures.emissionUtilisation, 'emissionRecyclage' : Voitures.emissionRecyclage,
    'emissionConception' : Voitures.emissionConception, 'emissionEntretien' : Voitures.emissionEntretien,
    'emissionTotale' : Voitures.emissionTotale}
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
        ListeVoiture.append(creationVoiture)
    return ListeVoiture, ListeModele 

def update(L1, L2):
    l = len(L1)
    L3 = []
    for i in range(l):
        L3 += [max(0,L1[i])+L2[i]]
    return L3

def representation(ListeVoiture, ListeModele): 
    ycoutBonus = [i.get('coutBonus') for i in ListeVoiture]
    ycoutAchat = [i.get('coutAchat') for i in ListeVoiture]
    ycoutEntretien = [i.get('coutEntretien') for i in ListeVoiture]
    ycoutUtilisation = [i.get('coutUtilisation') for i in ListeVoiture]
    xemissionRecyclage = [i.get('emissionRecyclage') for i in ListeVoiture]
    xemissionConception = [i.get('emissionConception') for i in ListeVoiture]
    xemissionEntretien = [i.get('emissionEntretien') for i in ListeVoiture]
    xemissionUtilisation = [i.get('emissionUtilisation') for i in ListeVoiture]
    TCO = [i.get('TCO') for i in ListeVoiture]
    emissionTotale = [i.get('emissionTotale') for i in ListeVoiture]

    Li1 = update(ycoutBonus, [0 for i in range(len(ListeVoiture))])
    Li2 = update(Li1, ycoutAchat)
    Li3 = update(Li2, ycoutEntretien)
    Lj1 = update(xemissionRecyclage, [0 for i in range(len(ListeVoiture))])
    Lj2 = update(Lj1,xemissionConception)
    Lj3 = update(Lj2, xemissionEntretien) 

    barWidth = 0.3
    r = len(ListeVoiture) # Nombre de groupe de colonnes
    r1 = range(r) #placement des colonnes cout
    r2 = [x + 0.5 for x in r1] #placement des colonnes emission
    r0 = [x + 0.25 for x in r1] # placement des colonnes TCO final
    Gender = ["TCO final", "Bonus-Malus", "Cout à l'achat", "Cout d'entretien", "Cout d'utilisation", "Recyclage", "Emission de conception", "Emision d'entretien", "Emission à l'utilisation"]

    plt.bar(r0, TCO, width = 0.1, color = 'darkslategrey', edgecolor = 'black', hatch = '/')
    plt.bar(r1, ycoutBonus, width = barWidth, color = 'chartreuse', edgecolor ='black')
    plt.bar(r1, ycoutAchat, width = barWidth, color = 'dodgerblue', edgecolor ='black', bottom=Li1)
    plt.bar(r1, ycoutEntretien, width = barWidth, color = 'crimson', edgecolor ='black', tick_label = 'Entretien', bottom=Li2)
    plt.bar(r1, ycoutUtilisation, width = barWidth, color = 'gold', edgecolor ='black', tick_label = 'Utilisation', bottom=Li3)
    plt.bar(r2, xemissionRecyclage, width = barWidth, color = 'lightgrey', edgecolor = 'black')
    plt.bar(r2, xemissionConception, width = barWidth, color = 'lightgrey', edgecolor = 'black', bottom = Lj1)
    plt.bar(r2, xemissionEntretien, width = barWidth, color = 'grey', edgecolor = 'black', bottom = Lj2)
    plt.bar(r2, xemissionUtilisation, width = barWidth, color = 'dimgray', edgecolor = 'black', bottom = Lj3)

    plt.xlabel('Modèles de voiture', fontsize = 15)
    plt.ylabel('TCO (€) _ Emission de Co2 (kg)', fontsize = 12)
    plt.title('TCO et émission de CO2 pour chaque véhicule')
    plt.xticks(r1, ListeModele)
    plt.legend(Gender)
    plt.show()
    # Rajouter une deuxième légende pour le CO2

def TestFinal(param):
    ListeVoiture, ListeModele = creationListe(param)
    representation(ListeVoiture, ListeModele)


#===============
#     Tests
#===============
"""
DrivingCycle = urbain               # variable parmi urbain, periurbain, autoroute, rural (sans guillemets !)
Conversion = True                   # boolean : True si conversion thermique à électrique/hybride, False sinon
Occasion = False                    # boolean : True si achat véhicule d'occasion, False sinon                   
DistanceQuotienne = 40              # km pour faire l'aller retour boulot-maison
Frequence = 6                       # Fréquence à la semaine : nombre de journées
Taille = 'petite'                   # Taille du véhicule, parmi {'petite', 'berline', 'citadine', 'dcompacte', 'familiale'} (le d devant compacte est voulu, pour avoir un indice différent)
parametre = {'drivingCyle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
TestFinal(parametre)
"""


