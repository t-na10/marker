import logging
import os
import re
import sys

import backoff
import dotenv
from openai import OpenAI, RateLimitError
from tqdm import tqdm


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

dotenv.load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')
openai = OpenAI(api_key=api_key)

# system prompt
SYSTEM_PROMPT_PATH = "scripts/prompt/system_prompt.txt"
with open(SYSTEM_PROMPT_PATH, "r") as f:
    SYSTEM_PROMPT = f.read()


@backoff.on_exception(backoff.expo, RateLimitError)
def get_completions_with_backoff(**kwargs):
    """backoff for RateLimitError."""
    return openai.chat.completions.create(**kwargs)

def split_text(text, max_chunk_size):
    """ split text into smaller chunks.

    Args:
        text (str):
        max_chunk_size (int):

    Returns:
        list: text(str) is split into smaller chunks.
    """
    chunks = []
    while len(text) > max_chunk_size:
        split_pos = text.rfind('\n', 0, max_chunk_size)
        if split_pos == -1:
            split_pos = max_chunk_size
        chunks.append(text[:split_pos])
        text = text[split_pos:].strip()
    chunks.append(text)
    return chunks

def format_markdown(file_path):
    """Re-format Markdown file using GPT-4.

    Args:
        file_path (Path): Path to the Markdown file.
    """
    content = file_path.read_text(encoding='utf-8').replace(' ', '').strip()
    max_chunk_size = 5000
    chunks = split_text(content, max_chunk_size)

    formatted_chunks = []
    for chunk in chunks:
        try:
            response = get_completions_with_backoff(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Chunk: <ocr>{chunk}</ocr>"},
                ]
            )
            formatted_chunk = response.choices[0].message.content
            match = re.search(r"<markdown>(.*?)</markdown>", formatted_chunk, re.DOTALL)
            if match:
                extracted_content = match.group(1).strip()
                formatted_chunks.append(extracted_content)
                logging.info(f"Formatted chunk: {extracted_content}")
            else:
                formatted_chunks.append(chunk)
                logging.warning(f"Chunk without markdown tags: {chunk}")
        except Exception as e:
            logging.error(f"Error formatting Markdown chunk: {e}")
            formatted_chunks.append(chunk)

    formatted_content = '\n\n'.join(formatted_chunks)
    formatted_file_path = file_path.with_name(file_path.stem + "_formatted" + file_path.suffix)
    formatted_file_path.write_text(formatted_content, encoding='utf-8')

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("ex. python gpt_formatter.py <path_to_markdown_file>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists() or not file_path.is_file():
        print(f"not found file: {file_path}")
        sys.exit(1)

    format_markdown(file_path)
