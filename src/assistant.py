"""File to handle running the LLM AI assistant."""

from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
import time
from operator import itemgetter
from typing import List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from langchain_core.runnables import (
    RunnableLambda,
    ConfigurableFieldSpec,
    RunnablePassthrough,
)
from langchain_core.runnables.history import RunnableWithMessageHistory

# global variable to store the message history.
store = {}

def get_session_history(
    user_id: str, conversation_id: str
) -> BaseChatMessageHistory:
    if (user_id, conversation_id) not in store:
        store[(user_id, conversation_id)] = InMemoryHistory()
    return store[(user_id, conversation_id)]



def calculate_model_diagnostics(start_time, end_time, total_tokens):
    """Function to track the performance of the AI model."""
    # Calculate elapsed time and average tokens per second
    elapsed_time = end_time - start_time
    tokens_per_second = total_tokens / elapsed_time if elapsed_time > 0 else 0

    # Print diagnostic information about the model's performance.
    print("\n\n\tModel diagnostics:")
    print(f"* Total tokens: {total_tokens}")
    print(f"* Elapsed time: {elapsed_time:.2f} seconds")
    print(f"* Average tokens per second: {tokens_per_second:.2f} t/s")


def main():
    # Initialize the Ollama model with parameters
    chat_model = ChatOllama(
        model="phi3:3.8b",
        temperature= 0,
        top_p=0.9,  # Top-p (nucleus) sampling
        frequency_penalty=0.2,  # Penalize new tokens based on their existing frequency
        presence_penalty=0.2,  # Penalize new tokens based on whether they appear in the text so far
        stream=True,  # Enable streaming of the response
        max_tokens=50
        # format="json",  # Specify the Output format

    )

    # Define the different prompts used for running the model.
    
    # Pre answer prompt template for determining how to answer the question and what actions to take on behalf of the user.
    f = open("src/prompt-templates/classifier-prompt.txt", "r")
    classification_prompt_template = f.read()

    # Prompt template for handling the model's conversational questions.
    f = open("src/prompt-templates/conversation-prompt.txt", "r")
    conversation_prompt_template = f.read()

    # Standard chatting model template for the assistant.
    default_model_prompt_template = "<|system|>\n <|end|>\n<|user|>\nQuestion: {question}<|end|>\n<|assistant|>"


    # Define a prompt template with the new structure
    prompt = PromptTemplate(
        input_variables = ["question"],
        template = conversation_prompt_template,
        conversation_history = True,
        validate_template = True
    )

    # Create a chain by combining the prompt and the model
    chain = prompt | chat_model

    # Create the chain with message history.

    chain_with_history = RunnableWithMessageHistory(
        chain,
        # Uses the get_by_session_id function defined in the example
        # above.
        get_by_session_id,
        input_messages_key="question",
        history_messages_key="history",
    )


    while True:

        # Define the question
        question = input(" > ")

        # Start the diagnostic experiments' timing.
        start_time = time.time()

        # Run the chain with the question using invoke and stream the response
        total_tokens = 0
        response = ""
        # Print out a blank line to separate the lines in the terminal.
        print()

        for chunk in chain.stream({"question": question}):
            response += chunk.content
            # print(chunk.content, end="", flush=True)
            total_tokens += len(chunk.content.split())

        print(f"Timely: {response}")
        # End the diagnostic experiments' timing.
        end_time = time.time()

        # Calculate and output the model performance data.
        calculate_model_diagnostics(start_time, end_time, total_tokens)


if __name__ == "__main__":
    main()
