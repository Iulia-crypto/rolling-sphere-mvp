from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import datetime
import textwrap

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        # Create single timestamp for consistency
        self.report_timestamp = datetime.now()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E7D32')
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#388E3C')
        )
        
        # Header style
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.HexColor('#4CAF50')
        )
    
    def _format_activities_text(self, activities, max_width=35):
        """Format activities text to prevent overflow with proper line wrapping"""
        if not activities:
            return 'None'
        
        # Clean and format activity names
        formatted_activities = [act.replace('_', ' ').title() for act in activities]
        
        # Join activities with line breaks for better cell formatting
        if len(formatted_activities) == 1:
            activity_text = formatted_activities[0]
            # Wrap long single activities
            if len(activity_text) > max_width:
                return textwrap.fill(activity_text, width=max_width, break_long_words=True)
            return activity_text
        
        # For multiple activities, use line breaks instead of commas
        result_lines = []
        current_line = ""
        
        for activity in formatted_activities:
            if not current_line:  # First activity on line
                current_line = activity
            elif len(current_line + ", " + activity) <= max_width:
                current_line += ", " + activity
            else:
                # Current line is full, start new line
                result_lines.append(current_line)
                current_line = activity
            
            # If we have too many lines, truncate
            if len(result_lines) >= 3:
                remaining = len(formatted_activities) - formatted_activities.index(activity)
                if remaining > 1:
                    result_lines.append(f"...and {remaining} more")
                break
        
        # Add the last line if there's content
        if current_line and len(result_lines) < 3:
            result_lines.append(current_line)
        
        return "\n".join(result_lines)
    
    def _wrap_text(self, text, max_width=20):
        """Wrap text to prevent overflow in table cells"""
        if len(text) <= max_width:
            return text
        
        # Use textwrap to break long text properly for PDF table cells
        wrapped = textwrap.fill(text, width=max_width, break_long_words=True)
        # Return with proper line breaks for table cells
        return wrapped
    
    def generate_report(self, emissions_data, company_info, include_recommendations=True, include_detailed_breakdown=True):
        """
        Generate a comprehensive PDF report
        """
        try:
            buffer = io.BytesIO()
            
            
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            story = []
            
            # Title page
            self._add_title_page(story, company_info, emissions_data)
            
            # Executive summary
            self._add_executive_summary(story, emissions_data)
            
            # GHG Protocol Scope Analysis
            self._add_scope_analysis(story, emissions_data)
            
            # Emissions breakdown
            self._add_emissions_breakdown(story, emissions_data)
            
            # Charts and visualizations
            self._add_visualizations(story, emissions_data)
            
            # Detailed breakdown if requested
            if include_detailed_breakdown:
                self._add_detailed_breakdown(story, emissions_data)
            
            # Recommendations if requested
            if include_recommendations:
                self._add_recommendations(story, emissions_data)
            
            # Footer information
            self._add_footer_info(story, emissions_data)
            
            # Simple, safe page numbering to avoid PDF corruption
            def add_page_number(canvas, doc):
                """Add page number to each page"""
                canvas.saveState()
                canvas.setFont('Helvetica', 8)
                page_num = canvas.getPageNumber()
                text = f"Page {page_num}"
                canvas.drawRightString(A4[0] - 72, 36, text)
                canvas.restoreState()
            
            # Build PDF with simple page numbering
            doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return None
    
    def _add_title_page(self, story, company_info, emissions_data):
        """Add title page to the report"""
        # Rolling Sphere Branding Header
        rolling_sphere_title = Paragraph(
            "<b>Rolling Sphere Technologies</b>", 
            ParagraphStyle(
                'RollingSphere',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=5,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#1f77b4')
            )
        )
        story.append(rolling_sphere_title)
        
        # Subtitle for Rolling Sphere
        rolling_sphere_subtitle = Paragraph(
            "Professional Environmental Analysis", 
            ParagraphStyle(
                'RollingSphereSubtitle',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=40,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#666666')
            )
        )
        story.append(rolling_sphere_subtitle)
        
        # Company name and report title
        story.append(Paragraph(f"{company_info.get('name', 'Company')} Carbon Footprint Report", self.title_style))
        story.append(Spacer(1, 30))
        
        # Report period
        story.append(Paragraph(f"Reporting Year: {company_info.get('year', 2024)}", self.subtitle_style))
        story.append(Spacer(1, 40))
        
        # Key metrics summary table
        total_emissions = emissions_data['summary']['total_co2_kg']
        total_tonnes = emissions_data['summary']['total_co2_tonnes']
        total_activities = emissions_data['summary']['total_activities']
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total CO2 Emissions\n(kg)', f'{total_emissions:,.2f}'],
            ['Total CO2 Emissions\n(tonnes)', f'{total_tonnes:.2f}'],
            ['Total Activities\nRecorded', str(total_activities)],
            ['Report Generated', self.report_timestamp.strftime('%Y-%m-%d')],
        ]
        
        if company_info.get('contact'):
            summary_data.append(['Contact Person', company_info['contact']])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 40))
        
        # Footer with Rolling Sphere
        footer_text = Paragraph(
            "<i>This report was generated by Rolling Sphere Technologies' CO2 Emissions Calculator</i><br/><i>© Rolling Sphere Technologies - Professional Environmental Analysis Solutions</i>",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#666666')
            )
        )
        story.append(footer_text)
        story.append(PageBreak())
    
    def _add_executive_summary(self, story, emissions_data):
        """Add enhanced executive summary section with dashboard"""
        # Keep title and content together
        executive_elements = []
        executive_elements.append(Paragraph("Executive Dashboard", self.title_style))
        executive_elements.append(Spacer(1, 20))
        
        total_emissions = emissions_data['summary']['total_co2_kg']
        total_tonnes = emissions_data['summary']['total_co2_tonnes']
        
        # Executive Dashboard with scope breakdown
        if 'by_scope' in emissions_data:
            scope_data = emissions_data['by_scope']
            scope1_kg = scope_data['scope_1']['total_kg']
            scope2_kg = scope_data['scope_2']['total_kg']
            scope3_kg = scope_data['scope_3']['total_kg']
            scope1_percent = (scope1_kg / total_emissions * 100) if total_emissions > 0 else 0
            scope2_percent = (scope2_kg / total_emissions * 100) if total_emissions > 0 else 0
            scope3_percent = (scope3_kg / total_emissions * 100) if total_emissions > 0 else 0
            
            # Enhanced dashboard table with scope indicators
            dashboard_data = [
                ['Overall Status', 'Value', 'Scope Breakdown'],
                [f'Total Emissions: {total_tonnes:.2f} tonnes CO2e', f'{total_emissions:,.2f} kg', f'SCOPE 1: {scope1_percent:.1f}% ({scope1_kg/1000:.2f}t)'],
                [f'Total Activities: {emissions_data["summary"]["total_activities"]}', f'{emissions_data["summary"]["unique_activity_types"]} activity types', f'SCOPE 2: {scope2_percent:.1f}% ({scope2_kg/1000:.2f}t)'],
                ['Report Status: COMPLETE', 'GHG Protocol Compliant', f'SCOPE 3: {scope3_percent:.1f}% ({scope3_kg/1000:.2f}t)']
            ]
        else:
            # Fallback dashboard without scope data
            dashboard_data = [
                ['Overall Status', 'Value', 'Details'],
                [f'Total Emissions: {total_tonnes:.2f} tonnes CO2e', f'{total_emissions:,.2f} kg', 'All scopes included'],
                [f'Total Activities: {emissions_data["summary"]["total_activities"]}', f'{emissions_data["summary"]["unique_activity_types"]} activity types', 'Multi-category analysis'],
                ['Report Status: COMPLETE', 'GHG Protocol Compliant', 'Professional analysis']
            ]
        
        dashboard_table = Table(dashboard_data, colWidths=[2.5*inch, 2*inch, 2.5*inch])
        dashboard_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f8ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        executive_elements.append(dashboard_table)
        executive_elements.append(Spacer(1, 20))
        
        summary_text = f"""
        This comprehensive carbon footprint analysis presents <b>{total_emissions:,.2f} kg CO2 equivalent 
        ({total_tonnes:.2f} tonnes CO2e)</b> total emissions calculated using official government emission factors.
        <br/><br/>
        The analysis covers {emissions_data['summary']['total_activities']} activities across 
        {emissions_data['summary']['unique_activity_types']} categories, providing complete GHG Protocol compliance 
        with Scope 1, 2, and 3 classification.
        """
        
        executive_elements.append(Paragraph(summary_text, self.styles['Normal']))
        executive_elements.append(Spacer(1, 30))
        
        # Keep executive summary title and content together
        story.append(KeepTogether(executive_elements))
    
    def _add_emissions_breakdown(self, story, emissions_data):
        """Add emissions breakdown by activity type"""
        # Create table data with properly formatted headers
        breakdown_data = [['Activity Type', 'CO2 Emissions\n(kg)', 'CO2 Emissions\n(tonnes)', 'Percentage']]
        
        total_emissions = emissions_data['summary']['total_co2_kg']
        
        for activity_type, emissions in emissions_data['by_activity'].items():
            percentage = (emissions / total_emissions) * 100 if total_emissions > 0 else 0
            # Format activity type with text wrapping for better cell fit
            formatted_activity = self._wrap_text(activity_type.replace('_', ' ').title(), max_width=18)
            breakdown_data.append([
                formatted_activity,
                f'{emissions:,.2f}',
                f'{emissions/1000:.2f}',
                f'{percentage:.1f}%'
            ])
        
        breakdown_table = Table(breakdown_data, colWidths=[2.2*inch, 1.4*inch, 1.4*inch, 1*inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('WORDWRAP', (0, 0), (-1, -1), 'LTR'),
        ]))
        
        # Keep the title and table together to prevent page splitting
        breakdown_elements = [
            Paragraph("Emissions Breakdown by Activity Type", self.subtitle_style),
            Spacer(1, 10),
            breakdown_table
        ]
        story.append(KeepTogether(breakdown_elements))
        story.append(Spacer(1, 15))
        
        # Create pie chart for emissions by activity type
        if emissions_data['by_activity']:
            # Prepare elements to keep together: title and chart
            visual_analysis_elements = []
            visual_analysis_elements.append(Paragraph("Visual Analysis", self.subtitle_style))
            visual_analysis_elements.append(Spacer(1, 5))
            
            drawing = Drawing(400, 250)
            pie = Pie()
            pie.x = 100
            pie.y = 25
            pie.width = 180
            pie.height = 180
            
            # Prepare data for pie chart
            labels = list(emissions_data['by_activity'].keys())
            values = list(emissions_data['by_activity'].values())
            
            pie.data = values
            
            # Create shorter, non-overlapping labels
            short_labels = []
            for label in labels:
                short_label = label.replace('_', ' ').title()
                # Truncate long labels to prevent overlap
                if len(short_label) > 10:
                    short_label = short_label[:10] + ".."
                short_labels.append(short_label)
            
            pie.labels = short_labels
            
            # Position labels outside the pie to avoid overlap
            pie.pointerLabelMode = 'LeftAndRight'
            pie.sameRadii = True
            pie.simpleLabels = 0
            
            # Set colors for each slice
            colors_list = [colors.HexColor('#4CAF50'), colors.HexColor('#8BC34A'), 
                          colors.HexColor('#CDDC39'), colors.HexColor('#FFC107'),
                          colors.HexColor('#FF9800'), colors.HexColor('#FF5722')]
            
            # Set basic styling
            pie.strokeWidth = 1
            
            drawing.add(pie)
            visual_analysis_elements.append(drawing)
            
            # Keep the title and chart together on the same page
            story.append(KeepTogether(visual_analysis_elements))
            story.append(Spacer(1, 20))
    
    def _add_scope_analysis(self, story, emissions_data):
        """Add enhanced GHG Protocol Scope Analysis section with recommendations"""
        # Keep title and initial content together
        scope_elements = []
        scope_elements.append(Paragraph("Enhanced GHG Protocol Scope Analysis", self.title_style))
        scope_elements.append(Spacer(1, 20))
        
        # Check if scope data exists
        if 'by_scope' not in emissions_data:
            scope_elements.append(Paragraph("Scope data not available", self.styles['Normal']))
            scope_elements.append(Spacer(1, 30))
            story.append(KeepTogether(scope_elements))
            return
        
        scope_data = emissions_data['by_scope']
        total_emissions = emissions_data['summary']['total_co2_kg']
        
        # Create scope breakdown table
        scope_table_data = [['GHG Scope', 'Description', 'CO2 Emissions\n(kg)', 'CO2 Emissions\n(tonnes)', 'Percentage', 'Main Activities']]
        
        # Scope 1 - Direct Emissions
        scope1_kg = scope_data['scope_1']['total_kg']
        scope1_tonnes = scope1_kg / 1000
        scope1_percent = (scope1_kg / total_emissions * 100) if total_emissions > 0 else 0
        # Dynamic text handling for activities - wrap and truncate based on content
        scope1_activities = self._format_activities_text(scope_data['scope_1']['activities'], max_width=35)
        
        scope_table_data.append([
            'SCOPE 1\n(Direct)',
            'Direct emissions from\nowned/controlled sources',
            f'{scope1_kg:,.2f}',
            f'{scope1_tonnes:.2f}',
            f'{scope1_percent:.1f}%',
            scope1_activities or 'None'
        ])
        
        # Scope 2 - Energy Emissions  
        scope2_kg = scope_data['scope_2']['total_kg']
        scope2_tonnes = scope2_kg / 1000
        scope2_percent = (scope2_kg / total_emissions * 100) if total_emissions > 0 else 0
        scope2_activities = self._format_activities_text(scope_data['scope_2']['activities'], max_width=35)
        
        scope_table_data.append([
            'SCOPE 2\n(Energy)',
            'Indirect emissions from\npurchased energy',
            f'{scope2_kg:,.2f}',
            f'{scope2_tonnes:.2f}',
            f'{scope2_percent:.1f}%',
            scope2_activities or 'None'
        ])
        
        # Scope 3 - Other Indirect Emissions
        scope3_kg = scope_data['scope_3']['total_kg']
        scope3_tonnes = scope3_kg / 1000
        scope3_percent = (scope3_kg / total_emissions * 100) if total_emissions > 0 else 0
        scope3_activities = self._format_activities_text(scope_data['scope_3']['activities'], max_width=35)
        
        scope_table_data.append([
            'SCOPE 3\n(Indirect)',
            'Other indirect emissions\nfrom value chain',
            f'{scope3_kg:,.2f}',
            f'{scope3_tonnes:.2f}',
            f'{scope3_percent:.1f}%',
            scope3_activities or 'None'
        ])
        
        # Create and style the scope table
        # Dynamic column widths based on content length
        scope_table = Table(scope_table_data, colWidths=[0.8*inch, 1.2*inch, 0.9*inch, 0.9*inch, 0.7*inch, 2.8*inch])
        scope_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#E8F5E8')),  # Scope 1 light green
            ('BACKGROUND', (0, 2), (0, 2), colors.HexColor('#E3F2FD')),  # Scope 2 light blue
            ('BACKGROUND', (0, 3), (0, 3), colors.HexColor('#FFF3E0')),  # Scope 3 light orange
            ('BACKGROUND', (1, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
            ('ALIGN', (5, 1), (5, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('WORDWRAP', (0, 0), (-1, -1), 'LTR'),
        ]))
        
        # Add table to scope elements
        scope_elements.append(scope_table)
        scope_elements.append(Spacer(1, 20))
        
        # Keep the entire scope analysis together
        story.append(KeepTogether(scope_elements))
        
        # Add scope-specific recommendations based on data
        recommendations_elements = []
        recommendations_elements.append(Paragraph("Scope-Specific Recommendations", self.header_style))
        recommendations_elements.append(Spacer(1, 10))
        
        scope_recs = []
        
        if scope1_kg > 0:
            scope_recs.append(f"<b>SCOPE 1 ({scope1_tonnes:.2f}t):</b> Focus on direct emission sources: {scope1_activities}. Consider equipment upgrades and operational efficiency improvements.")
        else:
            scope_recs.append("<b>SCOPE 1:</b> No direct emissions detected - excellent performance.")
        
        if scope2_kg > 0:
            scope_recs.append(f"<b>SCOPE 2 ({scope2_tonnes:.2f}t):</b> Energy-related emissions from: {scope2_activities}. Consider renewable energy sources and efficiency measures.")
        else:
            scope_recs.append("<b>SCOPE 2:</b> No energy emissions detected - excellent renewable energy use.")
        
        if scope3_kg > 0:
            scope_recs.append(f"<b>SCOPE 3 ({scope3_tonnes:.2f}t):</b> Value chain emissions from: {scope3_activities}. Consider supply chain optimization and process improvements.")
        else:
            scope_recs.append("<b>SCOPE 3:</b> No indirect emissions detected.")
        
        for rec in scope_recs:
            recommendations_elements.append(Paragraph(rec, self.styles['Normal']))
            recommendations_elements.append(Spacer(1, 8))
        
        recommendations_elements.append(Spacer(1, 15))
        
        # Keep recommendations title and content together
        story.append(KeepTogether(recommendations_elements))
        
        # Add methodology section
        methodology_text = """
        <b>Calculation Methodology:</b> This analysis uses official emission factors from UK Government GHG 
        Conversion Factors 2023, EPA Emission Factors for GHG Inventories, and IPCC Guidelines for National 
        GHG Inventories. All calculations follow GHG Protocol standards for organizational carbon accounting.
        """
        # Keep methodology with recommendations in a separate block
        methodology_elements = []
        methodology_elements.append(Paragraph(methodology_text, self.styles['Normal']))
        methodology_elements.append(Spacer(1, 30))
        story.append(KeepTogether(methodology_elements))
    
    def _add_visualizations(self, story, emissions_data):
        """Add charts and visualizations - this method is now integrated into breakdown"""
        pass  # Content moved to breakdown section to keep title and chart together
    
    def _add_detailed_breakdown(self, story, emissions_data):
        """Add detailed breakdown table"""
        story.append(PageBreak())
        
        # Create detailed table
        detailed_data = [['Activity Type', 'Category', 'Amount', 'Unit', 'Emission\nFactor', 'CO2 Emissions\n(kg)']]
        
        for item in emissions_data['detailed_results'][:20]:  # Limit to first 20 items to fit on page
            detailed_data.append([
                item['activity_type'].replace('_', ' ').title(),
                item['category'].replace('_', ' ').title(),
                f"{item['amount']:,.2f}",
                item['unit'],
                f"{item['emission_factor']:.4f}",
                f"{item['co2_emissions_kg']:,.2f}"
            ])
        
        if len(emissions_data['detailed_results']) > 20:
            detailed_data.append(['...', '...', '...', '...', '...', '...'])
            detailed_data.append(['', '', '', '', 'Total:', f"{emissions_data['summary']['total_co2_kg']:,.2f}"])
        
        detailed_table = Table(detailed_data, colWidths=[1.1*inch, 1*inch, 0.7*inch, 0.5*inch, 0.8*inch, 1.3*inch])
        detailed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('WORDWRAP', (0, 0), (-1, -1), 'LTR'),
        ]))
        
        # Keep the detailed table together to prevent page splitting
        detailed_elements = [
            Paragraph("Detailed Emissions Data", self.subtitle_style),
            Spacer(1, 10),
            detailed_table
        ]
        story.append(KeepTogether(detailed_elements))
        story.append(Spacer(1, 30))
    
    def _add_recommendations(self, story, emissions_data):
        """Add recommendations section"""
        story.append(PageBreak())
        
        # Keep title and content together
        recommendations_elements = []
        recommendations_elements.append(Paragraph("Specific Action Recommendations", self.subtitle_style))
        recommendations_elements.append(Spacer(1, 20))
        
        intro_text = """
        <b>High-Impact Actions Based on Your Actual Data:</b>
        """
        recommendations_elements.append(Paragraph(intro_text, self.styles['Normal']))
        recommendations_elements.append(Spacer(1, 15))
        
        # Generate data-driven recommendations
        if emissions_data.get('by_activity'):
            # Sort activities by emissions (highest first)
            sorted_activities = sorted(emissions_data['by_activity'].items(), key=lambda x: x[1], reverse=True)
            total_emissions = emissions_data['summary']['total_co2_kg']
            
            for i, (activity_type, emissions_kg) in enumerate(sorted_activities[:5], 1):  # Top 5 activities
                activity_name = activity_type.replace('_', ' ').title()
                emissions_tonnes = emissions_kg / 1000
                percentage = (emissions_kg / total_emissions) * 100
                
                rec_text = f"<b>{i}. Focus on {activity_name}</b> - Currently {emissions_tonnes:.2f} tonnes CO2e ({percentage:.1f}% of total emissions). This represents your highest impact opportunity for reduction."
                recommendations_elements.append(Paragraph(rec_text, self.styles['Normal']))
                recommendations_elements.append(Spacer(1, 8))
        else:
            # Fallback generic recommendations if no activity data
            generic_recs = [
                "Conduct energy efficiency audit for immediate impact opportunities",
                "Implement monitoring systems to track emissions by activity type",
                "Set science-based emission reduction targets aligned with company goals",
                "Engage suppliers in sustainability initiatives for Scope 3 reductions"
            ]
            
            for i, rec in enumerate(generic_recs, 1):
                rec_text = f"<b>{i}.</b> {rec}"
                recommendations_elements.append(Paragraph(rec_text, self.styles['Normal']))
                recommendations_elements.append(Spacer(1, 8))
        
        recommendations_elements.append(Spacer(1, 20))
        
        additional_text = """
        <b>Implementation Strategy:</b><br/>
        1. Prioritize actions based on emissions impact and cost-effectiveness<br/>
        2. Set specific, measurable targets for top emission activities<br/>
        3. Implement regular monitoring using the same calculation methodology<br/>
        4. Consider professional verification for carbon accounting accuracy<br/>
        5. Develop comprehensive sustainability policy based on this analysis
        """
        recommendations_elements.append(Paragraph(additional_text, self.styles['Normal']))
        
        # Keep all recommendations content together
        story.append(KeepTogether(recommendations_elements))
    
    def _add_footer_info(self, story, emissions_data):
        """Add enhanced professional footer with methodology details"""
        story.append(PageBreak())
        
        # Keep footer title and content together
        footer_elements = []
        footer_elements.append(Spacer(1, 30))
        footer_elements.append(Paragraph("Professional Environmental Analysis Report", self.title_style))
        footer_elements.append(Spacer(1, 20))
        
        # Data sources and methodology
        methodology_data = [
            ['Data Sources & Standards', 'Verification Status'],
            ['UK Government GHG Conversion Factors 2023', '✓ Official Government Source'],
            ['EPA Emission Factors for GHG Inventories', '✓ US Environmental Protection Agency'],
            ['IPCC Guidelines for National GHG Inventories', '✓ International Panel on Climate Change'],
            ['GHG Protocol Scope Classification', '✓ World Resources Institute Standard']
        ]
        
        methodology_table = Table(methodology_data, colWidths=[3.5*inch, 2.5*inch])
        methodology_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f8ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        footer_elements.append(methodology_table)
        footer_elements.append(Spacer(1, 30))
        
        # Professional footer with company information
        current_date = self.report_timestamp
        
        footer_info_data = [
            ['Report Generated', 'Contact Information'],
            [f'{current_date.strftime("%Y-%m-%d %H:%M")}', 'rollingsphere.project@gmail.com'],
            [f'Data Quality: {emissions_data["summary"]["total_activities"]} activities analyzed', 'Rolling Sphere Technologies'],
            ['Professional Environmental Analysis', 'Official Emission Factor Sources']
        ]
        
        footer_table = Table(footer_info_data, colWidths=[3*inch, 3*inch])
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4dabf7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e3f2fd')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        footer_elements.append(footer_table)
        footer_elements.append(Spacer(1, 20))
        
        disclaimer_text = """
        <b>Professional Disclaimer:</b> This carbon footprint analysis is based on official government 
        emission factors and internationally recognized calculation methodologies. All data sources are 
        verified and current. Results provide accurate baseline measurements for sustainability planning 
        and compliance reporting. This report maintains 100% data integrity using only legitimate 
        emission factor databases.
        """
        footer_elements.append(Paragraph(disclaimer_text, self.styles['Normal']))
        
        # Keep all footer content together
        story.append(KeepTogether(footer_elements))
