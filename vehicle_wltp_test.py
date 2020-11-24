import numpy as np 
from drivetrain_fast import * 
import matplotlib.pyplot as plt
from scipy import integrate 

params = {}

# Vehicle parameters 
params['m'] = 1500 				# Vehicle empty mass 
params['Cd'] = 0.33				# Drag coefficient []
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
wltp = DrivingCycle('wltp_classe_3.csv')
t,v,a = wltp.tva() 

# No road grade 
theta = np.zeros(t.shape)

wem, Tem, Ftrac, Pel = vehicle.apply_acceleration_cycle(t, a, theta=0, v0=0, gear=0, params={})

plt.plot(t, Tem * wem / 1000)
plt.plot(t, Pel / 1000)
plt.show()

from scipy import integrate

Eel = integrate.cumtrapz(Pel/(1000*3600), t, initial=0)
plt.figure(2)
plt.plot(t,Eel)
plt.show()
