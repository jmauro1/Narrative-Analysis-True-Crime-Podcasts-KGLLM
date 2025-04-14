"""
USAGE 
1. Replace input_file in the main method with the .txt file containing the query you want to be asked
2. Replace context_files in the main mehtod with all files related to the topic at hand
"""
import openai
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import tiktoken
from datetime import datetime

# Set your OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

def get_text_embedding(text):
    """Get the embedding for a given text using OpenAI's text-embedding-3-small model."""
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response['data'][0]['embedding']

def get_gpt4_response(prompt):
    """Generate a response using GPT-4o-mini model."""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return response.choices[0].message['content'].strip()

def load_input_file(file_path):
    """Load text from a .txt file."""
    with open(file_path, 'r') as file:
        return file.read().strip()

def save_results(input_text, response, output_file):
    """Save the input text and generated response to an output file."""
    with open(output_file, 'w') as file:
        file.write("Input:\n")
        file.write(input_text + "\n\n")
        file.write("Response:\n")
        file.write(response)

def get_num_tokens(texts, model):
    num_tokens = []
    encoding = tiktoken.encoding_for_model(model)
    for text in texts:
        num_tokens.append(len(encoding.encode(text)))
    return num_tokens

def my_text_splitter(input_text, chunk_size=1200, separator=None, model='gpt-4o-mini'):
    if separator is None:
        separator = ["\n\n", ".", " "]

    if not separator:
        return []
    outputs = []
    sep = separator[0]
    seg_texts = input_text.split(sep)
    text_tokens = get_num_tokens(seg_texts, model)
    temp_tokens = 0
    for text, text_token in zip(seg_texts, text_tokens):
        if not text:
            continue
        if temp_tokens + text_token <= chunk_size:
            if temp_tokens == 0:
                outputs.append(text)
            else:
                outputs[-1] += sep + text
            temp_tokens += text_token
        else:
            if text_token > chunk_size:
                sub_output = my_text_splitter(text, chunk_size, separator[1:])
                outputs.extend(sub_output)
                temp_tokens = 0
            else:
                outputs.append(text)
                temp_tokens = text_token

    return outputs

def generate_rag_response(input_text, context_texts, k = 5):
    """Generate a RAG response by combining retrieval and generation. Finds the top k most related chunks to input"""
    # Embed the input text
    input_embedding = np.array(get_text_embedding(input_text)).reshape(1, -1)

    # Embed context chunks
    context_embeddings = []

    overall_text_chunks = []
    
    for text in context_texts:
        chunks = my_text_splitter(text)
        embeddings = [get_text_embedding(chunk) for chunk in chunks]
        context_embeddings.extend(embeddings)
        overall_text_chunks.extend(chunks)

    context_embeddings = np.array(context_embeddings)

    # Compute similarities
    similarities = cosine_similarity(input_embedding, context_embeddings).flatten()

    # Retrieve the top K most relevant context chunks
    top_k_indices = np.argsort(similarities)[-k:]  # Get indices of top K chunks
    top_k_chunks = [overall_text_chunks[i] for i in top_k_indices]

    # Create prompt with the top K context chunks
    context_text = "\n\n".join(top_k_chunks)
    prompt = f"Context:\n{context_text}\n\nQuestion: {input_text}\nAnswer:"

    # Get GPT-4o-mini response
    return get_gpt4_response(prompt)

def main():
    input_file = "testQueries.txt" # Replace with your .txt file path
    context_files = ["./ragtest/input/text_chunks.txt"]  # Replace with data model should use in the RAG, it can be a list of many files

    # Load input and context texts
    input_text = load_input_file(input_file)
    context_texts = [load_input_file(file) for file in context_files]

    # Generate RAG response
    response = generate_rag_response(input_text, context_texts)
    print("Response:", response)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"naiveRAGoutput_{timestamp}.txt"

    save_results(input_text, response, output_file)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()


