import requests
import json
from definitions import GPT_api_endpoint, GPT_api_key
import os
import openai


def chatGPT(prompt, max_token=800, model_engine="gpt-3.5-turbo"):
    """
    Each dialog message needs to provide role and content. There are three roles: system, user or assistant.

    system: The system message is equivalent to an administrator, who can set the behavior and characteristics of the assistant.
        In the example above, the assistant is indicated You are a helpful assistant.
    user: The user message is ourselves, which can be asked by the user, or directly let the developer build some prompts in advance.
            Some reference ChatGPT Prompts
    assistant: The assistant message is the reply provided by the ChatGPT API before, and it is stored here.
            You can also modify this reply or make up a dialogue yourself to make the whole dialogue more smooth.
    :param prompt:
    :param max_token:
    :param model_engine:
    :return:
    """
    # setting OpenAI key
    openai.api_key = GPT_api_key

    system_message = "You are HRGPT a senior HR manager, that wants to help people land their dream job."



    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": prompt}]
    )
    output_text = response['choices'][0]['message']['content']
    return output_text


def generate_prompt(form, user):
    form_type = form.data.get("form_type")

    if form_type == "cover_letter_section":
        what_generate = "a cover letter"
    elif form_type == "email_hr_section":
        what_generate = "an first email to HR for a job application"
    elif form_type == "message_hr_section":
        what_generate = "a linkedin message to HR for a job application"
    else:
        raise Exception("the passed form type doesn't exist!")

    # company information
    company_name = form.cleaned_data['company_name']
    job_role = form.cleaned_data['job_role']
    hr_name = form.cleaned_data['hr_name']
    job_post = form.cleaned_data['job_post']
    add_more_work = form.cleaned_data['add_more_work']


    base_prompt = f"""Please generate {what_generate} for the job applicant with the following details:
                    Applicant's Information:
                    - Name: {user.name}
                    - Status: {user.status}
                    - Hard Skills: {user.hard_skills}
                    - Soft Skills: {user.soft_skills}
                    - Education: {user.education}
                    - Work Experience: {user.work_experience}
                    - Hobbies: {user.hobbies}
                    
                    Job Information:
                    - Company Name: {company_name}
                    - Job Role: {job_role}
                    - HR Name: {hr_name}
                    - Job Post: {job_post}
                    - Additional Information: {add_more_work}
                    
                    Please create a personalized and engaging {what_generate} for the job applicant, focusing on their
                    experiences, skills, and qualifications in a natural and conversational manner. Highlight the applicant's
                    strengths and explain why they would be a valuable addition to the company. Avoid presenting
                    information in list form, and instead weave these details seamlessly into the narrative.
                    Ensure the content is unique, persuasive, and captures a positive and motivated attitude but keep it Coincided.
                    Provide only the requested {what_generate}, without including any unrelated or unnecessary text."""

    try:
        return chatGPT(base_prompt)
        #return base_prompt
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error calling chatGPT: {e}")
