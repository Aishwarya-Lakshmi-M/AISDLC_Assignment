"""Streamlit demo interface for the Reminder Agent."""

from datetime import datetime
import os

from .context import EvaluationContext, ReminderRequest
from .parser import AIAdapterConfig, GeminiAIResponseClient, ProviderNeutralAIAdapter


def build_demo_request(
    text: str,
    reference_datetime_text: str,
    timezone_text: str,
) -> ReminderRequest:
    reference_datetime = None
    value = reference_datetime_text.strip()
    if value:
        try:
            reference_datetime = datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError(
                "Reference datetime must be ISO 8601, including a UTC offset."
            ) from error
        if reference_datetime.tzinfo is None or reference_datetime.utcoffset() is None:
            raise ValueError("Reference datetime must include a UTC offset.")

    return ReminderRequest(
        text=text,
        context=EvaluationContext(
            reference_datetime=reference_datetime,
            timezone=timezone_text.strip() or None,
        ),
    )


def main() -> None:
    try:
        import streamlit as st
    except ImportError as error:
        raise RuntimeError(
            'Install the demo dependencies with: python -m pip install -e ".[demo,gemini]"'
        ) from error

    model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    st.set_page_config(page_title="Reminder Agent")
    st.title("Reminder Agent")
    st.write(
        "Turn a natural-language request into reminder details. "
        "This demo does not save, schedule, or send reminders."
    )
    st.caption(f"Provider: Gemini · Model: {model}")

    with st.form("reminder_request"):
        text = st.text_area(
            "What would you like to be reminded about?",
            value="Remind me to study Python tomorrow at 6 PM",
            height=100,
        )
        reference_datetime = st.text_input(
            "Reference datetime (ISO 8601 with UTC offset)",
            value="2026-11-22T14:30:00+05:30",
            help="Static demo context; it is not the machine's current time.",
        )
        timezone = st.text_input(
            "Timezone",
            value="Asia/Kolkata",
            help="Use an IANA timezone such as Asia/Kolkata or America/New_York.",
        )
        submitted = st.form_submit_button("Create reminder details")

    if not submitted:
        return
    if not text.strip():
        st.warning("Enter a reminder request first.")
        return

    try:
        request = build_demo_request(text, reference_datetime, timezone)
    except ValueError as error:
        st.error(str(error))
        return

    try:
        from google.genai.errors import APIError
    except ImportError:
        st.error(
            'Install the Gemini dependency with: python -m pip install -e ".[gemini]"'
        )
        return

    try:
        adapter = ProviderNeutralAIAdapter(
            GeminiAIResponseClient(),
            AIAdapterConfig(provider="gemini", model=model),
        )
        result = adapter.generate(request)
    except (ValueError, RuntimeError) as error:
        st.error(str(error))
        return
    except APIError as error:
        st.error(f"Gemini request failed: {error}")
        return

    if result.status == "ready":
        st.success("Reminder details are ready.")
    else:
        st.info("More information is needed.")
    st.json(result.to_dict())


if __name__ == "__main__":
    main()
