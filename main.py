import argparse
import json
import os
import sys

from call_function import available_functions
from call_function import call_function
from dotenv import load_dotenv
from openai import OpenAI

from prompts import system_prompt


MAX_TURNS = 10

def main() -> None:
    # Read the prompt and output options from the command line.
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("user_prompt", type=str, help="Prompt to send to the LLM")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    # Load the API key from the environment (or a local .env file).
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable not set")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    # Start the conversation with the assistant's instructions and the user's prompt.
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]
    if args.verbose:
        print(f"User prompt: {args.user_prompt}\n")

    response = generate_content(client, messages, args.verbose)
       




def generate_content(client: OpenAI, messages: list, verbose: bool) -> None:
    for i in range(MAX_TURNS): 

        # Send the conversation and available tools to the model.
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=available_functions,
        )
        # Usage data is expected so token counts can be reported when requested.
        if not response.usage:
            raise RuntimeError("API response appears to be malformed")

        # Print token usage only when verbose output is enabled.
        if verbose:
            print("Prompt tokens:", response.usage.prompt_tokens)
            print("Response tokens:", response.usage.completion_tokens)

        # Add agent response to messages list to update context for future requests
        message = response.choices[0].message
        messages.append(message)

        # If the model did not request a tool, end loop and display text response.
        if not message.tool_calls:
            print("Response:")
            print(message.content)
            return 
        # If the maximum number of iterations is reached with no final response, exit
        elif i==MAX_TURNS:
            print("Maximum number of iterations reached")
            sys.exit(1)


        # Execute each function requested by the model.
        for tool_call in message.tool_calls:
            if tool_call.type != "function":
                continue
            
            # Run the requested function and ensure it returned a usable message.
            result_message = call_function(tool_call, verbose)

            if not result_message or not result_message.get("content"):
                raise RuntimeError(
                    f"Tool {tool_call.function.name!r} returned an empty message"
                )

            # if verbose flag used, print function output
            if verbose:
                print(f"-> {result_message['content']}")

            messages.append(result_message)
    


# Run the command-line entry point only when this file is executed directly.
if __name__ == "__main__":
    main()
