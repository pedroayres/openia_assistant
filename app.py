import os
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_vector_store_and_upload(file_paths):
    vector_store = client.vector_stores.create(name="NB Test")
    file_streams = [open(path, "rb") for path in file_paths]

    file_batch = client.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=file_streams
    )

    print("Batch status:", file_batch.status)
    print("Files uploaded:", file_batch.file_counts)
    return vector_store.id

def create_and_configure_assistant(vector_store_id):
    assistant = client.beta.assistants.create(
        name="General Knowledge Assistant",
        instructions="You are a helpful assistant that provides information on general topics. Use the provided content to answer the user's questions.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )

    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )
    return assistant

def create_thread():
    return client.beta.threads.create()

def interact_with_assistant(thread, assistant):
    print("\nYou can now chat with the Assistant. Type 'exit' to end the conversation.\n")

    while True:
        question = input("You: ")

        if question.lower() in ["sair", "exit", "quit"]:
            print("Ending the conversation...")
            break

        print("Thinking...")

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        while run.status in ["queued", "in_progress", "cancelling"]:
            print(f"Current status: {run.status}...")
            time.sleep(1.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            response = next(
                (m.content[0].text.value for m in messages.data if m.role == "assistant"),
                "No response found."
            )
            clean_response = response.split('【')[0].strip().replace('. ', '.\n')
            print(f"Assistant:\n{clean_response}\n")
        else:
            print(f"A problem occurred: {run.status}")

def main():
    vector_store_id = create_vector_store_and_upload(["example.pdf"])
    assistant = create_and_configure_assistant(vector_store_id)
    thread = create_thread()
    interact_with_assistant(thread, assistant)

if __name__ == "__main__":
    main()