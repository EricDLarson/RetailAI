#!/usr/bin/env python3

"""
Google Retail API performance testing script.
Measures search performance by executing queries and reporting timing metrics.
"""

import sys
import time
from pathlib import Path
from typing import List

from google.cloud.retail_v2 import SearchRequest, SearchServiceClient
from google.api_core import exceptions
from google.oauth2 import service_account


# --- Configuration ---
PROJECT_ID = ""
KEY_FILE = "path to keyfile.json"
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

LOCATION = "global"
CATALOG = "default_catalog"
PLACEMENT = "default_search"
QUERY_FILE = "queries.txt"
VISITOR_ID = "12345"
PAGE_SIZE = 100
FILTER = 'availability: ANY("IN_STOCK")'
QUERY_EXPANSION = {'condition':'AUTO'}

def validate_configuration():
    """Validate that required configuration is set."""
    if not PROJECT_ID:
        print("Error: PROJECT_ID is not set.")
        return False
    
    if not Path(KEY_FILE).exists():
        print(f"Error: Service account key file not found at '{KEY_FILE}'")
        return False
    
    if not Path(QUERY_FILE).exists():
        print(f"Error: Query file not found at '{QUERY_FILE}'")
        return False
    
    return True


def create_credentials():
    """Create credentials from service account key file."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            KEY_FILE,
            scopes=SCOPES
        )
        return credentials
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None


def read_queries(query_file: str) -> List[str]:
    """Read search queries from file, one per line."""
    queries = []
    with open(query_file, 'r', encoding='utf-8') as f:
        for line in f:
            query = line.strip()
            if query:
                queries.append(query)
    return queries


def perform_search(client: SearchServiceClient, placement_path: str, query: str) -> tuple:
    """Perform a single search request and return (result_count, duration_ms, success)."""
    start_time = time.time()
    
    try:
        request = SearchRequest(
            placement=placement_path,
            visitor_id=VISITOR_ID,
            query=query,
            page_size=PAGE_SIZE,
            query_expansion_spec=QUERY_EXPANSION,
            filter=FILTER
        )
        
        response_pager = client.search(request=request)
        first_page = next(iter(response_pager.pages))
        result_count = len(first_page.results)
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        return result_count, duration_ms, True
        
    except exceptions.GoogleAPIError as e:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        print(f"  ✗ API Error: {e}")
        return 0, duration_ms, False
    except Exception as e:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        print(f"  ✗ Error: {e}")
        return 0, duration_ms, False


def main():
    """Main function to execute the performance test."""
    print("Google Retail API Performance Test")
    print("=" * 50)
    
    # Validate configuration
    if not validate_configuration():
        sys.exit(1)
    
    # Read queries
    try:
        queries = read_queries(QUERY_FILE)
    except Exception as e:
        print(f"Error reading query file: {e}")
        sys.exit(1)
    
    if not queries:
        print(f"No queries found in '{QUERY_FILE}'. Exiting.")
        sys.exit(0)
    
    print(f"Found {len(queries)} queries to test")
    
    # Initialize client
    try:
        credentials = create_credentials()
        if not credentials:
            sys.exit(1)
        
        client = SearchServiceClient(credentials=credentials)
        print("✓ Client initialized successfully")
    except Exception as e:
        print(f"Error initializing client: {e}")
        sys.exit(1)
    
    # Build placement path
    placement_path = f"projects/{PROJECT_ID}/locations/{LOCATION}/catalogs/{CATALOG}/placements/{PLACEMENT}"
    print(f"Using placement: {placement_path}")
    print("-" * 50)
    
    # Execute searches and collect metrics
    total_start_time = time.time()
    successful_searches = 0
    failed_searches = 0
    total_results = 0
    durations = []
    
    for i, query in enumerate(queries, 1):
        print(f"[{i:3d}/{len(queries)}] Testing: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        
        result_count, duration_ms, success = perform_search(client, placement_path, query)
        durations.append(duration_ms)
        
        if success:
            successful_searches += 1
            total_results += result_count
            print(f"         ✓ {result_count} results in {duration_ms:.1f}ms")
        else:
            failed_searches += 1
            print(f"         ✗ Failed in {duration_ms:.1f}ms")
    
    total_end_time = time.time()
    total_duration_seconds = total_end_time - total_start_time
    
    # Print performance summary
    print("\n" + "=" * 50)
    print("PERFORMANCE SUMMARY")
    print("=" * 50)
    print(f"Total queries processed:    {len(queries)}")
    print(f"Successful searches:        {successful_searches}")
    print(f"Failed searches:            {failed_searches}")
    print(f"Total results found:        {total_results}")
    print(f"Average results per query:  {total_results / successful_searches if successful_searches > 0 else 0:.1f}")
    print()
    print(f"Total execution time:       {total_duration_seconds:.2f} seconds")
    print(f"Average time per request:   {sum(durations) / len(durations):.1f} ms")
    print(f"Fastest request:            {min(durations):.1f} ms")
    print(f"Slowest request:            {max(durations):.1f} ms")
    print(f"Requests per second:        {len(queries) / total_duration_seconds:.2f}")
    
    if successful_searches > 0:
        successful_durations = [durations[i] for i, query in enumerate(queries) 
                              if perform_search(client, placement_path, query)[2]]
        print(f"Avg time (successful only): {sum(d for d in durations if d > 0) / successful_searches:.1f} ms")


if __name__ == "__main__":
    main()

