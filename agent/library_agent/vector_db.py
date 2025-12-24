"""Vector database utilities for semantic search over policy documents."""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not installed. Run: pip install chromadb")

logger = logging.getLogger(__name__)

# Vector DB storage location
BASE_DIR = Path(__file__).parent
VECTOR_DB_DIR = BASE_DIR / ".chroma_db"


def get_chroma_client():
    """Get or create ChromaDB client."""
    if not CHROMADB_AVAILABLE:
        raise ImportError("ChromaDB not installed. Install with: pip install chromadb")
    
    VECTOR_DB_DIR.mkdir(exist_ok=True)
    
    client = chromadb.PersistentClient(
        path=str(VECTOR_DB_DIR),
        settings=Settings(anonymized_telemetry=False)
    )
    return client


def get_or_create_collection(collection_name: str = "policy_documents"):
    """Get or create a ChromaDB collection for policy documents."""
    client = get_chroma_client()
    
    try:
        collection = client.get_collection(name=collection_name)
        logger.info(f"Loaded existing collection: {collection_name}")
    except Exception:
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "Policy documents and training materials"}
        )
        logger.info(f"Created new collection: {collection_name}")
    
    return collection


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for better semantic search.
    
    Args:
        text: Text to chunk
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap  # Overlap for context
    
    return chunks


def index_document(
    document_code: str,
    title: str,
    content: str,
    document_type: str = "policy",
    metadata: Optional[Dict[str, Any]] = None,
    skip_chunking: bool = False
) -> int:
    """Index a document in the vector database.
    
    Args:
        document_code: Unique document identifier (e.g., "POL-SEC-001")
        title: Document title
        content: Full document text
        document_type: Type of document (policy, handbook, catalog, etc.)
        metadata: Additional metadata dict
        skip_chunking: If True, store as single chunk (useful for JSON documents)
    
    Returns:
        Number of chunks indexed
    """
    collection = get_or_create_collection()
    
    # Check if document already exists - delete it first if re-indexing
    existing = collection.get(ids=[f"{document_code}_chunk_0"], include=["metadatas"])
    if existing["ids"]:
        # Delete existing chunks
        all_existing = collection.get(
            where={"document_code": document_code},
            include=["metadatas"]
        )
        if all_existing["ids"]:
            collection.delete(ids=all_existing["ids"])
            logger.info(f"Deleted existing {document_code} chunks for re-indexing")
    
    # Chunk the document (or use as single chunk)
    if skip_chunking or (document_type in ["catalog", "rules"] and len(content) < 10000):
        chunks = [content]
        logger.info(f"Indexing {document_code} as single chunk (skip_chunking={skip_chunking})")
    else:
        chunks = chunk_text(content)
        logger.info(f"Indexing {document_code}: {len(chunks)} chunks")
    
    # Prepare data for indexing
    ids = [f"{document_code}_chunk_{i}" for i in range(len(chunks))]
    documents = chunks
    metadatas = []
    
    for i in range(len(chunks)):
        chunk_metadata = {
            "document_code": document_code,
            "title": title,
            "document_type": document_type,
            "chunk_index": i,
            "total_chunks": len(chunks),
        }
        if metadata:
            chunk_metadata.update(metadata)
        metadatas.append(chunk_metadata)
    
    # Add to collection
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    logger.info(f"✅ Indexed {document_code}: {len(chunks)} chunks")
    return len(chunks)


def search_documents(
    query: str,
    n_results: int = 5,
    document_type: Optional[str] = None,
    document_code: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search documents using semantic similarity.
    
    Args:
        query: Search query text
        n_results: Number of results to return
        document_type: Filter by document type (optional)
        document_code: Filter by specific document code (optional)
    
    Returns:
        List of search results with:
        - document_code: Document identifier
        - title: Document title
        - content: Matching chunk content
        - chunk_index: Chunk number
        - distance: Similarity score (lower is better)
    """
    collection = get_or_create_collection()
    
    # Build where clause for filtering
    where = {}
    if document_type:
        where["document_type"] = document_type
    if document_code:
        where["document_code"] = document_code
    
    # Perform search
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where if where else None
    )
    
    # Format results
    formatted_results = []
    if results["ids"] and len(results["ids"][0]) > 0:
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "document_code": results["metadatas"][0][i].get("document_code"),
                "title": results["metadatas"][0][i].get("title"),
                "content": results["documents"][0][i],
                "chunk_index": results["metadatas"][0][i].get("chunk_index"),
                "distance": results["distances"][0][i] if results["distances"] else None,
                "metadata": results["metadatas"][0][i],
            })
    
    return formatted_results


def get_document_summary(document_code: str) -> Optional[Dict[str, Any]]:
    """Get summary information about an indexed document.
    
    Args:
        document_code: Document identifier
    
    Returns:
        Dictionary with document info or None if not found
    """
    collection = get_or_create_collection()
    
    try:
        results = collection.get(
            ids=[f"{document_code}_chunk_0"],  # Get first chunk for metadata
            include=["metadatas"]
        )
        
        if results["ids"]:
            metadata = results["metadatas"][0]
            return {
                "document_code": metadata.get("document_code"),
                "title": metadata.get("title"),
                "document_type": metadata.get("document_type"),
                "total_chunks": metadata.get("total_chunks"),
            }
    except Exception as e:
        logger.warning(f"Could not get summary for {document_code}: {e}")
    
    return None


def list_indexed_documents() -> List[str]:
    """List all document codes that are indexed.
    
    Returns:
        List of document codes
    """
    collection = get_or_create_collection()
    
    try:
        # Get all documents (limit to reasonable number)
        results = collection.get(limit=1000, include=["metadatas"])
        
        # Extract unique document codes
        document_codes = set()
        if results["metadatas"]:
            for metadata in results["metadatas"]:
                doc_code = metadata.get("document_code")
                if doc_code:
                    document_codes.add(doc_code)
        
        return sorted(list(document_codes))
    except Exception as e:
        logger.warning(f"Could not list documents: {e}")
        return []


def get_full_document_content(document_code: str) -> Optional[str]:
    """Retrieve full document content by reconstructing from all chunks.
    
    Args:
        document_code: Document identifier
    
    Returns:
        Full document text (reconstructed from chunks) or None if not found
    """
    collection = get_or_create_collection()
    
    try:
        # Get all chunks for this document
        results = collection.get(
            where={"document_code": document_code},
            include=["documents", "metadatas"],
            limit=1000  # Get all chunks
        )
        
        if not results["ids"]:
            return None
        
        # Sort chunks by chunk_index
        chunks_with_index = []
        for i, doc_id in enumerate(results["ids"]):
            chunks_with_index.append((
                results["metadatas"][i].get("chunk_index", 0),
                results["documents"][i]
            ))
        
        # Sort by chunk_index and join
        chunks_with_index.sort(key=lambda x: x[0])
        full_content = "\n\n".join(chunk[1] for chunk in chunks_with_index)
        
        return full_content
    except Exception as e:
        logger.exception(f"Error retrieving full document {document_code}: {e}")
        return None


def delete_document(document_code: str) -> bool:
    """Delete a document from the vector database.
    
    Args:
        document_code: Document identifier to delete
    
    Returns:
        True if deleted, False otherwise
    """
    collection = get_or_create_collection()
    
    try:
        # Get all chunk IDs for this document
        results = collection.get(
            where={"document_code": document_code},
            include=["ids"]
        )
        
        if results["ids"]:
            collection.delete(ids=results["ids"])
            logger.info(f"Deleted {document_code}: {len(results['ids'])} chunks")
            return True
        else:
            logger.warning(f"Document {document_code} not found")
            return False
    except Exception as e:
        logger.exception(f"Error deleting {document_code}: {e}")
        return False

