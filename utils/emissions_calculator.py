import pandas as pd
from datetime import datetime
from data.emission_factors import EMISSION_FACTORS
import numpy as np

class EmissionsCalculator:
    def __init__(self):
        self.emission_factors = EMISSION_FACTORS
        
        # GHG Protocol Scope categorization
        self.scope_categories = {
            'scope_1': ['fuel', 'heating', 'refrigerants', 'manufacturing'],
            'scope_2': ['electricity', 'cooling'],  # electricity and energy-related cooling/heating
            'scope_3': ['purchased_goods', 'business_travel', 'employee_commuting', 'waste', 
                       'water', 'paper', 'travel', 'shipping', 'digital', 'leased_assets', 
                       'investments', 'transportation']
        }
    
    def calculate_emissions(self, df):
        """
        Calculate CO2 emissions from the input data
        Returns a dictionary with detailed results and summaries
        """
        try:
            results = {
                'detailed_results': [],
                'summary': {},
                'by_activity': {},
                'by_category': {},
                'monthly_emissions': {},
                'by_scope': {
                    'scope_1': {'total_kg': 0, 'activities': [], 'categories': []},
                    'scope_2': {'total_kg': 0, 'activities': [], 'categories': []},
                    'scope_3': {'total_kg': 0, 'activities': [], 'categories': []}
                }
            }
            
            total_emissions = 0
            
            for index, row in df.iterrows():
                activity_type = str(row.get('activity_type', '')).lower().strip()
                category = str(row.get('category', '')).lower().strip()
                amount = float(row.get('amount', 0))
                unit = str(row.get('unit', '')).lower().strip()
                date = row.get('date', '')
                
                # Get emission factor
                emission_factor = self._get_emission_factor(activity_type, category, unit)
                
                if emission_factor > 0:
                    # Calculate CO2 emissions
                    co2_emissions = amount * emission_factor
                    total_emissions += co2_emissions
                    
                    # Store detailed result
                    detail = {
                        'activity_type': activity_type,
                        'category': category,
                        'amount': amount,
                        'unit': unit,
                        'emission_factor': emission_factor,
                        'co2_emissions_kg': co2_emissions,
                        'date': date
                    }
                    results['detailed_results'].append(detail)
                    
                    # Categorize by GHG Protocol Scope
                    scope = self._get_ghg_scope(activity_type)
                    results['by_scope'][scope]['total_kg'] += co2_emissions
                    if activity_type not in results['by_scope'][scope]['activities']:
                        results['by_scope'][scope]['activities'].append(activity_type)
                    if category not in results['by_scope'][scope]['categories']:
                        results['by_scope'][scope]['categories'].append(category)
                    
                    # Aggregate by activity type
                    if activity_type in results['by_activity']:
                        results['by_activity'][activity_type] += co2_emissions
                    else:
                        results['by_activity'][activity_type] = co2_emissions
                    
                    # Aggregate by category
                    if category in results['by_category']:
                        results['by_category'][category] += co2_emissions
                    else:
                        results['by_category'][category] = co2_emissions
                    
                    # Aggregate by month if date is available
                    if date:
                        try:
                            month_key = pd.to_datetime(date).strftime('%Y-%m')
                            if month_key in results['monthly_emissions']:
                                results['monthly_emissions'][month_key] += co2_emissions
                            else:
                                results['monthly_emissions'][month_key] = co2_emissions
                        except:
                            pass  # Skip if date parsing fails
            
            # Calculate summary statistics
            results['summary'] = {
                'total_co2_kg': total_emissions,
                'total_co2_tonnes': total_emissions / 1000,
                'total_activities': len(results['detailed_results']),
                'unique_activity_types': len(results['by_activity']),
                'calculation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
            return results
            
        except Exception as e:
            print(f"Error in emissions calculation: {str(e)}")
            return None
    
    def _get_emission_factor(self, activity_type, category, unit):
        """
        Get emission factor for given activity type, category, and unit
        Returns CO2 kg per unit
        """
        # Normalize inputs
        activity_type = activity_type.lower().replace(' ', '_')
        category = category.lower().replace(' ', '_')
        unit = unit.lower()
        
        # Look for specific emission factor
        if activity_type in self.emission_factors:
            activity_factors = self.emission_factors[activity_type]
            
            if category in activity_factors:
                category_factors = activity_factors[category]
                
                # Check for unit-specific factor
                if unit in category_factors:
                    return category_factors[unit]
                
                # Use default factor if available
                if 'default' in category_factors:
                    return category_factors['default']
            
            # Use activity default if available
            if 'default' in activity_factors:
                return activity_factors['default']
        
        # Return 0 if no emission factor found
        return 0.0
    
    def _generate_recommendations(self, results):
        """
        Generate emission reduction recommendations based on the results
        """
        recommendations = []
        
        if not results['by_activity']:
            return recommendations
        
        # Find highest emission activity
        max_activity = max(results['by_activity'], key=results['by_activity'].get)
        max_emissions = results['by_activity'][max_activity]
        
        # General recommendations based on highest emission source
        if max_activity == 'electricity':
            recommendations.extend([
                "Switch to renewable energy sources or green electricity tariffs",
                "Implement energy-efficient LED lighting systems",
                "Install programmable thermostats and energy management systems",
                "Consider solar panels or other on-site renewable energy generation"
            ])
        elif max_activity == 'fuel':
            recommendations.extend([
                "Transition to electric or hybrid vehicles",
                "Optimize delivery routes and consolidate trips",
                "Consider biofuels or other alternative fuel sources",
                "Implement fuel-efficient driving practices and training"
            ])
        elif max_activity == 'transportation':
            recommendations.extend([
                "Promote remote work and video conferencing",
                "Encourage public transportation or carpooling",
                "Consider electric vehicle fleet transition",
                "Implement travel policies to reduce business travel"
            ])
        elif max_activity == 'heating':
            recommendations.extend([
                "Upgrade to high-efficiency heating systems",
                "Improve building insulation and weatherproofing",
                "Consider heat pumps or other renewable heating sources",
                "Implement smart building controls and zoning"
            ])
        
        # Add general recommendations
        recommendations.extend([
            "Conduct regular energy audits to identify improvement opportunities",
            "Set science-based emission reduction targets",
            "Engage employees in sustainability initiatives",
            "Consider carbon offset programs for remaining emissions"
        ])
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _get_ghg_scope(self, activity_type):
        """
        Determine GHG Protocol Scope for activity type
        """
        if activity_type in self.scope_categories['scope_1']:
            return 'scope_1'
        elif activity_type in self.scope_categories['scope_2']:
            return 'scope_2'
        else:
            return 'scope_3'
