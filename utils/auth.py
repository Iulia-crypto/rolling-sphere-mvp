import streamlit as st
import streamlit_authenticator as stauth
import bcrypt
import json
import os
from datetime import datetime
from utils.database import DatabaseManager

class SimpleAuth:
    def __init__(self):
        self.db = DatabaseManager()
        self.users_file = "data/users.json"
        self.ensure_users_file()
    
    def ensure_users_file(self):
        """Ensure the users file exists"""
        if not os.path.exists("data"):
            os.makedirs("data")
        
        if not os.path.exists(self.users_file):
            # Create initial users file with a demo user
            demo_password = bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            initial_users = {
                "demo": {
                    "password": demo_password,
                    "name": "Demo User",
                    "email": "demo@example.com",
                    "created_at": datetime.now().isoformat()
                }
            }
            with open(self.users_file, 'w') as f:
                json.dump(initial_users, f, indent=2)
    
    def load_users(self):
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_users(self, users):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def hash_password(self, password):
        """Hash a password"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def register_user(self, username, password, name, email):
        """Register a new user"""
        try:
            # Try database first
            success, message = self.db.create_user(username, self.hash_password(password), name, email)
            if success:
                return True, message
        except Exception as e:
            print(f"Database registration failed: {e}")
        
        # Fallback to file-based storage
        users = self.load_users()
        
        if username in users:
            return False, "Username already exists"
        
        users[username] = {
            "password": self.hash_password(password),
            "name": name,
            "email": email,
            "created_at": datetime.now().isoformat()
        }
        
        self.save_users(users)
        return True, "User registered successfully"
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        try:
            # Try database first
            user_data = self.db.get_user(username)
            if user_data:
                if self.verify_password(password, user_data["password_hash"]):
                    return True, {
                        "name": user_data["name"],
                        "email": user_data["email"],
                        "created_at": user_data["created_at"]
                    }
                else:
                    return False, "Invalid password"
        except Exception as e:
            print(f"Database authentication failed: {e}")
        
        # Fallback to file-based storage
        users = self.load_users()
        
        if username not in users:
            return False, "Username not found"
        
        if self.verify_password(password, users[username]["password"]):
            return True, users[username]
        else:
            return False, "Invalid password"
    
    def show_login_form(self):
        """Show login form"""
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if username and password:
                    success, result = self.authenticate_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_info = result
                        st.session_state.username = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(result)
                else:
                    st.error("Please enter both username and password")
    
    def show_register_form(self):
        """Show registration form"""
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            username = st.text_input("Choose Username")
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if username and name and email and password and confirm_password:
                    if password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        success, message = self.register_user(username, password, name, email)
                        if success:
                            st.success(message)
                            st.info("You can now login with your credentials")
                        else:
                            st.error(message)
                else:
                    st.error("Please fill in all fields")
    
    def logout(self):
        """Logout user"""
        for key in ['authenticated', 'user_info', 'username']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    def get_current_user(self):
        """Get current user info"""
        return st.session_state.get('user_info', {})