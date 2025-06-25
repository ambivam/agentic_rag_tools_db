
#!/usr/bin/env python3

import os
import sys
from langchain.schema import Document

def test_chromadb_basic():
    """Test basic ChromaDB functionality without API key"""
    
    print("🧪 Testing ChromaDB Basic Integration...")
    
    try:
        # Test ChromaDB client initialization
        print("1. Testing ChromaDB client initialization...")
        import chromadb
        from chromadb.config import Settings
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path="./test_vector_store",
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        print("✅ ChromaDB client initialized successfully")
        
        # Test collection creation
        print("2. Testing collection creation...")
        collection_name = "test_documents"
        
        try:
            # Try to get existing collection
            collection = client.get_collection(collection_name)
            print(f"✅ Existing collection '{collection_name}' found")
        except Exception:
            # Create new collection
            collection = client.create_collection(
                name=collection_name,
                metadata={"description": "Test document embeddings"}
            )
            print(f"✅ New collection '{collection_name}' created")
        
        # Test adding some dummy data
        print("3. Testing document addition...")
        test_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        test_documents = [
            "ChromaDB is a powerful vector database for AI applications.",
            "FAISS was replaced with ChromaDB for better functionality.",
            "Vector databases enable semantic search and retrieval."
        ]
        test_metadatas = [
            {"filename": "test1.txt", "chunk_id": 0},
            {"filename": "test2.txt", "chunk_id": 0},
            {"filename": "test3.txt", "chunk_id": 0}
        ]
        test_ids = ["doc1", "doc2", "doc3"]
        
        collection.add(
            embeddings=test_embeddings,
            documents=test_documents,
            metadatas=test_metadatas,
            ids=test_ids
        )
        print("✅ Test documents added successfully")
        
        # Test querying
        print("4. Testing similarity search...")
        query_embedding = [0.15, 0.25, 0.35]
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=2
        )
        
        if results['documents'] and len(results['documents']) > 0:
            print(f"✅ Query returned {len(results['documents'][0])} results")
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i]
                print(f"   Result {i+1}: Distance={distance:.3f}, Content='{doc[:50]}...'")
        else:
            print("❌ Query returned no results")
            return False
        
        # Test collection info
        print("5. Testing collection info...")
        count = collection.count()
        print(f"✅ Collection contains {count} documents")
        
        # Clean up
        print("6. Cleaning up test data...")
        client.delete_collection(collection_name)
        print("✅ Test collection cleaned up")
        
        print("\n🎉 Basic ChromaDB integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_chromadb_integration():
    """Test ChromaDB integration with VectorStoreManager (requires API key)"""
    
    print("\n🧪 Testing Full ChromaDB Integration...")
    
    # Check if API key is available
    api_key = os.getenv("ABACUSAI_API_KEY") or "dummy_key_for_testing"
    
    if api_key == "dummy_key_for_testing":
        print("⚠️  No API key found. Skipping full integration test.")
        print("   To test with real embeddings, set the ABACUSAI_API_KEY environment variable.")
        return True
    
    try:
        from vector_store import VectorStoreManager
        
        # Initialize vector store manager
        print("1. Initializing VectorStoreManager with ChromaDB...")
        vector_store_manager = VectorStoreManager(
            openai_api_key=api_key,
            vector_db_path="./test_vector_store"
        )
        print("✅ VectorStoreManager initialized successfully")
        
        # Create test documents
        print("2. Creating test documents...")
        test_docs = [
            Document(
                page_content="ChromaDB is a powerful vector database for AI applications.",
                metadata={"filename": "test1.txt", "chunk_id": 0}
            ),
            Document(
                page_content="FAISS was replaced with ChromaDB for better functionality.",
                metadata={"filename": "test2.txt", "chunk_id": 0}
            ),
            Document(
                page_content="Vector databases enable semantic search and retrieval.",
                metadata={"filename": "test3.txt", "chunk_id": 0}
            )
        ]
        print(f"✅ Created {len(test_docs)} test documents")
        
        # Add documents to vector store
        print("3. Adding documents to ChromaDB...")
        success = vector_store_manager.add_documents(test_docs, show_progress=False)
        if success:
            print("✅ Documents added successfully")
        else:
            print("❌ Failed to add documents")
            return False
        
        # Test similarity search
        print("4. Testing similarity search...")
        query = "What is ChromaDB?"
        results = vector_store_manager.similarity_search(query, k=2)
        
        if results:
            print(f"✅ Similarity search returned {len(results)} results")
            for i, (doc, score) in enumerate(results):
                print(f"   Result {i+1}: Score={score:.3f}, Content='{doc.page_content[:50]}...'")
        else:
            print("❌ Similarity search returned no results")
            return False
        
        # Test store info
        print("5. Testing store info...")
        store_info = vector_store_manager.get_store_info()
        if store_info.get("initialized", False):
            print(f"✅ Store info: {store_info['total_documents']} docs, {store_info['total_embeddings']} embeddings")
        else:
            print("❌ Store not properly initialized")
            return False
        
        # Clean up
        print("6. Cleaning up test data...")
        vector_store_manager.clear_vector_store()
        print("✅ Test data cleaned up")
        
        print("\n🎉 Full ChromaDB integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run basic test first
    basic_success = test_chromadb_basic()
    
    # Run full integration test if basic test passes
    if basic_success:
        full_success = test_chromadb_integration()
        sys.exit(0 if (basic_success and full_success) else 1)
    else:
        sys.exit(1)
