from flask import Flask, request, jsonify
import json
from datetime import datetime
from typing import Optional, Any

app = Flask(__name__)


@app.route("/leak", methods=["GET", "POST"])
def listener():
    """Handle the HTTP requests"""
    method = request.method

    if method == "POST":
        args = request.args.to_dict()
        body_json = request.get_json(silent=True)
        raw_body = request.get_data(as_text=True)
        logger_helper(method, args, body_json, raw_body)
        return jsonify({"message": "POST received!"}), 200

    elif method == "GET":
        args = request.args.to_dict()
        body_json = request.get_json(silent=True)
        raw_body = request.get_data(as_text=True)
        logger_helper(method, args, body_json, raw_body)
        return jsonify({"message": "GET received!"}), 200

    else:
        return jsonify({"message": "Only POST and GET requests are accepted!"}), 400


def logger_helper(
    method: str, args: dict, body_json: Any, raw_body: Optional[str]
) -> None:
    """Helper to write the information into a logger file"""
    entry = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "method": method,
        "args": args,
        "json": body_json,
        "raw": raw_body,
    }
    with open("canary_hits.log", "a") as f:
        f.write(json.dumps(entry) + "\n")
    return None


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000)
