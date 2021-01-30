"""fichier du coeur du module"""

import requests
import json
import pandas as pd
import path as path
import ast


class VieScolaire:
    """classe du client la vie scolaire"""

    def __init__(self, save_id=True, display_logs=True, ignore_errors=False):
        """save_id : bool -> sauvegarde les identifiants s'ils fonctionnent
        display_logs : bool -> affiche les logs du client
        ignore_errors : bool -> ne lève pas d'erreurs"""

        # session
        self.requests_session = requests.session()

        # login
        self.__registered = False
        self.save_id = save_id

        # logs
        self.logs = []
        self.display_logs = display_logs
        self.ignore_errors = ignore_errors

        self.log("Création du client")

    @property
    def registered(self):
        return self.registered

    @registered.getter
    def registered(self):
        return self.__registered

    @registered.setter
    def registered(self, value):
        raise AttributeError("attribute 'registered' is not writable")

    # requête
    def request(self, new_path='', data=None, get=True):
        """execute une requête
        new_path : string -> chemin d'accès de la requête
        data : json -> les identifiants sous forme {"login": "[identifiant]", "password": "[mot de passe]"}
        get : bool -> requête de type get sinon post"""

        self.log(f"Envoie d'une requête à l'adresse {path.url + new_path}")

        if get:
            request = self.requests_session.get
        else:
            request = self.requests_session.post

        if type(data) is dict:
            data = json.dumps(data)

        response = request(
            url=path.url + new_path,
            data=data
        )

        if response.status_code == 200:
            self.log('Réponse de la requête réceptionnée')
        else:
            self.error(Exception, f"Requête non satisfaite, code d'erreur {response.status_code}")

        return response

    # log
    def log(self, log):
        """ajoute log aux logs et l'affiche si self.display est vérifié
        log : str -> la log"""

        self.logs.append(log)
        if self.display_logs:
            print(log)

    def error(self, error_type, message):
        self.log(message)
        if not self.ignore_errors:
            raise error_type(message)

    # connexion
    def connect(self, login=None, password=None, from_json=True, from_input=True, login_data=None):
        """s'identifie au site et renvoie True si la connexion a été faite avec succès
        from_json : bool -> essaie de charger les identifiants depuis un fichier login.json
        from_input : demande bool -> les informations qui manque dans l'invite de commande
        login : str -> identifiant
        password : str -> mot de passe
        login_data : json -> data"""

        if self.__registered:
            self.log('Le client est déjà connecté')
            return

        if from_json:
            """récupère les informations depuis le fichier json"""
            self.log('Récupération des identifiants à partir du fichier login.json')
            try:
                with open('login.json') as login_file:
                    login_data = json.load(login_file)
                self.log('Récupération des identifiants réussie')
            except (FileNotFoundError, json.decoder.JSONDecodeError):
                self.log('Impossible de récupérer les identifiants du fichier login.json')

        if login_data is None and from_input:
            self.log('Récupération des identifiants manquants')
            login_data = self.inp_pass(login=login, password=password)

        self.login(login_data)

    def login(self, login_data):
        """essaie de se connecter avec ces identifiants
        login_data : json -> data"""

        self.log('Connexion...')
        result = self.request(path.login, data=login_data)

        try:
            if json.loads(result.content.decode('utf-8'))['auth'] == 'ok':
                """vérifie la requête"""
                self.__registered = True
                self.log('Connexion réussi')
                if self.save_id:
                    with open('login.json', 'w') as login_file:
                        login_file.write(json.dumps(login_data))
                        self.log('Sauvegarde des identifiants')
            else:
                self.error(ValueError, 'Identifiant ou mot de passe incorrect')

        except KeyError:
            self.error(SyntaxError, "Formatage incorrect de l'identifiant ou du mot de passe")

    # méthodes statiques
    @staticmethod
    def inp_pass(login=None, password=None):
        """complète si nécessaire les informations de connexion depuis l'invite de commande"""

        if login is None:
            login = input('Identifiant :')
        if password is None:
            password = input('Mot de passe :')
        return {'login': login, 'password': password}

    @staticmethod
    def save_as(file, name):
        """sauvegarde un fichier avec son nom
        file : objet à sauvegarder
        name : nom à sauvegarder"""

        if type(file) is list:
            for n, element in enumerate(file):
                VieScolaire.save_as(element, f'{name} {n + 1}')
        elif type(file) is pd.DataFrame:
            file.to_csv(f'{name}.csv')
        elif type(file) is dict:
            file = json.dumps(file)
            VieScolaire.save_as(file, name + '.json')
        else:
            if type(file) is bytes:
                file = file.convert('utf-8')
            with open(name, 'w') as out:
                out.write(str(file))

    @staticmethod
    def convert(element, encoding='utf-8'):
        """converti le type de l'élément"""

        if type(element) is requests.Response:
            return VieScolaire.convert(element.content)
        if type(element) is bytes:
            return VieScolaire.convert(element.decode(encoding))
        if type(element) is str:
            if element.startswith('{'):
                return json.loads(element)
        return element

    @staticmethod
    def to_df(element, check_float=True):
        """converti une réponse en Dataframe
        check_float : bool -> modifie les ',' en '.'"""

        element = VieScolaire.convert(element)

        if check_float:
            element = element.replace(',', '.')
        tables = pd.read_html(element)
        return tables

    # méthodes effectives
    def nom_etab(self):
        """renvoie le nom de l'établissement"""

        request = self.request(path.nom_etab)
        return self.convert(request)["etabName"]

    def notifications(self):
        """renvoie les notifications"""

        request = self.request(path.notifications)
        return ast.literal_eval(self.convert(request))

    def releve(self, save_csv=True, csv_name='Relevé'):
        """renvoie le relevé de notes sous forme de tableau
        save_csv : bool -> sauvegarde le tableau sous forme de csv
        csv_name : str -> nom du fichier csv"""

        notes_request = self.request(new_path=path.notes)
        tables = self.to_df(notes_request)
        if save_csv:
            self.save_as(tables, csv_name)
        return tables

    def moyenne(self, save_csv=True, csv_name='Moyenne'):
        """renvoie la moyenne à chaque trimestre sous forme de tableau
        save_csv : bool -> sauvegarde le tableau sous forme de csv
        csv_name : str -> nom du fichier csv"""

        self.request(path.dossier, data={'fromMenu': True})
        moyenne_request = self.request(path.dossier_moyenne)
        tables = self.to_df(moyenne_request)
        if save_csv:
            self.save_as(tables, csv_name)
        return tables
