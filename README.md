# MIG ALEF

Les 4 fichiers .csv qui sont : 
  - cycle_autoroute_test_serre.csv
  - cycle_periurbain_test_serre.csv
  - cycle_urbain_test_serre.csv
  - wltp_classe_3.csv
représentent les 4 profils de vitesse / usages étudiés durant le MIG. 

Ces fichiers sont appelés dans le code python 'drivetrain_fast.py' qui représente la dynamique à l'utilisation d'une voiture
électrique pour mettre en évidence sa consommation.

Ensuite, le fichier python 'ConsoPuissance.py' détermine justement ces consommations d'énergie, pour le BEV et le FCEV. 
Nous y avons aussi introduit des calculs de consommation de véhicules HEV, PHEV, ICEV. 

Le fichier python 'calculDonnees.py' fait appel à 'ConsoPuissance.py' et au fichier 'base_voiture.csb' :
c'est le coeur du code, ordonnant toutes les informations que ce soit sur le prix ou les émissions carbones. 
Il représente l'outil de calcul de comparaison entre les différents modèles de véhicules. 

Le fichier 'Modelisations.py' fait appel à 'calculDonnees.py'. On y a simplement recensé différents dictionnaires, 
où un dictionnaire = 1 set de conditions initiales / valeurs d'entrées. 
On définit un dictionnaire d'input puis on le met en entrée de la fonction définie dans 'calculDonnees.py' TestFinal.
