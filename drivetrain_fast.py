import numpy as np 
import control as ctrl 
import matplotlib.pyplot as plt
from scipy import integrate 

"""
TODO 
- Implement regenerative braking
"""
GRAVITY = 9.81 # Gravity acceleration [m/s2]
AIR_DENSITY_25C_ONE_ATM = 1.1839 # Air density at 25 Celsius and 101325 Pa

class DrivingCycle: 
	def __init__(self, filename, N=-1):
		dc = np.genfromtxt(filename, delimiter = ",", skip_header = 2) 
		self.dc = dc[:N,:]
		self.t = dc[:N,0]
		self.v = dc[:N,1]
		self.a = dc[:N,2]

	def plot(self): 
		fig, ax = plt.subplots(2,1, sharex=True)
		ax[0].plot(self.t, self.v) 
		ax[1].plot(self.t, self.a) 

		ax[1].set_xlabel("Time (s)")
		ax[1].set_ylabel("Acceleration (m/s$^2$)")
		ax[0].set_ylabel("Speed (m/s)")

	def tva(self): 
		return [self.dc[:,i] for i in range(3)]

class Battery(ctrl.NonlinearIOSystem): 
	def __init__(self, params = {}):
		self.effc = params.get('effc', 0.98) # Coulombic efficiency 
		self.Ah = params.get('Ah', 120.)
		self.Voc = params.get('Voc', 420)
		self.Rint = params.get('Rint', 0.08)


	def update_charge(self, t, x, u, params = {}): 
		Ibat = u[0] # Battery current [A]
		return -Ibat * self.effc / (self.Ah * 3600)

	def output_battery(self, t, x, u, params = {}): 
		Ibat = u[0] # Battery current [A]
		SOC = x[0]
		Vbat = self.Voc - self.Rint * Ibat
		return [Vbat, SOC]

# class buckDCDC(ctrl.NonlinearIOSystem): 
# 	def __init__(self, params = {}):
# 		self.L = params.get('L', 0.98)
# 		self.T = 1/params.get('f', 52000.)
# 		self.eff = 0.95
# 		'''Define vehicle system''' 
# 		ctrl.NonlinearIOSystem.__init__(self,updfcn=self.update_buck, outfcn=self.output_buck, 
# 			inputs=['Vin','D','Iout'], outputs=['Vout', 'Iin'], states=['alpha'], name='buck')

# 	def update_buck(self, t, x, u, params={}): 

# 		return - 0.01 * x[0] + u[1] 

# 	def output_buck(self, t, x, u, params={}):
# 		Vin = u[0]
# 		D = u[1] + x[0]
# 		Iout = u[2]

# 		Io = Iout* self.L / self.T / Vin * Iout 
# 		Vo = max(D, 1 / (2 * self.L * Io / D ** 2 / Vin /self.T + 1))
		
# 		Vout = Vo * Vin 
# 		Iin =  self.eff * Vout * Iout / Vin  
# 		return Vout, Iin

# class DCElectricMotor():
# 	def __init__(self, params = {}):
# 		"""Initialize the DCElectricMotor instance."""
# 		self.R = params.get('Rem', 0.08)		# Resistance [Ohm]
# 		self.L = params.get('Lem', 0.001)		# Inductance [H]
# 		self.kV = params.get('kV', 0.0168)		# Voltage constant [V.s/rad]
# 		self.kT = params.get('kT', 0.0168)		# Torque constant [Nm/A]
# 		self.J = params.get('Jem', 0.0015) 	# Inertia moment [kg.m2]
# 		self.b = params.get('bem', 0.001) 		# Damping coefficient [N.s]
		
# 		A = np.matrix([[-self.R/self.L]])
# 		B = np.matrix([[1/self.L, -self.kV/self.L]])
# 		C = np.matrix([[1], [self.kT]])
# 		D = np.matrix([[0, 0], [0, -self.b]])

# 		self.ss = ctrl.StateSpace(A, B, C, D)
# 		self.iosys = ctrl.LinearIOSystem(self.ss, 
# 			inputs=['Vem','wem'], 
# 			outputs=['Iem', 'Tem'], 
# 			states=['Iem'], name='dcem')
# 		self.iosys.name = 'motor'

class ElectricDrive():
	def __init__(self, params = {}):
		"""Initialize the DCElectricMotor instance."""
		self.J = params.get('Jem', 0.0001) 			# Inertia moment [kg.m2]
		self.Tmax = params.get('Tmax', 50) 			# Max torque [N.m]
		self.Pmax = params.get('Pmax', 12e3)		# Max power [W]
		self.effmotor = params.get('effEDm', 0.9)	# Electric drive efficiency in motor mode []
		self.effgen = params.get('effEDg', 0.75)	# Electric drive efficiency in generator mode []

	def maximal_torque(self, wem):
		"""Return the maximal torque the motor can provide for a given angular speed.""" 
		maxTorque = self.Tmax
		maxPowerTorque = self.Pmax / np.maximum(wem, 1e-6)
		return np.minimum(maxTorque, maxPowerTorque)

	def efficiency(self, T, w): 
		"""Return the electric drive efficiency map."""
		# TODO: implement 2D interpolation 
		signP = np.sign(T * w)
		return 1/self.effmotor * np.maximum(signP, 0) - self.effgen * np.minimum(signP, 0)
		
	def input_power(self, T, w): 
		"""Return the electric drive input electric power."""
		return T * w * self.efficiency(T, w)

class Vehicle:
	def __init__(self, params = {}):
		"""Initialize Vehicle instance.""" 
		self.m = params.get('m', 115.)  
		self.Cd = params.get('Cd', 0.3)
		self.Af = params.get('Af', 0.3)
		self.AfCd = params.get('AfCd', self.Af * self.Cd) 

		self.Fbrkmax = params.get('Fbrkmax', 1500)
		self.motor = params.get('motor', ElectricDrive(params))
		self.transmission = params.get('motor', Transmission(params))
		self.wheels = params.get('wheels', Wheels(params))
		self.driver = params.get('driver', Driver(params))
		self.battery = params.get('battery', Battery(params))

	def force_break(self, y, v, gear=0):
		"""Compute the breaking force, split between mechanical and regenerative breaking."""
		if y > 0: 
			return 0, 0, 0
		else: 
			Faxl, Taxl, waxl = self.axl_force_torque_speed(self.motor.Tmax, v)
			maxMotorForce = Faxl # Maximum regeneration force at motor's Tmax. This is needed to define the motor signal yreg. 

			wmotor = self.transmission.input_angular_speed(waxl)
			maxRegTorqueMotor = self.motor.maximal_torque(wmotor)
			Faxl, Taxl, waxl = self.axl_force_torque_speed(maxRegTorqueMotor, v)
			maxRegForce = Faxl # Maximum regeneration force at a given rotation speed 

			maxBrkForce = self.Fbrkmax # Maximum break force
			
			Fbrk = -y * maxBrkForce 

			Freg = min(maxRegForce, Fbrk) # Ingenuous approach where we will use as much regeneration as possible.
			Fmech = Fbrk - Freg # Mechanical break will supply the missing breaking force. 
			
			yreg = Freg/maxMotorForce # Input signal to the motor. 

			return Fbrk, Fmech, yreg 

	def force_aerodynamic_drag(self, v, wind=0, Tamb=20, pamb=1013):
		"""Return the aerodynamic drag force."""
		rho = AIR_DENSITY_25C_ONE_ATM * (Tamb + 273.15) / 298.15 * 1013.25 / pamb 
		vrel = v + wind
		return 0.5 * rho * self.AfCd * vrel * np.abs(vrel)

	def force_rolling_friction(self, v, theta=0):
		"""Return the rolling friction force."""
		Fn = self.m * GRAVITY * np.cos(theta)
		return self.wheels.rolling_resistance(Fn, v)

	def force_gravity(self, theta=0): 
		"""Return the gravity body force"""
		return self.m * GRAVITY * np.sin(theta)

	def inst_power(self, v, Tmotor, Fbrk, theta=0, wind=0, Tamb=20, pamb=1013):
		Fg = self.force_gravity(theta)
		Fr = self.force_rolling_friction(v, theta)
		Fd = self.force_aerodynamic_drag(v, wind, Tamb, pamb)

		Faxl, Taxl, waxl = self.axl_force_torque_speed(Tmotor, v)
		Paxl, Pg, Pr, Pd, Pbrk = [F * v for F in [Faxl, Fg, Fr, Fd, Fbrk]]

		return Paxl, Pg, Pr, Pd, Pbrk

	def axl_force_torque_speed(self, Tmotor, v): 
		"""Return the axle force, torque and angular speed."""
		waxl = self.wheels.angular_speed(v)
		Taxl = self.transmission.output_torque(Tmotor, waxl) 
		Faxl = self.wheels.torque_to_force(Taxl) 
		return Faxl, Taxl, waxl

	def apply_acceleration_cycle(self, t, a, theta=0, v0=0, gear=0, params={}): 
		Tamb = params.get('Tamb', 20)	# Ambient temperature [Celsius]
		pamb = params.get('pamb', 1013)	# Ambient pressure [hPa]
		wind = params.get('wind', 0)	# Head wind [m/s]

		# Calculate position and speed from acceleration 
		v = integrate.cumtrapz(a, t, initial=v0)
		x = integrate.cumtrapz(v, t, initial=0)

		# Calculate other forces
		Fg = self.force_gravity(theta)
		Fr = self.force_rolling_friction(v, theta)
		Fd = self.force_aerodynamic_drag(v, wind, Tamb, pamb)

		# Vehicle acceleration 
		Jaxl = self.transmission.axl_inertia(self.motor.J, self.wheels.J)
		Ftrac = Fg + Fr + Fd + (self.m + self.wheels.rotational_mass(Jaxl)) * a

		Ttrac = self.wheels.force_to_torque(Ftrac)
		w = self.wheels.angular_speed(v)

		Tmotor = self.transmission.input_torque(Ttrac, w, gear)
		wmotor = self.transmission.input_angular_speed(w, gear)

		# Electric power input to the electric drive 
		Pel = self.motor.input_power(Tmotor, wmotor)

		return wmotor, Tmotor, Ftrac, Pel

class Wheels:
	def __init__(self, params={}):
		"""Initialize the wheels instance."""
		self.r = params.get('rw', 0.3) 		# Wheel radius [m]
		self.J = params.get('Jw', .32) 		# Total wheels inertia [kg.m2]
		self.Cr = params.get('Cr', 0.01)	# Rolling resistance coefficient []

	def rotational_mass(self, J):
		"""Calculate the equivalent rotational mass for a given inertia."""
		return J / self.r ** 2
		
	def rolling_resistance(self, Fn, v):
		"""Calculate the total rolling resistance as a function of the normal force."""
		return Fn * self.Cr * np.sign(np.clip(v, -0.01, 0.01))

	def angular_speed(self, v):
		"""Calculate the angular speed of the wheels."""
		return v / self.r

	def torque_to_force(self, T): 
		"""Calculate the longitudinal force from the torque."""
		return T / self.r 

	def force_to_torque(self, F): 
		"""Calculate the torque from the longitudinal force."""
		return F * self.r 

class Transmission:
	"""
	For efficiency, see : https://x-engineer.org/automotive-engineering/drivetrain/transmissions/drivetrain-losses-efficiency/
	"""
	def __init__(self, params = {}):
		"""Initialize the Transmission instance."""
		self.N = params.get('transRatio', [20.4]) # Transmission ratios []
		self.b = params.get('b', 0.01)  # Friction coefficient []
		self.effTransmission = params.get('effTransmission',0.95)

	def friction_torque(self, wout):
		"""Calculate the friction force acting on the transmission bearings and gears."""
		return self.b * wout 

	def axl_inertia(self, Jin, Jout, gear=0): 
		"""Calculate the total axle moment of inertia."""
		return self.N[gear] ** 2 * Jin +  Jout 

	def input_angular_speed(self, wout, gear=0): 
		"""Calculate the output angular speed."""
		return wout * self.N[gear]

	def output_torque(self, Tin, wout, gear=0): 
		"""Calculate the output torque."""
		Tout =  Tin * self.N[gear] - self.friction_torque(wout)
		return Tout 

	def input_torque(self, Tout, wout, gear=0): 
		"""Calculate the input torque."""
		#Tin = Tout / self.effTransmission ** np.sign(wout) / self.N[gear] 	#autre modele pedro
		
		Tin =  Tout / self.N[gear] + self.friction_torque(wout)/self.N[gear]   #autre modèle choisie qui semble plus cohérent en valeur finale de conso
		return Tin

class Driver(): 
	# Code from https://python-control.readthedocs.io/en/0.8.3/cruise-control.html
	def __init__(self,params={}): 
		self.sys = ctrl.NonlinearIOSystem(updfcn=self.pi_update, 
			outfcn=self.pi_split_accel_brake, name='driver',
		    inputs = ['v', 'vref'], outputs = ['ya'], 
		    states = ['z'], params=params)
		self.sys.name = 'driver'

	def pi_update(self, t, x, u, params={}):
		ki = params.get('ki', 0.1)
		kaw = params.get('kaw', 0.5)  # anti-windup gain

		# Assign variables for inputs and states (for readability)
		v = u[0]                    # current velocity
		vref = u[1]                 # reference velocity
		z = x[0]                    # integrated error

		# Compute the nominal controller output (needed for anti-windup)
		u_a = self.pi_output(t, x, u, params)

		# Compute anti-windup compensation (scale by ki to account for structure)
		u_aw = kaw/ki * (np.clip(u_a, 0, 1) - u_a) if ki != 0 else 0

		# State is the integrated error, minus anti-windup compensation
		return (vref - v) + u_aw


	def pi_output(self, t, x, u, params={}):
		# Get the controller parameters that we need
		kp = params.get('kp', 0.5)
		ki = params.get('ki', 0.1)

		# Assign variables for inputs and states (for readability)
		v = u[0]                    # current velocity
		vref = u[1]                 # reference velocity
		z = x[0]                    # integrated error

		# PI controller
		return kp * (vref - v) + ki * z

	def pi_split_accel_brake(self, t, x, u, params={}):
		y = self.pi_output(t, x, u, params)
		return np.clip(y,-1,1)
