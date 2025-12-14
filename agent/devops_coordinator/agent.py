"""
Multi-Agent System Root Coordinator
This root agent intelligently delegates tasks to specialized sub-agents:
- airflow_bot: Handles Apache Airflow workflow management
- kubernetes_bot: Handles Kubernetes cluster operations
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import Agent

# Add parent directory to path to import sibling agents
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import sub-agents
from airflow_bot.agent import root_agent as airflow_agent
from kubernetes_bot.agent import root_agent as kubernetes_agent

# Load environment variables from parent agent directory
env_path = parent_dir / ".env"
load_dotenv(env_path)

COORDINATOR_INSTRUCTION = """You are an intelligent DevOps coordinator assistant that helps users manage both Apache Airflow workflows and Kubernetes clusters.

Your role is to:
1. Understand user requests and determine which system they need help with
2. Delegate to the appropriate specialized assistant:
   - Use airflow_assistant for: DAGs, task runs, Airflow monitoring, workflow management, pipeline operations
   - Use kubernetes_assistant for: pods, deployments, services, namespaces, K8s cluster operations
3. Provide clear, helpful responses based on the specialized assistant's work

When a user asks about:
- Workflows, DAGs, tasks, pipelines, Airflow → Delegate to airflow_assistant
- Pods, deployments, services, namespaces, Kubernetes, K8s → Delegate to kubernetes_assistant
- Both systems → Handle sequentially or clarify which system to prioritize

Always be friendly, professional, and ensure users get accurate information from the right specialized system.
"""

# Create the root coordinator agent with sub-agents
root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="devops_coordinator",
    description="A coordinator that intelligently routes requests to Airflow or Kubernetes specialists",
    instruction=COORDINATOR_INSTRUCTION,
    sub_agents=[
        airflow_agent,
        kubernetes_agent,
    ],
)
