from dotenv import load_dotenv
import openai
from typing_extensions import override
from openai import AssistantEventHandler
from openai.types.beta.assistant_stream_event import ThreadMessageDelta, ThreadRunRequiresAction
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 
from agent_functions import *

# openai variables
load_dotenv()
client = openai.OpenAI()
model = 'gpt-4o'
assistant_id = 'asst_kQi8u6bDILpHc6NTXOJxXs6y'

class Assistant:
    thread_id = ""

    def __init__(self, model: str = model):
        # openai variables
        self.client    = client
        self.model     = model
        self.assistant = None
        self.thread    = None
        self.run       = None
        self.summary   = None

        # retrieve existing assistant based on hardcoded data
        self.assistant = self.client.beta.assistants.retrieve(
            assistant_id=assistant_id
            )
        
        # create thread as this initialization only occurs on boot up of app
        if Assistant.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id = Assistant.thread_id
            )
        else:
            self.thread = self.client.beta.threads.create()
            Assistant.thread_id = self.thread.id
      
    def add_user_prompt(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id = self.thread.id,
                role      = role,
                content   = content
            )

    def stream_response(self, assistant_reply_box, assistant_reply):
        with client.beta.threads.runs.create(
            assistant_id=self.assistant.id,
            thread_id=self.thread.id,
            stream=True
        ) as stream:
            # Iterate through the stream of events
            for event in stream:
                # Retrieve the list of runs
                runs_page = self.client.beta.threads.runs.list(thread_id=self.thread.id)

                # Convert the SyncCursorPage to a list (if possible) or iterate over it
                runs = list(runs_page.data)

                # Check if the list is not empty
                if runs:
                    # Get the first run
                    run = runs[0]
                    
                    # Check if the run has an id attribute
                    if hasattr(run, 'id'):
                        run_id = run.id
                    else:
                        print("Error: The run object does not have an 'id' attribute.")
                else:
                    print("Error: No runs found.")


                # Here, we only consider if there's a delta text
                if isinstance(event, ThreadMessageDelta):
                    if isinstance(event.data.delta.content[0], TextDeltaBlock):
                        # empty the container
                        assistant_reply_box.empty()
                        # add the new text
                        assistant_reply += event.data.delta.content[0].text.value
                        # display the new text
                        assistant_reply_box.markdown(assistant_reply)
                if isinstance(event, ThreadRunRequiresAction):
                    pass
                
                
        
        return assistant_reply
