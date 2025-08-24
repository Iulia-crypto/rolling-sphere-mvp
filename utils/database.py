import os
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import json
import pandas as pd

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Calculation(Base):
    __tablename__ = 'calculations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, sa.ForeignKey('users.id'), nullable=False)
    company_name = Column(String(200))
    company_info = Column(JSON)
    emissions_summary = Column(JSON)
    emissions_by_activity = Column(JSON)
    emissions_by_category = Column(JSON)
    monthly_emissions = Column(JSON)
    csv_row_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.engine = None
        self.SessionLocal = None
        self.setup_database()
    
    def setup_database(self):
        """Setup database connection and create tables"""
        try:
            if self.database_url and self.database_url.startswith('postgresql://'):
                # Handle Supabase/PostgreSQL URL format
                self.engine = create_engine(self.database_url)
                print("Connected to PostgreSQL database")
            else:
                # Use local SQLite
                if not os.path.exists('data'):
                    os.makedirs('data')
                self.engine = create_engine('sqlite:///data/emissions_calculator.db')
                print("Using local SQLite database")
            
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
                
        except Exception as e:
            print(f"Database connection failed: {e}")
            # Fallback to SQLite
            if not os.path.exists('data'):
                os.makedirs('data')
            self.engine = create_engine('sqlite:///data/emissions_calculator.db')
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def create_user(self, username: str, password_hash: str, name: str, email: str):
        """Create a new user"""
        db = self.get_session()
        try:
            # Check if user exists
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                return False, "Username already exists"
            
            new_user = User(
                username=username,
                password_hash=password_hash,
                name=name,
                email=email
            )
            db.add(new_user)
            db.commit()
            return True, "User created successfully"
        except Exception as e:
            db.rollback()
            return False, f"Error creating user: {str(e)}"
        finally:
            db.close()
    
    def get_user(self, username: str):
        """Get user by username"""
        db = self.get_session()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'password_hash': user.password_hash,
                    'name': user.name,
                    'email': user.email,
                    'created_at': user.created_at.isoformat()
                }
            return None
        finally:
            db.close()
    
    def save_calculation(self, username: str, company_info: dict, emissions_data: dict, csv_data):
        """Save a calculation to database"""
        db = self.get_session()
        try:
            # Get user
            user = db.query(User).filter(User.username == username).first()
            if not user:
                return None
            
            calculation = Calculation(
                user_id=user.id,
                company_name=company_info.get('name', ''),
                company_info=company_info,
                emissions_summary=emissions_data['summary'],
                emissions_by_activity=emissions_data['by_activity'],
                emissions_by_category=emissions_data['by_category'],
                monthly_emissions=emissions_data.get('monthly_emissions', {}),
                csv_row_count=len(csv_data) if csv_data is not None else 0
            )
            
            db.add(calculation)
            db.commit()
            return calculation.id
        except Exception as e:
            db.rollback()
            print(f"Error saving calculation: {e}")
            return None
        finally:
            db.close()
    
    def get_user_calculations(self, username: str, limit: int = 10):
        """Get calculations for a user"""
        db = self.get_session()
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                return []
            
            calculations = db.query(Calculation).filter(
                Calculation.user_id == user.id
            ).order_by(Calculation.created_at.desc()).limit(limit).all()
            
            result = []
            for calc in calculations:
                result.append({
                    'id': calc.id,
                    'timestamp': calc.created_at.isoformat(),
                    'company_info': calc.company_info,
                    'emissions_summary': calc.emissions_summary,
                    'emissions_by_activity': calc.emissions_by_activity,
                    'emissions_by_category': calc.emissions_by_category,
                    'monthly_emissions': calc.monthly_emissions,
                    'csv_row_count': calc.csv_row_count
                })
            
            return result
        finally:
            db.close()
    
    def get_calculation_history(self, username: str):
        """Get calculation history for charts"""
        calculations = self.get_user_calculations(username, limit=50)
        
        if not calculations:
            return pd.DataFrame()
        
        history_data = []
        for calc in calculations:
            history_data.append({
                "date": calc["timestamp"][:10],
                "total_emissions": calc["emissions_summary"]["total_co2_kg"],
                "company": calc["company_info"].get("name", "Unknown"),
                "activities_count": calc["csv_row_count"]
            })
        
        return pd.DataFrame(history_data)
    
    def delete_calculation(self, username: str, calculation_id: int):
        """Delete a specific calculation"""
        db = self.get_session()
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                return False
            
            calculation = db.query(Calculation).filter(
                Calculation.id == calculation_id,
                Calculation.user_id == user.id
            ).first()
            
            if calculation:
                db.delete(calculation)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            return False
        finally:
            db.close()