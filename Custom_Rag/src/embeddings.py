from langchain_openai import OpenAIEmbeddings

def create_embeddings(api_key):
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key,
    )
