from typing import Tuple

import os
import sys
import time

from dotenv import load_dotenv
import pandas as pd
import numpy as np
import wikipedia
from bs4 import BeautifulSoup as BS4
from spacy.lang.en import English
import tiktoken
import openai
from openai.embeddings_utils import distances_from_embeddings


WIKI_PAGE = 'wiki/Alan_Turing'

TOKEN_MODEL = 'cl100k_base'

EMBEDDING_MODEL = 'text-embedding-ada-002'

COMPLETION_MODEL = 'text-davinci-003'

MAX_CHUNK_TOKENS = 256


def get_text(textfile, wikipage):
    if not os.path.exists(textfile):
        wiki = wikipedia.page(wikipage)
        text = BS4(wiki.html(), 'html.parser').get_text()

        with open(textfile, 'w') as f:
            f.write(text)
        return text

    with open(textfile, 'r') as f:
        return f.read()


def text_preproc(serie: str):
    serie = serie.replace('\n', ' ')
    serie = serie.replace('\\n', ' ')
    serie = serie.replace('  ', ' ')
    serie = serie.replace('  ', ' ')

    return serie


def group_chunks(sentences, max_tokens) -> Tuple[str, int]:
    tokenizer = tiktoken.get_encoding(TOKEN_MODEL)

    # Get the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(" " + sentence))
                for sentence in sentences]

    chunks = []
    tokens_so_far = 0
    chunk = []

    for n, sentence in zip(n_tokens, sentences):
        if n + tokens_so_far > max_tokens:
            chunks.append((tokens_so_far, '. '.join(chunk) + '.'))
            tokens_so_far = 0
            chunk = []

        tokens_so_far += n
        chunk.append(sentence)

    return chunks


def spacy_paragraphs(text) -> Tuple[str, int]:
    chunks = []
    existing_ps = []

    # text = text_preproc(text)
    nlp = English()
    nlp.add_pipe('sentencizer')

    paragraphs = text.split('\n\n')
    for i, p in enumerate(paragraphs):
        existing_ps.append(p)

        if len(p) < 32 and i < len(paragraphs)-1:
            continue

        cs = spacy_chunks(nlp, '\n'.join(existing_ps))
        chunks += cs
        existing_ps = []

    return chunks


def spacy_chunks(pipeline, text) -> Tuple[str, int]:
    doc = pipeline(text)
    sentences = [sent.text for sent in doc.sents]

    return group_chunks(sentences, max_tokens=MAX_CHUNK_TOKENS)


def create_openai_embeddings(sentences):
    RETRIES = 10

    embedding_data = pd.DataFrame(sentences, columns=['text'])

    embeddings = []
    for sentence in sentences:
        for _ in range(RETRIES):
            try:
                print('Calling openAI embedding API...')
                embedding = openai.Embedding.create(
                    input=[sentence], model=EMBEDDING_MODEL,
                )['data'][0]['embedding']
            except openai.error.RateLimitError:
                print('Error: hit rate limiter, retrying...')
                time.sleep(10)
            except Exception:
                raise Exception
            else:
                break
        embeddings.append(embedding)

    embedding_data['embedding'] = embeddings
    return embedding_data


def get_embeddings(csvfile, chunks):
    if os.path.exists(csvfile):
        embedding_data = pd.read_csv(csvfile)
        embedding_data['embedding'] = embedding_data['embedding'].apply(
            eval).apply(np.array)
    else:
        embedding_data = create_openai_embeddings(chunks)
        embedding_data.to_csv(csvfile)

    return embedding_data


def create_context(question, embedding_data, max_chunks=5, max_length=1800):
    question_embedding_data = create_openai_embeddings([question])
    question_embedding = question_embedding_data['embedding'][0]

    embedding_data['distances'] = distances_from_embeddings(
        question_embedding, embedding_data['embedding'].values,
        distance_metric='cosine')

    cur_len = 0
    contexts = []

    n = 0
    for _, row in embedding_data.sort_values('distances',
                                             ascending=True).iterrows():
        print('Adding context...')
        if n > max_chunks:
            break
        n += 1

        # Add the length of the text to the current length
        cur_len += row['ntokens'] + 4
        if cur_len > max_length:
            break
        contexts.append(row['text'])

    return '\n\n###\n\n'.join(contexts)


def ask_question(question,
                 embedding_data,
                 max_embedding_length=1800,
                 max_tokens=600,
                 model='text-davinci-003'):
    context = create_context(question, embedding_data,
                             max_length=max_embedding_length)
    prompt = 'Answer the question based on the context, and if it ' + \
        'cannot be answered based on the context, say "I don\'t know"\n' + \
        f'Context:\n{context}\n' + \
        f'Question: {question}\n' + \
        'Answer:'

    print('Calling openAI completion API...')
    print('Prompt: ', prompt)
    response = openai.Completion.create(
        prompt=prompt,
        temperature=0,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        model=model,
    )

    return response['choices'][0]['text'].strip()


def main():
    wikiname = WIKI_PAGE.split('/')[-1]

    text = get_text(f'{wikiname}.txt', WIKI_PAGE)

    chunks = spacy_paragraphs(text)
    sentences = [sentence for _, sentence in chunks]

    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

    for chunk in chunks:
        print(chunk)

    embedding_data = get_embeddings(f'{wikiname}_embedding.csv', sentences)
    embedding_data['ntokens'] = pd.Series([n for n, _ in chunks])

    while True:
        try:
            question = input('Question: ')
            answer = ask_question(question, embedding_data)

            print('=' * 20)
            print(f'\n\nopenAI answer: {answer}\n\n')
            print('=' * 20)
        except KeyboardInterrupt:
            print('exiting...')
            sys.exit(1)


if __name__ == '__main__':
    main()
