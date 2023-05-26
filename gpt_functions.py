import sys
print(sys.executable)
import platform
import os

#core data wrangling
import pandas as pd
#show all columns in dataframe
pd.set_option('display.max_columns', None)

import json
import xmltodict
from bs4 import BeautifulSoup #as bs
import time
import markdown as md
from ast import literal_eval

#regular expressions
import re
import io

#html requests
import requests

#for pinecone
from tqdm.auto import tqdm

#chatgpt
import openai
from openai import APIError
from openai.embeddings_utils import get_embedding
import pinecone

#for saving files
import pickle

#for reading PDFs
from pdfminer.high_level import extract_text
#from PyPDF2 import PdfReader
from uuid import uuid4

import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import tiktoken
import tkinter as tk
from tkinter import messagebox

#### OpenAI API Key

###GPT MODEL. FOR GPT-4, USE "gpt-4", 8000 TOKENS, 1000 CHUNK SIZE
global_model="gpt-3.5-turbo"
global_max_tokens = 4000
global_completions = 4
global_chunk_size = 500 #gpt-3.5 works better with smaller vector chunks
openai.api_key = "api key"

#### Pinecone API key

PINECONE_API_KEY = 'api key'
PINECONE_API_ENV = 'env name'

#### User Identification

headers = {
    'User-Agent': 'name',
    'From': 'email' 
}

#### Global Embed Model - gpt3.5 and 4 compatible

mbed_model = 'text-embedding-ada-002'

"""
Helper Functions:
Counting Tokens & Chunking Text

Using "tiktoken" counter which is the most precise estimator for GPT-4
Not all of these are needed but I'm including them all for now.
"""

#####
##### CLEAN AN IMPORTED PDF
#####

def clean_extracted_text(text):
    text = re.sub(r'\s+', ' ', text)  # remove extra white spaces
    text = re.sub(r'\n+', '\n', text)  # remove extra new lines
    text = re.sub(r'(\n\s*)+', '\n', text)  # remove extra spaces at the start of each line
    text = re.sub(r'\x0c', '', text)  # remove form feed characters
    text = re.sub(r'\u200b', '', text)  # remove zero width spaces
    #bad character list
    bad_chars = ['\xd7', '\n', '\x99m', "\xf0", '\uf8e7'] 
    for i in bad_chars : 
        text = text.replace(i, '') 
    return text

#####
##### CHUNK INPUT TEXT
#####

def break_up_file_to_chunks(text, chunk_size=int(global_max_tokens/4), overlap_size=100):
    tokens = word_tokenize(text)
    return list(break_up_file(tokens, chunk_size, overlap_size))

def break_up_file(tokens, chunk_size, overlap_size):
    if len(tokens) <= chunk_size:
        yield tokens
    else:
        chunk = tokens[:chunk_size]
        yield chunk
        yield from break_up_file(tokens[chunk_size-overlap_size:], chunk_size, overlap_size)

def convert_to_detokenized_text(tokenized_text):
    prompt_text = " ".join(tokenized_text)
    prompt_text = prompt_text.replace(" 's", "'s")
    return prompt_text

#####
##### GET CORRECT TOKENS FOR GPT4
#####

def num_tokens_from_string(string: str, encoding_name ="cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

"""
KEY FUNCTION #1:
CHUNK A DOCUMENT TO PINECONE

This function assumes you have already extracted some data source to clean text. 
Your source can be anything, just as long as the variable "text" is a clean string. 
I've included some PDF examples because that is common, but you could also use HTML text etc.

The code below uses helper functions to:
* Chunk your text into various sizes
* Call the OpenAI embeddings API
* Store the embeddings as vectors in Pinecone 

Some of the muggle magic in here:
* Using a free Pinecone database - everything in one database
* I try to avoid any helper libraries - eg, langchain - I'm trying to stay as close to what I consider "base" APIs
* I just delete the vector DB every time this is called, so you're guaranteed to be looking at one document at a time.

There is some detritus in all of these functions, because I'm using these functions for a bunch of other projects.
Because I haven't fully abstracted all the details, I just work around these when I find them.
"""



def chunk_to_pinecone(df):
    
    df_return = pd.DataFrame(columns=['GUID', 'Name', 'Link', 'Tokens', 'Chunk Number', 'Chunk Text', 'Embeddings'])

    #THIS IS OUR PINECONE DATABASE
    index_name = "test"
    
    # Initialize connection to Pinecone
    pinecone.init(
    api_key="api key", 
    environment="env name"
    )
    
    # Connect to the index and view index stats
    index = pinecone.Index(index_name)
    index.describe_index_stats()
    
    # # Check if index already exists, create it if it doesn't
    # if index_name not in pinecone.list_indexes():
    #  pinecone.create_index(index_name, dimension=1536, metric='dotproduct')
    
    # clear out a pinecone database
    index.delete(deleteAll='true', namespace='')
    #row = df_raw.iloc[0:1]
    # PINECONE - CREATE VECTOR DATABASE
    #for i, row in df_raw.iloc[0:1].iterrows():
        
    text = str(df['Text'][0])     
    text_chunks = break_up_file_to_chunks(text, chunk_size = global_chunk_size)

    #for chunk in text_chunks:
    for i, chunk in enumerate(text_chunks):
    
        clean_text = convert_to_detokenized_text(chunk)
        
        embed_model = 'text-embedding-ada-002'

        response = openai.Embedding.create(
          input = clean_text,
          model = embed_model
        )
        
        embed = response['data'][0]['embedding']
    
        time.sleep(2)
            
        new_row = {'GUID': df['GUID'][0],
               'Name': df['Name'][0], 
               'Link': df['Link'][0], 
               'Tokens': len(chunk),
               'Chunk Number': i, 
               'Chunk Text': clean_text, 
               'Embeddings': embed,
               }
        
        new_df = pd.DataFrame([new_row])
            
        df_return  = pd.concat([df_return , new_df], axis=0, ignore_index=True)
               
    # Convert the DataFrame to a list of dictionaries
    # chunks = df_sources[(df_sources['Age'] == 22)].to_dict(orient='records')
    chunks =  df_return.to_dict(orient='records')
            
    for chunk in chunks:
        upsert_response = index.upsert(
            vectors=[
                {
                'id': chunk['GUID'] + str(chunk['Chunk Number']), 
                'values': chunk['Embeddings'], 
                'metadata':{
                    'Name': chunk['Name'],
                    'Link': chunk['Link'],
                    'Text': chunk['Chunk Text']
                }}
                
            ],
            namespace=''
        )
    print(index.describe_index_stats())


"""
KEY FUNCTION #2:
ASK A QUESTION OF THE PINECONE DOCUMENT

This function assumes you have uploaded a vectorized document to Pinecone
Will simply ask one question at a time of that document, and return to the window.
"""

def ask(question):
    #question = questions['Tick Size Reform'][0]                
    # question = 'Does the text support access fee reform?'
    
    prompt_instr = " please limit your answer strictly to this question, and if the answer is unclear, please respond that the letter does not specifically address the question. "
              
    #THIS IS OUR PINECONE DATABASE
    index_name = "test"
    
    # Initialize connection to Pinecone
    pinecone.init(
    api_key="api key", 
    environment="env name"
    )
    
    # Connect to the index and view index stats
    index = pinecone.Index(index_name)
    index.describe_index_stats()
    
    user_input = question + prompt_instr
    
    embed_query = openai.Embedding.create(
        input=user_input,
        engine=mbed_model
    )
    
    # retrieve from Pinecone
    query_embeds = embed_query['data'][0]['embedding']
    
    # get relevant contexts (including the questions)
    response = index.query(query_embeds, top_k=global_completions, include_metadata=True)
    #, filter={"GUID": {"$eq": "1aee345a-82e0-4d70-88fc-15073c362c92"}} 
    
    contexts = [item['metadata']['Text'] for item in response['matches']]
    
    augmented_query = "\n\n---\n\n".join(contexts)+"\n\n-----\n\n"+user_input # + query
    
    # system message to assign role the model
    system_msg = f"""You are a helpul machine learning assistant and tutor. Answer questions based on the context provided, provide support for your answer, or say Unable to find reference."
    """
    
    chat = openai.ChatCompletion.create(
        model=global_model,
        max_tokens=int(global_max_tokens-3000),
        temperature=0,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "assistant", "content": "\n".join(contexts)},
            {"role": "user", "content": question}
        
        ]
    )
    
    answer = chat['choices'][0]['message']['content'].strip()
    if answer:
        print(answer)
        return answer
    else:
        return "No answer found."
    
#### EXTRACT FROM A WEB LINK
####

#url = 'https://files.smallpdf.com/files/eb31d6ab4316e4cfd249898cfd8f4167.pdf?name=test.pdf'

#r = requests.get(url, headers=headers, allow_redirects=True)

# pdfminer.six, a great library
#text = extract_text(io.BytesIO(r.content))

# helper function to remove characters
#text = clean_extracted_text(text)

####
#### EXTRACT FROM A SAVED PDF
####

# recycling the url variable
#url = 'local file'

#text = extract_text(url)

# Verify we have what we want
#print(text)

####
#### UPLOAD YOUR DOCUMENT TO PINECONE
####

# Each Vector will have a unqiue ID - for now, we are using python uuids + chunk numbers
# For various reasons, I am handling everything as dataframes.

""" uuid = str(uuid4())
new_row = {
            'GUID': uuid,
            'Name': url, 
            'Link': 'Link', ##detritus, leave alone
            'Tokens': num_tokens_from_string(text), 
            'Text': text,
            }

new_df = pd.DataFrame([new_row])

chunk_to_pinecone(new_df) """

def ask_question_from_gui():
    question = question_entry.get()
    if question:
        answer = ask(question)
        # Clear the previous answer
        answer_text.delete(1.0, tk.END)
        # Insert the new answer
        if answer:
            answer_text.insert(tk.END, answer)
    else:
        messagebox.showwarning("Warning", "Please enter a question.")

def upload_from_url():
    # Get the URL from the entry field
    url = url_entry.get()
    if url:
        try:
            r = requests.get(url, headers=headers, allow_redirects=True)
            text = extract_text(io.BytesIO(r.content))
            text = clean_extracted_text(text)

            uuid = str(uuid4())
            new_row = {
                        'GUID': uuid,
                        'Name': url, 
                        'Link': 'Link', #detritus, leave alone
                        'Tokens': num_tokens_from_string(text), 
                        'Text': text,
                        }

            new_df = pd.DataFrame([new_row])
            chunk_to_pinecone(new_df)
        except Exception as e:
            messagebox.showerror("Error", "There was an error processing the URL.\n" + str(e))
    else:
        messagebox.showwarning("Warning", "Please enter a URL.")

# Creating tkinter window
root = tk.Tk()
root.geometry("800x600") # You can set any size
root.title("OpenAI and Pinecone Query Interface")

# Creating a label for url input
url_label = tk.Label(root, text = "Enter a URL:")
url_label.pack()

# Creating a text field for url
url_entry = tk.Entry(root, width = 100)
url_entry.pack()

# Creating a button for submission
upload_button = tk.Button(root, text = "Upload from URL", command = upload_from_url)
upload_button.pack()

# Creating a label for question input
question_label = tk.Label(root, text = "Enter your question:")
question_label.pack()

# Creating a text field for question
question_entry = tk.Entry(root, width = 100)
question_entry.pack()

# Creating a button for submission
submit_button = tk.Button(root, text = "Submit", command = ask_question_from_gui)
submit_button.pack()

# Creating a text field for answer
answer_label = tk.Label(root, text = "Answer:")
answer_label.pack()

# Create a scroll bar
scrollbar_horizontal = tk.Scrollbar(root, orient = 'horizontal')
scrollbar_horizontal.pack(side = 'bottom', fill = 'x')

scrollbar_vertical = tk.Scrollbar(root)
scrollbar_vertical.pack(side = 'right', fill = 'y')

# Create text widget and specify size.
answer_text = tk.Text(root, width = 80, height = 10, wrap = 'word',
                      xscrollcommand = scrollbar_horizontal.set,
                      yscrollcommand = scrollbar_vertical.set)

answer_text.pack()

# Configure the scrollbars
scrollbar_horizontal.config(command = answer_text.xview)
scrollbar_vertical.config(command = answer_text.yview)

# Running the GUI
root.mainloop()