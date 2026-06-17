import requests
import os
import json

from models.gcs import Salvar
from datetime import datetime

class Calendario(Salvar):
    def rodadas(self):
        ano_atual = datetime.now().year
        try:
            calendario = requests.get(f"https://api.jolpi.ca/ergast/f1/{ano_atual}.json").json()
            acesso = calendario["MRData"]["RaceTable"]["Races"]
        except Exception as e:
            raise Exception(f"erro: {e}")

        total_rodadas = acesso[-1]["round"]
        
        data_atual = datetime.today()

        rodada_atual = None

        try:
            consulta = requests.get(f"https://api.jolpi.ca/ergast/f1/{ano_atual}/results/?limit=500").json()
            races = consulta["MRData"]["RaceTable"]["Races"]
        except Exception as e:
            raise Exception(f"erro: {e}")
        rodada = int(races[-1]["round"]) + 1
        rodada_atual = acesso[rodada]

        prox_corrida_calendario = []
        prox_grandes_premios = []
        prox_cidade = []
        lat = []
        long = []
        for i in acesso:
            data = datetime.strptime(i["date"], "%Y-%m-%d")

            if data.date() >= data_atual.date(): 
                prox_corrida_calendario.append(i["date"])
                prox_cidade.append(i["Circuit"]["Location"]["locality"])
                prox_grandes_premios.append(i["raceName"])
                lat.append(i["Circuit"]["Location"]["lat"])
                long.append(i["Circuit"]["Location"]["long"])
        
        infos_corridas = {
            "datas": prox_corrida_calendario,
            "premio": prox_grandes_premios,
            "cidade": prox_cidade,
            "lat": lat,
            "long": long,
            "total_rodadas": total_rodadas,
            "rodada_atual": rodada_atual
        }
        return infos_corridas

    def salva_gcs(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "clever-axe-457319-g8-833d2d4ab67f.json"

        client = super().get_storage_client()
        bucket = client.bucket("f1-dashboard-pilotos")
        blob = bucket.blob("f1_calendario.json")

        blob.upload_from_string(
            json.dumps(self.rodadas(), ensure_ascii=False, indent=2),
            content_type="application/json"
        )