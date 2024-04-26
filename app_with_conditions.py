import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv


load_dotenv() ## load all our environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_prompt):
  model=genai.GenerativeModel('gemini-pro')

  safe = [
    {
      "category": "HARM_CATEGORY_DANGEROUS",
      "threshold": "BLOCK_NONE",
    },
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_NONE",
    },
    {
      "category": "HARM_CATEGORY_HATE_SPEECH",
      "threshold": "BLOCK_NONE",
    },
    {
      "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
      "threshold": "BLOCK_NONE",
    },
    {
      "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
      "threshold": "BLOCK_NONE",
    },
  ]
  
  response=model.generate_content(input_prompt , generation_config=genai.types.GenerationConfig(temperature=0.2), safety_settings=safe)
  if response is not None and hasattr(response, 'text'):
    return response.text
  else:
    return st.warning("Please re-run the app")

def input_pdf_text(uploaded_file):
  try:
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
      page = reader.pages[page]
      text += str(page.extract_text())
    return text
  except Exception as e:
    st.error(f"Error processing PDF: {e}")
    return None


## streamlit app
st.title("Resume Analyzer")
jd=st.text_area("Paste the Job Description")
uploaded_file=st.file_uploader("Upload Your Resume",type="pdf",help="Please upload the pdf")
submit = st.button("Submit")



if submit:
  if uploaded_file is not None:
    text=input_pdf_text(uploaded_file)

                  
    if text is not None:  # Check for successful PDF processing
       input_prompt=" resume_text:" + text  + "formulate the following in a good structured format" + """
        Please fill the placeholders above with the extracted information from the resume and job description.
        1) name = Extract the candidate's full name from resume_text only (if possible).
        2) degree = extract latest degree of candidate from resume_text only
        3) experience = carefully examine and extract how many years or months of industry relevant experience the candidate has based on resume_text only.
        4) candidate_summary = write a 50 word summary of the candidate based on resume_text only. 
        5) technical_skills = detect top  technical skills present in resume_text and give them a rating on a scale of 1-5 based on resume_text only. DONOT INCLUDE ANYTHING THAT IS NOT PRESENT IN THE RESUME_TEXT VARIABLE.
        6) non_technical_skills = 3 non technical skills of the candidate and give them a rating on a scale of 1-5 based on resume_text only.
        7) recommended_roles_for _candidate = classify the top two most suitable job roles for the candidate based on resume_text only. 
        8) domains_worked_in = extract the company and the domain of the company that candidate has worked in, that is service, product, software, etc based on your prior knowledge and resume_text only.    
        9) certifications = Recognise certifications from resume_text if available. job_description:""" + jd + """  
        10) missing_skills = also figure out the skills candidate is missing for the provided job_description.
        11) fit_score = Find out how fit the candidate is for the given job_description in percentage. For determining fit score take into consideration the skills and experience required for the role and the skills and experience of the candidate.
        12) status: generate a status of approved if fit_score is more than 70 percent, a status of reject if fit_score is less than 30 percent and a status of not sure if fit_score is between 31 percent and 69 percent.
        13) feedback: Generate a feedback mechanism for the candidate with respect to the job_description. Also include why the candidate is determined to be fit or not fit for the job description. write the feedback in third person.
        display all the above variables as a nicely formatted JSON object """
       print("--------------------------------------------------------------------------")
       print(text)
       response=get_gemini_response(input_prompt)
       if response is not None:  # Check for empty response from Gemini
          st.write(response)
       else:
          st.warning("Uploaded pdf may contain images!")
  else:
    st.warning("Please upload a PDF resume")
