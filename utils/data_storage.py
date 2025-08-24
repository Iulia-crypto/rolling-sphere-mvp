import json
import os
from datetime import datetime
import pandas as pd
from utils.database import DatabaseManager

class DataStorage:
    def __init__(self):
        self.db = DatabaseManager()
        self.data_dir = "data/user_data"
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_calculation(self, username, company_info, emissions_data, csv_data):
        """Save a calculation for a user"""
        try:
            # Try database first
            calc_id = self.db.save_calculation(username, company_info, emissions_data, csv_data)
            if calc_id is not None:
                return calc_id
        except Exception as e:
            print(f"Database save failed: {e}")
        
        # Fallback to file-based storage
        user_file = os.path.join(self.data_dir, f"{username}.json")
        
        # Load existing data
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                user_data = json.load(f)
        else:
            user_data = {"calculations": []}
        
        # Prepare calculation data
        calculation = {
            "id": len(user_data["calculations"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "company_info": company_info,
            "emissions_summary": emissions_data["summary"],
            "emissions_by_activity": emissions_data["by_activity"],
            "emissions_by_category": emissions_data["by_category"],
            "monthly_emissions": emissions_data.get("monthly_emissions", {}),
            "csv_row_count": len(csv_data) if csv_data is not None else 0
        }
        
        # Add to user data
        user_data["calculations"].append(calculation)
        
        # Keep only the last 50 calculations to manage file size
        if len(user_data["calculations"]) > 50:
            user_data["calculations"] = user_data["calculations"][-50:]
        
        # Save to file
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        return calculation["id"]
    
    def get_user_calculations(self, username, limit=10):
        """Get calculations for a user"""
        try:
            # Try database first
            calculations = self.db.get_user_calculations(username, limit)
            if calculations:
                return calculations
        except Exception as e:
            print(f"Database read failed: {e}")
        
        # Fallback to file-based storage
        user_file = os.path.join(self.data_dir, f"{username}.json")
        
        if not os.path.exists(user_file):
            return []
        
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        
        calculations = user_data.get("calculations", [])
        # Return most recent calculations first
        return sorted(calculations, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_calculation_history(self, username):
        """Get calculation history for charts"""
        try:
            # Try database first
            history_df = self.db.get_calculation_history(username)
            if not history_df.empty:
                return history_df
        except Exception as e:
            print(f"Database history read failed: {e}")
        
        # Fallback to file-based storage
        calculations = self.get_user_calculations(username, limit=50)
        
        if not calculations:
            return pd.DataFrame()
        
        # Create dataframe for trend analysis
        history_data = []
        for calc in calculations:
            history_data.append({
                "date": calc["timestamp"][:10],  # Just the date part
                "total_emissions": calc["emissions_summary"]["total_co2_kg"],
                "company": calc["company_info"].get("name", "Unknown"),
                "activities_count": calc["csv_row_count"]
            })
        
        return pd.DataFrame(history_data)
    
    def delete_calculation(self, username, calculation_id):
        """Delete a specific calculation"""
        user_file = os.path.join(self.data_dir, f"{username}.json")
        
        if not os.path.exists(user_file):
            return False
        
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        
        # Filter out the calculation to delete
        original_count = len(user_data["calculations"])
        user_data["calculations"] = [
            calc for calc in user_data["calculations"] 
            if calc["id"] != calculation_id
        ]
        
        if len(user_data["calculations"]) < original_count:
            with open(user_file, 'w') as f:
                json.dump(user_data, f, indent=2)
            return True
        
        return False