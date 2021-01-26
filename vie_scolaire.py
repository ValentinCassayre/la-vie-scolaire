"""fichier du coeur du module"""

import requests
import json
import pandas as pd
import path as path


class VieScolaire:
	"""classe du client la vie scolaire"""

	def __init__(self):
		self.requests_session = requests.session()
		self.registered = False
		self.save_id = True
		self.result = None
		self.out = None

	# requête
	def request(self, new_path='', data=None, get=True):
		"""execute une requête"""

		if get:
			request = self.requests_session.get
		else:
			request = self.requests_session.post
		response = request(
			url=path.url+new_path,
			data=data
		)
		return response

	# connexion
	def connect(self, login=None, password=None, from_json=True, from_input=True, login_data=None):
		"""s'identifie au site et renvoie True si la connexion a été faite avec succès"""

		if self.registered:
			"""client already connected"""
			return

		if from_json:
			"""récupère les informations depuis le fichier json"""
			try:
				with open('login.json') as login_file:
					login_data = json.load(login_file)
					login_data = json.dumps(login_data)
				self.save_id = True
			except FileNotFoundError:
				pass

		if login_data is None and from_input:
			login_data = self.inp_pass(login=login, password=password)

		self.login(login_data)

	def login(self, login_data):
		"""essaie de se connecter avec ces identifiants"""

		self.result = self.request(path.login, data=login_data)

		try:
			if json.loads(self.result.content.decode('utf-8'))['auth'] == 'ok':
				"""vérifie la requête"""
				self.registered = True
				if self.save_id:
					with open('login.json', 'w') as login_file:
						login_file.write(login_data)
			else:
				raise ValueError('invalid login or password')
		except KeyError:
			raise SyntaxError('invalid syntax of the login or password')

	# méthodes statiques
	@staticmethod
	def inp_pass(login=None, password=None):
		"""complète si nécessaire les informations de connexion depuis l'invite de commande"""

		if login is None:
			login = input('Identifiant :')
		if password is None:
			password = input('Mot de passe :')
		return json.dumps({'login': login, 'password': password})

	@staticmethod
	def save_as(file, name):
		"""sauvegarde un fichier avec son nom"""

		if type(file) is list:
			for n, element in enumerate(file):
				VieScolaire.save_as(element, f'{name} {n+1}')
		elif type(file) is pd.DataFrame:
			file.to_csv(f'{name}.csv')
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
			return VieScolaire.convert(element.convert(encoding))
		if type(element) is str:
			if element.startswith('{'):
				return json.loads(element)
		return element

	@staticmethod
	def to_df(element, check_float=True):
		"""converti une réponse en Dataframe"""

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

	def releve(self, save_csv=True):
		"""renvoie le relevé de notes sous forme de tableau"""

		notes_request = self.request(new_path=path.notes)
		tables = self.to_df(notes_request)
		if save_csv:
			self.save_as(tables, 'bulletin trimestre')
		return tables

	def moyenne(self, save_csv=True):
		"""renvoie la moyenne à chaque trimestre sous forme de tableau"""

		self.request(path.dossier, data=json.dumps({'fromMenu': True}))
		moyenne_request = self.request(path.dossier_moyenne)
		tables = self.to_df(moyenne_request)
		if save_csv:
			self.save_as(tables, 'moyennes trimestre')
		return tables
