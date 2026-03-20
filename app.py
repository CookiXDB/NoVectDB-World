from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import re
import sys
import tempfile
import subprocess

app = Flask(__name__)

def _find_repo(name):
    base = os.path.dirname(os.path.abspath(__file__))
    for candidate in (
        os.environ.get(name.upper().replace('-','_') + '_PATH', ''),
        os.path.join(base, name),
        os.path.join(base, '..', name),
    ):
        if candidate and os.path.isdir(candidate):
            return os.path.abspath(candidate)
    return os.path.abspath(os.path.join(base, name))

MATYOS_REPO = _find_repo('matyos_repo')
BRING_REPO  = _find_repo('bring_repo')

ANSI_RE = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
NOISE = ('urllib3', 'NotOpenSSLWarning', 'bring-parser not installed',
         'warnings.warn', 'NotOpenSSL')

def _strip(text):
    return ANSI_RE.sub('', text)

def _clean_stderr(text):
    lines = [l for l in text.split('\n')
             if l.strip() and not any(n in l for n in NOISE)]
    return '\n'.join(lines)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/polyfdor")
def polyfdor():
    return render_template("polyfdor.html")

@app.route("/matyos")
def matyos():
    return render_template("matyos.html")

@app.route("/polyfdos")
def polyfdos_os():
    return render_template("polyfdos_os.html")

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

@app.route("/api/run-el", methods=["POST"])
def run_el():
    data = request.get_json(force=True)
    code = data.get("code", "").strip()
    if not code:
        return jsonify({"output": "", "error": "No code provided"})

    el_fd, el_path   = tempfile.mkstemp(suffix='.el')
    run_fd, run_path = tempfile.mkstemp(suffix='.py')
    try:
        with os.fdopen(el_fd, 'w') as f:
            f.write(code)

        runner = (
            "import sys, os, warnings\n"
            "warnings.filterwarnings('ignore')\n"
            f"sys.path.insert(0, {repr(os.path.abspath(MATYOS_REPO))})\n"
            f"os.chdir({repr(os.path.abspath(MATYOS_REPO))})\n"
            "from compiler.main import El\n"
            f"El.compile(open({repr(el_path)}).read())\n"
        )
        with os.fdopen(run_fd, 'w') as f:
            f.write(runner)

        result = subprocess.run(
            [sys.executable, run_path],
            capture_output=True, text=True, timeout=10
        )
        raw_out = _strip(result.stdout)
        output = '\n'.join(l for l in raw_out.split('\n')
                          if not any(n in l for n in NOISE)).strip()
        error  = _clean_stderr(_strip(result.stderr))
        return jsonify({"output": output, "error": error or None})

    except subprocess.TimeoutExpired:
        return jsonify({"output": "", "error": "Execution timed out (10 s)"})
    except Exception as e:
        return jsonify({"output": "", "error": str(e)})
    finally:
        for p in (el_path, run_path):
            try: os.unlink(p)
            except: pass


@app.route("/api/parse-bring", methods=["POST"])
def parse_bring():
    data    = request.get_json(force=True)
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"result": {}, "error": "No content provided"})

    bring_abs = os.path.abspath(BRING_REPO)
    if bring_abs not in sys.path:
        sys.path.insert(0, bring_abs)

    try:
        from bring_parser.parser import (
            parse_bring_string, BringPrimitive, BringObject,
            BringArray, BringSchema, BringSchemaRule
        )

        def ser(val):
            if val is None:
                return {"t": "null", "v": None}
            if isinstance(val, BringPrimitive):
                return {"t": type(val.value).__name__, "v": val.value}
            if isinstance(val, BringArray):
                return {"t": "array", "v": [ser(i) for i in val.items]}
            if isinstance(val, BringSchema):
                return {
                    "t": "schema", "name": val.name,
                    "rules": [
                        {"key": r.key, "type": r.type,
                         "attrs": {a.name: a.value for a in r.attributes}}
                        for r in val.rules
                    ]
                }
            # BringObjectNode or BringObject
            if hasattr(val, 'items'):
                items = val.items if isinstance(val.items, dict) else {}
                ann   = getattr(val, 'annotations', {})
                return {"t": "object", "v": {k: ser(v) for k, v in items.items()}, "attrs": ann}
            if hasattr(val, 'value'):
                return {"t": type(val.value).__name__, "v": val.value}
            return {"t": "raw", "v": str(val)}

        raw    = parse_bring_string(content)
        result = {k: ser(v) for k, v in raw.items()}
        return jsonify({"result": result, "error": None})

    except Exception as e:
        return jsonify({"result": None, "error": str(e)})


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

if __name__ == "__main__":
    app.run(debug=True, port=5050)
