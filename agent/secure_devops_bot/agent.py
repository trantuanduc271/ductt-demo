import os
from google.adk.agents import Agent
from .rules import SANITIZATION_POLICY

def create_secure_devops_agent():
    """
    Create a security sanitization agent with GDPR/PCI DSS compliance.
    """
    return Agent(
        name="secure_devops_assistant",
        model="gemini-2.0-flash-exp",
        instruction=f"""Act as a security sanitization agent that analyzes input for GDPR- and PCI DSS–regulated data and outputs only a safely redacted version or a clear rejection when sanitization is not possible.

{SANITIZATION_POLICY}""",
        description="An AI agent that detects and sanitizes GDPR- and PCI DSS–regulated data by redacting sensitive content or rejecting unsafe inputs before further processing.",
    )

# Create the root agent
root_agent = create_secure_devops_agent()