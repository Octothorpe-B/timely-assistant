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
        temperature=0.35,
        max_tokens=150,  # Maximum number of tokens in the generated response
        top_p=0.9,  # Top-p (nucleus) sampling
        frequency_penalty=0.5,  # Penalize new tokens based on their existing frequency
        presence_penalty=0.5,  # Penalize new tokens based on whether they appear in the text so far
        stream=True,  # Enable streaming of the response
    )

    # Define a prompt template with the new structure
    prompt = PromptTemplate(
        input_variables=["question"],
        template="<|system|>\nYou are a helpful assistant. Your answers stick closely to what the user requests for you, and you do not deviate from the key elements of the request. If you do not know the answer for something please do not take a guess and just move on. <|end|>\n<|user|>\nQuestion: {question}<|end|>\n<|assistant|>",
    )

    # Create a chain by combining the prompt and the model
    chain = prompt | chat_model

    # Define the question
    question = "Please give step by step instructions on how I can include book writing into my daily routine, including on how to motivate myself if I don't feel like it. You are helping the user which struggles with breaking down large tasks and needs help from technology to help them know how to perform tasks step by step. Please number the steps and provide clear instructions. While you are providing all of the steps please be concise and clear in your instructions. The instructions should be as brief as possible an not exceeding two sentences per step."

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
