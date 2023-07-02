from flask import Flask, Response, jsonify, request
import json

import sys
sys.path.append("..")
from cad.calc.geo import Geo

app = Flask(__name__)

@app.route('/api/acoustic_simulation', methods=['POST'])
def acoustic_simulation():

    request_data = request.get_json()
    shape=request_data["geo"]
    geo=Geo(geo=shape)
    notes = geo.get_cadsd().get_notes()
    notes = notes[["freq", "impedance", "note-name", "cent-diff"]]

    spektra = geo.get_cadsd().get_all_spektra_df()


    result = {
        "notes": json.loads(notes.to_json(orient="records")),
        "spektra": {
            "freqs": list(spektra.freq),
            "impedance": list(spektra.impedance),
            "ground": list(spektra.ground),
            "overblow": list(spektra.overblow)
        }
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
