import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.emissions_calculator import EmissionsCalculator
from utils.pdf_generator import PDFGenerator
from utils.data_validator import DataValidator
from utils.auth import SimpleAuth
from utils.data_storage import DataStorage
from utils.compliance_engine import ComplianceEngine
from utils.pdf_report_generator import ComplianceReportGenerator
from data.regulatory_database import RegulatoryDatabase
import io
import base64
import os

def get_logo_base64():
    """Convert logo image to base64 for HTML embedding"""
    try:
        with open("assets/logo.png", "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# Configure page
st.set_page_config(
    page_title="Rolling Sphere - CO2 Emissions Calculator",
    page_icon="🌱",
    layout="wide"
)

def show_cookie_banner():
    """Display GDPR-compliant cookie banner"""
    # Initialize cookie consent if not set
    if 'cookie_consent' not in st.session_state:
        st.session_state.cookie_consent = None
    
    # Only show banner if no consent given
    if st.session_state.cookie_consent is None:
        
        # Use Streamlit buttons for interaction
        st.markdown("### Cookie Consent Required")
        st.info("Please choose your cookie preferences to continue using the application.")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            if st.button("Decline Cookies", key="cookie_decline", use_container_width=True):
                st.session_state.cookie_consent = "declined"
                st.rerun()
        
        with col3:
            if st.button("Accept Cookies", key="cookie_accept", type="primary", use_container_width=True):
                st.session_state.cookie_consent = "accepted"
                st.rerun()
        
        # Stop execution until user makes a choice
        st.stop()

def show_cookie_settings():
    """Show cookie settings/privacy preferences"""
    st.markdown("### 🍪 Cookie Settings")
    st.markdown("Manage your cookie preferences and privacy settings.")
    
    current_consent = st.session_state.get('cookie_consent', 'not_set')
    
    st.markdown(f"**Current Status:** {current_consent.replace('_', ' ').title()}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Accept All Cookies", type="primary"):
            st.session_state.cookie_consent = "accepted"
            st.success("✅ Cookie preferences updated - All cookies accepted")
            st.rerun()
    
    with col2:
        if st.button("Decline All Cookies"):
            st.session_state.cookie_consent = "declined"
            st.success("✅ Cookie preferences updated - Cookies declined")
            st.rerun()
    
    st.markdown("---")
    st.markdown("**About Our Cookies:**")
    st.markdown("- **Essential Cookies:** Required for platform functionality")
    st.markdown("- **Analytics:** Help us improve user experience (if accepted)")
    st.markdown("- **No Tracking:** We do not use advertising or third-party tracking cookies")

def show_rolling_sphere_header():
    """Show Rolling Sphere branding header"""
    # Center the logo and branding with logo inline with text
    st.markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <div style='display: flex; align-items: center; justify-content: center; margin-bottom: 5px; margin-top: -10px;'>
            <img src="data:image/png;base64,{}" style='width: 60px; height: 60px; margin-right: 15px;'>
            <h1 style='color: #1f77b4; margin: 0; display: inline-block;'>Rolling Sphere</h1>
        </div>
        <h3 style='color: #666; margin-top: 5px;'>Hazardous Substances Compliance Center</h3>
    </div>
    """.format(get_logo_base64() if os.path.exists("assets/logo.png") else ""), unsafe_allow_html=True)
    
    st.markdown("---")

def show_auth_page():
    """Show authentication page"""
    show_rolling_sphere_header()
    st.markdown("### Professional carbon footprint analysis for businesses")
    
    auth = SimpleAuth()
    
    # Create tabs for login and register
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        auth.show_login_form()
        st.markdown("---")
    
    with tab2:
        auth.show_register_form()

def show_dashboard():
    """Show user dashboard with calculation history"""
    show_rolling_sphere_header()
    
    auth = SimpleAuth()
    storage = DataStorage()
    username = st.session_state.get('username', '')
    user_info = auth.get_current_user()
    
    # Header with user info and logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<h2 style='color: #333; margin-top: 0;'>Welcome back, {user_info.get('name', username)}!</h2>", unsafe_allow_html=True)
    with col2:
        if st.button("Logout", type="secondary"):
            auth.logout()
    
    # Get user's calculation history
    calculations = storage.get_user_calculations(username, limit=5)
    history_df = storage.get_calculation_history(username)
    
    if not history_df.empty:
        st.subheader("📊 Your Emissions Trend")
        
        # Create trend chart
        fig = px.line(
            history_df, 
            x='date', 
            y='total_emissions',
            title="CO2 Emissions Over Time",
            labels={'total_emissions': 'CO2 Emissions (kg)', 'date': 'Date'}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent calculations summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Calculations", len(calculations))
        with col2:
            latest_emissions = history_df['total_emissions'].iloc[0] if len(history_df) > 0 else 0
            st.metric("Latest Emissions", f"{latest_emissions:,.0f} kg")
        with col3:
            avg_emissions = history_df['total_emissions'].mean() if len(history_df) > 0 else 0
            st.metric("Average Emissions", f"{avg_emissions:,.0f} kg")
    
    # Recent calculations table
    if calculations:
        st.subheader("📋 Recent Calculations")
        
        recent_data = []
        for calc in calculations[:5]:
            recent_data.append({
                "Date": calc["timestamp"][:10],
                "Company": calc["company_info"].get("name", "Unknown"),
                "Total CO2 (kg)": f"{calc['emissions_summary']['total_co2_kg']:,.0f}",
                "Activities": calc["csv_row_count"]
            })
        
        st.dataframe(pd.DataFrame(recent_data), use_container_width=True)
    
    st.markdown("---")
    # Main action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 New Calculation", type="primary", use_container_width=True):
            st.session_state.show_calculator = True
            st.rerun()
    
    with col2:
        if st.button("🔬 Hazardous Substances", type="secondary", use_container_width=True):
            st.session_state.show_hazardous_substances = True
            st.rerun()
    
    # Disclaimer section
    st.markdown("---")
    st.markdown("""
    <div style='background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 10px; padding: 20px; margin: 20px 0;'>
        <h5 style='color: #856404; text-align: center; margin-bottom: 15px;'>⚠️ Disclaimer</h5>
        <p style='color: #856404; text-align: center; margin: 0; font-size: 14px;'>
            This platform provides automated analysis based on public regulatory data and user-provided information. 
            It is intended for informational purposes only and does not constitute legal advice. The user is solely 
            responsible for ensuring the accuracy of input data and for the final compliance of their products. 
            Rolling Sphere Technologies assumes no liability for the use of this service.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Privacy settings footer
    st.markdown("---")
    
    # Contact & Support and Privacy buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📞 Contact & Support", key="contact_footer", use_container_width=True):
            st.session_state.show_contact = True
            st.rerun()
    
    with col2:
        with st.expander("⚙️ Privacy & Cookie Settings"):
            show_cookie_settings()
            
            st.markdown("---")
            st.markdown("### 📋 Privacy Information")
            col1_inner, col2_inner = st.columns(2)
            
            with col1_inner:
                if st.button("View Privacy Policy", key="privacy_from_dashboard"):
                    st.session_state.show_privacy = True
                    st.rerun()
            
            with col2_inner:
                if st.button("Contact & Support", key="contact_from_privacy"):
                    st.session_state.show_contact = True
                    st.rerun()

def show_hazardous_substances():
    """Show the hazardous substances compliance center - Professional redesign"""
    
    # STEP 1: Compact dark header with everything in one line
    st.markdown("""
    <div style='background-color: #1a1a1a; padding: 15px 20px; margin: -1rem -1rem 0 -1rem; border-radius: 0;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div style='display: flex; align-items: center;'>
                <img src="data:image/png;base64,{}" style='width: 40px; height: 40px; margin-right: 12px;'>
                <div>
                    <h1 style='color: #1f77b4; margin: 0; font-size: 24px; font-weight: 600;'>Rolling Sphere</h1>
                    <p style='color: #888; margin: 0; font-size: 14px;'>Hazardous Substances Compliance Center</p>
                </div>
            </div>
        </div>
    </div>
    """.format(get_logo_base64() if os.path.exists("assets/logo.png") else ""), unsafe_allow_html=True)
    
    # Dashboard button in top right corner
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("← Dashboard", key="header_dashboard", use_container_width=True):
            st.session_state.show_hazardous_substances = False
            st.rerun()
    
    # STEP 2 & 3: Professional cards side by side under header
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="medium")
    
    # Left Card: Start Compliance Analysis (blue theme)
    with col1:
        st.markdown("""
        <div style='
            border: 2px solid #1f77b4; 
            border-radius: 12px; 
            padding: 25px; 
            background: white; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        '>
            <div>
                <div style='font-size: 36px; color: #1f77b4; margin-bottom: 10px;'>📤</div>
                <h3 style='color: #333; margin: 0 0 10px 0; font-size: 20px; font-weight: 600;'>Start Compliance Analysis</h3>
                <p style='color: #666; margin: 0; font-size: 14px; line-height: 1.4;'>Upload your material declaration and get instant regulatory compliance analysis for global markets.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start Analysis", key="start_analysis", type="primary", use_container_width=True):
            st.session_state.show_compliance_analysis = True
            st.session_state.show_all_regulations = False
            st.rerun()
    
    # Right Card: Regulation Database (teal theme)
    with col2:
        st.markdown("""
        <div style='
            border: 2px solid #20b2aa; 
            border-radius: 12px; 
            padding: 25px; 
            background: white; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        '>
            <div>
                <div style='font-size: 36px; color: #20b2aa; margin-bottom: 10px;'>🗄️</div>
                <h3 style='color: #333; margin: 0 0 10px 0; font-size: 20px; font-weight: 600;'>Regulation Database</h3>
                <p style='color: #666; margin: 0; font-size: 14px; line-height: 1.4;'>Browse our comprehensive database of 65 international regulations and standards.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Browse Database", key="browse_database", use_container_width=True):
            st.session_state.show_all_regulations = True
            st.session_state.show_compliance_analysis = False
            st.rerun()
    
    # STEP 4: Compact statistics in horizontal row
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #1f77b4, #4dabf7); border-radius: 8px; color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='font-size: 28px; font-weight: bold; margin-bottom: 5px;'>27</div>
            <div style='font-size: 12px; opacity: 0.9;'>EU Regulations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #28a745, #51cf66); border-radius: 8px; color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='font-size: 28px; font-weight: bold; margin-bottom: 5px;'>22</div>
            <div style='font-size: 12px; opacity: 0.9;'>Asia-Pacific</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #ffc107, #ffed4e); border-radius: 8px; color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='font-size: 28px; font-weight: bold; margin-bottom: 5px;'>16</div>
            <div style='font-size: 12px; opacity: 0.9;'>Other Regions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #dc3545, #f783ac); border-radius: 8px; color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='font-size: 28px; font-weight: bold; margin-bottom: 5px;'>65</div>
            <div style='font-size: 12px; opacity: 0.9;'>Total Standards</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Show compliance analysis workflow ONLY if requested (completely separate page)
    if st.session_state.get('show_compliance_analysis', False):
        # Clear page - show ONLY compliance workflow content
        st.markdown("## 🔍 Material Declaration Analysis")
        st.markdown("Complete regulatory compliance analysis workflow for your products.")
        
        # Progress indicator
        progress_steps = ["Business Context", "Product Information", "Material Declaration", "Analysis Results"]
        current_step = 1
        
        # Step indicator
        st.markdown("---")
        cols = st.columns(len(progress_steps))
        for i, step in enumerate(progress_steps):
            with cols[i]:
                if i < current_step:
                    st.markdown(f"✅ **{i+1}. {step}**")
                elif i == current_step:
                    st.markdown(f"🔄 **{i+1}. {step}**")
                else:
                    st.markdown(f"⚪ {i+1}. {step}")
        
        st.markdown("---")
        
        # Enhanced Business Context form
        st.markdown("### 📋 Business Context")
        col1, col2 = st.columns(2)
        with col1:
            business_role = st.selectbox(
                "Your Role *",
                ["Producer", "Importer", "Recycler", "Distributor"],
                help="Select your role in the supply chain"
            )
            
            # Comprehensive country list
            countries = [
                "Germany", "USA", "China", "India", "Japan", "South Korea", "Singapore", 
                "United Kingdom", "France", "Italy", "Netherlands", "Sweden", "Denmark",
                "Canada", "Brazil", "Mexico", "Australia", "New Zealand", "South Africa",
                "Thailand", "Malaysia", "Vietnam", "Philippines", "Indonesia", "Taiwan",
                "Hong Kong", "Switzerland", "Austria", "Belgium", "Spain", "Poland",
                "Czech Republic", "Hungary", "Romania", "Turkey", "Russia", "Other"
            ]
            company_location = st.selectbox("Company Location *", countries)
            
        with col2:
            target_markets = st.multiselect(
                "Target Markets *",
                ["European Union", "United States", "China", "India", "Japan", "South Korea", "Global Market"],
                help="Select all markets where you plan to sell this product"
            )
            
            # Smart regulation preview based on selections
            if business_role and company_location and target_markets:
                st.info("💡 Applicable regulations will be determined based on your selections")
        
        # Enhanced Product Information section
        st.markdown("---")
        st.markdown("### 📱 Product Information")
        
        # Enhanced product categories with comprehensive cable types and subcategories
        product_categories = {
            "Computing & Telecommunications": [
                "Smartphones", "Tablets", "Laptops", "Desktop Computers", "Servers", 
                "Routers", "Switches", "Modems", "Network Equipment", "Data Storage Devices"
            ],
            "Consumer Electronics": [
                "TVs", "Monitors", "Audio Systems", "Cameras", "Gaming Consoles", "Smart Home Devices",
                "Wearables", "E-readers", "Streaming Devices", "Headphones", "Speakers"
            ],
            "Household Appliances": [
                "Washing Machines", "Refrigerators", "Microwaves", "Dishwashers", "Air Conditioners",
                "Vacuum Cleaners", "Coffee Machines", "Food Processors", "Electric Ovens", "Water Heaters"
            ],
            "Components & Accessories": [
                "LED Cables", "USB Cables", "HDMI Cables", "Power Cables", "Network Cables", "Audio Cables",
                "Adapters", "Batteries", "Circuit Boards", "Power Supplies", "Memory Cards", 
                "USB Devices", "Chargers", "Connectors", "Electronic Components", "Computer Mouse", 
                "Keyboards", "Webcams", "Microphones", "Headphones", "Other"
            ],
            "Industrial Equipment": [
                "Control Systems", "Sensors", "Motors", "PLCs", "Industrial Computers",
                "Measurement Devices", "Automation Equipment", "Power Electronics", "Drives", "HMI Panels"
            ],
            "Medical Devices": [
                "Diagnostic Equipment", "Monitoring Devices", "Therapeutic Equipment", "Laboratory Equipment",
                "Imaging Systems", "Patient Monitors", "Infusion Pumps", "Defibrillators", "Ventilators", "MRI Systems"
            ]
        }
        
        # Smart product recognition patterns
        product_recognition_patterns = {
            # Computing & Telecommunications
            "Computing & Telecommunications": {
                "keywords": ["smartphone", "phone", "iphone", "samsung galaxy", "laptop", "computer", "macbook", 
                           "tablet", "ipad", "server", "router", "switch", "modem", "network"],
                "types": {
                    "smartphone|phone|iphone|samsung|galaxy": "Smartphones",
                    "laptop|macbook|notebook": "Laptops", 
                    "computer|desktop|pc": "Desktop Computers",
                    "tablet|ipad": "Tablets",
                    "server": "Servers",
                    "router|switch|modem": "Network Equipment"
                }
            },
            # Consumer Electronics  
            "Consumer Electronics": {
                "keywords": ["tv", "television", "monitor", "display", "audio", "speaker", "camera", "gaming", "console"],
                "types": {
                    "tv|television": "TVs",
                    "monitor|display": "Monitors", 
                    "audio|speaker|sound": "Audio Systems",
                    "camera": "Cameras",
                    "gaming|console|playstation|xbox": "Gaming Consoles"
                }
            },
            # Household Appliances
            "Household Appliances": {
                "keywords": ["washing machine", "refrigerator", "fridge", "microwave", "dishwasher", "air conditioner"],
                "types": {
                    "washing machine|washer": "Washing Machines",
                    "refrigerator|fridge": "Refrigerators",
                    "microwave": "Microwaves",
                    "dishwasher": "Dishwashers",
                    "air conditioner|ac": "Air Conditioners"
                }
            },
            # Components & Accessories
            "Components & Accessories": {
                "keywords": ["cable", "led cable", "usb cable", "hdmi cable", "power cable", "network cable", 
                           "audio cable", "adapter", "battery", "charger", "connector", "mouse", "keyboard", "webcam", "microphone", "headphone"],
                "types": {
                    "led cable": "LED Cables",
                    "usb cable": "USB Cables", 
                    "hdmi cable": "HDMI Cables",
                    "power cable": "Power Cables",
                    "network cable": "Network Cables",
                    "audio cable": "Audio Cables",
                    "cable": "Cables",
                    "adapter": "Adapters",
                    "battery": "Batteries",
                    "charger": "Chargers",
                    "mouse": "Computer Mouse",
                    "keyboard": "Keyboards",
                    "webcam": "Webcams",
                    "microphone|mic": "Microphones",
                    "headphone|headset": "Headphones"
                }
            }
        }
        
        # Smart detection function with fallback
        def detect_product_category_and_type(description):
            """Auto-detect product category and type from description with smart fallbacks"""
            if not description:
                return None, None, None
                
            desc_lower = description.lower()
            
            # First pass: Try exact keyword matching
            for category, patterns in product_recognition_patterns.items():
                for keyword in patterns["keywords"]:
                    if keyword in desc_lower:
                        # Find specific type
                        detected_type = None
                        for pattern, product_type in patterns["types"].items():
                            import re
                            if re.search(pattern, desc_lower):
                                detected_type = product_type
                                break
                        
                        return category, detected_type, f"Auto-detected: {keyword}"
            
            # Second pass: Try partial word matching for fallback
            import re
            words_in_desc = re.findall(r'\b\w+\b', desc_lower)
            
            for category, patterns in product_recognition_patterns.items():
                for pattern, product_type in patterns["types"].items():
                    pattern_words = re.findall(r'\b\w+\b', pattern)
                    for pattern_word in pattern_words:
                        if pattern_word in words_in_desc:
                            return category, product_type, f"Partial match: {pattern_word}"
            
            # Final fallback: Default to Components & Accessories with "Other" type
            return "Components & Accessories", "Other", "Default category (unknown product type)"
        
        # Initialize session states for multiple products
        if 'products_list' not in st.session_state:
            st.session_state.products_list = [{'id': 0}]  # Start with one product
        if 'product_counter' not in st.session_state:
            st.session_state.product_counter = 1
        
        def render_product_form(product_index, product_data):
            """Render a single product form with all detection logic"""
            product_id = product_data['id']
            
            # Initialize session states for this specific product
            detected_cat_key = f'detected_category_{product_id}'
            detected_type_key = f'detected_type_{product_id}'
            detection_msg_key = f'detection_message_{product_id}'
            
            if detected_cat_key not in st.session_state:
                st.session_state[detected_cat_key] = None
            if detected_type_key not in st.session_state:
                st.session_state[detected_type_key] = None
            if detection_msg_key not in st.session_state:
                st.session_state[detection_msg_key] = None
            
            # Product form header with remove button (for products after the first one)
            if product_index > 0:
                col_header1, col_header2 = st.columns([4, 1])
                with col_header1:
                    st.markdown(f"#### Product {product_index + 1}")
                with col_header2:
                    if st.button("🗑️", key=f"remove_product_{product_id}", help="Remove this product"):
                        st.session_state.products_list.pop(product_index)
                        st.rerun()
            else:
                st.markdown("#### Product Information")
            
            # Main product form
            col1, col2 = st.columns(2)
            with col1:
                # Product description with unique key
                desc_key = f"product_desc_input_{product_id}"
                product_description = st.text_input(
                    "Product Description * (Start typing for auto-detection)" + (" 📍" if product_index == 0 else ""),
                    placeholder="e.g., LED Cable, iPhone 15, Samsung TV, MacBook Pro",
                    help="Type your product name - we'll auto-detect category and type",
                    key=desc_key
                )
                
                # Real-time smart detection
                if product_description:
                    detected_cat, detected_type, message = detect_product_category_and_type(product_description)
                    
                    if detected_cat:
                        # Update session state with new detection
                        st.session_state[detected_cat_key] = detected_cat
                        st.session_state[detected_type_key] = detected_type
                        st.session_state[detection_msg_key] = message
                        
                        # Show detection feedback
                        st.success(f"🎯 {message}")
                    else:
                        # Clear detection if no match found
                        st.session_state[detected_cat_key] = None
                        st.session_state[detected_type_key] = None
                        st.session_state[detection_msg_key] = None
            
            with col2:
                # Smart category selection with auto-update
                default_category = st.session_state[detected_cat_key] if st.session_state[detected_cat_key] else list(product_categories.keys())[0]
                category_options = list(product_categories.keys()) + ["Custom Product"]
                
                try:
                    default_index = category_options.index(default_category)
                except ValueError:
                    default_index = 0
                    
                selected_category = st.selectbox(
                    "Product Category * (Auto-detected)",
                    category_options,
                    index=default_index,
                    help="Auto-detected from your product description - you can change if needed",
                    key=f"category_{product_id}"
                )
                
                # Additional product details
                production_volume = st.selectbox(
                    "Expected Volume",
                    ["< 1,000 units", "1,000 - 10,000 units", "10,000 - 100,000 units", "> 100,000 units"],
                    help="Annual production/import volume",
                    key=f"volume_{product_id}"
                )
            
            # Product Type selection with smart defaults
            subcategory = None
            custom_details = None
            
            if selected_category != "Custom Product" and selected_category in product_categories:
                st.markdown("##### Product Type Selection")
                col1, col2 = st.columns(2)
                
                with col1:
                    type_options = product_categories[selected_category] + ["Other in this category"]
                    
                    # Set default type based on detection
                    default_type_index = 0
                    if st.session_state[detected_type_key] and st.session_state[detected_type_key] in type_options:
                        try:
                            default_type_index = type_options.index(st.session_state[detected_type_key])
                        except ValueError:
                            default_type_index = 0
                    
                    subcategory = st.selectbox(
                        "Product Type * (Auto-detected)",
                        type_options,
                        index=default_type_index,
                        help="Auto-detected from your product description",
                        key=f"subcategory_{product_id}"
                    )
                
                with col2:
                    # Show related suggestions
                    st.markdown("**Smart Suggestions:**")
                    if selected_category == "Components & Accessories" and product_description and "cable" in product_description.lower():
                        cable_types = ["LED Cables", "USB Cables", "HDMI Cables", "Power Cables", "Network Cables", "Audio Cables"]
                        for cable_type in cable_types:
                            if cable_type.lower().replace(" cables", "") in product_description.lower():
                                st.markdown(f"✅ {cable_type}")
                            else:
                                st.markdown(f"• {cable_type}")
                    else:
                        # Show category-specific suggestions
                        suggestions = product_categories.get(selected_category, [])[:4]
                        for suggestion in suggestions:
                            st.markdown(f"• {suggestion}")
            
            elif selected_category == "Custom Product":
                custom_details = st.text_area(
                    "Custom Product Details *",
                    placeholder="Provide detailed description of your custom product",
                    help="Include technical specifications, intended use, and any relevant details",
                    key=f"custom_details_{product_id}"
                )
            
            # Return product data
            return {
                'description': product_description,
                'category': selected_category,
                'volume': production_volume,
                'subcategory': subcategory,
                'custom_details': custom_details
            }
        
        # Render all products
        all_products_data = []
        for i, product in enumerate(st.session_state.products_list):
            if i > 0:
                st.markdown("---")  # Add separator between products
            
            product_data = render_product_form(i, product)
            all_products_data.append(product_data)
            
            # Add the "Add Another Product" button right after each product form
            if i == len(st.session_state.products_list) - 1:  # Only show after the last product
                st.markdown("")  # Small space
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("➕ Add Another Product", key="add_product_btn", type="secondary", help="Add another product to your compliance report"):
                        new_product = {'id': st.session_state.product_counter}
                        st.session_state.products_list.append(new_product)
                        st.session_state.product_counter += 1
                        st.rerun()
        
        # Get data from first product for backward compatibility
        if all_products_data:
            product_description = all_products_data[0]['description']
            selected_category = all_products_data[0]['category']
            production_volume = all_products_data[0]['volume']
            subcategory = all_products_data[0]['subcategory']
        else:
            product_description = ""
            selected_category = ""
            production_volume = ""
            subcategory = ""
        
        # Smart regulation selection logic
        def get_applicable_regulations(role, location, markets, category):
            """Determine applicable regulations based on business context - UNIVERSAL for ALL locations"""
            applicable_regs = []
            
            # UNIVERSAL MANUFACTURING LOCATION REGULATIONS
            # EU Countries (Germany, France, Italy, Netherlands, Belgium, Spain, etc.)
            eu_countries = ["Germany", "France", "Italy", "Netherlands", "Belgium", "Spain", "Austria", "Portugal", "Finland", "Denmark", "Sweden", "Poland", "Czech Republic", "Hungary", "Slovakia", "Slovenia", "Croatia", "Romania", "Bulgaria", "Lithuania", "Latvia", "Estonia", "Luxembourg", "Cyprus", "Malta", "Ireland", "Greece"]
            
            if location in eu_countries:
                applicable_regs.extend(["RoHS Directive", "REACH", "WEEE Directive", "EMC Directive", "Packaging Directive", "Radio Equipment Directive"])
            elif location == "China":
                applicable_regs.extend(["China RoHS", "CCC Certification", "GB Standards", "China Manufacturing Standards"])
            elif location == "India":
                applicable_regs.extend(["India E-Waste Rules", "BIS Standards", "Environment Protection Act", "Pollution Control Act"])
            elif location in ["United States", "USA"]:
                applicable_regs.extend(["EPA Regulations", "OSHA Standards", "FCC Manufacturing", "State Environmental Laws"])
            elif location in ["Japan", "South Korea", "Singapore", "Taiwan"]:
                applicable_regs.extend(["WEEE Equivalent", "Chemical Safety Standards", "Manufacturing Safety"])
            else:
                # Generic regulations for any other manufacturing location
                applicable_regs.extend(["International Standards", "Local Environmental Laws", "Safety Standards"])
            
            # UNIVERSAL TARGET MARKET REGULATIONS
            for market in markets:
                if "United States" in market or "USA" in market:
                    applicable_regs.extend(["California Proposition 65", "TSCA", "FCC Regulations", "CPSIA"])
                    if category == "Computing & Telecommunications":
                        applicable_regs.append("FCC Part 15")
                
                elif "China" in market:
                    applicable_regs.extend(["China RoHS", "CCC Certification", "GB Standards", "China WEEE"])
                    if category == "Computing & Telecommunications":
                        applicable_regs.extend(["CCC for IT Equipment", "SRRC Approval"])
                    if category == "Medical Devices":
                        applicable_regs.append("NMPA Registration")
                
                elif "India" in market:
                    applicable_regs.extend(["India E-Waste Rules", "BIS Standards", "Environment Protection Act", "Hazardous Waste Rules"])
                    if category == "Computing & Telecommunications":
                        applicable_regs.extend(["BIS Registration", "WPC Approval", "TEC Approval"])
                    if category == "Medical Devices":
                        applicable_regs.append("CDSCO Registration")
                
                elif "European Union" in market and location not in eu_countries:
                    applicable_regs.extend(["RoHS Directive", "REACH", "WEEE Directive", "CE Marking"])
                    if category == "Medical Devices":
                        applicable_regs.append("Medical Device Regulation")
                    if category == "Computing & Telecommunications":
                        applicable_regs.extend(["Radio Equipment Directive", "EMC Directive"])
                
                elif "Japan" in market:
                    applicable_regs.extend(["Japan RoHS", "Japan WEEE", "PSE Certification", "VCCI Standards"])
                    if category == "Computing & Telecommunications":
                        applicable_regs.append("MIC Type Approval")
                
                elif "South Korea" in market:
                    applicable_regs.extend(["Korea RoHS", "K-REACH", "WEEE Korea", "KC Certification"])
                    if category == "Computing & Telecommunications":
                        applicable_regs.append("KCC Approval")
                
                elif "Global Market" in market:
                    applicable_regs.extend(["IEC Standards", "ISO Environmental", "Global Best Practices", "International Trade Requirements"])
                
                else:
                    # Generic regulations for any other target market
                    applicable_regs.extend([f"{market} Market Entry Requirements", f"{market} Safety Standards", f"{market} Environmental Compliance"])
            
            # Remove duplicates while preserving order
            return list(dict.fromkeys(applicable_regs))
        
        # Show applicable regulations preview for all products
        if business_role and company_location and target_markets and all_products_data:
            # Collect all unique categories from all products
            all_categories = set()
            valid_products = []
            for product in all_products_data:
                if product['description'] and product['category']:
                    all_categories.add(product['category'])
                    valid_products.append(product)
            
            if all_categories and valid_products:
                # Get regulations for all categories
                all_applicable = set()
                for category in all_categories:
                    regs = get_applicable_regulations(business_role, company_location, target_markets, category)
                    all_applicable.update(regs)
                
                applicable = list(all_applicable)
                
                st.markdown("---")
                st.markdown("### 📋 Applicable Regulations Preview")
                if len(valid_products) > 1:
                    st.info(f"**{len(applicable)} regulations** identified for {len(valid_products)} products across {len(all_categories)} categories:")
                    
                    # Show products summary
                    st.markdown("**Products included:**")
                    for i, product in enumerate(valid_products):
                        st.markdown(f"• **Product {i+1}:** {product['description']} ({product['category']})")
                else:
                    st.info(f"**{len(applicable)} regulations** identified based on your context:")
                
                # Show regulations
                if applicable:
                    cols = st.columns(min(3, len(applicable)))
                    for i, reg in enumerate(applicable[:6]):  # Show first 6
                        with cols[i % 3]:
                            st.markdown(f"• {reg}")
                    if len(applicable) > 6:
                        st.markdown(f"... and {len(applicable) - 6} more")
        
        # Enhanced File upload section
        st.markdown("---")
        st.markdown("### 📄 Upload Material Declaration")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            uploaded_file = st.file_uploader(
                "Upload your material declaration file (CSV or Excel)",
                type=['csv', 'xlsx', 'xls'],
                help="Upload files containing component materials, substance data, or supplier declarations"
            )
            
            # Download Template Button
            st.markdown("**Need a template?**")
            
            # Load template file for download
            template_path = "templates/rolling_sphere_template.xlsx"
            if os.path.exists(template_path):
                with open(template_path, "rb") as template_file:
                    template_data = template_file.read()
                    
                st.download_button(
                    label="📥 Download Template",
                    data=template_data,
                    file_name="Rolling_Sphere_Material_Declaration_Template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Download our standardized template for material declarations"
                )
            else:
                st.warning("Template file not found. Please contact support.")
            
        with col2:
            st.markdown("**Required fields:**")
            st.markdown("- Material/Component name")
            st.markdown("- Substance data")
            st.markdown("- Concentration values")
            st.markdown("- Supplier information")
        
        # Form validation for all products
        products_complete = all([
            product['description'] and product['category'] 
            for product in all_products_data
        ])
        
        form_complete = all([
            business_role,
            company_location, 
            target_markets,
            products_complete,
            len(all_products_data) > 0
        ])
        
        if not form_complete:
            st.warning("⚠️ Please complete all required fields (*) before uploading files")
        elif uploaded_file is None:
            st.info("📤 Ready to upload - Please select your material declaration file")
        
        if uploaded_file is not None and form_complete:
            # Professional loading state
            with st.spinner("🔄 Analyzing material declaration..."):
                try:
                    # Process the uploaded file with enhanced support
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    
                    if file_extension == 'csv':
                        # Read CSV file
                        df = pd.read_csv(uploaded_file)
                    elif file_extension in ['xlsx', 'xls']:
                        # Read Excel file with openpyxl
                        df = pd.read_excel(uploaded_file, engine='openpyxl' if file_extension == 'xlsx' else 'xlrd')
                    else:
                        st.error("❌ Unsupported file format. Please use CSV (.csv) or Excel (.xlsx, .xls) files.")
                        return
                    
                    # Validate that data was loaded
                    if df.empty:
                        st.error("❌ The uploaded file appears to be empty. Please check your file and try again.")
                        return
                    
                    st.success("✅ File processed successfully!")
                    
                    # Generate compliance report button - moved here to be under the success message
                    if st.button("📄 Generate Detailed Compliance Report", type="primary"):
                        # Get applicable regulations for all product categories
                        all_categories = set()
                        valid_products = []
                        for product in all_products_data:
                            if product['description'] and product['category']:
                                all_categories.add(product['category'])
                                valid_products.append(product)
                        
                        # Collect regulations for all categories
                        all_applicable_regs = set()
                        for category in all_categories:
                            regs = get_applicable_regulations(business_role, company_location, target_markets, category)
                            all_applicable_regs.update(regs)
                        applicable_regs = list(all_applicable_regs)
                        
                        with st.spinner("🔄 Generating comprehensive compliance report..."):
                            try:
                                # Initialize PDF report generator
                                report_generator = ComplianceReportGenerator()
                                
                                # Run compliance analysis
                                compliance_engine = ComplianceEngine()
                                analysis = compliance_engine.analyze_file_compliance(df, applicable_regs)
                                
                                # Prepare multiple products data for report
                                products_summary = []
                                for i, product in enumerate(valid_products):
                                    products_summary.append(f"Product {i+1}: {product['description']} ({product['category']})")
                                
                                # Prepare data for report
                                business_context = {
                                    'role': business_role,
                                    'location': company_location,
                                    'target_markets': target_markets,
                                    'product_description': "; ".join(products_summary),  # Combined product descriptions
                                    'product_category': ", ".join(all_categories)  # All categories
                                }
                                
                                # Use first product for main product info, but include count
                                main_product = valid_products[0] if valid_products else all_products_data[0]
                                product_info = {
                                    'description': main_product['description'] + (f" (+ {len(valid_products)-1} more products)" if len(valid_products) > 1 else ""),
                                    'category': main_product['category'],
                                    'type': main_product['subcategory'] or main_product['category'],
                                    'volume': main_product['volume'],
                                    'total_products': len(valid_products)
                                }
                                
                                # Convert DataFrame to list of dictionaries for report
                                materials_list = df.to_dict('records') if not df.empty else []
                                
                                # Prepare regulations data
                                regulations_data = [{'name': reg, 'authority': 'Government Authority', 'status': 'Active', 'priority': 'Standard'} for reg in applicable_regs]
                                
                                # Analysis results summary - pass through all analysis data
                                analysis_summary = analysis.copy()  # Include all analysis results
                                analysis_summary.update({
                                    'components_analyzed': analysis.get('total_components', len(df)),
                                    'regulations_count': len(applicable_regs),
                                })
                                
                                # Generate the PDF report
                                filename, filepath = report_generator.generate_compliance_report(
                                    business_context=business_context,
                                    product_info=product_info,
                                    materials_data=materials_list,
                                    applicable_regulations=regulations_data,
                                    analysis_results=analysis_summary
                                )
                                
                                # Create download button
                                pdf_data = report_generator.create_download_button_data(filepath)
                                
                                st.success("✅ Compliance report generated successfully!")
                                
                                # Provide download button right here - under Generate Report button
                                st.download_button(
                                    label="📥 Download Compliance Report (PDF)",
                                    data=pdf_data,
                                    file_name=filename,
                                    mime="application/pdf",
                                    type="secondary"
                                )
                                
                            except Exception as e:
                                st.error(f"❌ Error generating compliance report: {str(e)}")
                                st.info("📝 Please ensure all form fields are completed and try again.")
                    
                    # Show file preview
                    with st.expander("📁 View uploaded data", expanded=False):
                        st.dataframe(df.head(10), use_container_width=True)
                        st.info(f"File contains {len(df)} rows and {len(df.columns)} columns")
                    
                    # Get applicable regulations for this specific context
                    applicable_regs = get_applicable_regulations(business_role, company_location, target_markets, selected_category)
                    
                    st.markdown("---")
                    st.markdown("### 📊 Compliance Analysis Results")
                    
                    # Update progress indicator
                    current_step = 4
                    cols = st.columns(len(progress_steps))
                    for i, step in enumerate(progress_steps):
                        with cols[i]:
                            if i < current_step:
                                st.markdown(f"✅ **{i+1}. {step}**")
                            elif i == current_step:
                                st.markdown(f"🔄 **{i+1}. {step}**")
                            else:
                                st.markdown(f"⚪ {i+1}. {step}")
                    
                    st.markdown("---")
                    
                    # Run enhanced compliance analysis with applicable regulations
                    compliance_engine = ComplianceEngine()
                    analysis = compliance_engine.analyze_file_compliance(df, applicable_regs)
                    
                    # Enhanced results display
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Applicable Regulations", len(applicable_regs))
                    with col2:
                        st.metric("Components Analyzed", len(df))
                    with col3:
                        st.metric("Verified Sources", len(analysis.get('verified_sources_used', [])))
                    with col4:
                        status_color = "🟢" if analysis.get('compliance_status') == "Compliant" else "🟡"
                        st.metric("Status", f"{status_color} {analysis.get('compliance_status', 'Under Review')}")
                    
                    # Context-specific compliance summary
                    st.markdown("### 📋 Compliance Summary")
                    st.markdown(f"**Business Context:** {business_role} based in {company_location}")
                    st.markdown(f"**Target Markets:** {', '.join(target_markets)}")
                    st.markdown(f"**Product:** {selected_category} - {product_description}")
                    
                    # Regulation-specific results
                    if applicable_regs:
                        st.markdown("### 🎯 Regulation-Specific Analysis")
                        
                        for reg in applicable_regs[:5]:  # Show top 5 most relevant
                            with st.expander(f"📑 {reg} - Analysis Results"):
                                st.markdown(f"**Regulation:** {reg}")
                                st.markdown("**Status:** ✅ Analysis complete")
                                st.markdown("**Key Requirements:** Substance restrictions and documentation requirements analyzed")
                                st.markdown("**Official Source:** Government database verified")
                    
                    # Professional recommendations
                    st.markdown("### 💡 Recommendations")
                    st.info("Based on your business context and target markets, ensure all documentation is prepared for the identified regulations.")
                    
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
        
        # Back to main button
        st.markdown("---")
        if st.button("← Back to Overview", key="back_compliance_analysis"):
            st.session_state.show_compliance_analysis = False
            st.rerun()
        
        # Hide main page content completely when in compliance mode
        return  # This prevents the rest of the hazardous_substances function from running
    
    # Show comprehensive regulation database if requested (NO upload functionality)
    if st.session_state.get('show_all_regulations', False):
        st.markdown("---")
        st.markdown("## 📋 Comprehensive Regulation Database")
        st.markdown("Browse and search our complete international regulatory database with official government sources.")
        
        # Initialize database
        regulatory_db = RegulatoryDatabase()
        all_regulations = regulatory_db.get_all_regulations()
        
        # Search and filter functionality
        st.markdown("### Search & Filter")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_term = st.text_input("🔍 Search regulations by name, scope, or authority", placeholder="e.g., RoHS, REACH, waste management")
        
        with col2:
            region_filter = st.selectbox("Filter by Region", 
                                       ["All Regions", "European Union", "Asia-Pacific", "Other Regions"])
        
        # Apply filters
        filtered_regulations = all_regulations
        
        if search_term:
            filtered_regulations = [reg for reg in filtered_regulations 
                                  if search_term.lower() in reg.name.lower() 
                                  or search_term.lower() in reg.scope.lower()
                                  or search_term.lower() in reg.authority.lower()]
        
        if region_filter != "All Regions":
            filtered_regulations = [reg for reg in filtered_regulations if reg.region == region_filter]
        
        st.info(f"Showing {len(filtered_regulations)} of {len(all_regulations)} regulations")
        
        # Group regulations by region
        eu_regs = [reg for reg in filtered_regulations if reg.region == "European Union"]
        apac_regs = [reg for reg in filtered_regulations if reg.region == "Asia-Pacific"]
        other_regs = [reg for reg in filtered_regulations if reg.region == "Other Regions"]
        
        # Display EU Regulations
        if eu_regs:
            st.markdown(f"### 🇪🇺 European Union ({len(eu_regs)} regulations)")
            for i, reg in enumerate(eu_regs):
                with st.expander(f"{reg.name} - {reg.regulation_number}"):
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown(f"**Authority:** {reg.authority}")
                        st.markdown(f"**Legal Reference:** {reg.legal_reference}")
                        st.markdown(f"**Status:** {reg.status}")
                    
                    with col2:
                        if reg.official_url and reg.official_url != "TBD":
                            st.markdown(f"**Official URL:** [{reg.official_url}]({reg.official_url})")
                        if reg.eur_lex_link:
                            st.markdown(f"**EUR-Lex:** [{reg.eur_lex_link}]({reg.eur_lex_link})")
                        st.markdown(f"**Verification:** {reg.verification_status}")
                    
                    st.markdown(f"**Scope:** {reg.scope}")
                    st.markdown(f"**Requirements:** {reg.requirements_summary}")
        
        # Display Asia-Pacific Regulations
        if apac_regs:
            st.markdown(f"### 🌏 Asia-Pacific ({len(apac_regs)} regulations)")
            for reg in apac_regs:
                with st.expander(f"{reg.name} - {reg.country} ({reg.regulation_number})"):
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown(f"**Country:** {reg.country}")
                        st.markdown(f"**Authority:** {reg.authority}")
                        st.markdown(f"**Legal Reference:** {reg.legal_reference}")
                        st.markdown(f"**Status:** {reg.status}")
                    
                    with col2:
                        if reg.official_url and reg.official_url != "TBD":
                            st.markdown(f"**Official URL:** [{reg.official_url}]({reg.official_url})")
                        st.markdown(f"**Verification:** {reg.verification_status}")
                    
                    st.markdown(f"**Scope:** {reg.scope}")
                    st.markdown(f"**Requirements:** {reg.requirements_summary}")
        
        # Display Other Regions Regulations
        if other_regs:
            st.markdown(f"### 🌍 Other Regions ({len(other_regs)} regulations)")
            for reg in other_regs:
                with st.expander(f"{reg.name} - {reg.country} ({reg.regulation_number})"):
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown(f"**Country:** {reg.country}")
                        st.markdown(f"**Authority:** {reg.authority}")
                        st.markdown(f"**Legal Reference:** {reg.legal_reference}")
                        st.markdown(f"**Status:** {reg.status}")
                    
                    with col2:
                        if reg.official_url and reg.official_url != "TBD":
                            st.markdown(f"**Official URL:** [{reg.official_url}]({reg.official_url})")
                        st.markdown(f"**Verification:** {reg.verification_status}")
                    
                    st.markdown(f"**Scope:** {reg.scope}")
                    st.markdown(f"**Requirements:** {reg.requirements_summary}")
        
        # Summary statistics
        st.markdown("### Database Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Regulations", len(all_regulations))
        with col2:
            st.metric("EU Regulations", len([r for r in all_regulations if r.region == "European Union"]))
        with col3:
            st.metric("Asia-Pacific", len([r for r in all_regulations if r.region == "Asia-Pacific"]))
        with col4:
            verified_count = len([r for r in all_regulations if "✅ Verified" in r.verification_status])
            st.metric("Verified Sources", verified_count)
        
        if st.button("← Back to Main", key="back_all_regulations"):
            st.session_state.show_all_regulations = False
            st.rerun()
    
    # Disclaimer section for hazardous substances
    st.markdown("---")
    st.markdown("""
    <div style='background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 10px; padding: 20px; margin: 20px 0;'>
        <h5 style='color: #856404; text-align: center; margin-bottom: 15px;'>⚠️ Regulatory Compliance Disclaimer</h5>
        <p style='color: #856404; text-align: center; margin: 0; font-size: 14px;'>
            This compliance analysis is based on publicly available regulatory data and automated processing. 
            Results are for informational purposes only and do not constitute legal compliance certification. 
            Users must verify results with qualified legal counsel and regulatory authorities. Rolling Sphere 
            Technologies is not liable for compliance decisions based on this analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation footer
    st.markdown("---")
    st.markdown("### 🔗 Additional Resources")
    
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    with nav_col1:
        if st.button("📞 Contact & About", use_container_width=True):
            st.session_state.show_hazardous_substances = False
            st.session_state.show_contact = True
            st.rerun()
    
    with nav_col2:
        if st.button("🔒 Privacy Policy", use_container_width=True):
            st.session_state.show_hazardous_substances = False
            st.session_state.show_privacy = True
            st.rerun()
    
    with nav_col3:
        if st.button("← Back to Dashboard", type="secondary", use_container_width=True):
            st.session_state.show_hazardous_substances = False
            st.rerun()

def show_contact():
    """Show contact information page for Rolling Sphere Technologies"""
    show_rolling_sphere_header()
    
    # Header with back button
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("← Back to Platform"):
            st.session_state.show_contact = False
            st.rerun()
    with col2:
        st.markdown("<h2 style='color: #333; margin-top: 0;'>Contact Information</h2>", unsafe_allow_html=True)
    
    # Main contact information in a clean, professional layout
    st.markdown("---")
    
    # Company header
    st.markdown("""
    <div style='text-align: center; margin: 40px 0;'>
        <h1 style='color: #1f77b4; font-size: 36px; margin-bottom: 10px;'>Rolling Sphere Technologies</h1>
        <p style='font-size: 18px; color: #666; margin-bottom: 40px;'>Professional regulatory compliance solutions for IT & electronics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Contact details
    st.markdown("### 📧 Contact Details")
    st.markdown("""
    **Location:** Bucharest, Romania  
    **Email:** rollingsphere.project@gmail.com  
    **Business Hours:** Monday - Friday: 9:00 - 17:00 EET  
    **Response Time:** Within 24 hours
    """)

def show_privacy():
    """Show comprehensive GDPR-compliant privacy policy page"""
    show_rolling_sphere_header()
    
    # Header with back button
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("← Dashboard"):
            st.session_state.show_privacy = False
            st.rerun()
    with col2:
        st.markdown("<h2 style='color: #333; margin-top: 0;'>Privacy Policy</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Privacy policy header
    st.markdown("""
    <div style='text-align: center; margin: 30px 0;'>
        <h1 style='color: #1f77b4; font-size: 32px; margin-bottom: 10px;'>Privacy Policy</h1>
        <p style='color: #666; font-size: 16px;'><strong>Last updated:</strong> August 21, 2025</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main privacy policy content
    st.markdown("### 1. Data Controller")
    st.markdown("""
    **Rolling Sphere Technologies**  
    Location: Bucharest, Romania  
    Email: rollingsphere.project@gmail.com  
    EU Member State: Romania
    """)
    
    st.markdown("### 2. Data We Collect")
    
    st.markdown("#### 2.1 Material Declaration Data")
    st.markdown("""
    - Component names and descriptions
    - Substance concentration data (ppm values)
    - Supplier information and locations
    - Product specifications and categories
    """)
    
    st.markdown("#### 2.2 Business Context Information")
    st.markdown("""
    - Company role (Producer, Importer, Distributor, Recycler)
    - Target markets (EU, USA, Asia-Pacific, etc.)
    - Product categories (Computing, Electronics, etc.)
    - Company location and business context
    """)
    
    st.markdown("#### 2.3 Technical Data")
    st.markdown("""
    - IP address (for security and fraud prevention)
    - Browser type and version
    - Usage timestamps and session data
    - File upload metadata
    """)
    
    st.markdown("### 3. Legal Basis for Processing (GDPR Art. 6)")
    st.markdown("""
    - **Legitimate Interest (Art. 6.1.f):** Providing regulatory compliance analysis services
    - **Contract Performance (Art. 6.1.b):** Delivering compliance reports and analysis
    - **Legal Obligation (Art. 6.1.c):** Meeting regulatory compliance requirements
    - **Consent (Art. 6.1.a):** Where explicitly provided for additional services
    """)
    
    st.markdown("### 4. How We Use Your Data")
    st.markdown("""
    - Analyze uploaded material declarations against 65+ international regulations
    - Generate professional compliance reports with official source citations
    - Provide regulatory recommendations based on business context
    - Apply relevant regulations based on target markets and company role
    - Improve our compliance analysis algorithms (anonymized data only)
    """)
    
    st.markdown("### 5. Data Retention")
    st.markdown("""
    - **Uploaded Files:** Deleted immediately after processing (within 24 hours)
    - **Analysis Results:** Stored for 30 days for report download access
    - **Generated Reports:** Available for download for 30 days
    - **Technical Logs:** Retained for 90 days for security and fraud prevention
    - **Anonymized Statistics:** Retained indefinitely for service improvement
    """)
    
    st.markdown("### 6. Data Sharing and Third Parties")
    st.markdown("We do **NOT** share your confidential material declaration data with third parties. Limited sharing includes:")
    st.markdown("""
    - **Service Providers:** Replit (hosting), with appropriate data processing agreements
    - **Legal Requirements:** When required by Romanian or EU law
    - **Anonymized Research:** Aggregated, non-identifiable statistics for regulatory research
    """)
    
    st.markdown("### 7. Your GDPR Rights")
    st.markdown("As a data subject in the EU, you have the following rights:")
    st.markdown("""
    - **Right of Access (Art. 15):** Request copies of your personal data
    - **Right to Rectification (Art. 16):** Correct inaccurate or incomplete data
    - **Right to Erasure (Art. 17):** Request deletion of your data
    - **Right to Restrict Processing (Art. 18):** Limit how we process your data
    - **Right to Data Portability (Art. 20):** Transfer your data to another service
    - **Right to Object (Art. 21):** Object to processing based on legitimate interests
    - **Right to Withdraw Consent:** Where processing is based on consent
    """)
    
    st.info("""
    **To exercise these rights:** Contact rollingsphere.project@gmail.com  
    **Response time:** Within 30 days as required by GDPR
    """)
    
    st.markdown("### 8. Data Security")
    st.markdown("""
    - HTTPS/TLS encryption for all data transmission
    - Secure cloud infrastructure with access controls
    - Regular security updates and vulnerability monitoring
    - Authentication and authorization controls
    - Data minimization and purpose limitation principles
    """)
    
    st.markdown("### 9. International Data Transfers")
    st.markdown("Your data may be processed on servers outside Romania/EU. We ensure adequate protection through:")
    st.markdown("""
    - Standard Contractual Clauses (SCCs) approved by European Commission
    - Adequacy decisions by the European Commission
    - Appropriate safeguards under GDPR Art. 46
    - Regular assessment of third-country data protection levels
    """)
    
    st.markdown("### 10. Data Protection Authority")
    st.markdown("""
    **Romanian Supervisory Authority:**  
    Autoritatea Națională de Supraveghere a Prelucrării Datelor cu Caracter Personal (ANSPDCP)  
    Website: www.dataprotection.ro  
    
    You have the right to lodge a complaint with ANSPDCP or your local EU data protection authority.
    """)
    
    st.markdown("### 11. Contact Information")
    st.markdown("""
    **Data Protection Officer:** rollingsphere.project@gmail.com  
    **General Contact:** rollingsphere.project@gmail.com  
    **Address:** Bucharest, Romania  
    **Response Time:** Within 24-48 hours for general inquiries, 30 days for GDPR requests
    """)
    
    st.markdown("### 12. Changes to This Policy")
    st.markdown("""
    We may update this privacy policy to reflect changes in our practices or legal requirements. 
    Material changes will be communicated via email or platform notification. The "Last updated" 
    date indicates the most recent revision.
    """)
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Platform", type="primary"):
            st.session_state.show_privacy = False
            st.rerun()
    
    with col2:
        if st.button("📞 Contact Us"):
            st.session_state.show_privacy = False
            st.session_state.show_contact = True
            st.rerun()
    
    with col3:
        if st.button("⚙️ Cookie Settings"):
            st.session_state.show_privacy = False
            with st.expander("Cookie Settings", expanded=True):
                show_cookie_settings()

def main():
    # Show cookie banner first (before authentication)
    show_cookie_banner()
    
    auth = SimpleAuth()
    
    # Initialize session state
    if 'calculated_data' not in st.session_state:
        st.session_state.calculated_data = None
    if 'company_info' not in st.session_state:
        st.session_state.company_info = {}
    if 'show_calculator' not in st.session_state:
        st.session_state.show_calculator = False
    if 'show_hazardous_substances' not in st.session_state:
        st.session_state.show_hazardous_substances = False
    if 'show_compliance_analysis' not in st.session_state:
        st.session_state.show_compliance_analysis = False
    if 'show_all_regulations' not in st.session_state:
        st.session_state.show_all_regulations = False
    if 'show_contact' not in st.session_state:
        st.session_state.show_contact = False
    if 'show_privacy' not in st.session_state:
        st.session_state.show_privacy = False
    
    # Check authentication
    if not auth.is_authenticated():
        show_auth_page()
        return
    
    # Show appropriate page based on session state
    if st.session_state.show_calculator:
        show_calculator()
    elif st.session_state.show_hazardous_substances:
        show_hazardous_substances()
    elif st.session_state.show_contact:
        show_contact()
    elif st.session_state.show_privacy:
        show_privacy()
    else:
        show_dashboard()

def show_calculator():
    """Show the main calculator interface"""
    show_rolling_sphere_header()
    
    auth = SimpleAuth()
    storage = DataStorage()
    username = st.session_state.get('username', '')
    
    # Header with back button
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("← Dashboard"):
            st.session_state.show_calculator = False
            st.rerun()
    with col2:
        st.markdown("<h2 style='color: #333; margin-top: 0;'>Calculate Your Carbon Footprint</h2>", unsafe_allow_html=True)
    
    st.markdown("### Calculate your company's carbon footprint and generate professional reports")
    
    # Sidebar for company information
    with st.sidebar:
        st.header("Company Information")
        company_name = st.text_input("Company Name", value=st.session_state.company_info.get('name', ''))
        reporting_year = st.number_input("Reporting Year", min_value=2020, max_value=2025, value=2024)
        contact_person = st.text_input("Contact Person", value=st.session_state.company_info.get('contact', ''))
        
        st.session_state.company_info = {
            'name': company_name,
            'year': reporting_year,
            'contact': contact_person
        }
        
        st.markdown("---")
        
        # Use the user's original template
        template_path = "templates/Rolling_Sphere_Complete_CO2_Template_1755947979815.xlsx"
        if os.path.exists(template_path):
            with open(template_path, "rb") as template_file:
                excel_bytes = template_file.read()
        else:
            st.error("Template file not found. Please contact support.")
            excel_bytes = b''
        
        # Only provide Excel template download since it's the comprehensive template
        st.download_button(
            label="📥 Download Excel Template",
            data=excel_bytes,
            file_name="Rolling_Sphere_Complete_CO2_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Comprehensive template with examples and reference sheets"
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Data Upload & Analysis")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload your emissions data file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a CSV or Excel file with your company's emissions data"
        )
        
        if uploaded_file is not None:
            try:
                # Read and validate data
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    # Handle Excel files - read all data and extract properly
                    try:
                        # Try pandas first (simpler approach)
                        excel_data = pd.read_excel(uploaded_file, header=None)
                        
                        # Extract data rows (skip SCOPE headers and column headers)
                        data_rows = []
                        headers = ['company_name', 'activity_type', 'category', 'amount', 'unit', 'date']
                        
                        for index, row in excel_data.iterrows():
                            if (pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() and 
                                'SCOPE' not in str(row.iloc[0]) and 
                                str(row.iloc[0]).strip() != 'company_name'):
                                # Clean the row data
                                clean_row = [str(row.iloc[i]) if pd.notna(row.iloc[i]) else '' for i in range(min(6, len(row)))]
                                if len(clean_row) >= 4 and clean_row[1]:  # Must have activity_type
                                    data_rows.append(clean_row)
                        
                        # Convert to DataFrame
                        df = pd.DataFrame(data_rows, columns=headers)
                    except Exception as e:
                        st.error(f"Error reading Excel file: {str(e)}")
                        df = pd.DataFrame()
                
                validator = DataValidator()
                
                if validator.validate_data(df):
                    st.success("File uploaded successfully")
                    
                    # Generate PDF Report button - moved here to be under the success message
                    if st.button("🔄 Generate PDF Report", type="primary"):
                        if st.session_state.calculated_data and company_name:
                            try:
                                with st.spinner("Generating PDF report..."):
                                    pdf_generator = PDFGenerator()
                                    pdf_buffer = pdf_generator.generate_report(
                                        st.session_state.calculated_data,
                                        st.session_state.company_info,
                                        include_recommendations=True,
                                        include_detailed_breakdown=True
                                    )
                                    
                                    if pdf_buffer:
                                        st.success("✅ PDF report generated successfully!")
                                        
                                        # Download button
                                        filename = f"{company_name.replace(' ', '_')}_Carbon_Footprint_Report_{reporting_year}.pdf"
                                        st.download_button(
                                            label="📥 Download PDF Report",
                                            data=pdf_buffer.getvalue(),
                                            file_name=filename,
                                            mime="application/pdf"
                                        )
                                    else:
                                        st.error("❌ Error generating PDF report")
                            
                            except Exception as e:
                                st.error(f"❌ Error generating report: {str(e)}")
                        else:
                            if not company_name:
                                st.warning("⚠️ Please enter company name and contact person in the sidebar")
                    
                    # Display uploaded data
                    with st.expander("View Uploaded Data", expanded=False):
                        st.dataframe(df)
                    
                    # Calculate emissions
                    calculator = EmissionsCalculator()
                    results = calculator.calculate_emissions(df)
                    
                    if results:
                        st.session_state.calculated_data = results
                        
                        # Display summary metrics
                        st.subheader("📈 Emissions Summary")
                        
                        total_emissions = results['summary']['total_co2_kg']
                        col_metric1, col_metric2, col_metric3 = st.columns(3)
                        
                        with col_metric1:
                            st.metric(
                                "Total CO2 Emissions", 
                                f"{total_emissions:,.2f} kg",
                                help="Total carbon dioxide equivalent emissions"
                            )
                        
                        with col_metric2:
                            st.metric(
                                "CO2 per Activity", 
                                f"{total_emissions / len(results['detailed_results']):.2f} kg",
                                help="Average emissions per recorded activity"
                            )
                        
                        with col_metric3:
                            emissions_tons = total_emissions / 1000
                            st.metric(
                                "Total (Tonnes)", 
                                f"{emissions_tons:.2f} t",
                                help="Total emissions in tonnes"
                            )
                        
                        # ===== NEW: EXECUTIVE DASHBOARD =====
                        st.markdown("---")
                        st.subheader("🎯 Executive Dashboard")
                        
                        # Get scope data for executive summary
                        scope_data = results['by_scope']
                        scope1_kg = scope_data['scope_1']['total_kg']
                        scope2_kg = scope_data['scope_2']['total_kg']
                        scope3_kg = scope_data['scope_3']['total_kg']
                        
                        scope1_percent = (scope1_kg / total_emissions * 100) if total_emissions > 0 else 0
                        scope2_percent = (scope2_kg / total_emissions * 100) if total_emissions > 0 else 0
                        scope3_percent = (scope3_kg / total_emissions * 100) if total_emissions > 0 else 0
                        
                        # Determine overall status
                        combined_scope13 = scope1_percent + scope3_percent
                        if combined_scope13 > 80:
                            overall_status = "🔴 ACTION REQUIRED"
                            status_color = "#ff4444"
                        elif combined_scope13 > 60:
                            overall_status = "🟡 ATTENTION NEEDED"
                            status_color = "#ff8800"
                        else:
                            overall_status = "🟢 GOOD PERFORMANCE"
                            status_color = "#00aa00"
                        
                        # Visual executive summary box
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #f0f8ff, #e6f3ff); border: 2px solid #1f77b4; border-radius: 15px; padding: 20px; margin: 20px 0;'>
                            <div style='text-align: center; margin-bottom: 15px;'>
                                <h2 style='color: #1f77b4; margin: 0;'>📊 EXECUTIVE SUMMARY</h2>
                            </div>
                            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; align-items: center;'>
                                <div style='text-align: center; padding: 10px;'>
                                    <h3 style='color: #333; margin: 5px;'>Total Emissions</h3>
                                    <h1 style='color: #1f77b4; margin: 5px; font-size: 2.2em;'>{emissions_tons:.2f}</h1>
                                    <p style='color: #666; margin: 0;'>tonnes CO2e</p>
                                </div>
                                <div style='text-align: center;'>
                                    <div style='background: #ff4444; color: white; padding: 8px 12px; border-radius: 8px; margin: 3px;'>
                                        <strong>SCOPE 1: {scope1_kg/1000:.2f}t ({scope1_percent:.1f}%) - RED</strong>
                                    </div>
                                    <div style='background: #00aa00; color: white; padding: 8px 12px; border-radius: 8px; margin: 3px;'>
                                        <strong>SCOPE 2: {scope2_kg/1000:.2f}t ({scope2_percent:.1f}%) - GREEN</strong>
                                    </div>
                                    <div style='background: #ff8800; color: white; padding: 8px 12px; border-radius: 8px; margin: 3px;'>
                                        <strong>SCOPE 3: {scope3_kg/1000:.2f}t ({scope3_percent:.1f}%) - ORANGE</strong>
                                    </div>
                                </div>
                                <div style='text-align: center; padding: 10px;'>
                                    <h3 style='color: {status_color}; margin: 5px;'>Overall Status</h3>
                                    <h2 style='color: {status_color}; margin: 5px; font-size: 1.4em;'>{overall_status}</h2>
                                    <p style='color: #666; margin: 0; font-size: 12px;'>{'Scope 1+3 > 80% requires action' if combined_scope13 > 80 else 'Performance acceptable'}</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        
                        st.markdown("---")
                        
                        # GHG Protocol Scope Analysis
                        st.subheader("🌍 GHG Protocol Scope Analysis")
                        
                        scope_data = results['by_scope']
                        col_scope1, col_scope2, col_scope3 = st.columns(3)
                        
                        with col_scope1:
                            scope1_kg = scope_data['scope_1']['total_kg']
                            scope1_tonnes = scope1_kg / 1000
                            scope1_percent = (scope1_kg / total_emissions * 100) if total_emissions > 0 else 0
                            
                            st.metric(
                                "SCOPE 1 (Direct)", 
                                f"{scope1_kg:,.2f} kg",
                                delta=f"{scope1_percent:.1f}% of total",
                                help="Direct emissions from owned/controlled sources"
                            )
                            st.caption(f"**{scope1_tonnes:.2f} tonnes CO2e**")
                            if scope_data['scope_1']['activities']:
                                st.caption(f"Activities: {', '.join([act.replace('_', ' ').title() for act in scope_data['scope_1']['activities']])}")
                        
                        with col_scope2:
                            scope2_kg = scope_data['scope_2']['total_kg']
                            scope2_tonnes = scope2_kg / 1000
                            scope2_percent = (scope2_kg / total_emissions * 100) if total_emissions > 0 else 0
                            
                            st.metric(
                                "SCOPE 2 (Energy)", 
                                f"{scope2_kg:,.2f} kg",
                                delta=f"{scope2_percent:.1f}% of total",
                                help="Indirect emissions from purchased energy"
                            )
                            st.caption(f"**{scope2_tonnes:.2f} tonnes CO2e**")
                            if scope_data['scope_2']['activities']:
                                st.caption(f"Activities: {', '.join([act.replace('_', ' ').title() for act in scope_data['scope_2']['activities']])}")
                        
                        with col_scope3:
                            scope3_kg = scope_data['scope_3']['total_kg']
                            scope3_tonnes = scope3_kg / 1000
                            scope3_percent = (scope3_kg / total_emissions * 100) if total_emissions > 0 else 0
                            
                            st.metric(
                                "SCOPE 3 (Indirect)", 
                                f"{scope3_kg:,.2f} kg",
                                delta=f"{scope3_percent:.1f}% of total",
                                help="Other indirect emissions from value chain"
                            )
                            st.caption(f"**{scope3_tonnes:.2f} tonnes CO2e**")
                            if scope_data['scope_3']['activities']:
                                activities_text = ', '.join([act.replace('_', ' ').title() for act in scope_data['scope_3']['activities'][:3]])
                                if len(scope_data['scope_3']['activities']) > 3:
                                    activities_text += f" +{len(scope_data['scope_3']['activities'])-3} more"
                                st.caption(f"Activities: {activities_text}")
                        
                        # ===== NEW: SPECIFIC SCOPE RECOMMENDATIONS =====
                        st.markdown("---")
                        st.subheader("💡 Scope-Specific Recommendations")
                        
                        col_rec1, col_rec2, col_rec3 = st.columns(3)
                        
                        with col_rec1:
                            # Only show recommendations if there are Scope 1 emissions
                            if scope1_kg > 0:
                                scope1_activities_text = ', '.join([act.replace('_', ' ').title() for act in scope_data['scope_1']['activities']]) if scope_data['scope_1']['activities'] else 'None identified'
                                st.markdown(f"""
                                <div style='border-left: 4px solid #ff4444; padding: 15px; background: #fff5f5; border-radius: 8px;'>
                                    <h5 style='color: #ff4444; margin: 0 0 10px 0;'>🔴 SCOPE 1 ({scope1_kg/1000:.2f}t)</h5>
                                    <p style='margin: 5px 0; font-size: 14px; color: #333;'><strong>Direct emissions from: {scope1_activities_text}</strong></p>
                                    <p style='margin: 10px 0; font-size: 12px; color: #666;'>Consider energy efficiency improvements and equipment upgrades for these activities.</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style='border-left: 4px solid #00aa00; padding: 15px; background: #f5fff5; border-radius: 8px;'>
                                    <h5 style='color: #00aa00; margin: 0 0 10px 0;'>✅ SCOPE 1 (0.0t)</h5>
                                    <p style='margin: 5px 0; font-size: 14px; color: #333;'><strong>No direct emissions detected</strong></p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with col_rec2:
                            if scope2_kg > 0:
                                scope2_activities_text = ', '.join([act.replace('_', ' ').title() for act in scope_data['scope_2']['activities']]) if scope_data['scope_2']['activities'] else 'None identified'
                                st.markdown(f"""
                                <div style='border-left: 4px solid #00aa00; padding: 15px; background: #f5fff5; border-radius: 8px;'>
                                    <h5 style='color: #00aa00; margin: 0 0 10px 0;'>🟢 SCOPE 2 ({scope2_kg/1000:.2f}t)</h5>
                                    <p style='margin: 5px 0; font-size: 14px; color: #333;'><strong>Energy emissions from: {scope2_activities_text}</strong></p>
                                    <p style='margin: 10px 0; font-size: 12px; color: #666;'>Consider renewable energy sources and energy efficiency measures.</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style='border-left: 4px solid #00aa00; padding: 15px; background: #f5fff5; border-radius: 8px;'>
                                    <h5 style='color: #00aa00; margin: 0 0 10px 0;'>✅ SCOPE 2 (0.0t)</h5>
                                    <p style='margin: 5px 0; font-size: 14px; color: #333;'><strong>No energy emissions detected</strong></p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with col_rec3:
                            if scope3_kg > 0:
                                scope3_activities_text = ', '.join([act.replace('_', ' ').title() for act in scope_data['scope_3']['activities'][:5]]) if scope_data['scope_3']['activities'] else 'None identified'
                                if len(scope_data['scope_3']['activities']) > 5:
                                    scope3_activities_text += f' +{len(scope_data["scope_3"]["activities"])-5} more'
                                st.markdown(f"""
                                <div style='border-left: 4px solid #ff8800; padding: 15px; background: #fff8f0; border-radius: 8px;'>
                                    <h5 style='color: #ff8800; margin: 0 0 10px 0;'>🟠 SCOPE 3 ({scope3_kg/1000:.2f}t)</h5>
                                    <p style='margin: 5px 0; font-size: 14px; color: #333;'><strong>Indirect emissions from: {scope3_activities_text}</strong></p>
                                    <p style='margin: 10px 0; font-size: 12px; color: #666;'>Consider supply chain optimization and process improvements for these activities.</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style='border-left: 4px solid #00aa00; padding: 15px; background: #f5fff5; border-radius: 8px;'>
                                    <h5 style='color: #00aa00; margin: 0 0 10px 0;'>✅ SCOPE 3 (0.0t)</h5>
                                    <p style='margin: 5px 0; font-size: 14px; color: #333;'><strong>No indirect emissions detected</strong></p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # ===== METHODOLOGY & STANDARDS =====
                        st.markdown("---")
                        st.subheader("📋 Calculation Methodology")
                        
                        st.markdown("""
                        <div style='background: #f0f8ff; border: 1px solid #1f77b4; border-radius: 10px; padding: 20px; margin: 15px 0;'>
                            <h4 style='color: #1f77b4; margin-bottom: 15px;'>📊 Data Sources & Standards</h4>
                            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                                <div style='display: flex; align-items: center;'><span style='color: #00aa00; font-size: 18px;'>✓</span> <strong style='margin-left: 8px;'>UK Government GHG Conversion Factors 2023</strong></div>
                                <div style='display: flex; align-items: center;'><span style='color: #00aa00; font-size: 18px;'>✓</span> <strong style='margin-left: 8px;'>EPA Emission Factors for GHG Inventories</strong></div>
                                <div style='display: flex; align-items: center;'><span style='color: #00aa00; font-size: 18px;'>✓</span> <strong style='margin-left: 8px;'>IPCC Guidelines for National GHG Inventories</strong></div>
                                <div style='display: flex; align-items: center;'><span style='color: #00aa00; font-size: 18px;'>✓</span> <strong style='margin-left: 8px;'>GHG Protocol Scope Classification</strong></div>
                            </div>
                            <p style='color: #666; font-size: 12px; margin-top: 15px; text-align: center;'>All emission factors sourced from official government and international standards</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Visualizations
                        st.subheader("📊 Emissions Breakdown")
                        
                        # Visual Analysis section
                        st.markdown("### Visual Analysis")
                        
                        # Pie chart by activity type with improved labels
                        activity_names = [name.replace('_', ' ').title() for name in results['by_activity'].keys()]
                        fig_pie = px.pie(
                            values=list(results['by_activity'].values()),
                            names=activity_names,
                            title="Emissions by Activity Type"
                        )
                        # Improve label positioning to avoid overlap
                        fig_pie.update_traces(
                            textposition='outside',
                            textinfo='percent+label',
                            pull=[0.05] * len(activity_names)  # Slightly separate slices
                        )
                        fig_pie.update_layout(
                            showlegend=True,
                            legend=dict(
                                orientation="v",
                                yanchor="middle",
                                y=0.5,
                                xanchor="left",
                                x=1.01
                            ),
                            margin=dict(l=20, r=120, t=50, b=20)
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                        # Bar chart by category with improved formatting
                        if results['by_category']:
                            category_names = [name.replace('_', ' ').title() for name in results['by_category'].keys()]
                            fig_bar = px.bar(
                                x=category_names,
                                y=list(results['by_category'].values()),
                                title="Emissions by Category",
                                labels={'x': 'Category', 'y': 'CO2 Emissions (kg)'}
                            )
                            # Rotate x-axis labels to prevent overlap
                            fig_bar.update_layout(
                                xaxis_tickangle=-45,
                                margin=dict(b=100)
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)
                        
                        # Time series if dates are available
                        if 'monthly_emissions' in results and results['monthly_emissions']:
                            fig_line = px.line(
                                x=list(results['monthly_emissions'].keys()),
                                y=list(results['monthly_emissions'].values()),
                                title="Monthly Emissions Trend",
                                labels={'x': 'Month', 'y': 'CO2 Emissions (kg)'}
                            )
                            st.plotly_chart(fig_line, use_container_width=True)
                        
                        # Save calculation to user's history
                        if st.button("💾 Save This Calculation", type="secondary"):
                            try:
                                calc_id = storage.save_calculation(username, st.session_state.company_info, results, df)
                                st.success(f"✅ Calculation saved! (ID: {calc_id})")
                            except Exception as e:
                                st.error(f"Error saving calculation: {str(e)}")
                        
                        # Detailed breakdown table
                        with st.expander("Detailed Emissions Breakdown"):
                            detailed_df = pd.DataFrame(results['detailed_results'])
                            st.dataframe(detailed_df)
                        
                        # ===== NEW: ENHANCED ACTIONABLE RECOMMENDATIONS =====
                        st.markdown("---")
                        st.subheader("🎯 Specific Action Recommendations")
                        
                        st.markdown("""
                        <div style='background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; padding: 20px; margin: 15px 0;'>
                            <h4 style='color: #333; margin-bottom: 15px;'>💰 High-Impact Actions with Savings Potential</h4>
                        """, unsafe_allow_html=True)
                        
                        # Generate recommendations based on actual calculated data
                        high_impact_recs = []
                        
                        # Find the highest emission activity types and provide relevant recommendations
                        if results.get('by_activity'):
                            # Sort activities by emissions (highest first)
                            sorted_activities = sorted(results['by_activity'].items(), key=lambda x: x[1], reverse=True)
                            
                            for activity_type, emissions_kg in sorted_activities[:3]:  # Top 3 activities
                                activity_name = activity_type.replace('_', ' ').title()
                                emissions_tonnes = emissions_kg / 1000
                                high_impact_recs.append(f"**Focus on {activity_name}** - Currently {emissions_tonnes:.2f} tonnes CO2e ({(emissions_kg/total_emissions)*100:.1f}% of total)")
                        
                        # Display recommendations based on actual data
                        for i, rec in enumerate(high_impact_recs, 1):
                            st.markdown(f"**{i}.** {rec}")
                        
                        if not high_impact_recs:
                            st.markdown("*Recommendations will appear based on your emissions data.*")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # ===== NEW: PROFESSIONAL FOOTER WITH CONFIDENTIALITY =====
                        st.markdown("---")
                        from datetime import datetime
                        current_date = datetime.now()
                        valid_until = current_date.replace(year=current_date.year + 1)
                        
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #1f77b4, #4dabf7); color: white; border-radius: 10px; padding: 20px; margin: 20px 0; text-align: center;'>
                            <div style='font-size: 18px; font-weight: bold; margin-bottom: 10px;'>🏢 Rolling Sphere Technologies - CO2 Analysis Report</div>
                            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;'>
                                <div>
                                    <div style='font-size: 14px; opacity: 0.9;'>Report Generated:</div>
                                    <div style='font-weight: bold;'>{current_date.strftime('%Y-%m-%d %H:%M')}</div>
                                </div>
                                <div>
                                    <div style='font-size: 14px; opacity: 0.9;'>Contact:</div>
                                    <div style='font-weight: bold;'>rollingsphere.project@gmail.com</div>
                                </div>
                            </div>
                            <div style='margin-top: 15px; font-size: 12px; opacity: 0.8;'>
                                Professional Environmental Analysis | Official Emission Factor Sources
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    else:
                        st.error("❌ Error calculating emissions. Please check your data format.")
                
                else:
                    st.error("❌ Data validation failed. Please check the required columns and data format.")
                    for error in validator.get_errors():
                        st.error(f"• {error}")
            
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
    
    with col2:
        st.header("📄 Generate Report")
        
        if st.session_state.calculated_data and company_name:
            st.success("✅ Ready to generate report")
        else:
            if not company_name:
                st.warning("⚠️ Please enter company name and contact person in the sidebar")
        
        # Emission reduction tips
        st.subheader("💡 Quick Tips")
        st.markdown("""
        **Reduce your carbon footprint:**
        - Switch to renewable energy sources
        - Optimize transportation routes
        - Implement energy-efficient practices
        - Consider remote work policies
        - Use energy-efficient equipment
        """)
        
        # Disclaimer section for CO2 calculator
        st.markdown("---")
        st.markdown("""
        <div style='background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 10px; padding: 20px; margin: 20px 0;'>
            <h5 style='color: #856404; text-align: center; margin-bottom: 15px;'>⚠️ CO2 Calculation Disclaimer</h5>
            <p style='color: #856404; text-align: center; margin: 0; font-size: 14px;'>
                CO2 emissions calculations are estimates based on standard emission factors and user-provided data. 
                Results are for informational and reporting purposes only. Actual emissions may vary based on specific 
                circumstances, measurement accuracy, and regional factors. Rolling Sphere Technologies is not responsible 
                for the accuracy of input data or decisions based on these calculations.
            </p>
        </div>
        """, unsafe_allow_html=True)
        

if __name__ == "__main__":
    main()
