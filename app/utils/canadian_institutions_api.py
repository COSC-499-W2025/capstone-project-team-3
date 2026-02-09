import urllib.request
import urllib.parse
import json
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Canadian Open Data API endpoint
CANADA_API_BASE = "https://open.canada.ca/data/en/api/3/action"
# Resource ID for post-secondary programs (contains institution names)
INSTITUTIONS_RESOURCE_ID = "4b97ce31-2499-442e-8374-f52c69938fee"

def search_institutions(query: str = "", limit: int = 100) -> List[Dict]:
    """
    Search Canadian post-secondary institutions via Open Canada API.
    
    Args:
        query: Search term to filter institutions
        limit: Maximum number of results to return
        
    Returns:
        List of institution dictionaries
    """
    try:
        # Build query URL
        url = f"{CANADA_API_BASE}/datastore_search?resource_id={INSTITUTIONS_RESOURCE_ID}&limit={limit}"
        if query:
            # Search specifically in institution_name_e field
            url += f"&q={urllib.parse.quote(query)}"
        
        logger.info(f"Fetching institutions from: {url}")
        
        # Make request
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        if not data.get("success"):
            logger.error(f"API request failed: {data}")
            return []
            
        # Extract records from response
        records = data.get("result", {}).get("records", [])
        
        if not records:
            logger.warning("No records returned from API")
            return []
        
        logger.info(f"Retrieved {len(records)} records")
        
        # Extract unique institutions with their programs
        institutions_map = {}
        
        for record in records:
            institution_name = record.get("institution_name_e", "Unknown")
            program_name = record.get("program_of_study_e", "Unknown")
            academic_level = record.get("academic_level_area_of_study_e", "Unknown")
            program_type = record.get("program_type_e", "Unknown")
            
            # Group programs by institution
            if institution_name not in institutions_map:
                institutions_map[institution_name] = {
                    "name": institution_name,
                    "programs": []
                }
            
            institutions_map[institution_name]["programs"].append({
                "program": program_name,
                "level": academic_level,
                "type": program_type
            })
        
        # Convert map to list
        institutions = list(institutions_map.values())
        
        logger.info(f"Processed {len(institutions)} unique institutions")
        return institutions
        
    except urllib.error.HTTPError as e:
        logger.exception(f"HTTP Error fetching institutions: {e.code} - {e.reason}")
        return []
    except urllib.error.URLError as e:
        logger.exception(f"URL Error fetching institutions: {e.reason}")
        return []
    except Exception as e:
        logger.exception(f"Unexpected error fetching institutions: {e}")
        return []


def get_all_institutions(cache_duration_hours: int = 24) -> List[str]:
    """
    Get a simple list of all unique institution names (suitable for autocomplete).
    
    Args:
        cache_duration_hours: How long to cache results (not implemented yet)
        
    Returns:
        List of institution names (sorted, unique)
    """
    try:
        # Fetch with high limit to get more institutions
        # Note: API has 5294 total records, so we'll fetch in batches
        all_institutions = set()
        limit = 1000
        offset = 0
        max_records = 5294  # Total from API
        
        while offset < max_records:
            url = f"{CANADA_API_BASE}/datastore_search?resource_id={INSTITUTIONS_RESOURCE_ID}&limit={limit}&offset={offset}"
            
            logger.info(f"Fetching batch: offset={offset}, limit={limit}")
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            if not data.get("success"):
                logger.error(f"API request failed at offset {offset}")
                break
            
            records = data.get("result", {}).get("records", [])
            
            if not records:
                break
            
            # Extract institution names
            for record in records:
                institution_name = record.get("institution_name_e")
                if institution_name and institution_name.strip():
                    all_institutions.add(institution_name.strip())
            
            offset += limit
            
            # Stop if we got fewer records than requested
            if len(records) < limit:
                break
        
        # Convert to sorted list
        institutions_list = sorted(list(all_institutions))
        
        logger.info(f"Retrieved {len(institutions_list)} unique institution names")
        return institutions_list
        
    except Exception as e:
        logger.exception(f"Error getting institution list: {e}")
        return []


def search_institutions_simple(query: str = "", limit: int = 50) -> List[str]:
    """
    Simple search that returns just institution names (for autocomplete).
    
    Args:
        query: Search term to filter institutions
        limit: Maximum number of results
        
    Returns:
        List of unique institution names matching the query
    """
    try:
        url = f"{CANADA_API_BASE}/datastore_search?resource_id={INSTITUTIONS_RESOURCE_ID}&limit={limit}"
        if query:
            url += f"&q={urllib.parse.quote(query)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        if not data.get("success"):
            return []
        
        records = data.get("result", {}).get("records", [])
        
        # Extract unique institution names
        institutions = set()
        for record in records:
            name = record.get("institution_name_e")
            if name and name.strip():
                institutions.add(name.strip())
        
        return sorted(list(institutions))
        
    except Exception as e:
        logger.exception(f"Error in simple search: {e}")
        return []