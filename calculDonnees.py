from scipy import integrate 

# Energie consommée par une voiture sur un cycle wltp1
Eel = integrate.cumtrapz(Pel/(1000*3600), t, initial=0)
plt.figure(2)
plt.plot(t,Eel)
plt.show()
