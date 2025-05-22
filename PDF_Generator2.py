from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import json
import re
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from plot_generator import generate_radar_chart

# Set up font styles using built-in Helvetica fonts
styles = getSampleStyleSheet()
styles['BodyText'].fontName = 'Helvetica'

# Attempt to register Arial fonts, fall back to Helvetica if unavailable
try:
    if os.path.exists('/Library/Fonts/Arial.ttf') and os.path.exists('/Library/Fonts/Arial Bold.ttf'):
        pdfmetrics.registerFont(TTFont('Arial', '/Library/Fonts/Arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', '/Library/Fonts/Arial Bold.ttf'))
        styles['BodyText'].fontName = 'Arial'
        print("Using Arial fonts.")
    else:
        print("Arial fonts not found at /Library/Fonts/. Using Helvetica fonts.")
except Exception as e:
    print(f"Error registering Arial fonts, using Helvetica: {e}")

def create_combined_pdf(logo_path, json_path):
    # Normalize paths for cross-platform compatibility
    logo_path = logo_path.replace('\\', '/')
    json_path = json_path.replace('\\', '/')

    # Load presentation.json
    try:
        with open("json/presentation.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Error: 'json/presentation.json' not found.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in 'json/presentation.json'.")
        return

    presentation_mode = data.get("presentation_mode", False)
    if isinstance(presentation_mode, str):
        presentation_mode = presentation_mode.lower() == 'on'

    # Load tabular data
    try:
        with open(json_path, 'r') as fp:
            tabular_data = json.load(fp)
    except FileNotFoundError:
        print(f"Error: '{json_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{json_path}'.")
        return

    # Define questions based on presentation mode
    if presentation_mode:
        llm_questions = [
            "Questions",
            "Did the Speaker Speak with Confidence ?",
            "Did the speaker vary their tone, speed, volume while delivering the speech/presentation? ",
            "Did the speech have a structure of Opening, Body and Conclusion? ",
            "Was the overall “Objective” of the speech delivered clearly?",
            "Was the content of the presentation/speech brief and to the point, or did it include unnecessary details that may have distracted or confused the audience?",
            "Was the content of the presentation/speech engaging, and did it capture the audience’s attention?",
            "Was the content of the presentation/speech relevant to the objective of the presentation?",
            "Was the content of the presentation/speech clear and easy to understand?",
            "Did the speaker add relevant examples, anecdotes and data to back their content?",
            "Did the speaker demonstrate credibility? Will you trust the speaker?",
            "Did the speaker clearly explain how the speech or topic would benefit you and what you could gain from it?",
            "Was the speaker able to evoke an emotional connection with the audience?",
            "Overall, were you convinced/ persuaded with the speaker’s view on the topic?"
        ]
    else:
        llm_questions = [
            "Questions",
            "Did the Speaker Speak with Confidence ?",
            "Was the content interesting and as per the guidelines provided?",
            "Who are you and what are your skills, expertise, and personality traits?",
            "Why are you the best person to fit this role?",
            "How are you different from others?",
            "What value do you bring to the role?",
            "Did the speech have a structure of Opening, Body, and Conclusion?",
            "Did the speaker vary their tone, speed, and volume while delivering the speech/presentation?",
            "How was the quality of research for the topic? Did the speech demonstrate good depth? Did they cite sources?",
            "How convinced were you with the overall speech on the topic? Was it persuasive? Will you consider them for the job/opportunity?"
        ]

    def clean_answer(answer):
        return re.sub(r'^\d+\.\s*', '', answer).strip()

    llm_answers = []
    if 'LLM' in tabular_data:
        llm_answers = re.split(r'\n(?=\d+\.)', tabular_data['LLM'])

    # Initialize PDF document
    doc = SimpleDocTemplate("reports/combined_report.pdf",
                            pagesize=letter,
                            topMargin=1.5*inch,
                            bottomMargin=0.8*inch)
    flowables = []

    def add_header_footer(canvas, doc):
        canvas.saveState()
        try:
            logo = Image(logo_path, width=2*inch, height=1*inch)
            logo.drawOn(canvas, (letter[0]-2*inch)/2, letter[1]-1.2*inch)
        except Exception as e:
            print(f"Error loading logo: {e}")
        website_text = "https://some.education.in"
        canvas.setFont("Helvetica", 9)
        canvas.linkURL("https://some.education.in",
                       (0.5*inch, 0.3*inch, 2.5*inch, 0.5*inch),
                       relative=1)
        canvas.drawString(0.5*inch, 0.3*inch, website_text)
        page_num = canvas.getPageNumber()
        canvas.drawRightString(letter[0]-0.5*inch, 0.3*inch, f"Page {page_num}")
        canvas.restoreState()

    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['BodyText'],
        fontName='Helvetica-Bold',
        fontSize=10,
        spaceAfter=12,
        leading=16
    )
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        spaceAfter=6,
        leftIndent=10
    )

    # Add title and date
    name = tabular_data.get('User Name', 'Unknown Candidate')
    now = datetime.now()
    formatted_date = now.strftime("%d %B %Y")
    title = Paragraph(
        f"<para alignment='center'><b>{name}</b><br/></para>"
        f"<para alignment='center'>{formatted_date}</para>",
        styles['Title']
    )

    # Add radar chart
    try:
        generate_radar_chart("output.png")
        if not os.path.exists("output.png"):
            raise FileNotFoundError("Radar chart image 'output.png' was not generated.")
        chart_img = Image('output.png', width=6*inch, height=3*inch)
        flowables.append(title)
        flowables.append(Spacer(1, 24))
        flowables.append(Paragraph("Overall Evaluation Summary", section_style))
        flowables.append(chart_img)
        flowables.append(Spacer(1, 18))
    except Exception as e:
        print(f"Error generating radar chart: {e}")
        flowables.append(title)
        flowables.append(Spacer(1, 24))
        flowables.append(Paragraph("Overall Evaluation Summary (Chart unavailable)", section_style))
        flowables.append(Spacer(1, 18))

    def add_quality_section(title, items):
        flowables.append(Paragraph(title, section_style))
        bullet_list = []
        for item in items:
            bullet_list.append(Paragraph(f"• {item}", bullet_style))
        flowables.extend(bullet_list)
        flowables.append(Spacer(1, 18))

    # Add quality analysis
    try:
        with open('json/quality_analysis.json', 'r') as fp:
            quality_data = json.load(fp)
        add_quality_section("Qualitative Analysis - Positive", quality_data.get("Qualitative Analysis", []))
        add_quality_section("Qualitative Analysis - Areas of Improvement", quality_data.get("Quantitative Analysis", []))
    except FileNotFoundError:
        print("Warning: 'json/quality_analysis.json' not found. Skipping quality analysis section.")
    except json.JSONDecodeError:
        print("Warning: Invalid JSON in 'json/quality_analysis.json'. Skipping quality analysis section.")

    flowables.append(Spacer(1, 18))
    flowables.append(PageBreak())

    # Detailed Evaluation Metrics
    section_style = ParagraphStyle('SectionStyle', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=10, spaceAfter=12, leading=16)
    flowables.append(Paragraph("<b>Detailed Evaluation Metrics</b>", section_style))
    flowables.append(Spacer(1, 24))

    normal_style = ParagraphStyle('NormalStyle', parent=styles['BodyText'], fontSize=10, leading=12, spaceAfter=6)
    bold_style = ParagraphStyle('BoldStyle', parent=normal_style, fontName='Helvetica-Bold')

    table_data = [
        [
            Paragraph("<b>No.</b>", bold_style),
            Paragraph("<b>Items to look out for</b>", bold_style),
            Paragraph("<b>5 point scale / Answer</b>", bold_style)
        ]
    ]

    for i, question in enumerate(llm_questions[1:], 1):
        if i == 1:
            sub_items = [
                ("Posture", "posture"),
                ("Smile", "Smile Score"),
                ("Eye Contact", "Eye Contact"),
                ("Energetic Start", "Energetic Start")
            ]
            items_text = "Did the speaker speak with confidence?<br/>" + "<br/>".join([f"• {item[0]}" for item in sub_items])
            scores = []
            for item in sub_items:
                key = item[1]
                metric_value = tabular_data.get(key)
                if metric_value == 1:
                    scores.append("Needs Improvement")
                elif metric_value == 2:
                    scores.append("Poor")
                elif metric_value == 3:
                    scores.append("Satisfactory")
                elif metric_value == 4:
                    scores.append("Good")
                elif metric_value == 5:
                    scores.append("Excellent")
                else:
                    scores.append("N/A")
            scores_text = "<br/>" + "<br/>".join([f"<b>{score}</b>" for score in scores])
            table_data.append([
                Paragraph(f"{i}.", normal_style),
                Paragraph(items_text, normal_style),
                Paragraph(scores_text, normal_style)
            ])
        else:
            answer_index = i - 1 if i - 1 < len(llm_answers) else None
            if answer_index is not None:
                answer = clean_answer(llm_answers[answer_index])
            else:
                answer = "N/A"
            table_data.append([
                Paragraph(f"{i}.", normal_style),
                Paragraph(question, normal_style),
                Paragraph(answer, normal_style)
            ])

    table = Table(table_data, colWidths=[40, 300, 200])
    table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    flowables.append(table)

    # Build the PDF
    try:
        doc.build(flowables,
                  onFirstPage=add_header_footer,
                  onLaterPages=add_header_footer)
        print("PDF generated successfully with dynamic table!")
    except Exception as e:
        print(f"Error generating PDF: {e}")

    # Clean up temporary radar chart file
    try:
        if os.path.exists("output.png"):
            os.remove("output.png")
            print("Removed temporary file: output.png")
    except Exception as e:
        print(f"Error removing temporary file: {e}")

if __name__ == "__main__":
    create_combined_pdf(os.path.join("logos", "logo.png"), os.path.join("json", "output.json"))