
from flask import Flask, render_template, jsonify, request, redirect, url_for
import pandas as pd
import numpy as np
import threading
from sklearn.linear_model import LinearRegression
import os
from app.utils import notify_user , load_data  # background

# Point Flask at app/templates and app/static
app = Flask(
    __name__,
    template_folder=os.path.join("app", "templates"),
    static_folder=os.path.join("app", "static"),
    static_url_path="/static"
)
@app.route("/forecast_next_week")
def api_forecast_next_week():
    """
    Return a 7-day price forecast using autoregressive LinearRegression.
    """
    df = load_data()
    ser = df.set_index("date")["price"].sort_index()
    vals = ser.values
    lag = 7

    if len(vals) <= lag:
        return jsonify({"error": "Not enough data to forecast"}), 400

    X, y = [], []
    for i in range(lag, len(vals)):
        X.append(vals[i - lag : i])
        y.append(vals[i])

    X = np.array(X)
    y = np.array(y)

    model = LinearRegression()
    model.fit(X, y)

    history = vals.tolist()
    preds = []
    for _ in range(7):
        input_seq = np.array(history[-lag:]).reshape(1, -1)
        next_price = model.predict(input_seq)[0]
        preds.append(next_price)
        history.append(next_price)

    future_idx = pd.date_range(ser.index[-1] + pd.Timedelta(days=1), periods=7)
    data = (
        pd.DataFrame({"date": future_idx, "price": preds})
        .assign(
            date=lambda d: d["date"].dt.strftime("%d %b %Y"),
            price=lambda d: d["price"].round(2),
        )
        .to_dict(orient="records")
    )

    return jsonify(data)


@app.route("/")
def index():
    return redirect(url_for("home"))


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/subscribe", methods=["POST"])
def subscribe():
    """
    Accepts JSON payload with phone_number, desired_price, etc., and starts alert worker.
    """
    data = request.get_json() or {}
    model_id = "1226219"
    phone_number = data.get("phone_number")
    desired_price = data.get("desired_price")
    description = data.get("description")
    current_price = float(data.get("current_price", 0))
    url = data.get(
        "url",
        "https://www.hashmalabait.co.il/product/%D7%98%D7%9C%D7%95%D7%95%D7%99%D7%96%D7%99%D7%94%2Dsamsung%2Due55du7100%2D4k%2D%E2%80%8F55%2D%E2%80%8F%D7%90%D7%99%D7%A0%D7%98%D7%A9%2D%D7%A1%D7%9E%D7%A1%D7%95%D7%A0%D7%92?aff=Zap&aff_a=1",
    )

    if not phone_number or desired_price is None:
        return jsonify({"status": "error", "message": "Missing phone_number or desired_price"}), 400

    threading.Thread(
        target=notify_user,
        args=(model_id, phone_number, float(desired_price), description, url),
        daemon=True,
    ).start()

    msg = "Got it! We'll notify you on Telegram when the price will drop."
    return jsonify({"status": "ok", "message": msg}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
