# funda_url_builder.py
"""
Enhanced Funda URL builder with comprehensive filter support.
Supports both legacy and modern Funda URL structures.
"""

from urllib.parse import urlencode, quote
import json
from typing import List, Dict, Any, Optional, Union


def build_funda_url(
    # Location parameters
    city: Optional[str] = None,
    area: Optional[str] = None,
    selected_area: Optional[List[str]] = None,
    postal_code: Optional[str] = None,
    radius: Optional[int] = None,
    
    # Price parameters
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    
    # Property type and characteristics
    property_type: Optional[str] = None,
    object_type: Optional[List[str]] = None,
    
    # Size parameters
    min_floor_area: Optional[int] = None,
    max_floor_area: Optional[int] = None,
    min_plot_area: Optional[int] = None,
    max_plot_area: Optional[int] = None,
    
    # Room parameters
    min_rooms: Optional[int] = None,
    max_rooms: Optional[int] = None,
    min_bedrooms: Optional[int] = None,
    max_bedrooms: Optional[int] = None,
    min_bathrooms: Optional[int] = None,
    max_bathrooms: Optional[int] = None,
    
    # Building characteristics
    construction_type: Optional[str] = None,
    build_period: Optional[str] = None,
    energy_label: Optional[List[str]] = None,
    
    # Furnishing and amenities
    furnished: Optional[bool] = None,
    partly_furnished: Optional[bool] = None,
    balcony: Optional[bool] = None,
    roof_terrace: Optional[bool] = None,
    garden: Optional[bool] = None,
    garden_orientation: Optional[List[str]] = None,
    parking: Optional[bool] = None,
    garage: Optional[bool] = None,
    
    # Accessibility and facilities
    lift: Optional[bool] = None,
    single_floor: Optional[bool] = None,
    disabled_access: Optional[bool] = None,
    elderly_access: Optional[bool] = None,
    
    # Listing parameters
    listed_since_days: Optional[int] = None,
    status: Optional[str] = None,
    available_from: Optional[str] = None,
    
    # Financial parameters
    service_costs_included: Optional[bool] = None,
    service_costs_excluded: Optional[bool] = None,
    min_service_costs: Optional[int] = None,
    max_service_costs: Optional[int] = None,
    
    # Search parameters
    keyword: Optional[str] = None,
    agent_id: Optional[int] = None,
    
    # Display parameters
    sort_by: Optional[str] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    
    # URL style preference
    use_modern_url: bool = True,
    transaction_type: str = "huur"  # "huur" or "koop"
) -> str:
    """
    Build a comprehensive Funda search URL with extensive filter support.
    
    Args:
        city: City name (e.g., "Amsterdam", "Rotterdam")
        area: Specific area within city
        selected_area: List of area codes for new URL format
        postal_code: Postal code filter
        radius: Search radius in km
        
        min_price/max_price: Price range in euros
        
        property_type: Legacy property type slug
        object_type: List of object types for modern URL
        
        Floor/plot area: Size filters in m²
        Room counts: Number of rooms, bedrooms, bathrooms
        
        construction_type: Construction type filter
        build_period: Building period filter
        energy_label: List of energy labels (A, B, C, etc.)
        
        Amenities: Various boolean filters for features
        garden_orientation: List of garden orientations
        
        Accessibility: Boolean filters for accessibility features
        
        listed_since_days: Days since listing
        status: Listing status
        available_from: Availability date
        
        Service costs: Boolean and range filters
        
        keyword: Search keyword
        agent_id: Specific agent ID
        
        sort_by: Sort order
        page: Page number
        per_page: Results per page
        
        use_modern_url: Use modern or legacy URL format
        transaction_type: "huur" (rent) or "koop" (buy)
    
    Returns:
        Complete Funda search URL
    """
    
    if use_modern_url:
        return _build_modern_url(
            city=city, area=area, selected_area=selected_area, postal_code=postal_code,
            radius=radius, min_price=min_price, max_price=max_price,
            object_type=object_type, min_floor_area=min_floor_area,
            max_floor_area=max_floor_area, min_plot_area=min_plot_area,
            max_plot_area=max_plot_area, min_rooms=min_rooms, max_rooms=max_rooms,
            min_bedrooms=min_bedrooms, max_bedrooms=max_bedrooms,
            min_bathrooms=min_bathrooms, max_bathrooms=max_bathrooms,
            construction_type=construction_type, build_period=build_period,
            energy_label=energy_label, furnished=furnished,
            partly_furnished=partly_furnished, balcony=balcony,
            roof_terrace=roof_terrace, garden=garden,
            garden_orientation=garden_orientation, parking=parking, garage=garage,
            lift=lift, single_floor=single_floor, disabled_access=disabled_access,
            elderly_access=elderly_access, listed_since_days=listed_since_days,
            status=status, available_from=available_from,
            service_costs_included=service_costs_included,
            service_costs_excluded=service_costs_excluded,
            min_service_costs=min_service_costs, max_service_costs=max_service_costs,
            keyword=keyword, agent_id=agent_id, sort_by=sort_by, page=page,
            per_page=per_page, transaction_type=transaction_type
        )
    else:
        return _build_legacy_url(
            city=city, min_price=min_price, max_price=max_price,
            property_type=property_type, min_floor_area=min_floor_area,
            max_floor_area=max_floor_area, min_rooms=min_rooms,
            max_rooms=max_rooms, min_bedrooms=min_bedrooms,
            max_bedrooms=max_bedrooms, energy_label=energy_label,
            keyword=keyword, transaction_type=transaction_type
        )


def _build_modern_url(**kwargs) -> str:
    """Build modern Funda URL using query parameters."""
    transaction_type = kwargs.get('transaction_type', 'huur')
    base_url = f"https://www.funda.nl/zoeken/{transaction_type}/"
    
    params = {}
    
    # Location parameters
    if kwargs.get('selected_area'):
        params['selected_area'] = json.dumps(kwargs['selected_area'])
    elif kwargs.get('city'):
        # Convert city to area code format
        city_code = kwargs['city'].lower().replace(' ', '-')
        params['selected_area'] = json.dumps([city_code])
    
    if kwargs.get('postal_code'):
        params['postal_code'] = kwargs['postal_code']
    
    if kwargs.get('radius'):
        params['radius'] = kwargs['radius']
    
    # Price range
    if kwargs.get('min_price') or kwargs.get('max_price'):
        price_range = f"{kwargs.get('min_price', 0)}-{kwargs.get('max_price', '')}"
        params['price'] = price_range
    
    # Object types
    if kwargs.get('object_type'):
        params['object_type'] = json.dumps(kwargs['object_type'])
    
    # Floor area
    if kwargs.get('min_floor_area') or kwargs.get('max_floor_area'):
        area_range = f"{kwargs.get('min_floor_area', 0)}-{kwargs.get('max_floor_area', '')}"
        params['floor_area'] = area_range
    
    # Plot area
    if kwargs.get('min_plot_area') or kwargs.get('max_plot_area'):
        plot_range = f"{kwargs.get('min_plot_area', 0)}-{kwargs.get('max_plot_area', '')}"
        params['plot_area'] = plot_range
    
    # Rooms
    if kwargs.get('min_rooms') or kwargs.get('max_rooms'):
        rooms_range = f"{kwargs.get('min_rooms', 0)}-{kwargs.get('max_rooms', '')}"
        params['rooms'] = rooms_range
    
    # Bedrooms
    if kwargs.get('min_bedrooms') or kwargs.get('max_bedrooms'):
        bed_range = f"{kwargs.get('min_bedrooms', 0)}-{kwargs.get('max_bedrooms', '')}"
        params['bedrooms'] = bed_range
    
    # Bathrooms
    if kwargs.get('min_bathrooms') or kwargs.get('max_bathrooms'):
        bath_range = f"{kwargs.get('min_bathrooms', 0)}-{kwargs.get('max_bathrooms', '')}"
        params['bathrooms'] = bath_range
    
    # Energy labels
    if kwargs.get('energy_label'):
        params['energy_label'] = json.dumps(kwargs['energy_label'])
    
    # Boolean filters
    boolean_filters = {
        'furnished': 'furnished',
        'partly_furnished': 'partly_furnished',
        'balcony': 'balcony',
        'roof_terrace': 'roof_terrace',
        'garden': 'garden',
        'parking': 'parking',
        'garage': 'garage',
        'lift': 'lift',
        'single_floor': 'single_floor',
        'disabled_access': 'disabled_access',
        'elderly_access': 'elderly_access'
    }
    
    for key, param_name in boolean_filters.items():
        if kwargs.get(key) is True:
            params[param_name] = '1'
        elif kwargs.get(key) is False:
            params[param_name] = '0'
    
    # Garden orientation
    if kwargs.get('garden_orientation'):
        params['garden_orientation'] = json.dumps(kwargs['garden_orientation'])
    
    # Service costs
    if kwargs.get('min_service_costs') or kwargs.get('max_service_costs'):
        service_range = f"{kwargs.get('min_service_costs', 0)}-{kwargs.get('max_service_costs', '')}"
        params['service_costs'] = service_range
    
    # Listing parameters
    if kwargs.get('listed_since_days'):
        params['listed_since'] = kwargs['listed_since_days']
    
    if kwargs.get('status'):
        params['status'] = kwargs['status']
    
    if kwargs.get('available_from'):
        params['available_from'] = kwargs['available_from']
    
    # Search parameters
    if kwargs.get('keyword'):
        params['search_result'] = kwargs['keyword']
    
    if kwargs.get('agent_id'):
        params['agent_id'] = kwargs['agent_id']
    
    # Display parameters
    if kwargs.get('sort_by'):
        params['sort'] = kwargs['sort_by']
    
    if kwargs.get('page'):
        params['page'] = kwargs['page']
    
    if kwargs.get('per_page'):
        params['per_page'] = min(kwargs['per_page'], 50)  # Limit to 50 max per page
    else:
        params['per_page'] = 50  # Default to maximum for efficiency
    
    # Construction filters
    if kwargs.get('construction_type'):
        params['construction_type'] = kwargs['construction_type']
    
    if kwargs.get('build_period'):
        params['build_period'] = kwargs['build_period']
    
    # Build final URL
    if params:
        return base_url + '?' + urlencode(params, safe='[]')
    return base_url


def _build_legacy_url(**kwargs) -> str:
    """Build legacy Funda URL using path-based structure."""
    transaction_type = kwargs.get('transaction_type', 'huur')
    base_url = f"https://www.funda.nl/{transaction_type}/"
    
    path_parts = []
    query_params = {}
    
    # City
    if kwargs.get('city'):
        city_slug = kwargs['city'].lower().replace(' ', '-')
        path_parts.append(city_slug)
    
    # Property type mapping
    if kwargs.get('property_type'):
        type_mapping = {
            'woonhuis': 'woonhuis',
            'appartement': 'appartement',
            'studio': 'studio',
            'kamer': 'kamer',
            'parkeergelegenheid': 'parkeergelegenheid',
            'berging': 'berging',
            'opslagruimte': 'opslagruimte',
            'ligplaats': 'ligplaats',
            'standplaats': 'standplaats',
            'bouwgrond': 'bouwgrond'
        }
        prop_type = type_mapping.get(kwargs['property_type'].lower())
        if prop_type:
            path_parts.append(prop_type)
    
    # Price range
    if kwargs.get('min_price') or kwargs.get('max_price'):
        min_p = kwargs.get('min_price', 0)
        max_p = kwargs.get('max_price', '')
        path_parts.append(f"prijs-{min_p}-{max_p}")
    
    # Floor area
    if kwargs.get('min_floor_area') or kwargs.get('max_floor_area'):
        min_a = kwargs.get('min_floor_area', 0)
        max_a = kwargs.get('max_floor_area', '')
        path_parts.append(f"woonopp-{min_a}-{max_a}")
    
    # Rooms
    if kwargs.get('min_rooms') or kwargs.get('max_rooms'):
        min_r = kwargs.get('min_rooms', 0)
        max_r = kwargs.get('max_rooms', '')
        path_parts.append(f"kamers-{min_r}-{max_r}")
    
    # Bedrooms
    if kwargs.get('min_bedrooms') or kwargs.get('max_bedrooms'):
        min_b = kwargs.get('min_bedrooms', 0)
        max_b = kwargs.get('max_bedrooms', '')
        path_parts.append(f"slaapkamers-{min_b}-{max_b}")
    
    # Energy label
    if kwargs.get('energy_label'):
        if isinstance(kwargs['energy_label'], list):
            label = kwargs['energy_label'][0]  # Take first label for legacy URL
        else:
            label = kwargs['energy_label']
        path_parts.append(f"energielabel-{label.upper()}")
    
    # Keyword as query parameter
    if kwargs.get('keyword'):
        query_params['q'] = kwargs['keyword']
    
    # Build URL
    url = base_url + '/'.join(path_parts)
    if not url.endswith('/'):
        url += '/'
    
    if query_params:
        url += '?' + urlencode(query_params)
    
    return url


# Convenience functions for common use cases
def build_rental_url(**kwargs) -> str:
    """Build URL for rental properties."""
    return build_funda_url(transaction_type="huur", **kwargs)


def build_sale_url(**kwargs) -> str:
    """Build URL for properties for sale."""
    return build_funda_url(transaction_type="koop", **kwargs)


# Example usage and constants
PROPERTY_TYPES = {
    'woonhuis': 'House',
    'appartement': 'Apartment',
    'studio': 'Studio',
    'kamer': 'Room',
    'parkeergelegenheid': 'Parking',
    'berging': 'Storage',
    'opslagruimte': 'Storage space',
    'ligplaats': 'Berth',
    'standplaats': 'Pitch',
    'bouwgrond': 'Building plot'
}

ENERGY_LABELS = ['A++', 'A+', 'A', 'B', 'C', 'D', 'E', 'F', 'G']

GARDEN_ORIENTATIONS = ['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest']

SORT_OPTIONS = {
    'price_asc': 'Price (low to high)',
    'price_desc': 'Price (high to low)',
    'date_desc': 'Newest first',
    'date_asc': 'Oldest first',
    'floor_area_desc': 'Largest first',
    'floor_area_asc': 'Smallest first'
}


if __name__ == "__main__":
    # Example usage
    
    # Modern URL for Amsterdam apartments
    url1 = build_rental_url(
        selected_area=["amsterdam"],
        object_type=["appartement"],
        min_price=1000,
        max_price=2500,
        min_rooms=2,
        energy_label=["A", "B", "C"],
        furnished=True,
        balcony=True,
        use_modern_url=True
    )
    print("Modern URL:", url1)
    
    # Legacy URL for Rotterdam houses
    url2 = build_rental_url(
        city="Rotterdam",
        property_type="woonhuis",
        min_price=1500,
        max_price=3000,
        min_floor_area=100,
        min_bedrooms=3,
        energy_label="B",
        use_modern_url=False
    )
    print("Legacy URL:", url2)
    
    # Sale URL with comprehensive filters
    url3 = build_sale_url(
        city="Utrecht",
        min_price=300000,
        max_price=500000,
        min_floor_area=80,
        max_floor_area=120,
        min_bedrooms=2,
        max_bedrooms=3,
        energy_label=["A", "B"],
        garden=True,
        parking=True,
        sort_by="price_asc"
    )
    print("Sale URL:", url3)