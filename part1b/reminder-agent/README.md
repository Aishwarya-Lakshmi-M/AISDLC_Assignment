# Reminder Agent

Reminder Agent converts a natural-language reminder request into one structured JSON result.
It supports reminder creation only. It does not persist reminders, send notifications, integrate
with calendars, or perform rescheduling, snoozing, listing, or deletion.

## Requirements

- Python 3.11 or newer
- pytest
- Optional: a Gemini API key for real evaluation runs

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,gemini,demo]"
```

The app reads Gemini credentials from environment variables. In PowerShell, set the key and model
in the same terminal session used to launch the demo:

```powershell
$env:GEMINI_API_KEY = "your-key"
$env:GEMINI_MODEL = "gemini-3.5-flash-lite"
```

Never commit `.env` or paste an API key into source files, logs, chat transcripts, or evaluation
artifacts. Revoke a key immediately if it may have been exposed.

## Run Reminder Agent

The public application entry point is `create_reminder`:

```python
from datetime import datetime

from src.reminder_agent import EvaluationContext, ReminderRequest, create_reminder

request = ReminderRequest(
    "Remind me to study Python tomorrow at 6 PM",
    EvaluationContext(
        reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
        timezone="Asia/Kolkata",
    ),
)

print(create_reminder(request).to_dict())
```

Relative dates and times require an explicit reference datetime and timezone. The application does not
use the machine clock or infer a timezone.

## Local Demo UI

Launch the local Streamlit interface from the project root:

```powershell
python -m streamlit run demo_app.py
```

Open the local URL printed by Streamlit. The page uses a clearly labeled static reference datetime and
timezone that can be edited. It calls Gemini only when the submit button is pressed, using the
`GEMINI_API_KEY` and optional `GEMINI_MODEL` environment variables. The UI displays the validated
five-field result; it does not save or schedule reminders.

## Output Contract

Every result contains exactly five fields:

- `title`
- `date`
- `time`
- `status`
- `clarification`

Valid status values are `ready` and `needs_clarification`. Ready results use `YYYY-MM-DD`,
`HH:MM`, and a null clarification. Clarification results preserve known fields and use null for
unresolved fields.

## Local Tests

Run unit and contract tests:

```powershell
python -m pytest tests/unit tests/contract -q
```

Run semantic, harness, and design tests:

```powershell
python -m pytest tests/semantic tests/harness -q
```

Run the complete local suite:

```powershell
python -m pytest -q
```

Unit tests use mocked AI responses and do not call Gemini.

## Evaluation Harness

The frozen evaluation dataset is [evals/dataset.json](evals/dataset.json). It contains 20 cases covering
normal, boundary, ambiguous, missing, malformed, unsupported, and adversarial requests.

The one evaluation pipeline is:

```text
dataset -> AI application -> structural checks -> behavioral/invariant checks
-> semantic checks -> aggregate score -> PASS/FAIL
```

The contract and rules are documented in:

- [evals/scoring.md](evals/scoring.md)
- [evals/harness_contract.md](evals/harness_contract.md)

Structural and behavioral/safety checks are independent hard gates. Semantic scoring does not compensate
for structural, behavioral, or safety failures.

## Evaluation Thresholds

The frozen thresholds are:

- 20/20 structural passes
- 20/20 behavioral passes
- 20/20 safety passes
- 85% or higher semantic aggregate
- 18/20 or more overall case passes
- 80% or higher semantic pass for an individual case

Do not change thresholds or frozen dataset cases to improve evaluation results.

## Gemini Evaluation

Gemini evaluation requires `GEMINI_API_KEY` and `GEMINI_MODEL`. A cost-conscious first run should use
a lite/free-tier-capable model offered by the configured account. Model availability varies; verify
the account's available models before the run.

Use inter-request pacing so a 20-case run stays below free-tier request limits. The current harness
configuration supports `inter_request_delay_seconds`.

The real initial run is recorded in [evals/initial-results.json](evals/initial-results.json). It is
not a complete successful evaluation:

- 16 cases reached JSON-contract failures.
- 4 cases reached HTTP 429 free-tier quota errors.
- Those 4 quota cases were not model-evaluated.
- The initial outcome remains FAIL.

Failure details are documented in [evals/failure-analysis.md](evals/failure-analysis.md).

For T045, run one real 20-case Gemini evaluation only after quota recovery and revoking any exposed key.
A partial quota run must not be merged into a clean final run.

## Known Limitations

- The project currently uses a provider-neutral adapter and the official Google GenAI SDK.
- The initial evaluation is incomplete because of quota errors.
- Real model availability and quota limits can change.
- The application is a parser and structured-output project; it does not persist or schedule reminders.
