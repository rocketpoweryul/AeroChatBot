# get packages
import openai
import os

from openai            import OpenAI
from openai            import AssistantEventHandler
from typing_extensions import override

from agent_functions import *
from prompts         import *

def create_assistant(): 
    # make sure there is a .env file with the api key
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # create openai client
    client = OpenAI()

    # create assistant
    assistant = client.beta.assistants.create(
        name            = "Aerospace Certification Chatbot",
        instructions    = aero_expert_sysmsg,
        tools           = [fcn_call_tools],
        model           = "gpt-4o"
        )

    thread = client.beta.threads.create

    return assistant, thread

def add_msg_to_thread(user_message, client, thread):
    message = client.beta.threads.messages.create(
        thread_id   = thread.id,
        role        = "user",
        content     = user_message
        )

 
# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.
 
class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event):
      # Retrieve events that are denoted with 'requires_action'
      # since these will have our tool_calls
      if event.event == 'thread.run.requires_action':
        run_id = event.data.id  # Retrieve the run ID from the event data
        self.handle_requires_action(event.data, run_id)
 
    def handle_requires_action(self, data, run_id):
      tool_outputs = []
        
      for tool in data.required_action.submit_tool_outputs.tool_calls:
        if tool.function.name == "Look_Up_AC":
          tool_args = JSON.parse(tool.function
          output = Look_Up_AC
        
      # Submit all tool_outputs at the same time
      self.submit_tool_outputs(tool_outputs, run_id)
 
    def submit_tool_outputs(self, tool_outputs, run_id):
      # Use the submit_tool_outputs_stream helper
      with client.beta.threads.runs.submit_tool_outputs_stream(
        thread_id=self.current_run.thread_id,
        run_id=self.current_run.id,
        tool_outputs=tool_outputs,
        event_handler=EventHandler(),
      ) as stream:
        for text in stream.text_deltas:
          print(text, end="", flush=True)
        print()
 
# Then, we use the `stream` SDK helper 
# with the `EventHandler` class to create the Run 
# and stream the response.
 
with client.beta.threads.runs.stream(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Please address the user as Jane Doe. The user has a premium account.",
  event_handler=EventHandler(),
) as stream:
  stream.until_done()
    
