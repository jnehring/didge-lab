from flask import Flask, Response, jsonify, request
import json
import pickle
import pandas as pd
import threading
import logging

from didgelab.calc.geo import Geo
from didgelab.app import get_app
from .stats import EvolutionStats
from .evolution_state import EvolutionState

app = Flask(__name__)

def load_test_data():
    folder = "../../../../evolutions/2023-07-02T23-00-16/checkpoint_final/"
    latest_geos = pickle.load(open(folder + "geos.bin", "rb"))
    logs = pd.read_csv(folder + "stats.csv")
    latest_logs = logs[-1:].to_json(orient="records")
    latest_logs = json.loads(latest_logs)[0]

def on_generation_finished(i_generation, population):
    population = population[0:min(len(population), 20)]
    latest_geos = [p.make_geo() for p in population]

def init():
    get_app().subscribe("generation_finished", on_generation_finished)

@app.route('/api/general_evolution_info', methods=['GET'])
def general_evolution_info():

    stats_service = get_app().get_service(EvolutionStats)
    loss_data = stats_service.get_data()
    latest_logs = {key: values[-1] for key, values in loss_data.items()}

    for key in list(loss_data.keys()):
        if key != "generation" and key[-4:] != "_min":
            del loss_data[key]
    result = {
        "general": latest_logs,
        "losses": loss_data
    }
    return jsonify(result)

@app.route('/api/get_mutant/<i_mutant>', methods=['GET'])
def get_mutant(i_mutant):

    evolution_state = get_app().get_service(EvolutionState)
    # logging.info(evolution_state)
    i_mutant = int(i_mutant)

    geo = evolution_state.get_geo(i_mutant)
    notes = geo.get_cadsd().get_notes()
    spektra = geo.get_cadsd().get_all_spektra_df()
    
    result = {
        "geo": geo.geo,
        "loss": evolution_state.get_loss(i_mutant),
        "notes": json.loads(notes.to_json(orient="records")),
        "population_size": evolution_state.get_population_size(),
        "spektra": {
            "freqs": list(spektra.freq),
            "impedance": list(spektra.impedance),
            "ground": list(spektra.ground),
            "overblow": list(spektra.overblow)
        }
    }

    return jsonify(result)

def start_webwerver_non_blocking():
    starter = lambda: app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    threading.Thread(target=starter).start()

