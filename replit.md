# CO2 Emissions Calculator

## Overview

This is a comprehensive Streamlit-based web application that helps companies calculate their carbon footprint and generate professional CO2 emissions reports. The application features user authentication, data persistence, improved chart visualizations, and processes CSV data containing various business activities (electricity consumption, fuel usage, transportation, etc.). Users can create accounts, save calculation history, upload activity data, visualize emissions through interactive charts with better label positioning, and generate comprehensive PDF reports for sustainability reporting and compliance purposes.

## Recent Changes (August 2025)

✓ **User Authentication System**: Added login/registration with secure password hashing
✓ **Data Persistence**: PostgreSQL database integration with SQLite fallback for reliability
✓ **Enhanced Template**: Business-specific fields (company_name, electricity_kwh, natural_gas_m3, fuel_liters, business_travel_km, purchased_goods_eur, waste_tons, water_m3)
✓ **Improved Chart Labels**: Fixed pie chart overlap issues with better positioning and legend placement
✓ **User Dashboard**: Personal calculation history with trend analysis and metrics
✓ **Save Functionality**: Users can save calculations to personal history
✓ **Rolling Sphere Branding**: Integrated company logo and branding throughout application and PDF reports
✓ **Hazardous Substances Module**: Added new navigation and basic page structure for regulatory compliance (August 19, 2025)
✓ **Regulatory Database Framework**: Implemented comprehensive international regulatory database structure for 65+ regulations (August 19, 2025)
✓ **Compliance Engine**: Connected database to file analysis system with official source verification (August 19, 2025)
✓ **Chapter 2A Implementation**: Added all 27 EU regulations with official EUR-Lex URLs and verification (August 19, 2025)
✓ **Chapter 2B Implementation**: Updated all 22 Asia-Pacific regulations with corrected official URLs and proper legal references per user requirements (August 19, 2025)
✓ **Chapter 2C Implementation**: Added all 16 Other Regions regulations covering USA, Canada, Latin America, Africa, and Middle East with official government URLs (August 19, 2025)
✓ **Complete Database Achievement**: Reached 65 total international regulations (27 EU + 22 Asia-Pacific + 16 Other Regions) with verified official sources (August 19, 2025)
✓ **Button Functionality Fix**: Separated "Start Compliance Analysis" and "View Detailed Regulation Database" into completely different actions with distinct content (August 19, 2025)
✓ **GDPR Cookie Banner**: Implemented bulletproof cookie consent system with both fixed HTML banner and Streamlit fallback buttons for GDPR compliance (August 21, 2025)
✓ **Contact & Privacy Implementation**: Added comprehensive contact page with Rolling Sphere company information, contact details, services overview, and GDPR compliance information in Streamlit format (August 21, 2025)
✓ **GDPR Privacy Policy**: Implemented complete GDPR-compliant privacy policy page with all required sections: data controller information, legal basis for processing, data retention policies, user rights, and Romanian ANSPDCP contact information (August 21, 2025)
✓ **Navigation & Disclaimers**: Added comprehensive navigation links between all pages (Contact, Privacy, Dashboard) and implemented page-specific disclaimers for CO2 calculations and regulatory compliance analysis with professional legal warnings (August 21, 2025)

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Framework**: Single-page web application with sidebar navigation for company information input and main content area for data upload, visualization, and report generation
- **Interactive Visualizations**: Uses Plotly Express and Plotly Graph Objects for dynamic charts including pie charts for emissions breakdown by activity type and time-series visualizations for monthly trends
- **Session State Management**: Maintains user data (company information and calculated emissions) across page interactions to preserve workflow state

### Backend Architecture
- **Modular Design**: Core functionality separated into utility modules:
  - `EmissionsCalculator`: Handles all emission calculations using predefined emission factors
  - `DataValidator`: Validates CSV input data structure, data types, and value ranges
  - `PDFGenerator`: Creates professional PDF reports using ReportLab library
- **Data Processing Pipeline**: CSV upload → validation → emission calculations → visualization → PDF generation
- **Emission Factors Database**: Centralized repository of CO2 emission factors for various activities (electricity, fuels, transportation) sourced from UK Government GHG Conversion Factors 2023, EPA guidelines, and IPCC standards

### Data Architecture
- **CSV Input Format**: Expects structured data with columns for activity_type, category, amount, unit, and optional date
- **In-Memory Processing**: All data processing occurs in memory using Pandas DataFrames with no persistent storage
- **Flexible Unit Handling**: Supports multiple unit types (kWh, MWh, liters, gallons, kg, tonnes, km, miles) with automatic conversion to appropriate emission factors

### Report Generation
- **PDF Creation**: Uses ReportLab library to generate professional reports with custom styling, charts, and detailed breakdowns
- **Multi-Section Reports**: Includes executive summary, detailed emissions breakdown, visualizations, and optional recommendations section
- **Download Functionality**: Provides direct PDF download through Streamlit's download button with base64 encoding

## External Dependencies

### Python Libraries
- **Streamlit**: Web application framework for the user interface
- **Pandas**: Data manipulation and analysis for CSV processing
- **Plotly**: Interactive visualization library for charts and graphs
- **ReportLab**: PDF generation library for creating professional reports
- **NumPy**: Numerical computing support for calculations

### Data Sources
- **UK Government GHG Conversion Factors 2023**: Primary source for emission factors
- **EPA Emission Factors**: US Environmental Protection Agency guidelines
- **IPCC Guidelines**: International Panel on Climate Change standards for greenhouse gas inventories

### File Dependencies
- **CSV Data Input**: User-provided activity data in comma-separated values format
- **Template Generation**: Application provides downloadable CSV template for proper data formatting
- **PDF Output**: Generated reports as downloadable PDF files

## Module Architecture

### Hazardous Substances Compliance Module (New - August 19, 2025)

**Purpose**: Provides regulatory compliance tools for IT/Electronics companies managing hazardous substance regulations (RoHS, REACH, etc.)

**Navigation Integration**: 
- Added "🔬 Hazardous Substances" button to main dashboard alongside existing "📊 New Calculation" button
- Uses Streamlit session state (`show_hazardous_substances`) for navigation
- Maintains consistent Rolling Sphere branding and header structure

**File Structure**:
- `src/routes/hazardous_substances.py`: Route handler and configuration (placeholder for future modular restructuring)
- Main implementation currently in `app.py` as `show_hazardous_substances()` function

**Features Implemented**:
- Basic page structure with professional styling
- Navigation from dashboard and back
- Consistent branding with CO2 Calculator
- Placeholder content for future compliance features

**Planned Features**:
- Material Declaration Management
- Supplier Compliance Tracking  
- Regulatory Updates & Notifications
- Compliance Report Generation
- Risk Assessment Tools

### Chapter 2: International Regulatory Database Framework (August 19, 2025)

**Database Architecture**:
- Comprehensive structure for 65+ international regulations
- Regional organization: EU (27), Asia-Pacific (22), Other Regions (16) 
- Official source verification system with government URL tracking
- Regulation data model with required fields: name, number, scope, requirements, authority, official URL, legal reference, verification status

**Compliance Engine Integration**:
- `utils/compliance_engine.py`: Connects file uploads to verified regulatory database
- Only uses regulations with verified official sources for compliance checking
- Regional analysis and product category filtering capabilities
- Compliance report generation with official source citations

**Implementation Status**:
- ✅ Database framework structure completed
- ✅ Compliance engine connected and functional
- ✅ Display framework with required fields established
- ✅ Chapter 2A: Complete EU regulations implementation (27 regulations) with official EUR-Lex URLs
- ✅ Chapter 2B: Complete Asia-Pacific regulations implementation (22 regulations) from India, China, Japan, South Korea
- ✅ Chapter 2C: Complete Other Regions regulations implementation (16 regulations) covering USA, Canada, Latin America, Africa, Middle East
- ✅ **COMPLETE**: All 65 international regulations with verified official government sources
- ✅ **Button Separation**: Fixed functionality so "Start Compliance Analysis" shows upload forms only, "View Detailed Regulation Database" shows database only

**Files Created**:
- `data/regulatory_database.py`: Core database classes and management
- `utils/compliance_engine.py`: File analysis and compliance checking
- Enhanced hazardous substances page with database statistics and roadmap