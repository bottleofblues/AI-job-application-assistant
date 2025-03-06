import openai  # Ensure OpenAI is properly imported
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pdfkit

# Function to scrape job details
def scrape_linkedin_job(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    job_title = soup.find("h1").text.strip() if soup.find("h1") else "Job Title Not Found"
    company = soup.find("a", class_="topcard__org-name-link").text.strip() if soup.find("a", class_="topcard__org-name-link") else "Company Not Found"
    job_description = soup.find("div", class_="description__text").text.strip() if soup.find("div", class_="description__text") else "Job Description Not Found"

    return job_title, company, job_description

# Function to generate a cover letter
def generate_cover_letter(job_title, company, job_description, existing_letter):
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # Use new OpenAI client

    prompt = f"""
    Based on the following job details, tailor this cover letter accordingly:
    Job Title: {job_title}
    Company: {company}
    Job Description: {job_description}
    
    Existing Cover Letter:
    {existing_letter}

    Rewrite the cover letter to make it highly relevant and impactful.
    """

    response = client.chat.completions.create(  # Use correct OpenAI API call
        model="gpt-4",  
        messages=[
            {"role": "system", "content": "You are a professional resume and cover letter writer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    return response.choices[0].message.content  # Correct response handling

# Function to generate a PDF
def generate_pdf(text, filename):
    pdfkit.from_string(text, filename)

# Streamlit UI
st.title("📄 AI Job Application Assistant")
st.write("Paste a LinkedIn job posting link, upload your resume, and get a tailored cover letter + updated resume.")

# Input: LinkedIn Job Posting URL
linkedin_url = st.text_input("🔗 Paste LinkedIn Job URL:")

# Upload Resume
uploaded_resume = st.file_uploader("📂 Upload your current resume (PDF)", type="pdf")

# Existing Cover Letter (Optional)
existing_cover_letter = st.text_area("✍️ Paste an existing cover letter (optional)")

if st.button("Generate Cover Letter & Resume"):
    if linkedin_url:
        job_title, company, job_desc = scrape_linkedin_job(linkedin_url)
        
        if not existing_cover_letter:
            existing_cover_letter = "Dear Hiring Manager, I'm excited to apply for this role..."
        
        new_cover_letter = generate_cover_letter(job_title, company, job_desc, existing_cover_letter)

        # Display & Download Cover Letter
        st.subheader("📃 Your Tailored Cover Letter:")
        st.text_area("AI-Generated Cover Letter:", new_cover_letter, height=300)

        # Generate PDF
        cover_letter_pdf = "Cover_Letter.pdf"
        generate_pdf(new_cover_letter, cover_letter_pdf)
        st.download_button(label="📥 Download Cover Letter (PDF)", data=open(cover_letter_pdf, "rb").read(), file_name=cover_letter_pdf, mime="application/pdf")

        st.success("🎉 Your cover letter is ready! Resume update is the next step.")
    else:
        st.error("Please provide a LinkedIn job posting URL.")

if __name__ == "__main__":
    st.write("App loaded successfully!")  # Helps verify if the app runs

