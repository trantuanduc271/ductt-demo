"""View ChromaDB vector database contents."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from vector_db import (
    get_chroma_client,
    get_or_create_collection,
    list_indexed_documents,
    get_document_summary,
    get_full_document_content,
    CHROMADB_AVAILABLE
)


def view_all_documents():
    """List all indexed documents with summary information."""
    if not CHROMADB_AVAILABLE:
        print("ERROR: ChromaDB not installed. Run: pip install chromadb")
        return
    
    print("=" * 80)
    print("ChromaDB Vector Database - Document Index")
    print("=" * 80)
    print()
    
    try:
        client = get_chroma_client()
        collection = get_or_create_collection()
        
        # Get collection info
        count = collection.count()
        print(f"Total chunks in database: {count}")
        print()
        
        # List all documents
        document_codes = list_indexed_documents()
        
        if not document_codes:
            print("No documents found in the database.")
            return
        
        print(f"Found {len(document_codes)} unique documents:\n")
        
        for doc_code in document_codes:
            summary = get_document_summary(doc_code)
            if summary:
                print(f"Document: {doc_code}")
                print(f"  Title: {summary.get('title', 'N/A')}")
                print(f"  Type: {summary.get('document_type', 'N/A')}")
                print(f"  Total Chunks: {summary.get('total_chunks', 'N/A')}")
                print()
        
        print("=" * 80)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


def view_document_details(document_code: str):
    """View detailed information about a specific document."""
    if not CHROMADB_AVAILABLE:
        print("ERROR: ChromaDB not installed. Run: pip install chromadb")
        return
    
    print("=" * 80)
    print(f"Document Details: {document_code}")
    print("=" * 80)
    print()
    
    try:
        collection = get_or_create_collection()
        
        # Get all chunks for this document
        results = collection.get(
            where={"document_code": document_code},
            include=["documents", "metadatas", "ids"],
            limit=1000
        )
        
        if not results["ids"]:
            print(f"Document {document_code} not found in database.")
            return
        
        # Get summary
        summary = get_document_summary(document_code)
        if summary:
            print(f"Title: {summary.get('title', 'N/A')}")
            print(f"Type: {summary.get('document_type', 'N/A')}")
            print(f"Total Chunks: {summary.get('total_chunks', 'N/A')}")
            print()
        
        # Show chunk information
        print(f"Chunk Details ({len(results['ids'])} chunks):")
        print("-" * 80)
        
        # Sort by chunk_index
        chunks_with_meta = []
        for i, doc_id in enumerate(results["ids"]):
            chunks_with_meta.append((
                results["metadatas"][i].get("chunk_index", 0),
                doc_id,
                results["documents"][i],
                results["metadatas"][i]
            ))
        
        chunks_with_meta.sort(key=lambda x: x[0])
        
        for chunk_idx, doc_id, content, metadata in chunks_with_meta:
            print(f"\nChunk {chunk_idx} (ID: {doc_id})")
            print(f"  Content preview: {content[:100]}...")
            print(f"  Full length: {len(content)} characters")
        
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


def view_document_content(document_code: str, max_length: int = 5000):
    """View full content of a document."""
    if not CHROMADB_AVAILABLE:
        print("ERROR: ChromaDB not installed. Run: pip install chromadb")
        return
    
    print("=" * 80)
    print(f"Document Content: {document_code}")
    print("=" * 80)
    print()
    
    try:
        content = get_full_document_content(document_code)
        
        if not content:
            print(f"Document {document_code} not found in database.")
            return
        
        if len(content) > max_length:
            print(f"Content (first {max_length} characters, total: {len(content)}):")
            print("-" * 80)
            print(content[:max_length])
            print("\n... (truncated)")
        else:
            print("Full Content:")
            print("-" * 80)
            print(content)
        
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


def view_collection_stats():
    """View statistics about the collection."""
    if not CHROMADB_AVAILABLE:
        print("ERROR: ChromaDB not installed. Run: pip install chromadb")
        return
    
    print("=" * 80)
    print("ChromaDB Collection Statistics")
    print("=" * 80)
    print()
    
    try:
        collection = get_or_create_collection()
        
        total_chunks = collection.count()
        print(f"Total chunks: {total_chunks}")
        
        # Get all documents
        document_codes = list_indexed_documents()
        print(f"Unique documents: {len(document_codes)}")
        
        # Count by type
        type_counts = {}
        results = collection.get(limit=1000, include=["metadatas"])
        
        if results["metadatas"]:
            for metadata in results["metadatas"]:
                doc_type = metadata.get("document_type", "unknown")
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        print("\nDocuments by type:")
        for doc_type, count in sorted(type_counts.items()):
            print(f"  {doc_type}: {count} chunks")
        
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View ChromaDB vector database contents")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all indexed documents"
    )
    parser.add_argument(
        "--document",
        type=str,
        help="View details for a specific document (by document_code)"
    )
    parser.add_argument(
        "--content",
        type=str,
        help="View full content of a specific document (by document_code)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="View collection statistics"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=5000,
        help="Maximum length to display for document content (default: 5000)"
    )
    
    args = parser.parse_args()
    
    # Default to list if no specific action
    if not any([args.list, args.document, args.content, args.stats]):
        args.list = True
    
    if args.stats:
        view_collection_stats()
    elif args.content:
        view_document_content(args.content, max_length=args.max_length)
    elif args.document:
        view_document_details(args.document)
    elif args.list:
        view_all_documents()


