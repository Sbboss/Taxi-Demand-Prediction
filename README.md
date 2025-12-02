# Driver Zone Recommender (Streamlit)

Run the Streamlit UI to predict suggested zones for drivers.

## Prerequisites
- Python 3.8+
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
streamlit run streamlit_app.py
```

Opens at `http://localhost:8501`

## Run with ngrok (Public URL)

First, get a free ngrok account and auth token from https://ngrok.com

Then run:

```bash
export NGROK_AUTH_TOKEN='your_ngrok_token_here'
ngrok http <port>
```

This will print a public URL like `https://xxxx-xx-xxx-xxx-xx.ngrok.io` that you can share.

## Usage

The sidebar contains controls for:
- **Current Zone** - select your starting zone
- **Hour of Day** - choose time (0-23)
- **Driving Metric** - optimize for demand, avg_fare, avg_trip_time_min, or income_per_min
- **Number of suggestions** - how many zones to recommend

Click `Predict` to see recommendations and the map. Use `Reset` to clear results.
# Taxi-Demand-Prediction
