
import os
import json
import uuid
import sys
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
import faiss
import logging
from config import Config

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Manage FAISS vector store for document embeddings with cross-platform support"""
    
    def __init__(self, openai_api_key: str, vector_db_path: str = None):
        self.openai_api_key = openai_api_key
        
        # Use pathlib for cross-platform path handling
        if vector_db_path is None:
            self.vector_db_path = str(Path(__file__).parent / "vector_store")
        else:
            self.vector_db_path = str(Path(vector_db_path).resolve())
        
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            model=Config.OPENAI_EMBEDDING_MODEL
        )
        
        # FAISS-specific attributes
        self.index = None
        self.embedding_dimension = 1024  # dimension for text-embedding-3-small
        self.document_metadata = {}
        self.document_texts = []  # Store document texts separately
        self.document_ids = []    # Store document IDs for mapping
        
        # Ensure directory exists with proper error handling
        self._create_vector_store_directory()
        
        # Initialize FAISS index
        self._initialize_index()
        
        # Load existing vector store if available
        self.load_vector_store()
    
    def _create_vector_store_directory(self):
        """Create vector store directory with cross-platform support"""
        try:
            vector_path = Path(self.vector_db_path)
            vector_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Vector store directory created/verified: {self.vector_db_path}")
        except PermissionError as e:
            if sys.platform.startswith('win'):
                error_msg = (
                    f"Permission denied creating vector store directory on Windows. "
                    f"Try running as administrator or check folder permissions. "
                    f"Path: {self.vector_db_path}. Error: {str(e)}"
                )
            else:
                error_msg = f"Permission denied creating vector store directory: {str(e)}"
            logger.error(error_msg)
            raise PermissionError(error_msg)
        except Exception as e:
            logger.error(f"Error creating vector store directory: {str(e)}")
            raise
    
    def _initialize_index(self):
        """Initialize FAISS index with platform-specific configurations"""
        try:
            # Create FAISS index using L2 distance (Euclidean)
            # IndexFlatL2 is good for small to medium datasets
            self.index = faiss.IndexFlatL2(self.embedding_dimension)
            
            logger.info(f"FAISS index initialized at {self.vector_db_path}")
        except Exception as e:
            error_msg = f"Error initializing FAISS index: {str(e)}"
            if sys.platform.startswith('win'):
                error_msg += (
                    "\n\nWindows troubleshooting tips:\n"
                    "1. Check if path contains special characters\n"
                    "2. Try running as administrator\n"
                    "3. Ensure antivirus isn't blocking file operations\n"
                    "4. Check available disk space"
                )
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def add_documents(self, documents: List[Document], show_progress: bool = True) -> bool:
        """Add documents to vector store"""
        try:
            if not documents:
                logger.warning("No documents provided to add to vector store")
                return False
            
            logger.info(f"Adding {len(documents)} documents to vector store")
            
            if show_progress:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            if show_progress:
                status_text.text("Generating embeddings...")
                progress_bar.progress(0.3)
            
            # Prepare data for FAISS
            texts = [doc.page_content for doc in documents]
            
            # Generate embeddings
            embeddings = self.embeddings.embed_documents(texts)
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Debug: Check dimensions
            actual_dim = embeddings_array.shape[1]
            logger.info(f"Embedding dimensions - Expected: {self.embedding_dimension}, Actual: {actual_dim}")
            if actual_dim != self.embedding_dimension:
                logger.error(f"Dimension mismatch! FAISS index expects {self.embedding_dimension} but got {actual_dim}")
                # Re-initialize index with correct dimension
                self.embedding_dimension = actual_dim
                self.index = faiss.IndexFlatL2(self.embedding_dimension)
                logger.info(f"Re-initialized FAISS index with dimension {self.embedding_dimension}")
            
            if show_progress:
                status_text.text("Adding documents to FAISS index...")
                progress_bar.progress(0.6)
            
            # Add embeddings to FAISS index
            start_index = len(self.document_texts)
            self.index.add(embeddings_array)
            
            # Store document data with internal mapping
            for i, doc in enumerate(documents):
                doc_id = str(uuid.uuid4())
                
                # Store text and ID for mapping
                self.document_texts.append(doc.page_content)
                self.document_ids.append(doc_id)
                
                # Store metadata with internal doc_id for backward compatibility
                internal_doc_id = start_index + i
                metadata = doc.metadata.copy()
                metadata['internal_doc_id'] = internal_doc_id
                metadata['doc_id'] = doc_id
                
                # Update document metadata mapping
                self.document_metadata[internal_doc_id] = metadata
            
            if show_progress:
                status_text.text("Saving vector store...")
                progress_bar.progress(0.9)
            
            # Save vector store to disk
            self.save_vector_store()
            
            if show_progress:
                status_text.text("Vector store updated successfully!")
                progress_bar.progress(1.0)
            
            logger.info(f"Successfully added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            import traceback
            error_msg = f"Error adding documents to vector store: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Full traceback: {traceback.format_exc()}")
            if show_progress:
                st.error(error_msg)
                st.error("Check the application logs for full error details")
                # Add debug info in an expander
                with st.expander("Debug Information"):
                    st.code(traceback.format_exc())
            return False
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 5, 
        score_threshold: float = 0.0
    ) -> List[Tuple[Document, float]]:
        """Perform similarity search with scores"""
        try:
            if self.index is None or self.index.ntotal == 0:
                logger.warning("Vector store not initialized or empty")
                return []
            
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Perform similarity search using FAISS
            # FAISS returns L2 distances, we need to convert to similarity scores
            k_search = min(k, self.index.ntotal)
            distances, indices = self.index.search(query_vector, k_search)
            
            # Convert FAISS results to expected format
            search_results = []
            
            for i in range(len(distances[0])):
                distance = distances[0][i]
                index = indices[0][i]
                
                # Skip invalid indices
                if index < 0 or index >= len(self.document_texts):
                    continue
                
                # Convert L2 distance to similarity score
                # For L2 distance, smaller values mean more similar
                # We use a simple inverse transformation: score = 1 / (1 + distance)
                similarity_score = 1.0 / (1.0 + distance)
                
                # Filter by score threshold if specified
                if score_threshold > 0 and similarity_score < score_threshold:
                    continue
                
                # Get document text and metadata
                doc_text = self.document_texts[index]
                doc_metadata = self.document_metadata.get(index, {})
                
                # Create Document object
                doc = Document(
                    page_content=doc_text,
                    metadata=doc_metadata
                )
                
                search_results.append((doc, similarity_score))
            
            # Log each match with its score and filename
            for doc, similarity_score in search_results:
                logger.info(f"Match: {doc.metadata.get('filename', 'unknown')} (score: {similarity_score:.3f})")
        
            logger.info(f"Similarity search returned {len(search_results)} results for query: {query[:50]}...")
            return search_results
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            return []
    
    def save_vector_store(self) -> bool:
        """Save FAISS vector store and metadata to disk"""
        try:
            # Ensure parent directory exists
            vector_path = Path(self.vector_db_path)
            vector_path.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            if self.index is not None and self.index.ntotal > 0:
                index_path = vector_path / "faiss_index.bin"
                faiss.write_index(self.index, str(index_path))
                logger.info(f"FAISS index saved to {index_path}")
            
            # Save metadata mapping
            metadata_path = vector_path / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.document_metadata, f, indent=2, ensure_ascii=False)
            
            # Save document texts and IDs
            texts_path = vector_path / "document_texts.pkl"
            with open(texts_path, 'wb') as f:
                pickle.dump(self.document_texts, f)
            
            ids_path = vector_path / "document_ids.pkl"
            with open(ids_path, 'wb') as f:
                pickle.dump(self.document_ids, f)
            
            logger.info(f"Vector store saved to {self.vector_db_path}")
            return True
            
        except Exception as e:
            error_msg = f"Error saving vector store: {str(e)}"
            if sys.platform.startswith('win'):
                error_msg += (
                    "\n\nWindows troubleshooting tips:\n"
                    "1. Check if file is locked by another process\n"
                    "2. Verify write permissions to the directory\n"
                    "3. Try closing any applications that might be using the file"
                )
            logger.error(error_msg)
            return False
    
    def load_vector_store(self) -> bool:
        """Load FAISS vector store from disk"""
        try:
            vector_path = Path(self.vector_db_path)
            index_path = vector_path / "faiss_index.bin"
            metadata_path = vector_path / "metadata.json"
            texts_path = vector_path / "document_texts.pkl"
            ids_path = vector_path / "document_ids.pkl"
            
            # Check if vector store files exist
            if not index_path.exists():
                logger.info("No existing FAISS index found")
                return False
            
            # Load FAISS index
            try:
                self.index = faiss.read_index(str(index_path))
                logger.info(f"FAISS index loaded from {index_path}")
            except Exception as e:
                logger.error(f"Error loading FAISS index: {str(e)}")
                return False
            
            # Load metadata if exists
            if metadata_path.exists():
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        self.document_metadata = json.load(f)
                        # Convert string keys back to integers for backward compatibility
                        self.document_metadata = {int(k): v for k, v in self.document_metadata.items()}
                    logger.info(f"Metadata loaded from {metadata_path}")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Error loading metadata, starting fresh: {str(e)}")
                    self.document_metadata = {}
            
            # Load document texts if exists
            if texts_path.exists():
                try:
                    with open(texts_path, 'rb') as f:
                        self.document_texts = pickle.load(f)
                    logger.info(f"Document texts loaded from {texts_path}")
                except Exception as e:
                    logger.warning(f"Error loading document texts: {str(e)}")
                    self.document_texts = []
            
            # Load document IDs if exists
            if ids_path.exists():
                try:
                    with open(ids_path, 'rb') as f:
                        self.document_ids = pickle.load(f)
                    logger.info(f"Document IDs loaded from {ids_path}")
                except Exception as e:
                    logger.warning(f"Error loading document IDs: {str(e)}")
                    self.document_ids = []
            
            # Log information about loaded documents
            logger.info(f"Vector store loaded successfully from {self.vector_db_path}")
            logger.info(f"Number of documents in vector store: {len(self.document_texts)}")
            logger.info("Document filenames in vector store:")
            unique_files = set()
            for idx, metadata in self.document_metadata.items():
                if 'filename' in metadata:
                    unique_files.add(metadata['filename'])
            for filename in sorted(unique_files):
                logger.info(f"  - {filename}")
            return True
                
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
    
    def clear_vector_store(self) -> bool:
        """Clear all documents from vector store"""
        try:
            vector_path = Path(self.vector_db_path)
            
            # Remove FAISS index file
            index_path = vector_path / "faiss_index.bin"
            if index_path.exists():
                try:
                    index_path.unlink()
                    logger.info("FAISS index file removed")
                except Exception as e:
                    logger.warning(f"Could not remove FAISS index file: {str(e)}")
            
            # Remove metadata file
            metadata_path = vector_path / "metadata.json"
            if metadata_path.exists():
                try:
                    metadata_path.unlink()
                    logger.info("Metadata file removed")
                except Exception as e:
                    logger.warning(f"Could not remove metadata file: {str(e)}")
            
            # Remove document texts file
            texts_path = vector_path / "document_texts.pkl"
            if texts_path.exists():
                try:
                    texts_path.unlink()
                    logger.info("Document texts file removed")
                except Exception as e:
                    logger.warning(f"Could not remove document texts file: {str(e)}")
            
            # Remove document IDs file
            ids_path = vector_path / "document_ids.pkl"
            if ids_path.exists():
                try:
                    ids_path.unlink()
                    logger.info("Document IDs file removed")
                except Exception as e:
                    logger.warning(f"Could not remove document IDs file: {str(e)}")
            
            # Reset in-memory objects
            self.index = faiss.IndexFlatL2(self.embedding_dimension)
            self.document_metadata = {}
            self.document_texts = []
            self.document_ids = []
            
            logger.info("Vector store cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            return False
    
    def get_store_info(self) -> Dict[str, Any]:
        """Get information about the vector store"""
        try:
            if self.index is None:
                return {
                    "initialized": False,
                    "total_documents": 0,
                    "total_embeddings": 0,
                    "platform": sys.platform,
                    "vector_db_path": self.vector_db_path,
                    "vector_db_type": "FAISS"
                }
            
            # Get FAISS index statistics
            total_embeddings = self.index.ntotal
            
            # Get unique files
            unique_files = set()
            for metadata in self.document_metadata.values():
                if 'filename' in metadata:
                    unique_files.add(metadata['filename'])
            
            return {
                "initialized": True,
                "total_documents": len(self.document_metadata),
                "total_embeddings": total_embeddings,
                "unique_files": len(unique_files),
                "files": list(unique_files),
                "platform": sys.platform,
                "vector_db_path": self.vector_db_path,
                "vector_db_type": "FAISS",
                "embedding_dimension": self.embedding_dimension,
                "index_type": str(type(self.index).__name__)
            }
            
        except Exception as e:
            logger.error(f"Error getting store info: {str(e)}")
            return {"error": str(e), "platform": sys.platform, "vector_db_type": "FAISS"}
    
    def get_document_by_id(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Get document metadata by ID"""
        return self.document_metadata.get(doc_id)
    
    def search_documents_by_metadata(self, **kwargs) -> List[Dict[str, Any]]:
        """Search documents by metadata fields"""
        matching_docs = []
        
        for doc_id, metadata in self.document_metadata.items():
            match = True
            for key, value in kwargs.items():
                if key not in metadata or metadata[key] != value:
                    match = False
                    break
            
            if match:
                matching_docs.append({
                    "doc_id": doc_id,
                    "metadata": metadata
                })
        
        return matching_docs
