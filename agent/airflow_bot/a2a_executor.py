from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from agent import root_agent

from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService

class AirflowAgentExecutor(AgentExecutor):
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        self.runner = Runner(
            app_name="airflow_bot",
            agent=root_agent,
            session_service=self.session_service,
            artifact_service=self.artifact_service
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_input = context.get_user_input()
        print(f"Received input: {user_input}")
        
        session_id = context.request.message.context_id or "default_session"

        try:
            async for event in self.runner.run_async(
                user_id="a2a_user",
                session_id=session_id,
                new_message=user_input
            ):
                # event is google.adk.events.Event
                # We are interested in events that have content (ModelResponse)
                if event.content:
                    text_response = ""
                    # Check if content has parts (google.genai.types.Message or similar)
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                text_response += part.text
                    # Fallback if it has text attribute directly
                    elif hasattr(event.content, 'text') and event.content.text:
                        text_response = event.content.text
                    
                    if text_response:
                        print(f"Sending response: {text_response[:100]}...")
                        await event_queue.enqueue_event(new_agent_text_message(text_response))

        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f"Error executing agent: {str(e)}"
            print(error_msg)
            await event_queue.enqueue_event(new_agent_text_message(error_msg))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass
