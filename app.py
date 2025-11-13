import streamlit as st
import json
import os
from datetime import datetime
import PyPDF2
import io

# Page configuration
st.set_page_config(
    page_title="AI Research Paper Analyzer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'papers' not in st.session_state:
    st.session_state.papers = []
if 'comparison_result' not in st.session_state:
    st.session_state.comparison_result = None

# Helper function to extract text from PDF
def extract_pdf_text(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text[:5000]  # First 5000 chars
    except:
        return "Error extracting PDF text"

# Mock AI analysis function (replace with actual API call)
def analyze_paper(title, text):
    return {
        "id": len(st.session_state.papers) + 1,
        "title": title,
        "authors": ["Author 1", "Author 2"],
        "abstract": text[:500] if text else "No abstract available",
        "year": 2024,
        "executive_summary": f"This paper on '{title}' presents comprehensive research findings.",
        "key_findings": [
            "Key finding 1",
            "Key finding 2",
            "Key finding 3"
        ],
        "methodology": "Experimental and analytical methods were employed.",
        "sections": [
            {"title": "Introduction", "summary": "Background and motivation"},
            {"title": "Methods", "summary": "Research methodology"},
            {"title": "Results", "summary": "Key findings and data"},
            {"title": "Discussion", "summary": "Analysis and implications"}
        ],
        "keywords": ["AI", "Research", "Analysis"],
        "category": "Computer Science",
        "status": "completed"
    }

# Mock comparison function
def compare_papers(selected_papers):
    return {
        "papers": selected_papers,
        "analysis": {
            "common_themes": ["Artificial Intelligence", "Machine Learning", "Data Analysis"],
            "agreements": [
                {
                    "title": "ML Performance Benefits",
                    "description": "All papers agree that machine learning improves performance.",
                    "papers": [p["title"] for p in selected_papers]
                }
            ],
            "contradictions": [
                {
                    "title": "Optimal Model Size",
                    "description": "Papers disagree on optimal model architecture.",
                    "conflicting_views": [
                        "Paper A suggests larger models",
                        "Paper B advocates for smaller, efficient models"
                    ]
                }
            ],
            "research_gaps": [
                {
                    "gap": "Limited real-world deployment studies",
                    "potential_impact": "Understanding practical implementation challenges"
                }
            ],
            "unique_contributions": [
                {"paper": p["title"], "contribution": f"Novel approach in {p['category']}"}  
                for p in selected_papers
            ]
        }
    }

# Sidebar navigation
st.sidebar.title("📚 ResearchAI")
page = st.sidebar.radio("Navigate", ["Library", "Upload Paper", "Compare Papers"])

# ===== LIBRARY PAGE =====
if page == "Library":
    st.title("📚 Research Library")
    
    if not st.session_state.papers:
        st.info("No research papers uploaded yet. Go to 'Upload Paper' to add papers.")
    else:
        # Stats overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Papers", len(st.session_state.papers))
        with col2:
            completed = sum(1 for p in st.session_state.papers if p["status"] == "completed")
            st.metric("Analyzed", completed)
        with col3:
            categories = set(p.get("category", "Other") for p in st.session_state.papers)
            st.metric("Categories", len(categories))
        
        st.divider()
        
        # Display papers
        for paper in st.session_state.papers:
            with st.expander(f"📄 {paper['title']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if paper.get('authors'):
                        st.write(f"**Authors:** {', '.join(paper['authors'])}")
                    if paper.get('year'):
                        st.write(f"**Year:** {paper['year']}")
                    if paper.get('category'):
                        st.badge(paper['category'])
                
                with col2:
                    if paper['status'] == 'completed':
                        st.success("✓ Analyzed")
                    else:
                        st.warning("⟳ Processing")
                
                if paper.get('executive_summary'):
                    st.write("**Executive Summary:**")
                    st.write(paper['executive_summary'])
                
                if paper.get('key_findings'):
                    st.write("**Key Findings:**")
                    for finding in paper['key_findings']:
                        st.write(f"• {finding}")
                
                if paper.get('sections'):
                    st.write("**Sections:**")
                    for section in paper['sections']:
                        st.write(f"**{section['title']}:** {section['summary']}")

# ===== UPLOAD PAGE =====
elif page == "Upload Paper":
    st.title("📤 Upload Research Papers")
    
    st.write("Upload your research papers (PDF format) for AI-powered analysis.")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("🔍 Analyze Papers", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Processing {file.name}...")
                
                # Extract PDF text
                pdf_text = extract_pdf_text(file)
                
                # Analyze paper
                paper_data = analyze_paper(file.name.replace('.pdf', ''), pdf_text)
                
                # Add to session state
                st.session_state.papers.append(paper_data)
                
                # Update progress
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.empty()
            progress_bar.empty()
            st.success(f"✓ Successfully analyzed {len(uploaded_files)} paper(s)!")
            st.balloons()

# ===== COMPARE PAGE =====
elif page == "Compare Papers":
    st.title("🔬 Compare Research Papers")
    
    if len(st.session_state.papers) < 2:
        st.warning("You need at least 2 papers to compare. Upload more papers first.")
    else:
        st.write("Select papers to compare and identify agreements, contradictions, and research gaps.")
        
        # Paper selection
        paper_titles = [p['title'] for p in st.session_state.papers]
        selected_titles = st.multiselect(
            "Select papers to compare (2-5 papers)",
            paper_titles,
            max_selections=5
        )
        
        if len(selected_titles) >= 2:
            if st.button("🔍 Compare Selected Papers", type="primary"):
                with st.spinner("Analyzing papers..."):
                    selected_papers = [p for p in st.session_state.papers if p['title'] in selected_titles]
                    st.session_state.comparison_result = compare_papers(selected_papers)
                    st.success("Comparison complete!")
        
        # Display comparison results
        if st.session_state.comparison_result:
            result = st.session_state.comparison_result
            analysis = result['analysis']
            
            st.divider()
            st.subheader("📊 Comparison Analysis")
            
            # Selected Papers
            st.write("### Papers Being Compared")
            for idx, paper in enumerate(result['papers'], 1):
                st.write(f"{idx}. **{paper['title']}** - {', '.join(paper.get('authors', []))}")
            
            st.divider()
            
            # Common Themes
            if analysis.get('common_themes'):
                st.write("### 💡 Common Themes")
                cols = st.columns(len(analysis['common_themes']))
                for idx, theme in enumerate(analysis['common_themes']):
                    with cols[idx]:
                        st.info(theme)
            
            # Agreements
            if analysis.get('agreements'):
                st.write("### ✅ Areas of Agreement")
                for idx, agreement in enumerate(analysis['agreements'], 1):
                    with st.container():
                        st.write(f"**{idx}. {agreement['title']}**")
                        st.write(agreement['description'])
                        if agreement.get('papers'):
                            st.caption(f"Papers: {', '.join(agreement['papers'])}")
            
            # Contradictions
            if analysis.get('contradictions'):
                st.write("### ⚠️ Contradictions")
                for idx, contradiction in enumerate(analysis['contradictions'], 1):
                    with st.container():
                        st.write(f"**{idx}. {contradiction['title']}**")
                        st.write(contradiction['description'])
                        if contradiction.get('conflicting_views'):
                            for view in contradiction['conflicting_views']:
                                st.write(f"• {view}")
            
            # Research Gaps
            if analysis.get('research_gaps'):
                st.write("### 🔍 Research Gaps")
                for idx, gap in enumerate(analysis['research_gaps'], 1):
                    with st.container():
                        st.write(f"**{idx}. {gap['gap']}**")
                        st.write(f"*Potential Impact:* {gap['potential_impact']}")
            
            # Unique Contributions
            if analysis.get('unique_contributions'):
                st.write("### 🌟 Unique Contributions")
                for contribution in analysis['unique_contributions']:
                    st.success(f"**{contribution['paper']}**: {contribution['contribution']}")
            
            # Reset button
            if st.button("🔄 New Comparison"):
                st.session_state.comparison_result = None
                st.rerun()

# Footer
st.sidebar.divider()
st.sidebar.caption("AI Research Paper Analyzer v1.0")
st.sidebar.caption("Built with Streamlit 🎈")
