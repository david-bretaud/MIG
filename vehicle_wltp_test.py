import numpy as np 
from drivetrain_fast import * 
import matplotlib.pyplot as plt
from scipy import integrate 

params = {}

# Rendement chaîne énergie
effPAC = 0.5       #efficacité pile à combustible
effBattEV = 0.95      #efficacité batterie EV
# Vehicle parameters 
params['m'] = 1500 				# Vehicle empty mass 
params['Cd'] = 0.33				# Drag coefficient [] #0.29 toyota mirai
params['Af'] = 2.35  			# Frontal area [m2]
params['Fbrkmax'] = 15e3 		# Maximal break force [N]

# Wheel parameters 
params['rw'] = 0.3 				# Wheel radius [m]
params['Jw'] = .32				# Total wheels inertia [kg.m2]
params['Cr'] = 0.009			# Rolling resistance coefficient []

# Transmission parameters 
params['transRatio'] = [4.0] 	# Transmission ratios []
params['b'] = 1  			    # Friction coefficient []

# Electric drive parameters 
params['Jem'] = 0.0001 			# Inertia moment [kg.m2]
params['Tmax'] = 220			# Max torque [N.m]
params['Pmax'] = 80e3			# Max power [W]
params['effEDm'] = 0.90 		# Electric drive efficiency in motor mode []
params['effEDg'] = 0.75			# Electric drive efficiency in generator mode []
	
# Ambient parameters 
params['Tamb'] = 20				# Ambient temperature [Celsius]
params['pamb'] = 1013			# Ambient pressure [hPa]
params['wind'] = 0				# Head wind [m/s]


# Create vehicle
vehicle = Vehicle(params)

# Import WLTP driving cycle 
wltp = DrivingCycle("C:\\Users\\paul\\OneDrive\\Bureau\\cours\\MIG_info\\notebook\\MIG\\wltp_classe_3.csv")

t,v,a = wltp.tva() 

# No road grade 
theta = np.zeros(t.shape)

wem, Tem, Ftrac, Pel = vehicle.apply_acceleration_cycle(t, a, theta=0, v0=0, gear=0, params={})

from scipy import integrate 

Eel = integrate.cumtrapz(Pel/(1000*3600), t, initial=0)
distance = integrate.cumtrapz(v, t, initial=0)

plt.figure(1)
plt.plot(t,v,color='C1')
plt.xlabel('temps(s)')
plt.ylabel('vitesse voiture')

plt.figure(6)
plt.plot(t,effBattEV*100*Eel/(distance/1000), label = 'consommation (kWh/100km) sur le trajet choisie')
plt.xlabel('temps(s)')
plt.ylabel('consommation (kWh/100km)')  #pas vraiment la consommation instantanée
plt.legend()

plt.figure(2)
plt.plot(t,distance/1000)
plt.ylabel('distance parcourue(km)')
plt.xlabel('temps(s)')



plt.figure(3)
plt.plot(t, Tem * wem / 1000 , label = 'puissance mécanique moteur')
plt.plot(t, Pel / 1000 , label='puissance élec')
plt.legend()
plt.xlabel('temps(s)')
plt.ylabel('puissance électrique(kW)')






plt.figure(4)
plt.plot(t,Eel, label = 'énergie électrique consommée')
plt.xlabel('temps(s)')
plt.ylabel("énergie(kWh)")

plt.legend()



plt.figure(5)
plt.plot(t, Eel/(33.3*effPAC))  #conversion energie en kg de H2
plt.xlabel('temps(s)')
plt.ylabel('consommation hydrogène(kg)')
plt.ylim(0,1)


plt.show()