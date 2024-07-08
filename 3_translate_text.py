from googletrans import Translator
import time

from tqdm import tqdm

def _translate(chunk, translator):
    translated = translator.translate(chunk, src='en', dest='it')
    translated_sentences = translated.text.split('. ')  # Split translated text into sentences
    translated_text = '. '.join(translated_sentences)  # Join translated sentences
    return translated_text

def translate_text(input_file, output_file):
    # Read input text from the file
    with open(input_file, 'r', encoding='utf-8') as f:
        input_text = f.read().strip()
    
    # Split input text into sentences
    sentences = input_text.split('. ')
    
    # Translate text from English to Italian in chunks of 5 sentences
    translator = Translator()
    translated_chunks = []
    chunk_size = 50  # Number of sentences to translate in each chunk
    for i in tqdm(range(0, len(sentences), chunk_size)):
        chunk = '. '.join(sentences[i:i+chunk_size])  # Join X sentences into one chunk
        try:
            translated_text = _translate(chunk, translator)
            translated_chunks.append(translated_text)
        except Exception as ex:
            print(f"Translation failed for chunk {i+1}-{i+chunk_size}. Error: {ex}")
            print("Length in characters:", len(chunk))
            translated_chunks.append("")  # Append empty string for failed translations
            # split chunk into smaller chunks
            _sentences = chunk.split('. ')
            rel = chunk_size // 2
            for j in range(0, len(_sentences), rel):
                _chunk = '. '.join(_sentences[j:j+rel])
                try:
                    translated_text = _translate(_chunk, translator)
                    translated_chunks[-1] += translated_text
                except Exception as ex:
                    print(f"Translation failed for chunk {j+1}-{j+5}. Error: {ex}")
                    print("Length in characters:", len(_chunk))
                    translated_chunks[-1] += ""

        time.sleep(1)  # Add a small delay between API calls
    
    # Write translated chunks to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in translated_chunks:
            f.write(chunk + '\n')

# File paths
input_file = 'output.txt'
output_file = 'output.ita.txt'

# Translate and save the text in chunks
translate_text(input_file, output_file)
