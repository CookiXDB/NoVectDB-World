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

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

if __name__ == "__main__":
    app.run(debug=True, port=5050)
