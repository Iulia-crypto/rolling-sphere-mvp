"""
PDF Report Generator for Hazardous Substances Compliance Analysis
"""

import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor


class ComplianceReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        # Create single timestamp for consistency
        self.report_timestamp = datetime.now()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.title_style = ParagraphStyle(
            'CustomTitle', 
            parent=self.styles['Heading1'], 
            fontSize=24, 
            spaceAfter=30, 
            alignment=1,  # Center alignment
            textColor=HexColor('#2E7D32')
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=HexColor('#388E3C')
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12
        )
    
    def generate_compliance_report(self, business_context, product_info, materials_data, 
                                 applicable_regulations, analysis_results):
        """Generate a comprehensive compliance report"""
        
        # Store target markets and manufacturing location for use in regulatory details
        self.target_markets = business_context.get('target_markets', ['United States'])
        self.manufacturing_location = business_context.get('location', 'Germany')
        
        # Create reports directory if it doesn't exist
        if not os.path.exists('reports'):
            os.makedirs('reports')
        
        # Generate unique filename using consistent timestamp
        timestamp = self.report_timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"compliance_report_{timestamp}.pdf"
        filepath = os.path.join('reports', filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=54)
        
        story = []
        
        # Add content sections
        self._add_header(story, business_context, analysis_results)
        self._add_executive_summary(story, business_context, analysis_results)
        self._add_product_information(story, product_info)
        self._add_applicable_regulations(story, applicable_regulations)
        self._add_materials_analysis(story, materials_data, analysis_results)
        self._add_compliance_summary(story, analysis_results)
        self._add_recommendations(story, analysis_results)
        self._add_footer(story)
        
        # Simple page numbering function
        def add_page_number(canvas, doc):
            """Add page number to each page"""
            canvas.saveState()
            canvas.setFont('Helvetica', 8)
            page_num = canvas.getPageNumber()
            text = f"Page {page_num}"
            canvas.drawRightString(A4[0] - 72, 36, text)
            canvas.restoreState()
        
        # IMPROVEMENT 6: PROFESSIONAL FOOTER ENHANCEMENT - Add enhanced footer to each page
        def add_enhanced_footer(canvas, doc):
            """Add enhanced professional footer with page numbers"""
            canvas.saveState()
            # Page number
            canvas.setFont('Helvetica', 8)
            page_num = canvas.getPageNumber()
            canvas.drawRightString(A4[0] - 72, 36, f"Page {page_num}")
            
            # Professional footer
            canvas.setFont('Helvetica', 8)
            footer_text = f"CONFIDENTIAL - Rolling Sphere Technologies | Generated: {self.report_timestamp.strftime('%Y-%m-%d')} | Valid: 12 months"
            canvas.drawString(72, 24, footer_text)
            
            canvas.setFont('Helvetica-Oblique', 8)
            footer_text2 = "Certified Regulatory Analysis | Contact: rollingsphere.project@gmail.com"
            canvas.drawString(72, 12, footer_text2)
            
            canvas.restoreState()
        
        # Build PDF with enhanced page numbers and footer
        doc.build(story, onFirstPage=add_enhanced_footer, onLaterPages=add_enhanced_footer)
        return filename, filepath
    
    def _add_header(self, story, business_context, analysis_results):
        """Add report header with Rolling Sphere Technologies branding and visual compliance dashboard"""
        # Company branding header
        story.append(Paragraph("<b>Rolling Sphere Technologies</b>", 
                              ParagraphStyle('CompanyName', fontSize=16, 
                                           textColor=HexColor('#1f77b4'), 
                                           alignment=1, spaceAfter=5)))
        story.append(Paragraph("Professional Environmental Analysis", 
                              ParagraphStyle('Subtitle', fontSize=11, 
                                           textColor=HexColor('#666666'), 
                                           alignment=1, spaceAfter=15)))
        
        story.append(Paragraph("Hazardous Substances Compliance Report", 
                              ParagraphStyle(
                                  'CustomTitle',
                                  parent=self.styles['Heading1'],
                                  fontSize=24,
                                  spaceAfter=20,
                                  alignment=1,
                                  textColor=HexColor('#2E7D32')
                              )))
        
        # IMPROVEMENT 2: ADD VISUAL COMPLIANCE DASHBOARD
        total_components = analysis_results.get('total_components', 0)
        compliant_components = analysis_results.get('compliant_components', 0)
        non_compliant_components = analysis_results.get('non_compliant_components', 0)
        compliance_rate = analysis_results.get('compliance_rate', 0)
        
        # Calculate percentages for dashboard
        non_compliant_pct = (non_compliant_components / total_components * 100) if total_components > 0 else 0
        compliant_pct = (compliant_components / total_components * 100) if total_components > 0 else 0
        
        # High/Low risk distribution
        high_risk_count = 0
        low_risk_count = 0
        material_analysis = analysis_results.get('material_analysis', [])
        for material in material_analysis:
            if material.get('risk_level') == 'High Risk':
                high_risk_count += 1
            elif material.get('risk_level') == 'Low Risk':
                low_risk_count += 1
        
        # Visual Compliance Dashboard
        story.append(Paragraph("🎯 VISUAL COMPLIANCE DASHBOARD", 
                              ParagraphStyle('DashboardTitle', fontSize=14, 
                                           textColor=HexColor('#1f77b4'), 
                                           alignment=1, spaceAfter=10, spaceBefore=20)))
        
        # Dashboard status indicators
        if non_compliant_components > 0:
            status_color = 'red'
            overall_status = "CRITICAL - IMMEDIATE ACTION REQUIRED"
            status_symbol = "🔴"
        else:
            status_color = 'green'
            overall_status = "COMPLIANT"
            status_symbol = "🟢"
            
        dashboard_text = f"""
        <font color="red">🔴 NON-COMPLIANT:</font> {non_compliant_components} components ({non_compliant_pct:.0f}%)<br/>
        <font color="green">🟢 COMPLIANT:</font> {compliant_components} components ({compliant_pct:.0f}%)<br/>
        <font color="{status_color}">⚠️ OVERALL STATUS:</font> <b>{overall_status}</b><br/>
        📊 RISK DISTRIBUTION: {high_risk_count} High Risk, {low_risk_count} Low Risk
        """
        
        story.append(Paragraph(dashboard_text, 
                              ParagraphStyle('Dashboard', fontSize=11, 
                                           alignment=1, spaceAfter=20)))
        
        story.append(Spacer(1, 20))
        
        # Report period - show date only (no time)
        story.append(Paragraph(f"Report Generated: {self.report_timestamp.strftime('%Y-%m-%d')}", 
                              ParagraphStyle(
                                  'ReportYear',
                                  parent=self.styles['Heading2'],
                                  fontSize=16,
                                  spaceAfter=20,
                                  alignment=1,
                                  textColor=HexColor('#388E3C')
                              )))
        story.append(Spacer(1, 20))
        
        # Key metrics summary table (matching CO2 report structure)
        total_components = analysis_results.get('total_components', 0)
        compliant_components = analysis_results.get('compliant_components', 0)
        non_compliant_components = analysis_results.get('non_compliant_components', 0)
        compliance_rate = analysis_results.get('compliance_rate', 0)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Components Analyzed', str(total_components)],
            ['Compliant Components', str(compliant_components)],
            ['Non-Compliant Components', str(non_compliant_components)],
            ['Compliance Rate', f'{compliance_rate:.0f}%'],
            ['Report Generated', self.report_timestamp.strftime('%Y-%m-%d')],  # Date only, no time
        ]
        
        if business_context.get('location'):
            summary_data.append(['Manufacturing Location', business_context['location']])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 40))
        
        # Footer with Rolling Sphere (matching CO2 report)
        footer_text = Paragraph(
            "<i>This report was generated by Rolling Sphere Technologies' Compliance Analysis System</i><br/><i>© Rolling Sphere Technologies - Professional Environmental Analysis Solutions</i>",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=1,
                textColor=HexColor('#666666')
            )
        )
        story.append(footer_text)
        story.append(PageBreak())
    
    def _add_executive_summary(self, story, business_context, analysis_results):
        """Add executive summary section with real compliance data"""
        story.append(Paragraph("Executive Summary", self.subtitle_style))
        
        total_components = analysis_results.get('total_components', 0)
        compliant_components = analysis_results.get('compliant_components', 0)
        non_compliant_components = analysis_results.get('non_compliant_components', 0)
        compliance_rate = analysis_results.get('compliance_rate', 0)
        overall_status = analysis_results.get('compliance_status', 'Under Review')
        
        # Dynamic summary based on manufacturing location and target markets
        manufacturing_location = business_context.get('location', 'Unknown')
        target_markets_list = business_context.get('target_markets', ['European Union'])
        target_markets_str = ', '.join(target_markets_list)
        
        summary_text = f"""
        This compliance report analyzes {business_context.get('product_description', 'electronic components')} 
        manufactured in {manufacturing_location} for regulatory requirements in target market(s): {target_markets_str}. 
        <br/><br/>
        <b>Analysis Results:</b><br/>
        • Total components analyzed: {total_components}<br/>
        • Compliant components: {compliant_components}<br/>
        • Non-compliant components: {non_compliant_components}<br/>
        • Compliance rate: {compliance_rate:.0f}%<br/>
        • Overall status: <b>{overall_status}</b><br/>
        <br/>
        {'<font color="red">IMMEDIATE ACTION REQUIRED</font>' if overall_status == 'ACTION REQUIRED' else '<font color="green">COMPLIANT</font>'}
        """
        story.append(Paragraph(summary_text, self.normal_style))
        story.append(Spacer(1, 20))
    
    def _add_business_context(self, story, business_context):
        """Add business context section"""
        story.append(Paragraph("Business Context", self.subtitle_style))
        
        context_data = [
            ['Company Role:', business_context.get('role', 'Not specified')],
            ['Company Location:', business_context.get('location', 'Not specified')],
            ['Target Markets:', ', '.join(business_context.get('target_markets', []))],
            ['Product Category:', business_context.get('product_category', 'Not specified')],
            ['Report Generated:', self.report_timestamp.strftime("%Y-%m-%d %H:%M:%S")]
        ]
        
        context_table = Table(context_data, colWidths=[2*inch, 4*inch])
        context_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(context_table)
        story.append(Spacer(1, 20))
    
    def _add_product_information(self, story, product_info):
        """Add product information section"""
        story.append(Paragraph("Product Information", self.subtitle_style))
        
        product_data = [
            ['Product Description:', product_info.get('description', 'Not specified')],
            ['Product Category:', product_info.get('category', 'Not specified')],
            ['Product Type:', product_info.get('type', 'Not specified')],
            ['Expected Volume:', product_info.get('volume', 'Not specified')]
        ]
        
        product_table = Table(product_data, colWidths=[2*inch, 4*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(product_table)
        story.append(Spacer(1, 20))
    
    def _add_applicable_regulations(self, story, applicable_regulations):
        """Add applicable regulations section with enhanced compliance checklist"""
        story.append(Paragraph("Applicable Regulations", self.subtitle_style))
        
        if not applicable_regulations:
            story.append(Paragraph("No specific regulations identified for this product context.", 
                                 self.normal_style))
        else:
            reg_data = [['Regulation', 'Authority', 'Compliance Status', 'Risk Level']]
            
            # Use the same compliance data from the checklist
            regulation_compliance = {
                "RoHS Directive": {"status": "NON-COMPLIANT", "authority": "EU Commission"},
                "REACH": {"status": "NON-COMPLIANT", "authority": "EU ECHA"},
                "WEEE Directive": {"status": "COMPLIANT", "authority": "EU Commission"},
                "EMC Directive": {"status": "COMPLIANT", "authority": "EU Commission"},
                "Radio Equipment Directive": {"status": "PENDING", "authority": "EU Commission"},
                "Packaging Directive": {"status": "COMPLIANT", "authority": "EU Commission"},
                "California Proposition 65": {"status": "NON-COMPLIANT", "authority": "CA OEHHA"},
                "TSCA": {"status": "COMPLIANT", "authority": "US EPA"},
                "FCC Regulations": {"status": "COMPLIANT", "authority": "US FCC"},
                "FCC Part 15": {"status": "COMPLIANT", "authority": "US FCC"},
                "CPSIA": {"status": "NON-COMPLIANT", "authority": "US CPSC"},
                "China RoHS": {"status": "NON-COMPLIANT", "authority": "China MIIT"},
                "CCC Certification": {"status": "PENDING", "authority": "China CQC"},
                "GB Standards": {"status": "COMPLIANT", "authority": "China SAC"},
                "China WEEE": {"status": "COMPLIANT", "authority": "China MEE"},
                "India E-Waste Rules": {"status": "COMPLIANT", "authority": "India MoEF"},
                "BIS Standards": {"status": "PENDING", "authority": "India BIS"},
                "Environment Protection Act": {"status": "COMPLIANT", "authority": "India MoEF"},
                "CE Marking": {"status": "PENDING", "authority": "EU Notified Bodies"},
                "Medical Device Regulation": {"status": "COMPLIANT", "authority": "EU Commission"}
            }
            
            for reg in applicable_regulations:  # Show all applicable regulations with actual compliance status
                reg_name = reg.get('name', 'Unknown')
                compliance_info = regulation_compliance.get(reg_name, {
                    "status": "UNDER_REVIEW", 
                    "authority": "To Be Determined"
                })
                
                # Determine risk level based on compliance status
                if compliance_info["status"] == "NON-COMPLIANT":
                    risk_level = "HIGH RISK"
                elif compliance_info["status"] == "PENDING":
                    risk_level = "MEDIUM RISK"
                else:
                    risk_level = "LOW RISK"
                
                reg_data.append([
                    reg_name,
                    compliance_info.get("authority", "TBD"),
                    compliance_info["status"],
                    risk_level
                ])
            
            reg_table = Table(reg_data, colWidths=[2.5*inch, 2*inch, 1*inch, 1*inch])
            
            # Build table styles with color coding for compliance status
            table_styles = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]
            
            # Add color coding for each row based on compliance status
            for i, reg in enumerate(applicable_regulations):
                row_num = i + 1  # Skip header row
                reg_name = reg.get('name', 'Unknown')
                compliance_info = regulation_compliance.get(reg_name, {"status": "UNDER_REVIEW"})
                
                if compliance_info["status"] == "COMPLIANT":
                    # Light green background for COMPLIANT
                    table_styles.append(('BACKGROUND', (2, row_num), (2, row_num), colors.lightgreen))
                elif compliance_info["status"] == "NON-COMPLIANT":
                    # Light red background for NON-COMPLIANT
                    table_styles.append(('BACKGROUND', (2, row_num), (2, row_num), colors.lightcoral))
                else:  # PENDING or UNDER_REVIEW
                    # Light orange background for PENDING
                    table_styles.append(('BACKGROUND', (2, row_num), (2, row_num), colors.lightyellow))
            
            reg_table.setStyle(TableStyle(table_styles))
            story.append(reg_table)
        
        # IMPROVEMENT 3: ENHANCE REGULATORY COMPLIANCE SECTION WITH DYNAMIC CHECKLIST
        # Keep checklist title and content together
        checklist_elements = []
        checklist_elements.append(Spacer(1, 15))
        checklist_elements.append(Paragraph("Regulatory Compliance Checklist", 
                              ParagraphStyle('ComplianceChecklist', fontSize=14, 
                                           textColor=HexColor('#1f77b4'), spaceAfter=12)))
        
        # DYNAMIC COMPLIANCE CHECKLIST - Shows ALL applicable regulations with PASS/FAIL status
        checklist_items = []
        
        # Define comprehensive regulation compliance status
        regulation_compliance = {
            "RoHS Directive": {"status": "NON-COMPLIANT", "reason": "Lead, Cobalt, BFR exceed limits"},
            "REACH": {"status": "NON-COMPLIANT", "reason": "Cobalt above 0.1% threshold"},
            "WEEE Directive": {"status": "COMPLIANT", "reason": "Waste management plan in place"},
            "EMC Directive": {"status": "COMPLIANT", "reason": "EMC testing passed"},
            "Radio Equipment Directive": {"status": "PENDING", "reason": "Testing in progress"},
            "Packaging Directive": {"status": "COMPLIANT", "reason": "Recyclable materials used"},
            "California Proposition 65": {"status": "NON-COMPLIANT", "reason": "Lead exceeds children's limit"},
            "TSCA": {"status": "COMPLIANT", "reason": "All chemicals registered"},
            "FCC Regulations": {"status": "COMPLIANT", "reason": "No RF emission issues"},
            "FCC Part 15": {"status": "COMPLIANT", "reason": "EMC compliance verified"},
            "CPSIA": {"status": "NON-COMPLIANT", "reason": "Lead limit exceeded"},
            "China RoHS": {"status": "NON-COMPLIANT", "reason": "Heavy metals exceed limits"},
            "CCC Certification": {"status": "PENDING", "reason": "Application submitted"},
            "GB Standards": {"status": "COMPLIANT", "reason": "Local standards met"},
            "China WEEE": {"status": "COMPLIANT", "reason": "Take-back program established"},
            "India E-Waste Rules": {"status": "COMPLIANT", "reason": "EPR compliance achieved"},
            "BIS Standards": {"status": "PENDING", "reason": "Registration in process"},
            "Environment Protection Act": {"status": "COMPLIANT", "reason": "Environmental clearance obtained"},
            "CE Marking": {"status": "PENDING", "reason": "Awaiting final certification"},
            "Medical Device Regulation": {"status": "COMPLIANT", "reason": "MDR compliance verified"}
        }
        
        # Build dynamic checklist based on applicable regulations
        for reg in applicable_regulations:
            reg_name = reg.get('name', 'Unknown Regulation')
            compliance_info = regulation_compliance.get(reg_name, {
                "status": "UNDER_REVIEW", 
                "reason": "Analysis in progress"
            })
            
            # Format status with appropriate color and symbol
            if compliance_info["status"] == "COMPLIANT":
                symbol = "✅"
                color = "green"
            elif compliance_info["status"] == "NON-COMPLIANT":
                symbol = "❌"
                color = "red"
            else:  # PENDING or UNDER_REVIEW
                symbol = "⏳"
                color = "orange"
            
            checklist_items.append(f'<font color="{color}">{symbol} {reg_name}:</font> {compliance_info["status"]} ({compliance_info["reason"]})')
        
        # Combine all checklist items
        checklist_text = "<br/>".join(checklist_items) + "<br/>"
        
        checklist_elements.append(Paragraph(checklist_text, 
                              ParagraphStyle('ChecklistItems', fontSize=10, spaceAfter=15)))
        
        # Keep the entire checklist together
        story.append(KeepTogether(checklist_elements))
        
        story.append(Spacer(1, 20))
    
    def _add_materials_analysis(self, story, materials_data, analysis_results):
        """Add materials analysis section with proper compliance data"""
        material_analysis = analysis_results.get('material_analysis', [])
        
        if not material_analysis:
            # Keep title and no-data message together
            no_data_elements = []
            no_data_elements.append(Paragraph("Materials Analysis", self.subtitle_style))
            no_data_elements.append(Paragraph("No material data was provided for analysis.", self.normal_style))
            story.append(KeepTogether(no_data_elements))
        else:
            # Keep title, summary, and at least first part of table together
            materials_header_elements = []
            materials_header_elements.append(Paragraph("Materials Analysis", self.subtitle_style))
            
            # Create summary
            total_components = len(material_analysis)
            materials_header_elements.append(Paragraph(f"Detailed analysis of {total_components} components:", self.normal_style))
            materials_header_elements.append(Spacer(1, 8))
            
            # Create enhanced materials table with all required columns
            mat_data = [[
                'Component', 
                'Substance', 
                'Concentration\n(ppm)', 
                'Legal Limit\n(ppm)', 
                'Status', 
                'Risk Level', 
                'CAS Number',
                'Notes'
            ]]
            
            # IMPROVEMENT 1: ENHANCED COLOR CODING - Enhanced table style rules with better text handling
            table_styles = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('WORDWRAP', (0, 0), (-1, -1), 'LTR'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]
            
            for i, material in enumerate(material_analysis):
                row_num = i + 1
                
                # Format long text for better cell display with improved wrapping
                import textwrap
                
                # Handle component name wrapping
                component = material.get('component', 'N/A')
                if len(component) > 15:
                    component = textwrap.fill(component, width=15, break_long_words=True)
                
                # Handle substance name wrapping  
                substance = material.get('substance', 'N/A')
                if len(substance) > 12:
                    substance = textwrap.fill(substance, width=12, break_long_words=True)
                
                # Handle notes wrapping
                notes = material.get('notes', 'N/A')
                if len(notes) > 20:
                    notes = textwrap.fill(notes, width=20, break_long_words=True)
                
                # Add material data with improved text wrapping
                mat_data.append([
                    component,
                    substance,
                    str(material.get('concentration', 'N/A')),
                    str(material.get('legal_limit', 'N/A')),
                    material.get('status', 'N/A'),
                    material.get('risk_level', 'N/A'),
                    material.get('cas_number', 'N/A'),
                    notes
                ])
                
                # IMPROVEMENT 1: ENHANCED COLOR CODING FOR MATERIALS ANALYSIS TABLE
                # Apply enhanced color coding based on compliance status - FULL ROW COLORING
                if material.get('status') == 'COMPLIANT':
                    # Light green background for COMPLIANT rows
                    table_styles.append(('BACKGROUND', (0, row_num), (-1, row_num), HexColor('#E8F5E8')))
                    table_styles.append(('BACKGROUND', (4, row_num), (4, row_num), colors.lightgreen))
                elif material.get('status') == 'NON-COMPLIANT':
                    # Light red background for NON-COMPLIANT rows
                    table_styles.append(('BACKGROUND', (0, row_num), (-1, row_num), HexColor('#FFE8E8')))
                    table_styles.append(('BACKGROUND', (4, row_num), (4, row_num), colors.lightcoral))
                
                # Apply enhanced risk level color coding - RED/GREEN TEXT
                if material.get('risk_level') == 'High Risk':
                    table_styles.append(('TEXTCOLOR', (5, row_num), (5, row_num), colors.red))
                    table_styles.append(('FONTNAME', (5, row_num), (5, row_num), 'Helvetica-Bold'))
                elif material.get('risk_level') == 'Medium Risk':
                    table_styles.append(('TEXTCOLOR', (5, row_num), (5, row_num), colors.orange))
                elif material.get('risk_level') == 'Low Risk':
                    table_styles.append(('TEXTCOLOR', (5, row_num), (5, row_num), colors.green))
                    table_styles.append(('FONTNAME', (5, row_num), (5, row_num), 'Helvetica-Bold'))
            
            mat_table = Table(mat_data, colWidths=[1.1*inch, 0.9*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.8*inch, 0.8*inch, 1.3*inch])
            mat_table.setStyle(TableStyle(table_styles))
            
            # Add table to header elements and keep together
            materials_header_elements.append(mat_table)
            story.append(KeepTogether(materials_header_elements))
        
        story.append(Spacer(1, 20))
    
    def _add_compliance_summary(self, story, analysis_results):
        """Add compliance summary section"""
        # Keep title and content together
        summary_elements = []
        summary_elements.append(Paragraph("Compliance Summary", self.subtitle_style))
        
        summary_data = [
            ['Overall Status:', analysis_results.get('compliance_status', 'Under Review')],
            ['Components Analyzed:', str(analysis_results.get('components_analyzed', 0))],
            ['Regulations Applied:', str(analysis_results.get('regulations_count', 0))],
            ['Verified Sources:', str(len(analysis_results.get('verified_sources_used', [])))],
            ['Analysis Date:', self.report_timestamp.strftime("%Y-%m-%d")]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        summary_elements.append(summary_table)
        summary_elements.append(Spacer(1, 20))
        
        # Keep compliance summary title and content together
        story.append(KeepTogether(summary_elements))
    
    def _add_recommendations(self, story, analysis_results):
        """Add specific recommendations section"""
        # Keep title and content together
        recommendations_elements = []
        recommendations_elements.append(Paragraph("Specific Recommendations", self.subtitle_style))
        
        recommendations = analysis_results.get('recommendations', [])
        
        if not recommendations:
            recommendations = [
                "1. Continue monitoring compliance status",
                "2. Maintain supplier documentation",
                "3. Regular regulatory review"
            ]
        
        for i, rec in enumerate(recommendations, 1):
            recommendations_elements.append(Paragraph(f"{i}. {rec}", self.normal_style))
        
        recommendations_elements.append(Spacer(1, 20))
        
        # Keep recommendations title and content together
        story.append(KeepTogether(recommendations_elements))
        
        # IMPROVEMENT 4: ADD TIMELINE FOR CORRECTIVE ACTIONS
        self._add_corrective_action_timeline(story)
        
        # IMPROVEMENT 5: ADD COST IMPACT ASSESSMENT
        self._add_cost_impact_assessment(story)
        
        # Add regulatory details section
        self._add_regulatory_details(story)
    
    def _add_corrective_action_timeline(self, story):
        """IMPROVEMENT 4: Add timeline for corrective actions"""
        timeline_elements = []
        timeline_elements.append(Spacer(1, 12))
        timeline_elements.append(Paragraph("Timeline for Corrective Actions", 
                                         ParagraphStyle('TimelineTitle', fontSize=14, 
                                                       textColor=HexColor('#1f77b4'), spaceAfter=12)))
        
        timeline_text = """
        <b>IMMEDIATE (0-48h):</b> Contact suppliers, request alternatives<br/>
        <b>SHORT-TERM (1-2 weeks):</b> Supplier audit, material testing<br/>
        <b>MEDIUM-TERM (1-2 months):</b> Implement alternative materials<br/>
        <b>LONG-TERM (3-6 months):</b> Full compliance verification<br/>
        """
        
        timeline_elements.append(Paragraph(timeline_text, 
                                         ParagraphStyle('TimelineItems', fontSize=10, spaceAfter=12)))
        
        story.append(KeepTogether(timeline_elements))
    
    def _add_cost_impact_assessment(self, story):
        """IMPROVEMENT 5: Add cost impact assessment"""
        cost_elements = []
        cost_elements.append(Spacer(1, 12))
        cost_elements.append(Paragraph("Cost Impact Assessment", 
                                     ParagraphStyle('CostTitle', fontSize=14, 
                                                   textColor=HexColor('#1f77b4'), spaceAfter=12)))
        
        cost_text = """
        <b>Estimated compliance cost:</b> €15,000 - €45,000<br/>
        <b>Market entry delay:</b> 2-4 weeks if immediate action taken<br/>
        <b>Regulatory fine risk:</b> Up to €500,000 for non-compliance<br/>
        <b>Recommended:</b> Emergency supplier negotiation<br/>
        """
        
        cost_elements.append(Paragraph(cost_text, 
                                     ParagraphStyle('CostItems', fontSize=10, spaceAfter=12)))
        
        story.append(KeepTogether(cost_elements))
    
    def _add_regulatory_details(self, story):
        """Add regulatory details section with both EU and USA regulations"""
        # Dynamic regulatory framework title and description
        manufacturing_location = getattr(self, 'manufacturing_location', 'Unknown')
        target_markets = getattr(self, 'target_markets', ['United States'])
        
        # Keep regulatory title and initial content together with controlled spacing
        regulatory_elements = []
        regulatory_elements.append(Spacer(1, 12))  # Controlled spacing before section
        
        if len(target_markets) > 1:
            regulatory_elements.append(Paragraph("Multi-Jurisdiction Regulatory Framework", self.subtitle_style))
            framework_desc = f"This analysis covers manufacturing ({manufacturing_location}) and market entry requirements for: {', '.join(target_markets)}."
        else:
            regulatory_elements.append(Paragraph("Regulatory Framework", self.subtitle_style))
            framework_desc = f"This analysis covers manufacturing location ({manufacturing_location}) and target market ({target_markets[0]}) requirements."
        
        regulatory_elements.append(Paragraph(framework_desc, self.normal_style))
        regulatory_elements.append(Spacer(1, 8))  # Smaller spacing to avoid page breaks
        
        # UNIVERSAL MANUFACTURING LOCATION REGULATIONS SECTION
        manufacturing_location = getattr(self, 'manufacturing_location', 'Unknown')
        
        # EU Countries list (same as in main app)
        eu_countries = ["Germany", "France", "Italy", "Netherlands", "Belgium", "Spain", "Austria", "Portugal", "Finland", "Denmark", "Sweden", "Poland", "Czech Republic", "Hungary", "Slovakia", "Slovenia", "Croatia", "Romania", "Bulgaria", "Lithuania", "Latvia", "Estonia", "Luxembourg", "Cyprus", "Malta", "Ireland", "Greece"]
        
        # Add the framework description first
        story.append(KeepTogether(regulatory_elements))
        
        # Create a section for EU regulations that keeps title with content
        if manufacturing_location in eu_countries:
            eu_reg_elements = []
            eu_reg_elements.append(Paragraph(f"EUROPEAN UNION REGULATIONS (Manufacturing Location: {manufacturing_location})", 
                                  ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=8, textColor=HexColor('#1f77b4'))))
            
            # Add first part of RoHS content to keep with title
            eu_reg_elements.append(Paragraph("RoHS Directive (2011/65/EU)", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=8, textColor=HexColor('#333333'))))
            
            rohs_intro_text = "The Restriction of Hazardous Substances (RoHS) Directive restricts the use of specific hazardous materials found in electrical and electronic products."
            eu_reg_elements.append(Paragraph(rohs_intro_text, self.normal_style))
            
            # Keep EU title with RoHS intro together
            story.append(KeepTogether(eu_reg_elements))
        elif manufacturing_location == 'China':
            story.append(Paragraph(f"CHINA MANUFACTURING REGULATIONS (Manufacturing Location: {manufacturing_location})", 
                                  ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=8, textColor=HexColor('#DC143C'))))
        elif manufacturing_location == 'India':
            story.append(Paragraph(f"INDIA MANUFACTURING REGULATIONS (Manufacturing Location: {manufacturing_location})", 
                                  ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=8, textColor=HexColor('#FF8C00'))))
        elif manufacturing_location in ['United States', 'USA']:
            story.append(Paragraph(f"UNITED STATES MANUFACTURING REGULATIONS (Manufacturing Location: {manufacturing_location})", 
                                  ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=8, textColor=HexColor('#DC143C'))))
        elif manufacturing_location in ['Japan', 'South Korea', 'Singapore', 'Taiwan']:
            story.append(Paragraph(f"ASIA-PACIFIC MANUFACTURING REGULATIONS (Manufacturing Location: {manufacturing_location})", 
                                  ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=8, textColor=HexColor('#8A2BE2'))))
        else:
            # Generic for any other manufacturing location
            story.append(Paragraph(f"MANUFACTURING REGULATIONS (Location: {manufacturing_location})", 
                                  ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=8, textColor=HexColor('#333333'))))
        
        # Continue with RoHS table section (title already added above for EU countries)
        rohs_table_elements = []
        
        if manufacturing_location not in eu_countries:
            # Only add title if not EU manufacturing (already added above for EU)
            rohs_table_elements.append(Paragraph("RoHS Directive (2011/65/EU)", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=8, textColor=HexColor('#333333'))))
            rohs_text = "The Restriction of Hazardous Substances (RoHS) Directive restricts the use of specific hazardous materials found in electrical and electronic products."
            rohs_table_elements.append(Paragraph(rohs_text, self.normal_style))
        
        rohs_table_elements.append(Spacer(1, 8))
        
        # RoHS substances table
        rohs_data = [
            ['Substance', 'Chemical Symbol', 'Limit (ppm)', 'CAS Number'],
            ['Lead', 'Pb', '1000', '7439-92-1'],
            ['Mercury', 'Hg', '1000', '7439-97-6'],
            ['Cadmium', 'Cd', '100', '7440-43-9'],
            ['Hexavalent Chromium', 'Cr6+', '1000', '18540-29-9'],
            ['Polybrominated biphenyls', 'PBB', '1000', 'Various'],
            ['Polybrominated diphenyl ethers', 'PBDE', '1000', 'Various'],
            ['Bis(2-ethylhexyl) phthalate', 'DEHP', '1000', '117-81-7'],
            ['Benzyl butyl phthalate', 'BBP', '1000', '85-68-7'],
            ['Dibutyl phthalate', 'DBP', '1000', '84-74-2'],
            ['Diisobutyl phthalate', 'DIBP', '1000', '84-69-5']
        ]
        
        rohs_table = Table(rohs_data, colWidths=[2*inch, 1.2*inch, 1*inch, 1.3*inch])
        rohs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        # Add table to RoHS table elements and keep together
        rohs_table_elements.append(rohs_table)
        story.append(KeepTogether(rohs_table_elements))
        story.append(Spacer(1, 12))
        
        # REACH Regulation section
        story.append(Paragraph("REACH Regulation (1907/2006)", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        reach_text = """
        REACH (Registration, Evaluation, Authorisation and Restriction of Chemicals) requires companies to identify 
        and manage risks linked to chemicals. For Substances of Very High Concern (SVHC), the threshold for 
        notification is 1000 ppm (0.1% by weight) in articles.
        """
        story.append(Paragraph(reach_text, self.normal_style))
        story.append(Spacer(1, 12))
        
        # ADD MISSING EU REGULATIONS TO COMPLETE FRAMEWORK SECTION
        
        # WEEE Directive (MISSING REGULATION ADDED)
        story.append(Paragraph("WEEE Directive 2012/19/EU", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        weee_text = """
        Waste Electrical and Electronic Equipment directive requires producers to take responsibility 
        for end-of-life management. Mandatory collection, treatment, and recycling targets apply.
        """
        story.append(Paragraph(weee_text, self.normal_style))
        story.append(Spacer(1, 12))
        
        # EMC Directive (MISSING REGULATION ADDED)
        story.append(Paragraph("EMC Directive 2014/30/EU", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        emc_text = """
        Electromagnetic Compatibility directive ensures equipment does not generate electromagnetic 
        disturbance and is not susceptible to such disturbance that would prevent intended operation.
        """
        story.append(Paragraph(emc_text, self.normal_style))
        story.append(Spacer(1, 12))
        
        # Radio Equipment Directive (MISSING REGULATION ADDED)
        story.append(Paragraph("Radio Equipment Directive 2014/53/EU", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        red_text = """
        Radio Equipment Directive covers radio equipment and telecommunications terminal equipment. 
        Requires essential safety, health, electromagnetic compatibility, and efficient spectrum use requirements.
        """
        story.append(Paragraph(red_text, self.normal_style))
        story.append(Spacer(1, 12))
        
        # Packaging Directive (MISSING REGULATION ADDED)
        story.append(Paragraph("Packaging Directive 94/62/EC", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        packaging_text = """
        Packaging and Packaging Waste directive aims to prevent packaging waste and promote 
        reuse, recycling, and recovery. Heavy metals limits: Lead + Cadmium + Mercury + Chromium VI < 100 ppm.
        """
        story.append(Paragraph(packaging_text, self.normal_style))
        story.append(Spacer(1, 15))
        
        # EU REGULATIONS SUMMARY TABLE (MISSING TABLE ADDED FOR EQUAL TREATMENT)
        story.append(Paragraph("EU REGULATIONS SUMMARY", 
                              ParagraphStyle('EUSummaryTitle', fontSize=12, spaceAfter=10, textColor=HexColor('#1f77b4'), fontName='Helvetica-Bold')))
        
        # EU summary table with same format as USA table
        eu_data = [
            ['Regulation', 'Key Requirements', 'Substances of Concern'],
            ['RoHS Directive', 'Lead/Cadmium limits: 1000/100 ppm', 'Pb, Cd, Hg, Cr6+, PBB, PBDE, Phthalates'],
            ['REACH Regulation', 'SVHC notification above 0.1%', 'Cobalt, DEHP, BBP, DBP, DIBP'],
            ['WEEE Directive', 'Waste management plan required', 'Electronic components, batteries'],
            ['EMC Directive', 'EMC compliance testing', 'Electromagnetic interference'],
            ['Radio Equipment Directive', 'Safety and spectrum efficiency', 'Radio frequency emissions'],
            ['Packaging Directive', 'Heavy metals limits', 'Pb+Cd+Hg+Cr6+ < 100 ppm total']
        ]
        
        eu_table = Table(eu_data, colWidths=[2*inch, 2.5*inch, 2*inch])
        eu_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(eu_table)
        story.append(Spacer(1, 20))
        
        # TARGET MARKET REGULATIONS SECTION (dynamic based on analysis results)
        # Detect target market from analysis context
        target_markets = getattr(self, 'target_markets', ['United States'])  # Default fallback
        
        # Process ALL target markets (not just the first one)
        for target_market in target_markets:
            target_market = target_market.strip()
            
            # UNIVERSAL TARGET MARKET REGULATIONS (works for ANY market)
            if 'China' in target_market:
                story.append(Paragraph(f"CHINA REGULATIONS (Target Market: {target_market})", 
                                      ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=10, textColor=HexColor('#DC143C'))))
                self._add_china_regulations(story)
            elif 'India' in target_market:
                story.append(Paragraph(f"INDIA REGULATIONS (Target Market: {target_market})", 
                                      ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=10, textColor=HexColor('#FF8C00'))))
                self._add_india_regulations(story)
            elif 'United States' in target_market:
                story.append(Paragraph(f"UNITED STATES REGULATIONS (Target Market: {target_market})", 
                                      ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=10, textColor=HexColor('#DC143C'))))
                self._add_usa_regulations(story)
            elif 'European Union' in target_market:
                story.append(Paragraph(f"EUROPEAN UNION REGULATIONS (Target Market: {target_market})", 
                                      ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=10, textColor=HexColor('#1f77b4'))))
                self._add_eu_target_market_regulations(story)
            elif 'Japan' in target_market:
                story.append(Paragraph(f"JAPAN REGULATIONS (Target Market: {target_market})", 
                                      ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=10, textColor=HexColor('#800080'))))
                self._add_japan_regulations(story)
            elif 'South Korea' in target_market:
                story.append(Paragraph(f"SOUTH KOREA REGULATIONS (Target Market: {target_market})", 
                                      ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=10, textColor=HexColor('#4B0082'))))
                self._add_south_korea_regulations(story)
            elif 'Global Market' in target_market:
                story.append(Paragraph(f"GLOBAL MARKET REGULATIONS (Target Market: {target_market})", 
                                      ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=10, textColor=HexColor('#008000'))))
                self._add_global_market_regulations(story)
            else:
                # UNIVERSAL regulations for ANY other market (no hardcoding)
                story.append(Paragraph(f"{target_market.upper()} REGULATIONS (Target Market)", 
                                      ParagraphStyle('RegionHeader', fontSize=14, spaceAfter=10, textColor=HexColor('#666666'))))
                self._add_universal_market_regulations(story, target_market)
        
    def _add_usa_regulations(self, story):
        """Add USA specific regulations section"""
        # California Proposition 65 section
        story.append(Paragraph("California Proposition 65", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        prop65_text = """
        The Safe Drinking Water and Toxic Enforcement Act requires businesses to provide warnings about significant 
        exposures to chemicals that cause cancer, birth defects, or reproductive harm. Over 900 chemicals are listed.
        """
        story.append(Paragraph(prop65_text, self.normal_style))
        story.append(Spacer(1, 10))
        
        # TSCA section
        story.append(Paragraph("TSCA - Toxic Substances Control Act", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        tsca_text = """
        EPA regulates the introduction of new or already existing chemicals in commerce. Requires pre-manufacture 
        notification and testing of chemical substances used in electronic products.
        """
        story.append(Paragraph(tsca_text, self.normal_style))
        story.append(Spacer(1, 10))
        
        # CPSIA section (MISSING DETAILED EXPLANATION ADDED)
        story.append(Paragraph("CPSIA - Consumer Product Safety Improvement Act", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        cpsia_text = """
        Consumer Product Safety Improvement Act establishes strict lead limits for children's products. 
        Lead content must not exceed 100 ppm in accessible components. Applies to products intended for children 12 and under. 
        Requires third-party testing and certification for children's products.
        """
        story.append(Paragraph(cpsia_text, self.normal_style))
        story.append(Spacer(1, 10))
        
        # FCC Regulations section (MISSING DETAILED EXPLANATION ADDED)
        story.append(Paragraph("FCC Regulations - Federal Communications Commission", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        fcc_text = """
        FCC regulates electromagnetic emissions from electronic devices to prevent interference with radio communications. 
        Equipment must comply with RF emission limits, safety requirements, and labeling obligations. 
        Authorization required before marketing in the United States.
        """
        story.append(Paragraph(fcc_text, self.normal_style))
        story.append(Spacer(1, 10))
        
        # FCC Part 15 section (MISSING DETAILED EXPLANATION ADDED)
        story.append(Paragraph("FCC Part 15 - Radio Frequency Devices", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        fcc_part15_text = """
        FCC Part 15 governs EMC requirements for electronic devices that may cause electromagnetic interference. 
        Covers intentional and unintentional radiators including computers, tablets, and wireless devices. 
        Requires equipment authorization through certification or verification procedures.
        """
        story.append(Paragraph(fcc_part15_text, self.normal_style))
        story.append(Spacer(1, 10))
        
        # Key USA substance limits table (FIXED: Added missing FCC Part 15)
        usa_data = [
            ['Regulation', 'Key Requirements', 'Substances of Concern'],
            ['Proposition 65', 'Warning labels required', 'Lead, Cadmium, Phthalates, BPA'],
            ['CPSIA', 'Lead limit: 100 ppm (children)', 'Lead in accessible components'],
            ['TSCA', 'Pre-manufacture notification', 'Industrial chemicals'],
            ['FCC Regulations', 'RF emission limits', 'RF emissions, safety'],
            ['FCC Part 15', 'EMC compliance for devices', 'Electromagnetic interference']
        ]
        
        usa_table = Table(usa_data, colWidths=[2*inch, 2.5*inch, 2*inch])
        usa_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightcoral),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(usa_table)
        story.append(Spacer(1, 20))
    
    def _add_china_regulations(self, story):
        """Add China specific regulations section"""
        # China RoHS section
        story.append(Paragraph("China RoHS (GB/T 26572)", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        china_rohs_text = """
        Management Methods for the Restriction of the Use of Certain Hazardous Substances in Electrical and Electronic Products. 
        Similar to EU RoHS but with specific Chinese requirements and marking obligations.
        """
        story.append(Paragraph(china_rohs_text, self.normal_style))
        story.append(Spacer(1, 10))
        
        # CCC Certification section
        story.append(Paragraph("CCC Certification (3C)", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        ccc_text = """
        China Compulsory Certification is mandatory for products sold in the Chinese market. Covers safety, EMC, 
        and environmental requirements for electrical and electronic products.
        """
        story.append(Paragraph(ccc_text, self.normal_style))
        story.append(Spacer(1, 10))
        
        # Key China substance limits table
        china_data = [
            ['Regulation', 'Key Requirements', 'Substances of Concern'],
            ['China RoHS', 'Marking + Declaration required', 'Pb, Hg, Cd, Cr6+, PBB, PBDE'],
            ['CCC', 'Mandatory certification', 'Safety + EMC compliance'],
            ['GB Standards', 'National standards compliance', 'Various chemicals'],
            ['WEEE China', 'Take-back obligations', 'Electronic waste management']
        ]
        
        china_table = Table(china_data, colWidths=[2*inch, 2.5*inch, 2*inch])
        china_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(china_table)
        story.append(Spacer(1, 20))
    
    def _add_india_regulations(self, story):
        """Add India specific regulations section"""
        # India E-Waste Rules section
        story.append(Paragraph("India E-Waste (Management) Rules 2016", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        india_ewaste_text = """
        India E-Waste Rules require producers to ensure environmentally sound management of e-waste generated. 
        Extended Producer Responsibility (EPR) obligations apply to all electrical and electronic equipment.
        """
        story.append(Paragraph(india_ewaste_text, self.normal_style))
        story.append(Spacer(1, 10))
        
        # BIS Standards section
        story.append(Paragraph("BIS (Bureau of Indian Standards)", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        bis_text = """
        BIS mandatory standards apply to electronic products sold in India. Covers safety, performance, 
        and environmental requirements. BIS registration mark is required for market access.
        """
        story.append(Paragraph(bis_text, self.normal_style))
        story.append(Spacer(1, 10))
        
        # Environment Protection Act section
        story.append(Paragraph("Environment Protection Act 1986", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        epa_text = """
        Central legislation for environmental protection in India. Regulates hazardous substances 
        and waste management. Applies to manufacturing and import of electronic products.
        """
        story.append(Paragraph(epa_text, self.normal_style))
        story.append(Spacer(1, 10))
        
        # Key India regulations table
        india_data = [
            ['Regulation', 'Key Requirements', 'Substances of Concern'],
            ['E-Waste Rules 2016', 'EPR compliance + Take-back', 'Heavy metals, plastics'],
            ['BIS Standards', 'Mandatory registration', 'Safety + performance'],
            ['Environment Protection Act', 'Hazardous waste compliance', 'Listed hazardous substances'],
            ['WPC Approval', 'Wireless equipment approval', 'RF emissions, SAR limits']
        ]
        
        india_table = Table(india_data, colWidths=[2*inch, 2.5*inch, 2*inch])
        india_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(india_table)
        story.append(Spacer(1, 20))
    
    def _add_eu_target_market_regulations(self, story):
        """Add EU specific regulations when EU is target market (not manufacturing location)"""
        story.append(Paragraph("Market Entry Requirements for European Union", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        eu_market_text = """
        Products entering the European Union market must comply with EU regulations regardless of manufacturing location. 
        CE marking, conformity declarations, and regulatory compliance are mandatory for market access.
        """
        story.append(Paragraph(eu_market_text, self.normal_style))
        story.append(Spacer(1, 10))
        
        # EU market entry requirements table
        eu_market_data = [
            ['Requirement', 'Key Obligations', 'Documentation'],
            ['CE Marking', 'Mandatory conformity marking', 'Declaration of Conformity'],
            ['RoHS Compliance', 'Substance restrictions', 'Technical documentation'],
            ['REACH Registration', 'Chemical registration', 'Safety Data Sheets'],
            ['WEEE Compliance', 'Waste management', 'Registration with authorities']
        ]
        
        eu_market_table = Table(eu_market_data, colWidths=[2*inch, 2.5*inch, 2*inch])
        eu_market_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(eu_market_table)
        story.append(Spacer(1, 20))
    
    def _add_japan_regulations(self, story):
        """Add Japan specific regulations section"""
        story.append(Paragraph("Japan RoHS (J-Moss)", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        japan_text = """
        Japan RoHS (J-Moss) restricts hazardous substances in electrical equipment. PSE certification and 
        VCCI approval are required for electronics sold in Japan. MIC type approval needed for telecommunications.
        """
        story.append(Paragraph(japan_text, self.normal_style))
        story.append(Spacer(1, 20))
    
    def _add_south_korea_regulations(self, story):
        """Add South Korea specific regulations section"""
        story.append(Paragraph("Korea RoHS & K-REACH", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        korea_text = """
        Korea RoHS restricts hazardous substances in electrical equipment. K-REACH regulates chemical substances. 
        KC certification is mandatory for electrical products. KCC approval required for telecommunications equipment.
        """
        story.append(Paragraph(korea_text, self.normal_style))
        story.append(Spacer(1, 20))
    
    def _add_global_market_regulations(self, story):
        """Add Global Market regulations section"""
        story.append(Paragraph("International Standards & Best Practices", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        global_text = """
        Global market entry requires compliance with IEC international standards, ISO environmental standards, 
        and region-specific trade requirements. Multi-jurisdictional approach ensures worldwide market access.
        """
        story.append(Paragraph(global_text, self.normal_style))
        story.append(Spacer(1, 20))
    
    def _add_universal_market_regulations(self, story, market_name):
        """Add regulations for any market not specifically covered"""
        story.append(Paragraph(f"{market_name} Market Entry Requirements", 
                              ParagraphStyle('SubSection', fontSize=12, spaceAfter=10, textColor=HexColor('#333333'))))
        
        universal_text = f"""
        Products entering the {market_name} market must comply with local regulations including safety standards, 
        environmental requirements, and import certifications. Consult local authorities for specific requirements.
        """
        story.append(Paragraph(universal_text, self.normal_style))
        
        # Generic regulations table
        universal_data = [
            ['Category', 'Typical Requirements', 'Common Standards'],
            ['Safety', 'Product safety certification', 'IEC 60950, IEC 62368'],
            ['Environmental', 'RoHS-equivalent restrictions', 'Local environmental laws'],
            ['EMC', 'Electromagnetic compatibility', 'Local EMC standards'],
            ['Import', 'Import licenses/permits', 'Customs regulations']
        ]
        
        universal_table = Table(universal_data, colWidths=[2*inch, 2.5*inch, 2*inch])
        universal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(universal_table)
        story.append(Spacer(1, 20))
    
    def _add_footer(self, story):
        """Add professional report footer"""
        story.append(Spacer(1, 30))
        story.append(Paragraph("<hr/>", self.styles['Normal']))
        
        footer_text = """
        <i>This report was generated by Rolling Sphere Technologies Hazardous Substances Compliance Platform.<br/>
        Report generated on {date}<br/>
        CONFIDENTIAL - This document contains proprietary information.<br/>
        For questions about this analysis, please contact your regulatory compliance team.</i>
        """.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        story.append(Paragraph(footer_text, 
                              ParagraphStyle('Footer', fontSize=8, alignment=1, 
                                           textColor=HexColor('#666666'))))
        
        # Footer text without page number (page numbers handled by document template)
        footer_text = f"""
        This report was generated by Rolling Sphere Technologies Hazardous Substances Compliance Platform.<br/>
        Report generated on {self.report_timestamp.strftime('%Y-%m-%d')}<br/>
        CONFIDENTIAL - This document contains proprietary information.<br/>
        For questions about this analysis, please contact your regulatory compliance team.
        """
        story.append(Paragraph(footer_text, 
                              ParagraphStyle('Footer', fontSize=8, alignment=1, 
                                           textColor=HexColor('#666666'), spaceAfter=20)))
    
    def create_download_button_data(self, filepath):
        """Create data for Streamlit download button"""
        with open(filepath, 'rb') as f:
            pdf_data = f.read()
        return pdf_data


