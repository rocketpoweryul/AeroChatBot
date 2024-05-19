from dotenv import load_dotenv
import openai
from typing_extensions import override
from openai import AssistantEventHandler
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 

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
        run = client.beta.threads.runs.create(
            assistant_id=self.assistant.id,
            thread_id=self.thread.id,
            stream=True
        )
        
        # Iterate through the stream of events
        for event in run:
            # There are various types of streaming events
            # See here: https://platform.openai.com/docs/api-reference/assistants-streaming/events

            # Here, we only consider if there's a delta text
            if isinstance(event, ThreadMessageDelta):
                if isinstance(event.data.delta.content[0], TextDeltaBlock):
                    # empty the container
                    assistant_reply_box.empty()
                    # add the new text
                    assistant_reply += event.data.delta.content[0].text.value
                    # display the new text
                    assistant_reply_box.markdown(assistant_reply)
        
        return assistant_reply
