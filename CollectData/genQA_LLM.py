import os
import json
import time
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from constant import CONTENT_FOLDER, NUM_QA, QA_FOLDER
from system_prompt import SYSTEM_PROMPT, USER_PROMPT
import tiktoken
import math

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Ensure output folder exists
os.makedirs(QA_FOLDER, exist_ok=True)

# GPT-3.5-Turbo-16k settings
model_name = "gpt-3.5-turbo-16k"
MAX_CONTEXT = 16385  # Model's max token limit

# Function to count tokens
def count_tokens(text, model="gpt-3.5-turbo-16k"):
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

# Function to split text into overlapping batches
def split_text_into_batches(text, max_tokens=12000, overlap_tokens=500, model="gpt-3.5-turbo-16k"):
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    batches = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        batch_tokens = tokens[start:end]
        batch_text = enc.decode(batch_tokens)
        batches.append(batch_text)
        start += max_tokens - overlap_tokens
    return batches

# Function to generate QA pairs with retry logic for missing pairs
def generate_qa_pairs(content_text, numb_pairs, max_retries=3):
    attempt = 0
    generated_pairs = []

    while attempt < max_retries and len(generated_pairs) < numb_pairs:
        try:
            # Construct prompt and calculate input tokens
            prompt = USER_PROMPT.format(NUM_PAIRS=str(numb_pairs - len(generated_pairs)), INPUT_CONTENT=content_text)
            system_tokens = count_tokens(SYSTEM_PROMPT)
            user_tokens = count_tokens(prompt)
            content_tokens = count_tokens(content_text)
            input_tokens = system_tokens + user_tokens
            print(f"System prompt: {system_tokens} tokens, User prompt: {user_tokens} tokens, Content: {content_tokens} tokens, Total input: {input_tokens} tokens")

            # Ensure enough space for response
            max_response_tokens = min(8000, MAX_CONTEXT - input_tokens)
            if max_response_tokens < 500:  # Minimum reasonable output
                raise ValueError(f"Input tokens ({input_tokens}) leave insufficient room for response ({max_response_tokens}). Reduce batch size or prompt length.")

            print(f"Processing batch with {input_tokens} tokens, requesting {numb_pairs - len(generated_pairs)} more QA pairs, max response: {max_response_tokens} tokens...")

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_response_tokens,
                stop=None  # Ensure it doesn't stop early
            )

            if not response or not hasattr(response, "choices") or not response.choices:
                print("Error: Empty response from API, retrying...")
                attempt += 1
                time.sleep(2 ** attempt)
                continue

            result_text = response.choices[0].message.content.strip()
            start_idx = result_text.find('[')
            end_idx = result_text.rfind(']') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = result_text[start_idx:end_idx]
                new_pairs = json.loads(json_str)

                if isinstance(new_pairs, list):
                    generated_pairs.extend(new_pairs)
                    generated_pairs = generated_pairs[:numb_pairs]  # Trim excess if over-generated
                    print(f"Total generated so far: {len(generated_pairs)}/{numb_pairs}")
                else:
                    print("Error: Unexpected format in JSON response, retrying...")

            else:
                print("Error: No valid JSON in response, retrying...")
                attempt += 1
                time.sleep(2 ** attempt)
                continue

        except OpenAIError as e:
            if e.http_status == 429:
                delay = 2 ** attempt
                print(f"Rate limit hit, waiting {delay}s...")
                time.sleep(delay)
            else:
                print(f"API Error: {e}, retrying...")
                attempt += 1
                time.sleep(2)
        except ValueError as e:
            print(f"Error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}, retrying...")
            attempt += 1
            time.sleep(2)

    print(f"Final generated: {len(generated_pairs)}/{numb_pairs}")
    return generated_pairs

# Main function to process all text files
def main():
    for txt_file in os.scandir(CONTENT_FOLDER):
        if txt_file.is_file() and txt_file.name.endswith('.txt'):
            file_name = txt_file.name.split('.')[0]
            output_file = os.path.join(QA_FOLDER, f"{file_name}_qa.json")
            temp_file = os.path.join(QA_FOLDER, f"{file_name}_qa_temp.json")

            if os.path.exists(output_file):
                print(f"Skipping {txt_file.name}, QA file already exists.")
                continue
            
            print("*"*50)
            print(f"Processing {txt_file.name}...")
            with open(txt_file.path, 'r', encoding='utf-8') as f:
                content = f.read()

            total_tokens = count_tokens(content)
            print(f"Total tokens in file: {total_tokens}")

            batches = split_text_into_batches(content, max_tokens=12000, overlap_tokens=500)
            num_batches = len(batches)
            print(f"Processing {num_batches} overlapping batches...")

            all_qa_pairs = []
            if os.path.exists(temp_file):
                with open(temp_file, 'r', encoding='utf-8') as f:
                    all_qa_pairs = json.load(f)

            if num_batches == 1:
                numb_pairs_list = [NUM_QA]
            else:
                avg_pairs = math.ceil(NUM_QA / num_batches)
                numb_pairs_list = [avg_pairs] * num_batches
                numb_pairs_list[-1] = max(1, NUM_QA - sum(numb_pairs_list[:-1]))

            for i, (batch, numb_pairs) in enumerate(zip(batches, numb_pairs_list)):
                if i < len(all_qa_pairs) // numb_pairs:
                    print(f"Skipping batch {i+1}/{num_batches}, already processed.")
                    continue

                print(f"Processing batch {i+1}/{num_batches}, requesting {numb_pairs} QA pairs...")
                qa_pairs = generate_qa_pairs(batch, numb_pairs)

                if qa_pairs:
                    all_qa_pairs.extend(qa_pairs)
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump(all_qa_pairs, f, ensure_ascii=False, indent=2)

            if all_qa_pairs:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(all_qa_pairs, f, ensure_ascii=False, indent=2)
                os.remove(temp_file)
                print(f"Successfully generated {len(all_qa_pairs)} QA pairs. Saved to {output_file}")
            else:
                print(f"Failed to generate QA pairs for {txt_file.name} (No valid QA pairs found).")

            print("*"*50)

if __name__ == "__main__":
    main()