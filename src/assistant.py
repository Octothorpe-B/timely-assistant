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
from globals import memory_storage  # Importing the global variable
import actions


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
    if (user_id, conversation_id) not in memory_storage:
        memory_storage[(user_id, conversation_id)] = InMemoryHistory()
    return memory_storage[(user_id, conversation_id)]


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


def save_json_to_dict(response):
    """Function to save the JSON data to a dictionary."""
    # Parse the JSON response
    try:
        # Load the JSON data from the file.
        response_json = json.loads(response)

        # Extract and store relevant values.
        # NOTE: In order to add new classifications you need to manually include them in in this extracted_values dictionary.
        extracted_values = {
            "classification": response_json.get("classification"),
            "sub-action": response_json.get("sub-action"),
            "time": response_json.get("time"),
            "sub-time": response_json.get("sub-time"),
            "tone": response_json.get("tone"),
            "complexity": response_json.get("complexity"),
        }

        # Return the extracted values from the JSON response.
        return extracted_values

    except json.JSONDecodeError as e:
        print(f"\nError parsing JSON response: {e}")
        return None


def initialize_classification_model():
    """Function to initialize the model for classifying the user's question."""
    # Pre answer prompt template for determining how to answer the question and what actions to take on behalf of the user.

    # Initialize the Ollama model with parameters
    chat_model = ChatOllama(
        model="phi3:3.8b",
        temperature=0.0,
        top_p=0.9,  # Top-p (nucleus) sampling
        frequency_penalty=0.2,  # Penalize new tokens based on their existing frequency
        presence_penalty=0.2,  # Penalize new tokens based on whether they appear in the text so far
        stream=True,  # Enable streaming of the response
        max_tokens=50,  # Limit the number of tokens generated
        format="json",  # Specify the output format
    )

    # Define the different prompts used for running the model.
    with open("src/prompt-templates/classifier-prompt.txt", "r") as f:
        classification_prompt_template = f.read()


    classifier_prompt = PromptTemplate(
        input_variables=["question"], template=classification_prompt_template
    )

    # Create a chain by combining the prompt and the model.
    classification_model_chain = classifier_prompt | chat_model

    # Return the classification AI model chain.
    return classification_model_chain


def initialize_conversational_model(classifier_values, action_prompt):
    """Function to initialize the model for conversational responses."""
    # Initialize the Ollama model with parameters
    chat_model = ChatOllama(
        model="llama3.1:8b",
        temperature=0,
        top_p=0.9,  # Top-p (nucleus) sampling
        frequency_penalty=0.2,  # Penalize new tokens based on their existing frequency
        presence_penalty=0.2,  # Penalize new tokens based on whether they appear in the text so far
        stream=True,  # Enable streaming of the response
    )

    # Join the list into a single string
    classifier_values_str = ", ".join(classifier_values)

    # Ensure action_prompt is not None
    if action_prompt is None:
        action_prompt = "null"

    # Define the prompt template with placeholders for history and question
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", action_prompt),
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


def query_classifier(classification_model, question):
    """Function to query the AI assistant with a question."""
    # Initialize the response variable to store the model's response and the tokens variable.
    response = ""
    total_tokens = 0

    # Run the chain with the question using invoke and stream the response
    for chunk in classification_model.stream({"question": question}):
        response += chunk.content
        print(chunk.content, end="", flush=True)
        total_tokens += len(chunk.content.split())

    classifier_values = save_json_to_dict(response)

    # Return the classifier values from the AI assistant.
    return classifier_values, total_tokens


def query_ai_assistant(classifications, conversational_model, question):
    """Function to query the AI assistant with a question."""
    # Print out a blank line to separate the lines in the terminal.
    print()

    # Initialize the response variable to store the model's response.
    response = ""
    total_tokens = 0

    for chunk in conversational_model.stream(
        {"question": question, "history": ""},
        config={"configurable": {"user_id": "129", "conversation_id": "1"}},
    ):
        response += chunk.content
        # print(chunk.content, end="", flush=True)
        total_tokens += len(chunk.content.split())

    # Return the response from the AI assistant.
    return response, total_tokens
