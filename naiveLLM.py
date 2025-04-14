import argparse
import openai
import os
from openai import OpenAI

client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

def get_gpt4o_mini_response(query):
    # This function interacts with the GPT-4o-mini model using the ChatCompletion endpoint
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ],
        max_tokens=4000
    )
    return response.choices[0].message.content.strip()

def main():
    parser = argparse.ArgumentParser(description="Ask GPT-4o-mini a query and get a response.")
    parser.add_argument('query', type=str, help='The query to ask GPT-4o-mini')
    args = parser.parse_args()

    input_query = "In reference to season 1 of the Serial Podcast: " + args.query 

    response = get_gpt4o_mini_response(input_query)
    print("Response from GPT-4o-mini:")
    print(response)

if __name__ == "__main__":
    main()
