"""
Institution cache manager for Canadian post-secondary institutions.
Loads institutions on startup and caches them in memory for fast access.
"""
import logging
import threading
from typing import List, Optional
from datetime import datetime, timedelta
from app.utils.canadian_institutions_api import get_all_institutions

logger = logging.getLogger(__name__)

class InstitutionCache:
    """
    Thread-safe singleton cache for Canadian institutions.
    Loads all institutions once and serves from memory.
    """
    
    _instance: Optional['InstitutionCache'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._institutions: List[str] = []
        self._last_updated: Optional[datetime] = None
        self._loading = False
        self._load_error: Optional[str] = None
        self._initialized = True
        
        # Start background loading
        self._start_background_load()
    
    def _start_background_load(self):
        """Start loading institutions in a background thread."""
        def load():
            try:
                logger.info("Starting background load of Canadian institutions...")
                self._loading = True
                institutions = get_all_institutions()
                
                with self._lock:
                    self._institutions = institutions
                    self._last_updated = datetime.now()
                    self._loading = False
                    self._load_error = None
                    
                logger.info(f"Successfully loaded {len(institutions)} institutions")
            except Exception as e:
                logger.exception("Failed to load institutions in background")
                with self._lock:
                    self._loading = False
                    self._load_error = str(e)
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
    
    def get_institutions(self, wait_if_loading: bool = True) -> List[str]:
        """
        Get cached institutions.
        
        Args:
            wait_if_loading: If True and cache is still loading, wait up to 30 seconds
            
        Returns:
            List of institution names
        """
        # If not loading, return immediately
        if not self._loading:
            return self._institutions.copy()
        
        # If loading and we should wait, wait up to 30 seconds
        if wait_if_loading:
            max_wait = 30
            waited = 0
            while self._loading and waited < max_wait:
                import time
                time.sleep(0.5)
                waited += 0.5
        
        return self._institutions.copy()
    
    def is_ready(self) -> bool:
        """Check if cache is loaded and ready."""
        return not self._loading and len(self._institutions) > 0
    
    def get_status(self) -> dict:
        """Get cache status information."""
        return {
            "ready": self.is_ready(),
            "loading": self._loading,
            "count": len(self._institutions),
            "last_updated": self._last_updated.isoformat() if self._last_updated else None,
            "error": self._load_error
        }
    
    def refresh(self):
        """Manually trigger a cache refresh."""
        if not self._loading:
            logger.info("Manually refreshing institution cache")
            self._start_background_load()
        else:
            logger.warning("Cache refresh already in progress")
    
    def search(self, query: str, limit: int = 50) -> List[str]:
        """
        Search institutions by query (case-insensitive).
        
        Args:
            query: Search term
            limit: Maximum results to return
            
        Returns:
            List of matching institution names
        """
        if not query:
            return self._institutions[:limit]
        
        query_lower = query.lower()
        
        # Separate results that start with query vs contain query
        starts_with = []
        contains = []
        
        for institution in self._institutions:
            institution_lower = institution.lower()
            if institution_lower.startswith(query_lower):
                starts_with.append(institution)
            elif query_lower in institution_lower:
                contains.append(institution)
            
            # Stop if we have enough results
            if len(starts_with) + len(contains) >= limit * 2:
                break
        
        # Prioritize "starts with" results
        results = starts_with + contains
        return results[:limit]


# Global singleton instance
_cache_instance: Optional[InstitutionCache] = None

def get_institution_cache() -> InstitutionCache:
    """Get the global institution cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = InstitutionCache()
    return _cache_instance
