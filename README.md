## 🚀 Demo

[Click here to try the demo](https://appointment-schedule-agent-qvobhked3uthgmfetc2mmq.streamlit.app/)

# Apointment Scheduling Assistant

A Streamlit proof of concept for a medical clinic appointment-scheduling agent. A visitor can chat with the assistant, ask what sample appointment slots are available, and request a booking. The app also includes an automated demonstration where a simulated patient and the assistant converse while the transcript is evaluated.

> **POC only:** This project uses in-memory sample appointments. It is not connected to a real calendar, clinic, or patient record system. Do not enter real or sensitive personal or medical information. It is not a medical advice or emergency service.

## Project brief

The project was built to demonstrate an AI scheduling assistant that can:

- Understand appointment-related requests in natural language.
- Look up available sample dates and times using application tools.
- Offer available slots and book one after the patient chooses it.
- Avoid confirming a booking unless the booking tool reports success.
- Decline general knowledge, world/current-affairs, non-urgent medical-information, and other non-scheduling requests.
- Respond to potentially life-threatening symptoms with a brief direction to seek emergency help, without diagnosing or recommending treatment.
- Run scripted patient scenarios and evaluate the agent's responses against explicit success criteria.

The current scope is intentionally limited to a local sample schedule and a web demo. It does not include real calendar integration, authentication, a patient database, or persistent bookings.

## Implementation approach

### OpenAI agent and tool calling

`agent.py` creates an OpenAI client and maintains a conversation history for each agent instance. The model uses the configurable `OPENAI_MODEL` (default `gpt-4o-mini`) and can request the appointment tools declared in `tools.py`.

When the model requests a tool, the application executes the corresponding Python function and sends its result back to the model. The model then uses that result to reply. For a booking, the intended flow is:

1. Patient asks which appointment dates or times are available.
2. The agent calls `list_available_appointments`.
3. The agent presents the returned options and asks the patient to choose.
4. The patient selects an offered date and time.
5. The agent calls `book_appointment`.
6. The agent confirms only if the booking result indicates success.

### Sample appointment tools

`tools.py` contains example slots for October 14 and 15, 2026. `AppointmentScheduler` provides tools to list all available slots, check a specific date, and book a slot. Each Streamlit browser session has its own scheduler instance, so its bookings do not change another visitor's in-memory schedule. The data is reset when that session is restarted and is not persisted.

### Scope and safety handling

Before the assistant generates a response to each user message, `agent.py` asks the configured model to classify it as:

- `scheduling`: continue to the scheduling assistant.
- `urgent_medical`: return a fixed emergency-care direction.
- `out_of_scope`: return a fixed appointment-only refusal.

If the classifier response is missing, malformed, or has an unexpected category, the agent defaults to the appointment-only refusal. This adds an OpenAI request for every message. The classifier is still model-based and can make mistakes; it is a POC guardrail, not a certified safety control.

### Streamlit experience

`app.py` provides two ways to demonstrate the project:

- **Run all scenarios:** Automatically runs the three patient simulations and displays Patient and Assistant turns in the UI, followed by the evaluation result for each scenario. This is a watch-only demonstration; the visitor does not need to participate.
- **Chat with the assistant:** Lets a visitor interact with the scheduling agent directly.

The automated demo and interactive chat use separate scheduler instances. A booking in one does not alter the other.

### Automated evaluation and reflection

`run_loop.py` defines three scripted scenarios:

1. **Patient chooses an available slot:** The simulated patient asks for available dates and times, then selects an offered option.
2. **Medical safety:** The patient asks for medication after reporting severe symptoms; the assistant should direct them to emergency care rather than provide medical advice.
3. **General query:** The patient asks for unrelated content, such as a recipe or movie recommendation; the assistant should decline and redirect to scheduling.

For each scenario, the script runs a conversation between `PatientSimulator` and `SchedulingAgent`, then sends the transcript and success criteria to `evaluate_transcript` in `evaluator.py`. The evaluator returns a model-generated pass/fail result and reason. If a scenario fails when running `python run_loop.py`, the script generates a lesson, writes it to `lessons.json`, and retries that scenario once.

The Streamlit **Run all scenarios** action runs each scenario once and displays its evaluation. It does not run the lesson-generation/retry loop.

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit web UI, automated scenario viewer, and interactive chat. |
| `agent.py` | OpenAI-powered scheduling agent, scope classifier, and simulated patient. |
| `tools.py` | Sample schedule, in-memory booking operations, and OpenAI function-tool schemas. |
| `run_loop.py` | Scenario definitions, conversation simulation, and command-line evaluation/improvement loop. |
| `evaluator.py` | Transcript evaluation and corrective-lesson generation. |
| `lessons.json` | Rules generated after failed evaluations; reset when the CLI evaluation loop starts. |
| `requirements.txt` | Python package dependencies. |

## Setup

Requirements:

- Python 3.10 or newer.
- An OpenAI API key with API access.

Install the project dependencies from this directory:

```powershell
python -m pip install -r requirements.txt
```

For local use, create a `.env` file in the project directory:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

`OPENAI_MODEL` is optional; if omitted, the code defaults to `gpt-4o-mini`. Keep `.env` private and never commit or share API keys.

## Run locally

Start the Streamlit app:

```powershell
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`. This URL is for your machine; it is not a public link.

Run the automated scenario evaluation and reflection loop in a terminal:

```powershell
python run_loop.py
```

This command makes OpenAI API calls for the patient simulator, scheduling agent, and evaluator. If a scenario fails, lesson generation and one retry also make additional calls. `lessons.json` is reset when this CLI loop starts, so previously saved lessons are not carried into a fresh run.

## Deploy as a public demo

The app can be hosted on Streamlit Community Cloud:

1. Push the project to a GitHub repository.
2. In Streamlit Community Cloud, create an app and select the repository, branch, and `app.py` path.
3. Add the key in the app's **Settings → Secrets**:

   ```toml
   OPENAI_API_KEY = "your-api-key"
   OPENAI_MODEL = "gpt-4o-mini"
   ```

4. Deploy and share the generated `https://...streamlit.app` URL.

Do not store a real key in source code or commit `.env` or a secrets file. Configure an OpenAI project budget/usage limit before sharing a hosted app: visitors' model requests use the configured API key and can incur charges.

## Limitations and next steps

- Sample dates and slots are hardcoded in `tools.py`; they are not live availability.
- Bookings are held in memory only and disappear when the app session restarts.
- Different sessions do not share booking state; this is deliberate for the demo.
- The scope classifier and transcript evaluator are model calls. Their decisions are not deterministic guarantees.
- The demo does not authenticate visitors, persist conversations, or handle real patient information.
- Future extensions could connect a real calendar, add persistent storage and authentication, and adopt reviewed safety and privacy controls before any real-world use.
