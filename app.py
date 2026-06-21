from flask import Flask, jsonify
from models.calendario_externo import Calendario
from models.campeonato_externo import Campeonato
from models.equipes_externo import Equipes
from models.pilotos_externo import Pilotos
import time

app = Flask(__name__)

@app.route("/etl/formula1", methods=["POST"])
def pipeline():
    calendario = Calendario()
    campeonato = Campeonato()
    equipes = Equipes()
    pilotos = Pilotos()
    try:
        calendario.salva_gcs()
        time.sleep(60)
        campeonato.salva_gcs()
        time.sleep(60)
        equipes.salva_gcs()
        time.sleep(60)
        pilotos.salva_gcs()
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


    return jsonify({
        "message": "Arquivos atualizados com sucesso"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)