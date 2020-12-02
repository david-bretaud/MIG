import numpy as np 
from drivetrain_fast import * 
import matplotlib.pyplot as plt
from scipy import integrate 

effPAC = 0.5          #efficacité pile à combustible
effBattEV = 0.9  
RFrein = 0.1

rural = '.\wltp_classe_3.csv'
urbain = '.\cycle_urbain_test_serre.csv'
periurbain = '.\cycle_periurbain_test.csv'
autoroute = '.\cycle_autoroute_serre.csv'
#à mettre dans le dictionnaire: masseTotale, CoeffTrainee

def puissance_necessaire(dico) :
    '''
    renvoie puissance minimale voiture cycle wltp
    '''
    cycle = DrivingCycle(rural)   
    t,v,a = cycle.tva()  #Import time, speed, accel
    theta = 0.*np.ones(t.shape)
    vehicle = Vehicle(dico)
    wem, Tem, Ftrac, Pel = vehicle.apply_acceleration_cycle(t, a,v,  theta,v0=0, gear=0 ) 
    Pel /= 1000 #Conversion to kW
    return max(Pel)
 

def consoEV(dico,cycle):
    '''
    renvoie conso voiture à batterie kWh/100km
    '''
    cycle = DrivingCycle(cycle)    
    t,v,a = cycle.tva()  #Import time, speed, accel
    theta = 0.*np.ones(t.shape)

    distance = integrate.cumtrapz(v, t, initial=0)
    vehicle = Vehicle(dico)
    wem, Tem, Ftrac, Pel = vehicle.apply_acceleration_cycle(t, a,v,  theta,v0=0, gear=0 ) 
    Pel /= 1000 #Conversion to kW
    distance /= 1000    #Conversion to km
    np.putmask(Pel, Pel<0, Pel*RFrein)  #Regenerative brake
    
    Eel = integrate.cumtrapz(Pel/(effBattEV*3600), t, initial=0)
    return (Eel[-4]/distance[-1])*100


def consoFCEV(dico, cycle) : 
    '''
    renvoie la conso en kgH2/100km
    '''
    cycle = DrivingCycle(cycle)
    t,v,a = cycle.tva()
    theta = 0.*np.ones(t.shape)
    
    distance = integrate.cumtrapz(v, t, initial=0)
    vehicle = Vehicle(dico)
    wem, Tem, Ftrac, Pel = vehicle.apply_acceleration_cycle(t, a,v,  theta,v0=0, gear=0) 
    Pel /= 1000 #Conversion to kW
    distance /= 1000    #Conversion to km
    np.putmask(Pel, Pel<0, Pel*RFrein)  #Regenerative brake
    
    Eel = integrate.cumtrapz(Pel/(effBattEV*3600), t, initial=0)
    return (Eel[-4]/distance[-1])*100/(effPAC*33.3)    #33.3kWh/kgH2


def consoEssence(dico, cycle):
    """
    Renvoie la consommation de carburant d'un ICEV-essence en L/100km en fonction de la masse du véhicule
    """
    x = dico.get('masseTotale')
    moyenne = (2*10**(-6)*x**2+0.0005*x + 2.8549)
    if cycle == urbain :
        return moyenne * 1.10
    elif cycle == autoroute : 
        return moyenne * 1.06
    elif cycle == periurbain :
        return moyenne
    elif cycle == rural :
        return moyenne * 0.9
    
 
def consoDiesel(dico, cycle):
    """
    Renvoie la consommation de carburant d'un ICEV-diesel en L/100km en fonction de la masse du véhicule
    """
    x = dico.get('masseTotale')
    moyenne = 2*10**(-6)*x**2-0.0008*x + 2.698
    if cycle == urbain :
        return moyenne * 1.10
    elif cycle == autoroute : 
        return moyenne * 1.06
    elif cycle == periurbain :
        return moyenne
    elif cycle == rural :
        return moyenne * 0.9
 
def consoHEV(dico, cycle):
    """
    Renvoie la consommation d'essence d'un HEV en L/100km en fonction de la masse du véhicule
    """
    x = dico.get('masseTotale')
    moyenne = 10**(-6)*x**2-0.0008*x + 2.7038
    if cycle == urbain :
        return moyenne * 1.10
    elif cycle == autoroute : 
        return moyenne * 1.06
    elif cycle == periurbain :
        return moyenne
    elif cycle == rural :
        return moyenne * 0.9
 
def consoPHEV(dico, cycle):
    """
    Renvoie la consommation d'essence d'un PHEV en L/100km en fonction de la masse du véhicule
    """
    x = dico.get('masseTotale')
    moyenne = 2.07 + (x-780)*0.82/1550
    if cycle == urbain :
        return moyenne * 1.10
    elif cycle == autoroute : 
        return moyenne * 1.06
    elif cycle == periurbain :
        return moyenne
    elif cycle == rural :
        return moyenne * 0.9

def consoPHEV(dico, cycle) :
    if cycle == urbain :
        A = 0.30
        B = 1 - A
    elif cycle == autoroute : 
        A = 0.95
        B = 1 - A
    elif cycle == periurbain :
        A = 0.5
        B = 1 - A
    elif cycle == rural :
        A = 0.7 
        B = 1 - A
    return [A*consoHEV(dico, cycle), B*consoEV(dico, cycle)]
   




