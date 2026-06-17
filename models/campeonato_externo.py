import requests
from datetime import datetime
import json
import os

from models.gcs import Salvar

ano_atual = datetime.now().year

class Campeonato(Salvar):
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
                "nome": f"{i["Driver"]["givenName"]} {i["Driver"]["familyName"]}",
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
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "clever-axe-457319-g8-833d2d4ab67f.json"

        client = super().get_storage_client()
        bucket = client.bucket("f1-dashboard-pilotos")
        blob = bucket.blob("f1_campeonato.json")

        blob.upload_from_string(
            json.dumps(self.tabela_campeonato(), ensure_ascii=False, indent=2),
            content_type="application/json"
        )