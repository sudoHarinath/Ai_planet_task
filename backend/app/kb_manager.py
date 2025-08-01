# from datasets import load_dataset
# from langchain.schema import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import WebBaseLoader
# from qdrant_client import QdrantClient, models
# from sentence_transformers import SentenceTransformer
# from fastembed import TextEmbedding, SparseTextEmbedding
# import torch # To check for CUDA availability
# from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
# # Use your specified embedding models
# DENSE_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# # For sparse, we will use a sentence-transformer based bi-encoder for simplicity here.
# # A true SPLADE model would require more complex setup.
# SPARSE_MODEL_NAME = "Qdrant/minicoil-v1"
# # dense_embedding_model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
# #     miniCOIL_model = SparseTextEmbedding(model_name="Qdrant/minicoil-v1")
# # Determine device for computations
# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# print(f"Knowledge Base Manager using device: {DEVICE}")

# # Initialize models once to be reused
# dense_embedding_model = TextEmbedding(DENSE_MODEL_NAME, device=DEVICE)
# sparse_embedding_model = SparseTextEmbedding(SPARSE_MODEL_NAME, device=DEVICE)

# def embed_documents(docs: list[str]) -> tuple[list[list[float]], list[list[float]]]:
#     """Embeds a list of documents using both dense and sparse models."""
#     dense_embeddings = dense_embedding_model.encode(docs, convert_to_tensor=False).tolist()
#     sparse_embeddings = sparse_embedding_model.encode(docs, convert_to_tensor=False).tolist()
#     return dense_embeddings, sparse_embeddings



# def create_new_kb(collection_name: str, source_type: str, source_name: str, file_path: str = None):
#     """
#     Loads data from a source, processes it, and stores it in a new Qdrant collection.
#     """
#     print(f"Creating new KB '{collection_name}' from source '{source_type}': '{source_name}'")
#     documents = []

#     # Step 1: Load Data
#     if source_type == 'gsm8k':
#         dataset = load_dataset("openai/gsm8k", "main")
#         train_data = dataset['train']
#         for item in train_data:
#             documents.append(Document(page_content=item['question'], metadata={'answer': item['answer']}))
    
#     elif source_type == 'math500':
#         dataset = load_dataset("HuggingFaceH4/MATH-500")
#         test_data = dataset['test']
#         for item in test_data:
#             documents.append(Document(page_content=item['problem'], metadata={'answer': item['solution']}))

#     elif source_type == 'pdf_url':
#         loader = WebBaseLoader(source_name)
#         documents = loader.load()
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
#         chunks = text_splitter.split_documents(documents)
    
#     # NEW: Handle direct PDF file uploads
#     elif source_type == 'pdf_file':
#         if not file_path:
#             raise ValueError("File path must be provided for 'pdf_file' source type.")
#         loader = PyPDFLoader(file_path)
#         documents = loader.load()
#         print(len(documents))
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
#         chunks = text_splitter.split_documents(documents)
    
#     print(f"Loaded {len(documents)} documents.")
#     if not documents:
#         print("No documents loaded, aborting KB creation.")
#         return

#     # Step 2: Setup Qdrant Client
#     client = QdrantClient(path=f"./qdrant_data")
    
#     # Use your specified Qdrant collection configuration

    
#     # FIX: Using your exact collection creation code with named vectors
#     client.create_collection(
#         collection_name=collection_name,
#         vectors_config={
#             "sentence-transformers/all-MiniLM-L6-v2": models.VectorParams(
#                 size=384,
#                 distance=models.Distance.COSINE,
#             ),
#         },
#         sparse_vectors_config={
#             "miniCOIL": models.SparseVectorParams(modifier=models.Modifier.IDF),
#         }
#     )
#     print(f"---KB_MANAGER: Qdrant collection '{collection_name}' created with correct schema.---")

#     # Embed and Upsert using your exact logic
#     print("---KB_MANAGER: Embedding documents...---")
#     dense_embeddings = list(dense_embedding_model.embed(doc.page_content for doc in chunks))
#     miniCOIL_embeddings = list(sparse_embedding_model.embed(doc.page_content for doc in chunks))
    
#     points = []
#     for idx, (dense_e, minicoil_e, doc) in enumerate(zip(dense_embeddings, miniCOIL_embeddings, chunks)):
#         point = models.PointStruct(
#             id=idx,
#             vector={
#                 "sentence-transformers/all-MiniLM-L6-v2": dense_e,
#                 "miniCOIL": minicoil_e.as_object(),
#             },
#             payload=doc.metadata or {"page_content": doc.page_content}
#         )
#         points.append(point)

#     print(f"---KB_MANAGER: Upserting {len(points)} points...---")
#     client.upsert(collection_name=collection_name, points=points, wait=True)
#     print(f"---KB_MANAGER: Successfully upserted {len(points)} vectors.---")


from datasets import load_dataset
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import torch # To check for CUDA availability
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
# Use your specified embedding models
DENSE_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# For sparse, we will use a sentence-transformer based bi-encoder for simplicity here.
# A true SPLADE model would require more complex setup.
SPARSE_MODEL_NAME = "sentence-transformers/msmarco-MiniLM-L-6-v3"

# Determine device for computations
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Knowledge Base Manager using device: {DEVICE}")

# Initialize models once to be reused
dense_embedding_model = SentenceTransformer(DENSE_MODEL_NAME, device=DEVICE)
sparse_embedding_model = SentenceTransformer(SPARSE_MODEL_NAME, device=DEVICE)

def embed_documents(docs: list[str]) -> tuple[list[list[float]], list[list[float]]]:
    """Embeds a list of documents using both dense and sparse models."""
    dense_embeddings = dense_embedding_model.encode(docs, convert_to_tensor=False).tolist()
    sparse_embeddings = sparse_embedding_model.encode(docs, convert_to_tensor=False).tolist()
    return dense_embeddings, sparse_embeddings



def create_new_kb(collection_name: str, source_type: str, source_name: str, file_path: str = None):
    """
    Loads data from a source, processes it, and stores it in a new Qdrant collection.
    """
    print(f"Creating new KB '{collection_name}' from source '{source_type}': '{source_name}'")
    documents = []

    # Step 1: Load Data
    if source_type == 'gsm8k':
        dataset = load_dataset("openai/gsm8k", "main")
        train_data = dataset['train']
        for item in train_data:
            documents.append(Document(page_content=item['question'], metadata={'answer': item['answer']}))
    
    elif source_type == 'math500':
        dataset = load_dataset("HuggingFaceH4/MATH-500")
        test_data = dataset['test']
        for item in test_data:
            documents.append(Document(page_content=item['problem'], metadata={'answer': item['solution']}))

    elif source_type == 'pdf_url':
        loader = WebBaseLoader(source_name)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
    
    # NEW: Handle direct PDF file uploads
    elif source_type == 'pdf_file':
        if not file_path:
            raise ValueError("File path must be provided for 'pdf_file' source type.")
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
    
    print(f"Loaded {len(documents)} documents.")
    if not documents:
        print("No documents loaded, aborting KB creation.")
        return

    # Step 2: Setup Qdrant Client
    client = QdrantClient(path=f"./qdrant_data/{collection_name}")
    
    # Use your specified Qdrant collection configuration
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config={
            "dense": models.VectorParams(size=dense_embedding_model.get_sentence_embedding_dimension(), distance=models.Distance.COSINE),
            "sparse": models.VectorParams(size=sparse_embedding_model.get_sentence_embedding_dimension(), distance=models.Distance.DOT),
        }
    )
    print(f"Qdrant collection '{collection_name}' created.")

    # Step 3: Embed and Upsert
    contents = [doc.page_content for doc in documents]
    metadata = [doc.metadata for doc in documents]
    
    dense_embeddings, sparse_embeddings = embed_documents(contents)
    
    client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=idx,
                vector={"dense": dense_vec, "sparse": sparse_vec},
                payload=meta
            )
            for idx, (dense_vec, sparse_vec, meta) in enumerate(zip(dense_embeddings, sparse_embeddings, metadata))
        ],
        wait=True
    )
    print(f"Successfully upserted {len(documents)} vectors into '{collection_name}'.")