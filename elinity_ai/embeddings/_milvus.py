from pymilvus import MilvusClient
from dotenv import load_dotenv
from pymilvus import model
import os 

load_dotenv()


class MilvusDB: 
    def __init__(self,collection_name="tenants",dim=768):
        self._uri = os.getenv("MILVUS_URI")
        if not self._uri: 
            raise RuntimeError("MILVUS_URI not found")
        self._token=os.getenv("MILVUS_TOKEN")
        if not self._token:
            raise RuntimeError("MILVUS_TOKEN not found") 
        self.dim=dim
        self.collection_name=collection_name
        self.embedding_fn = model.DefaultEmbeddingFunction()
        self.client  = MilvusClient(uri=self._uri,token=self._token)
        if not self.client.has_collection(collection_name="tenants"):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    dimension=self.dim,
                )
    def embed_docs(self,docs):  
        return self.embedding_fn.encode_documents(docs)
        
    def upsert(self,data):
        res = self.client.insert(collection_name=self.collection_name,data=data)
        return res
    
    def query(self,query): 
        return self.client.query(query)
        
milvus_client = MilvusDB()