# services/prompt_services.py
import openai
from fastapi import HTTPException
from qdrant_client import QdrantClient
from src.config.settings import HTTP_500_INTERNAL_SERVER_ERROR
from src.config.settings import MAX_NO_SEARCH_RESULTS_QDRANT
from src.config.settings import QDRANT_COLLECTION


class PromptServices:
    """
    Class handling various prompt services related operations.
    """

    # Constructor
    def __init__(self,
                 openai_api_key,
                 qdrant_url,
                 qdrant_api_key,
                 openai_embedding_model,
                 openai_gpt_model):

        self._open_api_key = openai_api_key
        self._qdrant_url = qdrant_url
        self._qdrant_api_key = qdrant_api_key
        self._openai_embedding_model = openai_embedding_model
        self._openai_gpt_model = openai_gpt_model

        self._openai_client = openai.OpenAI(api_key=self._open_api_key)
        self._qdrant_client = QdrantClient(host=self._qdrant_url,
                                           api_key=self._qdrant_api_key)
        self._system_prompt = ("You are an assistant with knowledge of financial market. "
                               "Please use the provided context to answer the question. "
                               "Use as much information from the context as possible. "
                               "If you do not have the information, "
                               "please do not make up the answer.")

    #############################################
    # Get the embedding of the query using the provided embedding model
    def get_embedding(self, query):

        # Get the embedding of the query
        try:
            embedding_response = self._openai_client.embeddings.create(
                input=query,
                model=self._openai_embedding_model
            )
        except Exception as e:
            raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        return embedding_response.data[0].embedding

    #############################################
    # Search for closest texts in Qdrant vector database
    def get_context(self, embedding, number_of_points):

        try:
            search_results = self._qdrant_client.search(
                collection_name=QDRANT_COLLECTION,
                query_vector=embedding,
                limit=number_of_points
            )
        except Exception as e:
            raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        return search_results

    #############################################
    def get_response_closest_points(self, query, search_results):
        """
        Get the context from the closest points retrieved from get_context()
        """

        context = ""
        for result in search_results:
            context += result.payload['text'] + "\n"

        try:
            chat_response = self._openai_client.chat.completions.create(
                model=self._openai_gpt_model,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "assistant", "content": context},
                    {"role": "user", "content": query}
                ]
            )
        except Exception as e:
            raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        return chat_response.choices[0].message.content.strip()

    #############################################
    def get_response_consecutive_points(self, query, search_results):
        """
        Get the context from points around the single closest point
        """

        context = ""
        qdrant_id = search_results[0].id

        half_number_of_points = MAX_NO_SEARCH_RESULTS_QDRANT//2
        search_results = self._qdrant_client.retrieve(
            collection_name=QDRANT_COLLECTION,
            # Get MAX_NO_SEARCH_RESULTS_QDRANT consecutive points
            # around the closest point
            ids=list(
                range(max(0, qdrant_id - half_number_of_points),
                      qdrant_id + half_number_of_points + 1))
        )
        

        for result in search_results:
            context += result.payload['text'] + "\n"

        try:
            chat_response = self._openai_client.chat.completions.create(
                model=self._openai_gpt_model,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "assistant", "content": context},
                    {"role": "user", "content": query}
                ]
            )
        except Exception as e:
            print("Exception :", str(e))

        return chat_response.choices[0].message.content.strip()