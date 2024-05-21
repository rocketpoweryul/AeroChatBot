from dotenv import load_dotenv
import openai
from openai.types.beta.assistant_stream_event import ThreadMessageDelta, ThreadRunRequiresAction, ThreadMessageInProgress, ThreadMessageCompleted, ThreadRunCompleted
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 
from agent_functions import *
import json
import time

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

    def stream_response(self, assistant_reply_box):
        try:
            with client.beta.threads.runs.create(
                assistant_id=self.assistant.id,
                thread_id=self.thread.id,
                stream=True
            ) as stream:
                assistant_reply = ""
                start_time = time.time()
                max_duration = 120  # Maximum duration in seconds for streaming

                # Iterate through the stream of events
                for event in stream:
                    print("Event received!")  # Debug statement

                    # Check if the maximum duration has been exceeded
                    if time.time() - start_time > max_duration:
                        print("Stream timeout exceeded.")
                        break

                    # Handle different types of events
                    if isinstance(event, ThreadMessageDelta):
                        print("MSG ThreadMessageDelta event data")  # Debug statement
                        if isinstance(event.data.delta.content[0], TextDeltaBlock):
                            # add the new text
                            assistant_reply += event.data.delta.content[0].text.value
                            # display the new text
                            assistant_reply_box.markdown(assistant_reply)

                    elif isinstance(event, ThreadRunRequiresAction):
                        print("ThreadRunRequiresAction event data")  # Debug statement

                        # Get required actions
                        runs_page = self.client.beta.threads.runs.list(thread_id=self.thread.id)
                        runs = list(runs_page.data)
                        if runs:
                            run = runs[0]
                            run_id = run.id if hasattr(run, 'id') else None

                            if run_id:
                                required_actions = run.required_action.submit_tool_outputs.model_dump()
                                tool_outputs = []

                                # Loop through actions
                                for action in required_actions["tool_calls"]:
                                    # Identify function and params
                                    func_name = action["function"]["name"]
                                    arguments = json.loads(action["function"]["arguments"])
                                    print(f"Executing function: {func_name} with arguments: {arguments}")  # Debug statement

                                    # Run the agent function caller
                                    output = execute_required_function(func_name, arguments)
                                    print(f"Function {func_name} complete")  # Debug statement

                                    # Create the tool outputs
                                    tool_outputs.append({"tool_call_id": action["id"], "output": str(output)})

                                # Submit the outputs
                                if tool_outputs:
                                    print("Tool output acquired")
                                    with client.beta.threads.runs.submit_tool_outputs(
                                        thread_id=self.thread.id,
                                        run_id=run_id,
                                        tool_outputs=tool_outputs,
                                        stream = True
                                    ) as stream:
                                        print("Streaming response to tool output...")
                                        # Handle different types of events
                                        for event in stream:
                                            if isinstance(event, ThreadMessageDelta):
                                                print("TOOL ThreadMessageDelta event data")  # Debug statement
                                                if isinstance(event.data.delta.content[0], TextDeltaBlock):
                                                    # add the new text
                                                    assistant_reply += event.data.delta.content[0].text.value
                                                    # display the new text
                                                    assistant_reply_box.markdown(assistant_reply)

                    elif isinstance(event, ThreadMessageInProgress):
                        print("ThreadMessageInProgress event received")  # Debug statement
                        time.sleep(1)

                    elif isinstance(event, ThreadMessageCompleted):
                        print("Message completed.")  # Debug statement

                    elif isinstance(event, ThreadRunCompleted):
                        print("Run completed.")  # Debug statement

                    print("Loop iteration completed.")  # Debug statement to check loop progress

                return assistant_reply

        except Exception as e:
            print("An error occurred during streaming: ", str(e))
            return "An error occurred while processing your request."
