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
				pass

		self.settings = configparser.ConfigParser()
		self.settings.read(self.path+"/settings.ini")
		if len(self.settings["tokens"]["aviasales"]) <= 0:
			print("Укажите в файле settings.ini корректный ключ для переменной aviasales")
			exit()
		self.token = self.settings["tokens"]["aviasales"]
		self.url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
		self.kwargs = {}
		self.kwargs.update({
			"header" : "Accept-Encoding: gzip, deflate",
			"token" : self.token,
			"currency" : "rub", #USD, EUR, RUB
			"locale" : "ru",
			"limit" : 10,
			"period_type" : "month"
		})
		self.kwargs.update(kwargs)

	#скачивание файлов данных если их нет в папке с проектом
	def read_data_files(self):
		if os.path.exists(self.path+"/airlines.json") == False:
			wget.download(f"http://api.travelpayouts.com/data/{self.lang}/airlines.json", self.path+"/airlines.json")
		if os.path.exists(self.path+"/airports.json") == False:
			wget.download(f"http://api.travelpayouts.com/data/{self.lang}/airports.json", self.path+"/airports.json")
		if os.path.exists(self.path+"/cities.json") == False:
			wget.download(f"http://api.travelpayouts.com/data/{self.lang}/cities.json", self.path+"/cities.json")

		data_files_dict = {}
		#получение объекта с данными о городах где есть аэропорты
		with open(self.path+"/cities.json", "r", encoding="utf-8") as file:
			json_data_cities = json.loads(file.read())
			data_files_dict.update({"city" : {}})
			for cities in json_data_cities:
				data_files_dict["city"].update({cities["code"] : cities})
				# print(cities)

		#получение объекта с данными о аэропортах
		with open(self.path+"/airports.json", "r", encoding="utf-8") as file:
			json_data_airports = json.loads(file.read())
			data_files_dict.update({"airport" : {}})
			for airports in json_data_airports:
				data_files_dict["airport"].update({airports["code"] : airports})
			# print(airports_dict)

		#получение объекта с данными о авиокомпаниях
		with open(self.path+"/airlines.json", "r", encoding="utf-8") as file:
			json_data_airlines = json.loads(file.read())
			data_files_dict.update({"airline" : {}})
			for airlines in json_data_airlines:
				data_files_dict["airline"].update({airlines["code"] : airlines})
			# print(airlines_dict["SU"])
		return(data_files_dict)

	#функция получения данных из API Aviasales.ru по заданным параметрам
	def get_ticket_data(self):
		tickets_data = requests.get(self.url, self.kwargs).json()
		if "error" not in  tickets_data:
			data_files = self.read_data_files()
			tickets_list = []
			for tickets in tickets_data["data"]: 
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
				tickets_list.append(tickets["origin_city"] + " - " + tickets["destination_city"] + " " + "<a href='https://www.aviasales.ru" + tickets["link"] + "'>" + str(tickets["price"])+ "</a>" + self.kwargs["currency"] + " " + "(" + tickets["departure_at_date"] + ")" + "\n") 
				tickets_string = " ".join(tickets_list)
			return(tickets_string)
		else:
			# print("Ваш токен для API Avasales указан не верно или не валидный, проверьте указанный токен в личном кабинете https://app.travelpayouts.com/all_tools")
			# print("status: ", tickets_data["status"]," ", tickets_data["error"])
			print(tickets_data)
		