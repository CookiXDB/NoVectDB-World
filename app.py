from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/polyfdor")
def polyfdor():
    return render_template("polyfdor.html")

@app.route("/papers/novectDB")
def novectdb():
    return render_template("novectdb.html")

@app.route("/papers/hafdiConjecture")
def hafdi_conjecture():
    return render_template("hafdiConjecture.html")

@app.route("/papers/realistic")
def realistic():
    return render_template("realistic.html")

@app.route("/papers/contextOS")
def context_os():
    return render_template("contextOS.html")

@app.route("/papers/pizzaSugar")
def pizza_sugar():
    return render_template("pizzaSugar.html")

@app.route("/papers/fromProbsToEcoSys")
def from_probs_to_eco_sys():
    return render_template("fromProbsToEcoSys.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

if __name__ == "__main__":
    app.run(debug=True, port=5050)
