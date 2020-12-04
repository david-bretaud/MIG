from calculDonnees import * 

Conversion = False                   # boolean : True si conversion thermique à électrique/hybride, False sinon
Occasion = False                    # boolean : True si achat véhicule d'occasion, False sinon      
 
DrivingCycle = urbain           # variable parmi urbain, periurbain, autoroute, rural (sans guillemets !)              
DistanceQuotienne = 20   
Frequence = 5                    # Fréquence à la semaine : nombre de journées
Taille = 'citadine'  
modele_urbain_citadine = {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
Taille = 'petite'
modele_urbain_petite =  {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
Taille = 'dcompacte'
modele_urbain_compacte = {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
Taille  = 'familiale'
modele_urbain_familiale = {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
Taille  = 'berline'
modele_urbain_berline = {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
 
DrivingCycle = periurbain           # variable parmi urbain, periurbain, autoroute, rural (sans guillemets !)            
DistanceQuotienne = 50              # km pour faire l'aller retour boulot-maison
Frequence = 6                      # Fréquence à la semaine : nombre de journées
Taille = 'citadine'  
modele_periurbain_citadine =  {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
Taille = 'petite'
modele_periurbain_petite =  {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
Taille = 'berline'
modele_periurbain_berline = {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
Taille = 'dcompacte'
modele_periurbain_compacte = {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
 
DrivingCycle = rural           # variable parmi urbain, periurbain, autoroute, rural (sans guillemets !)            
DistanceQuotienne = 110   
Frequence = 5                    # Fréquence à la semaine : nombre de journées
Taille = 'familiale'  
modele_rural_familiale =  {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
Taille = 'berline'
modele_rural_berline =  {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
Taille = 'dcompacte'
modele_rural_compacte =  {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
 
DrivingCycle = autoroute           # variable parmi urbain, periurbain, autoroute, rural (sans guillemets !)       
DistanceQuotienne = 250   
Frequence = 3                    # Fréquence à la semaine : nombre de journées
Taille = 'berline'  
modele_autoroute_berline = {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
Taille = 'familiale'
modele_autoroute_familiale = {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
Taille = 'dcompacte'
modele_autoroute_compacte =  {'drivingCycle' : DrivingCycle, 'conversion' : Conversion, 'occasion' : Occasion, 'distQuot' : DistanceQuotienne , 'frequence' : Frequence, 'taille' : Taille}
 
TestFinal(modele_periurbain_compacte)