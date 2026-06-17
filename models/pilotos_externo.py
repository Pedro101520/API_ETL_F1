import requests
from datetime import datetime
import json
from google.cloud import storage
from google.oauth2 import service_account
import time


ano_atual = datetime.now().year
hoje = datetime.now().date()

class Pilotos():
    def __init__(self):
        print("Inicio 2")
        self.nome_id = self.lista_id()
        self.estreia = self.inicio_f1()
        self.posicao = self.posicao_campeonato()
        self.pole = self.pole_position()
        self.largada = self.media_posicao()
        self.qtde_mundial = self.calculo_mundial()
        self.info_por_corrida = self.pontos_posicao()
        self.info_agrupada = self.agrupa()


    def lista_id(self):
        ids = []
        try:
            infos = requests.get(f"https://api.jolpi.ca/ergast/f1/{ano_atual}/drivers/").json()
        except Exception as e:
            raise Exception(f"erro: {e}")
        for i in infos["MRData"]["DriverTable"]["Drivers"]:
            ids.append(i["driverId"])
        return {
            "id": ids
        }

    def inicio_f1(self):
        time.sleep(20)
        estreia = {}
        for i in self.nome_id["id"]:
            try:
                acesso = requests.get(f"https://api.jolpi.ca/ergast/f1/drivers/{i}/results/?limit=10&offset=0").json()
            except Exception as e:
                raise Exception(f"erro: {e}")
            try:
                if i not in estreia:
                    estreia[i] = {
                        "ano": acesso["MRData"]["RaceTable"]["Races"][0]["season"]
                    }
            except:
                if i not in estreia:
                    continue
        return estreia

    def posicao_campeonato(self):
        time.sleep(20)
        posicao = {}
        for i in self.nome_id["id"]:
            try:
                acesso = requests.get(f"https://api.jolpi.ca/ergast/f1/{ano_atual}/drivers/{i}/driverstandings/").json()
            except Exception as e:
                raise Exception(f"erro: {e}")
            try:
                if i not in posicao:
                    posicao[i] = {
                        "posicao": acesso["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"][0]["position"],
                        "pontos": acesso["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"][0]["points"]
                    }
            except:
                if i not in posicao:
                    posicao[i] = {
                        "posicao": 0,
                        "pontos": 0
                    }
        return posicao

    def pole_position(self):
        time.sleep(20)
        pole = {}
        for i in self.nome_id["id"]:
            try:
                acesso = requests.get(f"https://api.jolpi.ca/ergast/f1/{ano_atual}/drivers/{i}/results/").json()
            except Exception as e:
                raise Exception(f"erro: {e}")
            if i not in pole:
                pole[i] = {
                    "qtde_pole_position": 0
                }
            
            acesso_info = acesso["MRData"]["RaceTable"]["Races"]

            for j in acesso_info:
                valor = int(j["Results"][0].get("grid", 0))
                if valor == 1:
                    pole[i]["qtde_pole_position"] += 1

        return pole

    def media_posicao(self):
        time.sleep(20)
        media = {}
        for i in self.nome_id["id"]:
            try:
                acesso = requests.get(f"https://api.jolpi.ca/ergast/f1/{ano_atual}/drivers/{i}/results/").json()
            except Exception as e:
                raise Exception(f"erro: {e}")
            if i not in media:
                media[i] = {
                    "media": "N/A"
                }
            
            grid = 0
            total_valido = 0
            for j in acesso["MRData"]["RaceTable"]["Races"]:
                grid_posicao = int(j["Results"][0]["grid"])
                if grid_posicao > 0:
                    grid += grid_posicao
                    total_valido += 1
            
            if total_valido > 0:
                media[i]["media"] = str(grid / total_valido)

        return media

    def calculo_mundial(self):
        time.sleep(20)
        mundiais = {}

        lista_estreia = []
        for i in self.nome_id["id"]:
            try:
                lista_estreia.append(self.estreia[i]["ano"])
            except:
                continue

        if 0 in lista_estreia:
            lista_estreia.remove(0)
        menor_ano = min(lista_estreia)

        for i in self.nome_id["id"]:
            if i not in mundiais:
                mundiais[i] = {
                    "qtde_mundial": 0
                }

        for i in range(int(menor_ano), int(ano_atual)):
            try:
                acesso = requests.get(f"https://api.jolpi.ca/ergast/f1/{i}/driverstandings/1.json").json()
            except Exception as e:
                raise Exception(f"erro: {e}")
            vencedor_mundial = acesso["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"][0]["Driver"]["driverId"]
            if vencedor_mundial in mundiais:
                mundiais[vencedor_mundial]["qtde_mundial"] += 1
        
        return mundiais

    def pontos_posicao(self):
        time.sleep(20)
        posicao_valor = []
        for i in self.nome_id["id"]:
            try:
                acesso = requests.get(f"https://api.jolpi.ca/ergast/f1/{ano_atual}/drivers/{i}/results/").json()
                acesso_sprint = requests.get(f"https://api.jolpi.ca/ergast/f1/{ano_atual}/drivers/{i}/sprint/").json()
            except Exception as e:
                raise Exception(f"erro: {e}")
            rodada = acesso["MRData"]["RaceTable"]["Races"]
            rodada_sprint = acesso_sprint["MRData"]["RaceTable"]["Races"]

            dicionario_sprint = {}
            for sprint in rodada_sprint:
                if sprint["round"] not in dicionario_sprint:
                    dicionario_sprint[sprint["round"]] = sprint["SprintResults"][0]["points"]

            for j in rodada:
                posicao_valor.append({
                    "id_piloto": j["Results"][0]["Driver"]["driverId"],
                    "gp": j["Circuit"]["circuitName"],
                    "round": j["round"],
                    "ponto_por_corrida": j["Results"][0]["points"],
                    "posicao": j["Results"][0]["positionText"],
                    "pontos_sprint": dicionario_sprint.get(j["round"], "0"),
                    "id_gp": j["raceName"],
                    "data": j["date"],
                    "circuito": j["Circuit"]["circuitId"],
                    "grid": j["Results"][0]["grid"],
                    "voltas": j["Results"][0]["laps"],
                    "status": j["Results"][0]["status"],
                    "volta_mais_rapida": j["Results"][0].get("FastestLap", {}).get("Time", {}).get("time", "")
                })
        return posicao_valor

    def agrupa(self):
        info_agrupada = {}
        for i in self.info_por_corrida:
            if i["id_piloto"] not in info_agrupada:
                info_agrupada[i["id_piloto"]] = {
                    "corridas": []
                }
            
            info_agrupada[i["id_piloto"]]["corridas"].append({
                "gp": i["gp"],
                "round": i["round"],
                "ponto_por_corrida": i["ponto_por_corrida"],
                "posicao": i["posicao"],
                "pontos_por_sprint": i["pontos_sprint"],
                "id_gp": i["id_gp"],
                "data": i["data"],
                "circuito": i["circuito"],
                "grid": i["grid"],
                "voltas": i["voltas"],
                "status": i["status"],
                "volta_mais_rapida": i["volta_mais_rapida"]
            })
        return info_agrupada

    def estatisticas(self):
        time.sleep(20)
        infos_pilotos = {}

        for i in self.nome_id["id"]:
            try:
                acesso = requests.get(f"https://api.jolpi.ca/ergast/f1/{ano_atual}/drivers/{i}/results/").json()
            except Exception as e:
                raise Exception(f"erro: {e}")
            aceso_info = acesso["MRData"]["RaceTable"]["Races"]
            for j in aceso_info:
                aniversario = datetime.strptime(j["Results"][0]["Driver"]["dateOfBirth"], "%Y-%m-%d").date()
                idade = hoje.year - aniversario.year
                if (hoje.month < aniversario.month) or (hoje.month == aniversario.month and aniversario.day >= hoje.day):
                    idade -= 1

                if i not in infos_pilotos:
                    infos_pilotos[i] = {
                        "nome": f'{j["Results"][0]["Driver"]["givenName"]}',
                        "sobrenome": f'{j["Results"][0]["Driver"]["familyName"]}',
                        "nacionalidade": j["Results"][0]["Driver"]["nationality"],
                        "idade": idade,
                        "estreia": self.estreia[i]["ano"],
                        "posicao": self.posicao[i]["posicao"],
                        "media_largada": self.largada[i]["media"],
                        "pontos": self.posicao[i]["pontos"],
                        "pole_position": self.pole[i]["qtde_pole_position"],
                        "sigla": j["Results"][0]["Driver"]["code"],
                        "numero": j["Results"][0]["number"],
                        "equipe": j["Results"][0]["Constructor"]["name"],
                        "vitorias": 0,
                        "podios": 0,
                        "qtde_mundial": self.qtde_mundial[i]["qtde_mundial"],
                        "melhor_resultado": int(j["Results"][0]["position"]),
                        "abandonos": 0,
                        "id_piloto": j["Results"][0]["Driver"]["driverId"],
                        "pontuacao_individual": self.info_agrupada[i]["corridas"]
                    }

                if int(j["Results"][0]["position"]) == 1:
                    infos_pilotos[i]["vitorias"] += 1
                
                if int(j["Results"][0]["position"]) <= 3:
                    infos_pilotos[i]["podios"] += 1
                
                if infos_pilotos[i]["melhor_resultado"] > int(j["Results"][0]["position"]):
                    infos_pilotos[i]["melhor_resultado"] = int(j["Results"][0]["position"])
                
                if j["Results"][0]["status"] == 'Retired' or j["Results"][0]["status"] == "Did not start":
                    infos_pilotos[i]["abandonos"] += 1
                    
        return infos_pilotos

    def salva_gcs(self):
        client = client = storage.Client()
        bucket = client.bucket("f1-dashboard-pilotos")
        blob = bucket.blob("f1_pilotos.json")

        blob.upload_from_string(
            json.dumps(self.estatisticas(), ensure_ascii=False, indent=2),
            content_type="application/json"
        )