#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 14:37:29 2020

@author: Raphael
"""

import numpy as np 
from drivetrain_fast import * 
import matplotlib.pyplot as plt
from scipy import integrate 
effPAC = 0.5          #efficacité pile à combustible
effBattEV = 0.9  
RFrein = 0.1

#à mettre dans le dictionnaire: masseTotale, CoeffTrainee



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
    return (Eel[-4]/distance[-1])*100,max(Pel)

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
    return (Eel[-4]/distance[-1])*100/(effPAC*33.3),max(Pel)    #33.3kWh/kgH2 

