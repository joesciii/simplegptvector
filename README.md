# Simple GPT / Vector Database interfacing with UI

GUI to allow GPT to interact with data external to it's training or context too large for chat. Supports links to PDFs, html pages and plaintext.

Base functionality from here https://github.com/greg643/gpt including chunking and interfacing with apis. Chosen due to not requiring langchain or other helper libs. "Close to base APIs".

Apparently pinecone isn't needed https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb

But for now it's used. You need an OpenAI API key & a Pinecone env with API key. Make these env vars in the code if you want, hardcoded atm.

### Prerequisites

lots. check imports.


