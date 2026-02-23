# frontend/app.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_URL = "http://127.0.0.1:8000/api/v1/parse/resumes"
FEEDBACK_URL = "http://127.0.0.1:8000/api/v1/feedback"

st.set_page_config(
    page_title="Intelligent Resume Screening",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Branding
st.title(" Intelligent Resume Screening Engine")
st.caption("AI-powered resume ranking with detailed candidate analysis")

# Session state
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

if "user_ranking" not in st.session_state:
    st.session_state.user_ranking = []

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    min_experience = st.number_input(
        "Minimum Experience (years)",
        min_value=0.0,
        max_value=50.0,
        value=2.0,
        step=0.5
    )
    
    role = st.selectbox(
        "Target Role (optional)",
        ["Custom", "Backend Engineer", "Frontend Engineer", "Data Scientist", 
         "DevOps Engineer", "Full Stack Engineer"]
    )
    
    if role == "Custom":
        role = st.text_input("Enter role name")

# Main input section
st.subheader(" Input")

col1, col2 = st.columns(2)

with col1:
    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF or DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="Select multiple resume files to analyze"
    )

with col2:
    job_description = st.text_area(
        "Paste Job Description",
        height=150,
        placeholder="Paste full job description here..."
    )

# Action buttons
col1, col2, col3 = st.columns(3)

with col1:
    analyze_btn = st.button(" Analyze Resumes", width="stretch")

with col2:
    clear_btn = st.button(" Clear Results", width="stretch")

with col3:
    export_btn = st.button(" Export Results", width="stretch", 
                          disabled=(st.session_state.analysis_results is None))

# Clear results
if clear_btn:
    st.session_state.analysis_results = None
    st.session_state.user_ranking = []
    st.rerun()

# Analyze
if analyze_btn:
    if not uploaded_files or not job_description.strip():
        st.error(" Please upload at least one resume and provide a job description")
    else:
        with st.spinner(" Processing resumes and analyzing candidates..."):
            try:
                files = [("files", f) for f in uploaded_files]
                data = {
                    "job_description": job_description,
                    "role": role or None,
                    "min_experience": min_experience
                }
                
                response = requests.post(
                    API_URL,
                    files=files,
                    data=data,
                    timeout=300
                )
                
                if response.status_code == 200:
                    st.session_state.analysis_results = response.json()
                    st.success(" Analysis complete!")
                    st.rerun()
                else:
                    st.error(f" Backend error ({response.status_code})")
                    st.text(response.text)
            
            except Exception as e:
                st.error(f" Error: {str(e)}")

# Display results
if st.session_state.analysis_results:
    results = st.session_state.analysis_results
    
    # Summary metrics
    st.subheader(" Analysis Summary")
    
    metrics = results["metadata"]
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Candidates", metrics["total_candidates"])
    
    with col2:
        st.metric("Top Match", f"{metrics['top_match_score']:.1f}%")
    
    with col3:
        st.metric("Average Score", f"{metrics['average_score']:.1f}%")
    
    with col4:
        st.metric("Analysis Time", metrics["timestamp"].split("T")[1][:8])
    
    # Ranking table
    st.subheader("🏆 Ranked Candidates")
    
    ranking_data = []
    for r in results["ranking_result"]:
        ranking_data.append({
            "Rank": r["rank"],
            "Candidate": r["candidate_name"],
            "Match %": f"{r['overall_score']:.1f}%",
            "Skill Score": f"{r['component_scores']['skills']:.1f}%",
            "Experience": f"{r['component_scores']['experience']:.1f}%",
            "Readiness": r["readiness"],
            "Missing Skills": len(r["missing_skills"])
        })
    
    df = pd.DataFrame(ranking_data)
    st.dataframe(
        df,
        width="stretch",
        column_config={
            "Rank": st.column_config.NumberColumn(width="small"),
            "Candidate": st.column_config.TextColumn(width="medium"),
            "Match %": st.column_config.ProgressColumn(min_value=0, max_value=100),
            "Skill Score": st.column_config.ProgressColumn(min_value=0, max_value=100),
            "Experience": st.column_config.ProgressColumn(min_value=0, max_value=100)
        }
    )
    
    # Detailed analysis
    st.subheader(" Detailed Candidate Analysis")
    
    for r in results["ranking_result"]:
        with st.expander(
            f"#{r['rank']} {r['candidate_name']} ({r['overall_score']:.1f}%)",
            expanded=(r['rank'] == 1)
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Readiness Assessment**")
                st.write(f"Status: {r['readiness']}")
                st.write(f"Confidence: {r.get('confidence', 'N/A')}")
            
            with col2:
                st.write("**Score Breakdown**")
                scores = r["component_scores"]
                st.write(f"Skills: {scores['skills']:.1f}%")
                st.write(f"Experience: {scores['experience']:.1f}%")
                st.write(f"Education: {scores['education']:.1f}%")
                st.write(f"Keywords: {scores['keywords']:.1f}%")
            
            st.divider()
            
            st.write("**Summary**")
            st.write(r["explanation"])
            
            st.write("**Detailed Analysis**")
            st.write(r["detailed_analysis"])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Strengths**")
                for strength in r["strengths"]:
                    st.write(f" {strength}")
            
            with col2:
                st.write("**Areas for Development**")
                for weakness in r.get("weaknesses", []):
                    st.write(f" {weakness}")
            
            if r["missing_skills"]:
                st.write("**Missing Skills**")
                st.write(", ".join(r["missing_skills"]))
            
            if r["experience_gap"] > 0:
                st.write(f"**Experience Gap**: {r['experience_gap']:.1f} years")
    
    # Feedback section
    st.divider()
    st.subheader("Hiring Feedback")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_rank = st.selectbox(
            "Selected candidate rank",
            range(1, len(results["ranking_result"]) + 1),
            key="selected_rank"
        )
    
    with col2:
        feedback_notes = st.text_area(
            "Additional notes",
            placeholder="Share your hiring feedback..."
        )
    
    if st.button(" Submit Feedback"):
        selected_candidate = [
            r["candidate_name"] for r in results["ranking_result"] 
            if r["rank"] == selected_rank
        ][0]
        
        feedback_payload = {
            "job_description": job_description,
            "candidates": results["ranking_result"],
            "user_ranking": [str(selected_rank)],
            "selected_candidate": selected_candidate,
            "notes": feedback_notes
        }
        
        try:
            feedback_response = requests.post(FEEDBACK_URL, json=feedback_payload)
            if feedback_response.status_code == 200:
                st.success("Feedback submitted! This helps improve future rankings.")
            else:
                st.warning(" Feedback not saved, but analysis results are preserved.")
        except:
            st.warning("Feedback not saved, but analysis results are preserved.")