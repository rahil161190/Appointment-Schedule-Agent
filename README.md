# Apointment Scheduling Assistant

## 🚀 Demo

[Click here to try the demo](https://appointment-schedule-agent-qvobhked3uthgmfetc2mmq.streamlit.app/)

A Streamlit proof of concept for a medical clinic scheduling assistant. Visitors can chat with the assistant using sample appointment availability and choose between appointment booking, medical safety, and general query demonstrations.

## Requirements

- Python 3.10 or newer
- An OpenAI API key with access to the OpenAI API

## Setup

Open a terminal in this directory and install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a file named `.env` in this directory and add your API key:

```dotenv
OPENAI_API_KEY=your_api_key_here
# Optional: defaults to gpt-4o-mini
OPENAI_MODEL=gpt-4o-mini
```

Keep `.env` private; do not commit or share your API key. The application loads `.env` from this directory. You can also configure `OPENAI_API_KEY` and, optionally, `OPENAI_MODEL` in your shell environment instead.

## Run

Start the interactive web app from this directory:

```powershell
streamlit run app.py
```

Use **Run all scenarios** in the app to watch the simulated patient and assistant converse automatically and see each transcript's evaluation. This makes live OpenAI API calls for the patient, assistant, and evaluator. The regular chat remains available below the demo.

To run the automated scenario evaluation loop instead:

```powershell
python run_loop.py
```

## Deploying the web app

The app can be deployed on Streamlit Community Cloud. Configure `OPENAI_API_KEY` under the app's **Settings → Secrets**; do not put a real key in source code or commit a secrets file. Optionally set `OPENAI_MODEL` there (defaults to `gpt-4o-mini`). For local development, the app also reads these values from `.env`.

Each browser session gets its own conversation and in-memory copy of the sample schedule. Changes to bookings do not persist after the session ends. Configure OpenAI project-level budgets and rate limits before making a hosted instance public; a client-side session alone is not an abuse or spending limit.

## Scenario modes

- **Appointment booking:** Lists sample dates and times, then books the visitor's selected slot.
- **Medical safety:** Gives only a brief emergency-care direction for potentially life-threatening symptoms; it does not diagnose or recommend treatment.
- **General query:** Declines general knowledge, world/current-affairs, non-urgent medical-information, and other non-scheduling requests.

The demo uses sample availability defined in `tools.py`; it does not connect to a real calendar or booking system. Do not enter real or sensitive medical information.

Before generating a response, the app asks the configured model to classify each message as scheduling, urgent medical, or out of scope. Out-of-scope messages receive a fixed, application-generated refusal; urgent messages receive a fixed emergency-care direction. This adds one model request per message. The classifier is still an AI component and can misclassify requests, so this POC is not a certified safety control.

## Evaluation loop

`run_loop.py` simulates three patient scenarios and evaluates each transcript. If a scenario fails, it generates a behavioral rule and retries once. `lessons.json` is reset to an empty list each time the evaluation script starts.

## Troubleshooting

- **API key not found:** For local development, ensure `.env` is in this directory and contains `OPENAI_API_KEY=...`. For hosting, configure the key in the platform's secrets settings.
- **`ModuleNotFoundError`:** Activate the Python environment you intend to use, then run `python -m pip install -r requirements.txt` with that same `python` command.
- **API or model errors:** Check your network connection, OpenAI API key, selected model, and API access/quota.
