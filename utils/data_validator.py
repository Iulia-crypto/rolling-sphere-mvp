import pandas as pd
import numpy as np
from datetime import datetime

class DataValidator:
    def __init__(self):
        self.errors = []
        self.required_columns = ['activity_type', 'category', 'amount', 'unit']
        self.valid_activity_types = [
            'electricity', 'fuel', 'transportation', 'heating', 'cooling',
            'waste', 'water', 'paper', 'travel', 'shipping', 'manufacturing',
            'refrigerants', 'purchased_goods', 'business_travel', 
            'employee_commuting', 'digital', 'leased_assets', 'investments'
        ]
        self.valid_units = [
            'kwh', 'mwh', 'liters', 'litres', 'gallons', 'kg', 'tonnes', 'tons',
            'km', 'miles', 'hours', 'days', 'pieces', 'units', 'm3', 'cubic_meters',
            'eur', 'usd', 'gbp', 'nights', 'sheets', 'tonne_km', 'btu', 'joules',
            'imperial_gallons', 'pounds', 'cubic_feet', 'mj', 'kg_co2', 'gb_month',
            'gb', 'm2_month', 'm2', 'eur_invested', 'usd_invested', 'gbp_invested'
        ]
    
    def validate_data(self, df):
        """
        Validate the uploaded CSV data
        Returns True if validation passes, False otherwise
        """
        self.errors = []
        
        if df is None or df.empty:
            self.errors.append("No data provided or file is empty")
            return False
        
        # Check required columns
        if not self._check_required_columns(df):
            return False
        
        # Validate data types and values
        if not self._validate_data_types(df):
            return False
        
        # Validate activity types
        if not self._validate_activity_types(df):
            return False
        
        # Validate units
        if not self._validate_units(df):
            return False
        
        # Validate amounts
        if not self._validate_amounts(df):
            return False
        
        # Validate dates if present
        if 'date' in df.columns:
            if not self._validate_dates(df):
                return False
        
        return len(self.errors) == 0
    
    def _check_required_columns(self, df):
        """Check if all required columns are present"""
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        
        if missing_columns:
            self.errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            return False
        
        return True
    
    def _validate_data_types(self, df):
        """Validate basic data types"""
        valid = True
        
        # Check for completely empty rows
        empty_rows = df.isnull().all(axis=1).sum()
        if empty_rows > 0:
            self.errors.append(f"Found {empty_rows} completely empty rows")
            valid = False
        
        # Check for missing values in required columns
        for col in self.required_columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                self.errors.append(f"Missing values in required column '{col}': {missing_count} rows")
                valid = False
        
        return valid
    
    def _validate_activity_types(self, df):
        """Validate activity types against known categories"""
        if 'activity_type' not in df.columns:
            return True
        
        # Convert to lowercase and strip whitespace
        activity_types = df['activity_type'].astype(str).str.lower().str.strip()
        invalid_types = []
        
        for activity_type in activity_types.unique():
            if activity_type not in self.valid_activity_types and activity_type != 'nan':
                invalid_types.append(activity_type)
        
        if invalid_types:
            self.errors.append(f"Invalid activity types found: {', '.join(invalid_types)}")
            self.errors.append(f"Valid activity types: {', '.join(self.valid_activity_types)}")
            # Don't return False - just warn about unknown activity types
        
        return True
    
    def _validate_units(self, df):
        """Validate measurement units"""
        if 'unit' not in df.columns:
            return True
        
        # Convert to lowercase and strip whitespace
        units = df['unit'].astype(str).str.lower().str.strip()
        invalid_units = []
        
        for unit in units.unique():
            if unit not in self.valid_units and unit != 'nan':
                invalid_units.append(unit)
        
        if invalid_units:
            self.errors.append(f"Unknown units found: {', '.join(invalid_units)}")
            self.errors.append(f"Common units: {', '.join(self.valid_units[:10])}")
            # Don't return False - just warn about unknown units
        
        return True
    
    def _validate_amounts(self, df):
        """Validate amount values"""
        if 'amount' not in df.columns:
            return True
        
        valid = True
        
        # Check for non-numeric amounts
        try:
            # Check each value individually to avoid type issues
            non_numeric_count = 0
            negative_count = 0
            zero_count = 0
            
            for idx, amount in df['amount'].items():
                if pd.isnull(amount):
                    continue
                
                try:
                    numeric_amount = float(amount)
                    if numeric_amount < 0:
                        negative_count += 1
                    elif numeric_amount == 0:
                        zero_count += 1
                except (ValueError, TypeError):
                    non_numeric_count += 1
            
            if non_numeric_count > 0:
                self.errors.append(f"Non-numeric values found in 'amount' column: {non_numeric_count} rows")
                valid = False
            
            if negative_count > 0:
                self.errors.append(f"Negative amounts found: {negative_count} rows")
                valid = False
            
            if zero_count > 0:
                self.errors.append(f"Warning: Zero amounts found: {zero_count} rows")
                # Don't mark as invalid for zero amounts
            
        except Exception as e:
            self.errors.append(f"Error validating amounts: {str(e)}")
            valid = False
        
        return valid
    
    def _validate_dates(self, df):
        """Validate date format if date column is present"""
        if 'date' not in df.columns:
            return True
        
        valid = True
        invalid_dates = 0
        
        for index, date_str in df['date'].items():
            if pd.isnull(date_str):
                continue
            
            try:
                # Try to parse the date
                pd.to_datetime(date_str)
            except:
                invalid_dates += 1
        
        if invalid_dates > 0:
            self.errors.append(f"Invalid date formats found: {invalid_dates} rows")
            self.errors.append("Please use YYYY-MM-DD format for dates")
            valid = False
        
        return valid
    
    def get_errors(self):
        """Return list of validation errors"""
        return self.errors
    
    def get_data_summary(self, df):
        """Get summary statistics of the data"""
        if df is None or df.empty:
            return {}
        
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'activity_types': df['activity_type'].nunique() if 'activity_type' in df.columns else 0,
            'categories': df['category'].nunique() if 'category' in df.columns else 0,
            'date_range': None
        }
        
        # Get date range if dates are present
        if 'date' in df.columns:
            try:
                dates = pd.to_datetime(df['date'], errors='coerce')
                dates = dates.dropna()
                if len(dates) > 0:
                    summary['date_range'] = {
                        'start': dates.min().strftime('%Y-%m-%d'),
                        'end': dates.max().strftime('%Y-%m-%d')
                    }
            except:
                pass
        
        return summary
