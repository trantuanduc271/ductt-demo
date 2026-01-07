from posthog import Posthog
from posthog.ai.gemini import Client


# Initialize PostHog (replace with your own project API key & region host if needed)
posthog = Posthog(
    project_api_key="phc_B6jEmPA78ravxUqMDifZNNfdLSdZ1152BL076QzDPcv",
    host="https://us.i.posthog.com",
)


def main() -> None:
    """PostHog LLM analytics with Google Gemini (no Vertex AI)."""
    # Basic event so you can see normal events (no identify needed)
    posthog.capture(
        distinct_id="user-123",
        event="posthog_test_event",
        properties={
            "source": "ductt-demo",
            "message": "Hello from PostHog with Gemini number 2",
        },
    )

    # --- LLM analytics: direct Gemini API key, no Vertex AI ---
    client = Client(
        api_key="AIzaSyA4jqrzYKEtkRIgyMOYEpSTHxdNapicLJM",
        posthog_client=posthog,
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=["Hello, world!"],
        posthog_distinct_id="user-123",
        posthog_properties={"conversation_id": "demo_convo_1"},
    )

    print(response.text)

    # Ensure PostHog events are sent before the script exits
    posthog.flush()


if __name__ == "__main__":
    main()