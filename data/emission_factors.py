"""
Emission factors database for various activities and fuels
Values are in kg CO2 equivalent per unit

Sources:
- UK Government GHG Conversion Factors 2023
- EPA Emission Factors for Greenhouse Gas Inventories
- IPCC Guidelines for National Greenhouse Gas Inventories

All factors are approximate and may vary by region and specific circumstances
"""

EMISSION_FACTORS = {
    # Electricity (kg CO2 per kWh)
    'electricity': {
        'grid_electricity': {
            'kwh': 0.233,  # UK grid average
            'mwh': 233.0,
            'default': 0.233
        },
        'renewable_electricity': {
            'kwh': 0.0,
            'mwh': 0.0,
            'default': 0.0
        },
        'default': 0.233
    },
    
    # Fuels (kg CO2 per liter unless specified)
    'fuel': {
        'gasoline': {
            'liters': 2.31,
            'litres': 2.31,
            'gallons': 8.75,  # US gallons
            'default': 2.31
        },
        'petrol': {
            'liters': 2.31,
            'litres': 2.31,
            'gallons': 8.75,
            'default': 2.31
        },
        'diesel': {
            'liters': 2.68,
            'litres': 2.68,
            'gallons': 10.15,
            'default': 2.68
        },
        'natural_gas': {
            'kwh': 0.184,
            'mwh': 184.0,
            'm3': 1.85,  # cubic meters
            'cubic_meters': 1.85,
            'default': 0.184
        },
        'lpg': {
            'liters': 1.51,
            'litres': 1.51,
            'kg': 2.98,
            'default': 1.51
        },
        'heating_oil': {
            'liters': 2.52,
            'litres': 2.52,
            'gallons': 9.54,
            'default': 2.52
        },
        'default': 2.31
    },
    
    # Transportation (kg CO2 per km unless specified)
    'transportation': {
        'car_petrol': {
            'km': 0.171,
            'miles': 0.275,
            'default': 0.171
        },
        'car_diesel': {
            'km': 0.169,
            'miles': 0.272,
            'default': 0.169
        },
        'car_hybrid': {
            'km': 0.109,
            'miles': 0.175,
            'default': 0.109
        },
        'car_electric': {
            'km': 0.047,  # Based on grid electricity
            'miles': 0.076,
            'default': 0.047
        },
        'motorcycle': {
            'km': 0.113,
            'miles': 0.182,
            'default': 0.113
        },
        'bus': {
            'km': 0.089,  # Per passenger km
            'miles': 0.143,
            'default': 0.089
        },
        'train': {
            'km': 0.035,  # Per passenger km
            'miles': 0.056,
            'default': 0.035
        },
        'flight_domestic': {
            'km': 0.255,  # Per passenger km
            'miles': 0.410,
            'default': 0.255
        },
        'flight_international': {
            'km': 0.195,  # Per passenger km
            'miles': 0.314,
            'default': 0.195
        },
        'taxi': {
            'km': 0.171,
            'miles': 0.275,
            'default': 0.171
        },
        'delivery_van': {
            'km': 0.235,
            'miles': 0.378,
            'default': 0.235
        },
        'truck': {
            'km': 0.891,  # Heavy goods vehicle
            'miles': 1.434,
            'default': 0.891
        },
        'default': 0.171
    },
    
    # Heating (kg CO2 per kWh unless specified)
    'heating': {
        'natural_gas': {
            'kwh': 0.184,
            'mwh': 184.0,
            'm3': 1.85,
            'cubic_meters': 1.85,
            'default': 0.184
        },
        'heating_oil': {
            'liters': 2.52,
            'litres': 2.52,
            'kwh': 0.245,
            'default': 0.245
        },
        'electricity': {
            'kwh': 0.233,
            'mwh': 233.0,
            'default': 0.233
        },
        'lpg': {
            'liters': 1.51,
            'litres': 1.51,
            'kg': 2.98,
            'kwh': 0.214,
            'default': 0.214
        },
        'biomass': {
            'kg': 0.0,  # Considered carbon neutral
            'tonnes': 0.0,
            'kwh': 0.0,
            'default': 0.0
        },
        'district_heating': {
            'kwh': 0.150,  # District heating factor
            'mwh': 150.0,
            'default': 0.150
        },
        'default': 0.184
    },
    
    # Cooling/Air Conditioning (kg CO2 per kWh)
    'cooling': {
        'electricity': {
            'kwh': 0.233,
            'mwh': 233.0,
            'default': 0.233
        },
        'district_cooling': {
            'kwh': 0.120,  # District cooling factor
            'mwh': 120.0,
            'default': 0.120
        },
        'default': 0.233
    },
    
    # Waste (kg CO2 per kg unless specified)
    'waste': {
        'general_waste': {
            'kg': 0.7,
            'tonnes': 700.0,
            'tons': 700.0,
            'default': 0.7
        },
        'recycling': {
            'kg': 0.1,
            'tonnes': 100.0,
            'tons': 100.0,
            'default': 0.1
        },
        'organic_waste': {
            'kg': 0.3,
            'tonnes': 300.0,
            'tons': 300.0,
            'default': 0.3
        },
        'default': 0.7
    },
    
    # Water (kg CO2 per liter unless specified)
    'water': {
        'mains_water': {
            'liters': 0.000298,
            'litres': 0.000298,
            'm3': 0.298,
            'cubic_meters': 0.298,
            'gallons': 0.00113,
            'default': 0.000298
        },
        'default': 0.000298
    },
    
    # Paper (kg CO2 per sheet or kg)
    'paper': {
        'office_paper': {
            'sheets': 0.0046,  # A4 sheet
            'kg': 1.84,
            'default': 0.0046
        },
        'recycled_paper': {
            'sheets': 0.0028,
            'kg': 1.12,
            'default': 0.0028
        },
        'default': 0.0046
    },
    
    # Travel/Accommodation (kg CO2 per night for hotels)
    'travel': {
        'hotel_night': {
            'nights': 29.0,  # Per room per night
            'default': 29.0
        },
        'default': 29.0
    },
    
    # Shipping/Freight (kg CO2 per tonne-km)
    'shipping': {
        'road_freight': {
            'tonne_km': 0.099,
            'default': 0.099
        },
        'rail_freight': {
            'tonne_km': 0.024,
            'default': 0.024
        },
        'air_freight': {
            'tonne_km': 1.016,
            'default': 1.016
        },
        'sea_freight': {
            'tonne_km': 0.015,
            'default': 0.015
        },
        'default': 0.099
    },
    
    # Manufacturing (kg CO2 per unit - very approximate)
    'manufacturing': {
        'steel': {
            'kg': 2.3,
            'tonnes': 2300.0,
            'default': 2.3
        },
        'aluminum': {
            'kg': 9.0,
            'tonnes': 9000.0,
            'default': 9.0
        },
        'plastic': {
            'kg': 2.0,
            'tonnes': 2000.0,
            'default': 2.0
        },
        'concrete': {
            'kg': 0.13,
            'tonnes': 130.0,
            'default': 0.13
        },
        'process_emissions': {
            'kg_co2': 1.0,  # Direct CO2 emissions
            'kg': 1.0,
            'tonnes': 1000.0,
            'default': 1.0
        },
        'default': 1.0
    },
    
    # Refrigerants (kg CO2 per kg of refrigerant - GWP values)
    'refrigerants': {
        'r134a': {
            'kg': 1430,  # GWP of R-134a
            'default': 1430
        },
        'r410a': {
            'kg': 2088,  # GWP of R-410A
            'default': 2088
        },
        'r22': {
            'kg': 1810,  # GWP of R-22
            'default': 1810
        },
        'default': 1430
    },
    
    # Purchased Goods (kg CO2 per Euro/USD/GBP spent)
    'purchased_goods': {
        'office_supplies': {
            'eur': 0.45,  # Average 0.45 kg CO2 per Euro spent on office supplies
            'usd': 0.40,  # Average 0.40 kg CO2 per USD spent
            'gbp': 0.50,  # Average 0.50 kg CO2 per GBP spent
            'default': 0.45
        },
        'raw_materials': {
            'eur': 0.60,  # Higher factor for raw materials
            'usd': 0.55,
            'gbp': 0.65,
            'default': 0.60
        },
        'default': 0.45
    },
    
    # Business Travel (kg CO2 per km or per night)
    'business_travel': {
        'flights_domestic': {
            'km': 0.255,  # Per passenger km
            'miles': 0.410,
            'default': 0.255
        },
        'flights_international': {
            'km': 0.195,  # Per passenger km
            'miles': 0.314,
            'default': 0.195
        },
        'hotel_nights': {
            'nights': 29.0,  # Per room per night
            'default': 29.0
        },
        'car_rental': {
            'km': 0.171,  # Similar to petrol car
            'miles': 0.275,
            'default': 0.171
        },
        'default': 0.255
    },
    
    # Employee Commuting (kg CO2 per km)
    'employee_commuting': {
        'car_commuting': {
            'km': 0.171,  # Average car emissions
            'miles': 0.275,
            'default': 0.171
        },
        'public_transport': {
            'km': 0.035,  # Train/bus average
            'miles': 0.056,
            'default': 0.035
        },
        'default': 0.171
    },
    
    # Digital/IT (kg CO2 per unit)
    'digital': {
        'cloud_services': {
            'gb_month': 0.5,  # Per GB per month
            'gb': 0.5,
            'default': 0.5
        },
        'data_centers': {
            'kwh': 0.233,  # Same as grid electricity
            'default': 0.233
        },
        'default': 0.5
    },
    
    # Leased Assets (kg CO2 per unit)
    'leased_assets': {
        'office_space': {
            'm2_month': 2.5,  # Per square meter per month
            'm2': 2.5,
            'default': 2.5
        },
        'default': 2.5
    },
    
    # Investments (kg CO2 per Euro invested - very approximate)
    'investments': {
        'portfolio_emissions': {
            'eur_invested': 0.25,  # Per Euro invested
            'usd_invested': 0.22,
            'gbp_invested': 0.28,
            'default': 0.25
        },
        'default': 0.25
    }
}

# Unit conversion factors (to convert to standard units)
UNIT_CONVERSIONS = {
    # Energy conversions to kWh
    'mwh': 1000.0,  # MWh to kWh
    'btu': 0.000293071,  # BTU to kWh
    'joules': 2.77778e-7,  # Joules to kWh
    'kwh': 1.0,
    
    # Volume conversions to liters
    'gallons': 3.78541,  # US gallons to liters
    'imperial_gallons': 4.54609,  # Imperial gallons to liters
    'litres': 1.0,
    'liters': 1.0,
    'm3': 1000.0,  # cubic meters to liters
    'cubic_meters': 1000.0,
    
    # Mass conversions to kg
    'tonnes': 1000.0,  # tonnes to kg
    'tons': 907.185,  # US tons to kg
    'pounds': 0.453592,  # pounds to kg
    'kg': 1.0,
    
    # Distance conversions to km
    'miles': 1.60934,  # miles to km
    'km': 1.0,
    
    # Other
    'pieces': 1.0,
    'units': 1.0,
    'sheets': 1.0,
    'nights': 1.0,
    'hours': 1.0,
    'days': 1.0,
    'kg_co2': 1.0,  # Direct CO2 emissions
    'gb_month': 1.0,  # Gigabytes per month
    'gb': 1.0,  # Gigabytes
    'm2_month': 1.0,  # Square meters per month
    'm2': 1.0,  # Square meters
    'eur_invested': 1.0,  # Euros invested
    'usd_invested': 1.0,  # USD invested
    'gbp_invested': 1.0   # GBP invested
}
