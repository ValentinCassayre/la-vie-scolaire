"""exemple d'utilisation du client"""

from vie_scolaire import VieScolaire  # récupère le module

# note : tous les arguments des fonctions sont optionnels et sont juste affiché pour une meilleure compréhension

client = VieScolaire(save_id=True, display_logs=True)  # créer un client
# save_id : bool -> sauvegarde les identifiants s'ils fonctionnent
# display_logs : bool -> affiche les logs du client

client.connect(from_json=True, from_input=True)  # connecte le client
# from_json : bool -> essaie de charger les identifiants depuis un fichier login.json
# from_input : demande bool -> les informations qui manque dans l'invite de commande

client.releve(save_csv=True, csv_name='Relevé')  # relève les notes
# save_csv : bool -> sauvegarde le tableau sous forme de csv
# csv_name : str -> nom du fichier csv

client.moyenne(save_csv=True, csv_name='Moyenne')  # relève les moyennes
# save_csv : bool -> sauvegarde le tableau sous forme de csv
# csv_name : str -> nom du fichier csv

input()  # bloque l'invite de commandes
