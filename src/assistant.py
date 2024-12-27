"""File to handle running the LLM AI assistant."""

from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
import time


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
        format="json",  # Specify the Output format
        max_tokens=50
    )

    # Define the different prompts used for running the model.
    
    # Pre answer prompt template for determining how to answer the question and what actions to take on behalf of the user.
    f = open("src/prompt-templates/classifier-prompt.txt", "r")
    classification_prompt_template = f.read()

    # Standard chatting model template for the assistant.
    default_model_prompt_template = "<|system|>\n <|end|>\n<|user|>\nQuestion: {question}<|end|>\n<|assistant|>"


    # Define a prompt template with the new structure
    prompt = PromptTemplate(
        input_variables=["question"],
        template= classification_prompt_template
    )

    # Create a chain by combining the prompt and the model
    chain = prompt | chat_model

    # Define the question
    question = "Hey timely can you remind me to leave for my appointment at the time I need to to get there 15 minutes before it starts?"

    # Start the diagnostic experiments' timing.
    start_time = time.time()

    # Run the chain with the question using invoke and stream the response
    total_tokens = 0
    response = ""
    # Print out a blank line to separate the lines in the terminal.
    print()

    for chunk in chain.stream({"question": question}):
        response += chunk.content
        print(chunk.content, end="", flush=True)
        total_tokens += len(chunk.content.split())

    # End the diagnostic experiments' timing.
    end_time = time.time()

    # Calculate and output the model performance data.
    calculate_model_diagnostics(start_time, end_time, total_tokens)


if __name__ == "__main__":
    main()
