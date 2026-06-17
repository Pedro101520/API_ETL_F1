import requests
from datetime import datetime
import json
from google.cloud import storage
from google.oauth2 import service_account

ano_atual = datetime.now().year

class Campeonato():
    def tabela_campeonato(self):
        tabela_camp = {
            "tabela_pilotos": [],
            "tabela_equipes": []
        }

        try:
            acesso = requests.get(f"https://api.jolpi.ca/ergast/f1/{ano_atual}/driverstandings/").json()
            info = acesso["MRData"]["StandingsTable"]["StandingsLists"][0]

            acesso_equipe = requests.get(f"https://api.jolpi.ca/ergast/f1/{ano_atual}/constructorstandings/").json()
            info_equipe = acesso_equipe["MRData"]["StandingsTable"]["StandingsLists"][0]
        except Exception as e:
            raise Exception(f"erro: {e}")

        for i in info["DriverStandings"]:  
            tabela_camp["tabela_pilotos"].append({
                "nome": f'{i["Driver"]["givenName"]} {i["Driver"]["familyName"]}',
                "equipe": i["Constructors"][0]["name"],
                "pais": i["Driver"]["nationality"],
                "vitorias": i["wins"],
                "pontos": i["points"]
            })
        
        for j in info_equipe["ConstructorStandings"]:
            tabela_camp["tabela_equipes"].append({
                "nome": j["Constructor"]["name"],
                "pais": j["Constructor"]["nationality"],
                "vitorias": j["wins"],
                "pontos": j["points"]
            })

        return tabela_camp


    def salva_gcs(self):
        client = client = storage.Client()
        bucket = client.bucket("f1-dashboard-pilotos")
        blob = bucket.blob("f1_campeonato.json")

        blob.upload_from_string(
            json.dumps(self.tabela_campeonato(), ensure_ascii=False, indent=2),
            content_type="application/json"
        )