import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import re

# Page configuration with custom theme
st.set_page_config(
    page_title="ResumeAI - Smart ATS Analyzer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with dark theme and no empty white boxes
st.markdown("""
<style>
    /* Main theme styles */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        font-weight: 400;
        color: #94A3B8;
        margin-bottom: 2rem;
    }
    .result-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #F8FAFC;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #334155;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #F8FAFC;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        padding: 0.5rem 0;
        border-bottom: 1px solid #334155;
    }
    .percentage-match {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .highlight {
        background-color: #1E40AF;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: 500;
    }
    .card {
        background-color: #1E293B;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #334155;
    }
    .empty-notice {
        color: #94A3B8;
        font-style: italic;
        padding: 0.5rem 0;
    }
    .success {color: #10B981;}
    .warning {color: #F59E0B;}
    .danger {color: #EF4444;}
    .stButton button {
        background-color: #3B82F6;
        color: white;
        font-weight: 600;
        border-radius: 0.3rem;
        padding: 0.5rem 2rem;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #2563EB;
        border-color: #2563EB;
    }
    
    /* Override default Streamlit theme */
    .stApp {
        background-color: #0F172A;
        color: #E2E8F0;
    }
    .stTextArea textarea, .stFileUploader {
        background-color: #1E293B;
        color: #E2E8F0;
        border: 1px solid #334155;
        border-radius: 0.5rem;
    }
    header {
        background-color: transparent !important;
    }
    .css-18e3th9 {
        padding-top: 2rem;
    }
    
    /* Remove default content area border/padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0;
        max-width: 95%;
    }
    
    /* Handle empty sections */
    .empty-section {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Configure Gemini API
try:
    genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])
except:
    # Fallback to local .env file
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def get_gemini_response(input):
    """Get response from Gemini model"""
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(input)
        return response.text
    except Exception as e:
        return f"Error in generating response: {str(e)}"

def input_pdf_text(uploaded_file):
    """Extract text from uploaded PDF file"""
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    n_pages = len(reader.pages)
    
    with st.spinner(f"Extracting text from {n_pages} pages..."):
        for page in range(n_pages):
            p = reader.pages[page]
            text = text + '\n' + str(p.extract_text())
    return text

def display_match_score(score_text):
    """Display the match score with appropriate color coding"""
    try:
        score = int(score_text.strip('%'))
        if score >= 80:
            color = "success"
        elif score >= 60:
            color = "warning"
        else:
            color = "danger"
        
        st.markdown(f'<div class="percentage-match {color}">{score_text}</div>', unsafe_allow_html=True)
    except:
        st.markdown(f'<div class="percentage-match">{score_text}</div>', unsafe_allow_html=True)

def clean_section_content(content):
    """Clean and format section content"""
    if not content or content.strip() == "":
        return None
    
    # Replace markdown lists with HTML lists for better formatting
    content = re.sub(r'^\s*-\s+(.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    if re.search(r'<li>', content):
        content = f"<ul>{content}</ul>"
    
    # Add highlighting to important terms
    keywords = ['missing', 'weak', 'strong', 'excellent', 'poor', 'good', 'improve']
    for keyword in keywords:
        content = re.sub(r'\b' + keyword + r'\b', f'<span class="highlight">{keyword}</span>', content, flags=re.IGNORECASE)
    
    return content

# App Header
st.markdown('<div class="main-header">ResumeAI - Smart ATS Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Optimize your resume for Applicant Tracking Systems and increase your chances of landing an interview</div>', unsafe_allow_html=True)

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">Step 1: Upload Your Resume</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="Resume Upload", 
        type='pdf', 
        help='Please upload Resume in PDF format',
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        st.success(f"Successfully uploaded: {uploaded_file.name}")

with col2:
    st.markdown('<div class="section-header">Step 2: Enter Job Description</div>', unsafe_allow_html=True)
    jd = st.text_area(
        label="Job Description", 
        height=250, 
        placeholder="Paste the complete job description here...",
        label_visibility="collapsed"
    )

# Analyze button
analyze_col1, analyze_col2, analyze_col3 = st.columns([2,3,2])
with analyze_col2:
    submit = st.button("Analyze Resume")

# Results section
if submit:
    if uploaded_file is not None and jd.strip():
        with st.spinner("Analyzing your resume against the job description... This may take a minute."):
            # Get the text from file
            text = input_pdf_text(uploaded_file)
            inputs = {"Resume": [text], "Job Description": [jd]}
            
            # Prompt Template
            input_prompt = f"""
            Act as a senior ATS (Applicant Tracking System) specialist with extensive experience in tech fields including 
            software engineering, data science, data analysis, and big data engineering.
            
            Evaluate the resume against the given job description, considering the competitive job market.
            Provide detailed analysis to help improve the resume's effectiveness.
            
            Below is the input dictionary containing the Resume and Job Description content:
            {str(inputs)}
            
            Provide analysis in the following structure, with ONLY these exact 9 sections:
            
            PERCENTAGE MATCH: Provide a single percentage score (e.g., 75%) representing how well the resume matches the job description.
            
            MISSING & WEAK KEYWORDS: List specific industry keywords that are missing or underrepresented in the resume.
            
            SKILLS ALIGNMENT: Categorize and analyze alignment of Technical Skills, Soft Skills, and Tools & Technologies.
            
            EXPERIENCE & ROLE SUITABILITY: Evaluate job title relevance, experience level match, and impact metrics.
            
            ATS-FRIENDLY FORMATTING: Assess structure, bullet points, readability, and formatting issues.
            
            EDUCATION & CERTIFICATIONS: Analyze qualification match and identify any certification gaps.
            
            ACTION WORDS & STRENGTH: Identify weak phrases, passive voice, and suggest stronger alternatives.
            
            CAREER INSIGHTS: Suggest alternative job roles, salary benchmarks, and growth opportunities.
            
            RESUME SUMMARY: Provide 5-7 bullet points summarizing the key elements of the RESUME ONLY.
            
            IMPORTANT: Format each section title in bold with a colon. Keep sections clearly separated.
            IMPORTANT: Don't leave any section empty. Provide comprehensive information for each section.
            """
            
            # Get Gemini response
            response = get_gemini_response(input_prompt)
            
            # Display results in a structured way
            st.markdown('<div class="result-header">Resume Analysis Results</div>', unsafe_allow_html=True)
            
            # Process the response to extract sections
            section_mapping = {
                "PERCENTAGE MATCH:": "ATS Score",
                "MISSING & WEAK KEYWORDS:": "Missing & Weak Keywords",
                "SKILLS ALIGNMENT:": "Skills Alignment",
                "EXPERIENCE & ROLE SUITABILITY:": "Experience & Role Suitability",
                "ATS-FRIENDLY FORMATTING:": "ATS-Friendly Formatting",
                "EDUCATION & CERTIFICATIONS:": "Education & Certifications",
                "ACTION WORDS & STRENGTH:": "Action Words & Resume Strength",
                "CAREER INSIGHTS:": "Career Insights",
                "RESUME SUMMARY:": "Resume Summary"
            }
            
            # Split into sections with regex to better handle multi-paragraph content
            pattern = r'({})\s*(.+?)(?={}|$)'.format(
                '|'.join(map(re.escape, section_mapping.keys())),
                '|'.join(map(re.escape, section_mapping.keys()))
            )
            matches = re.findall(pattern, response, re.DOTALL)
            
            # Create a dictionary to store section content
            sections_data = {}
            for section_title, content in matches:
                clean_title = section_title.strip()
                clean_content = content.strip()
                sections_data[clean_title] = clean_content
            
            # Display each section with proper formatting
            for api_section, display_name in section_mapping.items():
                content = sections_data.get(api_section, "")
                formatted_content = clean_section_content(content)
                
                if formatted_content:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="section-header">{display_name}</div>', unsafe_allow_html=True)
                    
                    if api_section == "PERCENTAGE MATCH:":
                        display_match_score(content)
                    else:
                        st.markdown(formatted_content, unsafe_allow_html=True)
                        
                    st.markdown('</div>', unsafe_allow_html=True)
    
    elif not uploaded_file:
        st.error("Please upload your resume first.")
    elif not jd.strip():
        st.error("Please enter the job description.")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #334155; color: #94A3B8; font-size: 0.8rem;">
    ResumeAI - Helping you land your dream job with AI-powered resume optimization
</div>
""", unsafe_allow_html=True)