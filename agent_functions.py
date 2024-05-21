import requests

def execute_required_function(func_name, arguments):
    if func_name == "get_FAA_regulation":
        return get_FAA_regulation(arguments['regulation'])

def get_FAA_regulation(regulation):
    base_url = "https://www.ecfr.gov/api"
    
    # Step 1: Get the list of agency slugs
    agencies_url = f"{base_url}/admin/v1/agencies.json"
    response = requests.get(agencies_url)
    if response.status_code != 200:
        raise Exception("Failed to retrieve agencies")
    
    agencies_data = response.json()
    agencies = agencies_data.get("agencies", [])
    faa_slug = None
    
    # Look for FAA within the nested structure
    for agency in agencies:
        if agency['name'] == "Department of Transportation":
            for child_agency in agency.get('children', []):
                if child_agency['name'] == "Federal Aviation Administration":
                    faa_slug = child_agency['slug']
                    break
    
    if not faa_slug:
        raise Exception("FAA agency slug not found")
    
    # Step 2: Search for the regulation using the FAA slug
    search_url = f"{base_url}/search/v1/results"
    params = {
        'query': regulation,
        'agency_slugs[]': faa_slug,
        'per_page': 3,  # Limiting to 10 results for brevity
        'page': 1
    }
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        raise Exception("Failed to retrieve search results")
    
    results = response.json()
    return results
