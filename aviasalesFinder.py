from tarfile import ENCODING
import os
import requests
import json
from datetime import datetime
import configparser
import wget

class FindMeTickets():
	#setup settings
	def __init__(self, **kwargs):
		self.abs_file_path = os.path.abspath(__file__)
		self.path, self.filename = os.path.split(self.abs_file_path)
		if os.path.exists(self.path+"/settings.ini") == False:
			with open(self.path+"/settings.ini", "w", encoding="utf-8") as file:
				file.write("[tokens]\n#insert your aviasales partner token\naviasales =")
		self.settings = configparser.ConfigParser()
		self.settings.read(self.path+"/settings.ini")
		if len(self.settings["tokens"]["aviasales"]) <= 0:
			print("Insert the correct key for the aviasales variable in the settings.ini file")
			exit()
		self.token = self.settings["tokens"]["aviasales"]
		self.url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
		self.kwargs = {}
		self.kwargs.update({
			"header" : "Accept-Encoding: gzip, deflate",
			"token" : self.token,
			"currency" : "usd", #usd, eur, rub
			"locale" : "en", #for example: en, it, de. More examples https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
			"limit" : 10, # from 0 to 1000
			"period_type" : "month" #day, month, year
			#see more parameters https://support.travelpayouts.com/hc/en-us/articles/203956163
		})
		self.kwargs.update(kwargs)

	#downloading data files if they are not in the project folder
	def read_data_files(self):
		if os.path.exists(self.path+"/airlines.json") == False:
			wget.download(f"http://api.travelpayouts.com/data/{self.lang}/airlines.json", self.path+"/airlines.json")
		if os.path.exists(self.path+"/airports.json") == False:
			wget.download(f"http://api.travelpayouts.com/data/{self.lang}/airports.json", self.path+"/airports.json")
		if os.path.exists(self.path+"/cities.json") == False:
			wget.download(f"http://api.travelpayouts.com/data/{self.lang}/cities.json", self.path+"/cities.json")

		data_files_dict = {}
		#getting an object with data about cities where there are airports
		with open(self.path+"/cities.json", "r", encoding="utf-8") as file:
			json_data_cities = json.loads(file.read())
			data_files_dict.update({"city" : {}})
			for cities in json_data_cities:
				data_files_dict["city"].update({cities["code"] : cities})
				# print(cities)

		#getting an object with data about airports
		with open(self.path+"/airports.json", "r", encoding="utf-8") as file:
			json_data_airports = json.loads(file.read())
			data_files_dict.update({"airport" : {}})
			for airports in json_data_airports:
				data_files_dict["airport"].update({airports["code"] : airports})
			# print(airports_dict)

		#getting an object with data about airlines
		with open(self.path+"/airlines.json", "r", encoding="utf-8") as file:
			json_data_airlines = json.loads(file.read())
			data_files_dict.update({"airline" : {}})
			for airlines in json_data_airlines:
				data_files_dict["airline"].update({airlines["code"] : airlines})
			# print(airlines_dict["SU"])
		return(data_files_dict)

	#function for obtaining data from the Aviasales.ru API according to the specified parameters
	def get_ticket_data(self):
		tickets_data = requests.get(self.url, self.kwargs).json()
		if "error" not in  tickets_data:
			data_files = self.read_data_files()
			tickets_list = []
			for tickets in tickets_data["data"]: 
				tickets["link"] = "https://www.aviasales.ru" + tickets["link"]
				tickets["currency"] = self.kwargs["currency"]
				tickets["departure_at_date"] = datetime.strptime(tickets["departure_at"],"%Y-%m-%dT%H:%M:%S%z")
				tickets["departure_at_date"] = datetime.strftime(tickets["departure_at_date"], "%d.%m.%y")
				if tickets["origin_airport"] == data_files["airport"][tickets["origin_airport"]]["code"]:
					tickets["origin_airport"] = data_files["airport"][tickets["origin_airport"]]["name"]
				if tickets["destination_airport"] == data_files["airport"][tickets["destination_airport"]]["code"]:
					tickets["destination_airport"] = data_files["airport"][tickets["destination_airport"]]["name"]
				if tickets["origin"] == data_files["city"][tickets["origin"]]["code"]:
					tickets["origin_city"] = data_files["city"][tickets["origin"]]["cases"]["su"]
					tickets["origin_country_code"] = data_files["city"][tickets["origin"]]["country_code"]
				if tickets["destination"] == data_files["city"][tickets["destination"]]["code"]:
					tickets["destination_city"] = data_files["city"][tickets["destination"]]["cases"]["su"]
					tickets["destination_country_code"] = data_files["city"][tickets["destination"]]["country_code"]
				if tickets["airline"] == data_files["airline"][tickets["airline"]]["code"]:
					if data_files["airline"][tickets["airline"]]["name"] != None:
						tickets["airline"] = data_files["airline"][tickets["airline"]]["name"]
					else:
						tickets["airline"] = data_files["airline"][tickets["airline"]]["name_translations"]["en"]
				tickets_list.append(tickets)
			return(tickets_list)
		else:
			print(tickets_data)
		