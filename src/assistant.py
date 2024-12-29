"""File to handle running the LLM AI assistant."""

from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
import time
import json
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


# NOTE: Global variable to store the message history.
# For future development the store is where you would connect to the message history database.
store = {}


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        """Clear the message history"""
        self.messages = []


def get_session_history(user_id: str, conversation_id: str) -> BaseChatMessageHistory:
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


def save_json_to_list(json_file):
    """Function to save the JSON data to a list."""
    # Parse the JSON response
    try:
        # Load the JSON data from the file.
        response_json = json.loads(response)

        # Extract and store relevant values.
        # NOTE: In order to add new classifications you need to manually include them in in this extracted_values dictionary.
        extracted_values = {
            "classification": response_json.get("classification"),
            "sub_action": response_json.get("sub-action"),
            "time": response_json.get("time"),
            "sub-time": response_json.get("sub-time"),
            "tone": response_json.get("tone")
        }

        # Format the extracted values as a string.
        dict_string = ", ".join(f"{key}: {value}" for key, value in extracted_values.items())

        return dict_string

    except json.JSONDecodeError as e:
        print(f"\nError parsing JSON response: {e}")
        return None


def initialize_classification_model():
    """Function to initialize the model for classifying the user's question."""
    # Pre answer prompt template for determining how to answer the question and what actions to take on behalf of the user.

    # Initialize the Ollama model with parameters
    chat_model = ChatOllama(
        model = "phi3:3.8b",
        temperature = 0.0,
        top_p = 0.9,  # Top-p (nucleus) sampling
        frequency_penalty = 0.2,  # Penalize new tokens based on their existing frequency
        presence_penalty = 0.2,  # Penalize new tokens based on whether they appear in the text so far
        stream = True,  # Enable streaming of the response
        max_tokens = 50,  # Limit the number of tokens generated
        format = "json",  # Specify the output format
    )

    # Define the different prompts used for running the model.
    f = open("src/prompt-templates/classifier-prompt.txt", "r")
    classification_prompt_template = f.read()

    # Define a prompt template with the new structure.
    prompt = PromptTemplate(
        input_variables=["question"],
        template= classification_prompt_template
    )

    # Create a chain by combining the prompt and the model.
    chain = prompt | chat_model

    # Return the classification AI model chain.
    return chain


def initialize_conversational_model(classifier_values):
    """Function to initialize the model for conversational responses."""
    # Initialize the Ollama model with parameters
    chat_model = ChatOllama(
        model="phi3:3.8b",
        temperature=0.1,
        top_p=0.9,  # Top-p (nucleus) sampling
        frequency_penalty=0.2,  # Penalize new tokens based on their existing frequency
        presence_penalty=0.2,  # Penalize new tokens based on whether they appear in the text so far
        stream=True,  # Enable streaming of the response
    )

    # Prompt template for handling the model's conversational questions.
    f = open("src/prompt-templates/conversation-prompt.txt", "r")
    conversation_prompt_template = f.read()

    # NOTE: Legacy model template for phi-3 3.8b
    # default_model_prompt_template = "<|system|>\n <|end|>\n<|user|>\nQuestion: {question}<|end|>\n<|assistant|>"
    print(classifier_values)
    conversation_prompt_template = conversation_prompt_template + "\nThe following data are the different semantic classifications of the user's prompts. Please use this information when crafting your response.\n" + classifier_values

    # Define the prompt template with placeholders for history and question
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", conversation_prompt_template),
            MessagesPlaceholder(variable_name="history"),
            ("user", "Question: {question}"),
        ]
    )

    # Create a chain by combining the prompt and the model.
    chain = prompt | chat_model

    # Wrap the chain with message history management.
    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history=get_session_history,
        input_messages_key="question",
        history_messages_key="history",
        history_factory_config=[
            ConfigurableFieldSpec(
                id="user_id",
                annotation=str,
                name="User ID",
                description="Unique identifier for the user.",
                default="",
                is_shared=True,
            ),
            ConfigurableFieldSpec(
                id="conversation_id",
                annotation=str,
                name="Conversation ID",
                description="Unique identifier for the conversation.",
                default="",
                is_shared=True,
            ),
        ],
    )

    # Return the conversational AI model chain with message history.
    return with_message_history


if __name__ == "__main__":

    # Initialize the classification model to determine the type of question.
    classification_chain = initialize_classification_model()

    while True:
        # Define the question
        question = input(" > ")

        # If the user types "exit", then exit the program.
        if str(question) == "exit" or str(question) == "quit":
            break
        else:
            # Initialize the response variable to store the model's response.
            response = ""

            # Start the diagnostic experiments' timing and initialize the analytics .
            start_time = time.time()
            total_tokens = 0

            # Run the chain with the question using invoke and stream the response
            for chunk in classification_chain.stream({"question": question}):
                response += chunk.content
                print(chunk.content, end="", flush=True)
                total_tokens += len(chunk.content.split())

            classifier_values = save_json_to_list(response)

            # Initialize the conversational model.
            with_message_history = initialize_conversational_model(classifier_values)

            # Print out a blank line to separate the lines in the terminal.
            print()

            response = ""

            for chunk in with_message_history.stream(
                {"question": question, "history": ""},
                config={"configurable": {"user_id": "129", "conversation_id": "1"}},
            ):
                response += chunk.content
                print(chunk.content, end="", flush=True)
                total_tokens += len(chunk.content.split())

            # End the diagnostic experiments' timing.
            end_time = time.time()

            # Calculate and output the model performance data to the terminal.
            calculate_model_diagnostics(start_time, end_time, total_tokens)
