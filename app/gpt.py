#r
#  Uses resumes & bios from ResumeDownloader.py, interface with OpenAI GPT 4.0-Turbo, prints result & saves into GPTout.json.

# TODO:
# # [done] Copying latest files from WildApricot "SiteUploads" to local directory: Try to make it update once every 6 hours in live build under a different file
# # [done] Extracting data from DOCX resume files
# # Look into making the resume retrieval as a tool not as a message.
# # Look into making a main.py file for flask app. For example, download files, summarise resumecache every 6 hours.
# # Drawback: Look into batch translating. Some people are missing when using multithreading chat completions GPT for summarising. Also chat completions will be unreliable in the future. Avg tokens sent for summary are ~220K. Batch will be better.

from openai import OpenAI
import json
import json2table
from docx import Document
import fitz  # PyMuPDF
import os
import numpy as np
from dotenv import load_dotenv
import os
import ResumesDownloader
import datetime
from concurrent.futures import ThreadPoolExecutor

"""
How the program works:
    1. Loaded resumes are divided into chunks. (to not go over rate limit. upgrade openapi limit to level 2 for more)
    2. Message is sent as argument to chatgpt.
    3. conversation history is appended to conversation_history (to keep context / memory of previous conversation throughout chat)
    4. step 2. and 3. repeated until end.
"""

class GPT:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def update_files(self):
        ResumesDownloader.download_all_files()
        # Logic to copy and update files every 6 hours
        # This function should be called periodically
        print("Updating files from remote source...")
        # TODO: Implement ResumesDownloader.py

    def extract_text_from_docx(self, file_path):
        """
        Extract info from doc / docx files.
        """
        try:
            pre, ext = os.path.splitext(file_path) # file_path is the file getting renamed, pre is the part of file name before extension and ext is current extension
            os.rename(file_path, pre + '.doc')
            file_path = file_path.replace('.pdf', '.doc')
            doc = Document(file_path)
            return ("\n".join([para.text for para in doc.paragraphs]))
        except Exception as e:
            # error if not doc or pdf. Delete file.
            os.remove(file_path)
        
    def extract_text_from_pdf(self, file_path):
        """
        Extract info from PDF files.
        """
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except:
            # Handle errors (e.g., .docx detected)
            return (self.extract_text_from_docx(file_path))
        
    def is_valid_resume(self, text):
        """
        Simple check for if file is a resume / bio. Just checks if these words are present, if not it's probably a company presentation or unrelated.
        """
        return "Experience" in text or "Education" in text or "Skills" in text
    
    def load_files(self, directory):
            """
            Made to parse resumes for data.
            1. Try to extract file as a pdf.
                a) If fails, rename file as .doc, and try to extract text again. <extract_text_from_pdf>
                b) If fails, must be a non doc / pdf adjacent file (eg. jpg, ppt) -> delete file.
            2. If text has keywords that should be in a resume, then add contents. If not, ignore. (eg. company presentation)
            """
            content = []
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if filename.endswith(".pdf"):
                    text = self.extract_text_from_pdf(file_path)
                else:
                    text = None
                if text and self.is_valid_resume(text):
                    content.append({"filename": filename, "text": text})
            return content
    
    def gpt_request(self, data, message, *conversation_history):
        """
        Send requests to GPT-4 with the provided chunks of text and conversation history.
        Args:
            message (str): The main user message or prompt.
            conversation_history (list): Previous conversation messages for context.
        """
        print('Loading...')
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are provided the resumes of members at a company and the conversations history. Help the user as needed."},
                {"role": "system", "content": f'Resumes: {data}'},
                {"role": "system", "content": f'Conversation History: {conversation_history}'},
                {"role": "user", "content": message},
            ],
            stream=True,
        )
        reply = ''
        for chunk in completion: # Streaming response
            if chunk.choices[0].delta.content is not None:
                reply += (chunk.choices[0].delta.content)
                print(chunk.choices[0].delta.content, end="")

        context = [reply, message]
        return context
    
    def summarize(self, content):
        """
        Summarize given content.
        """
        print('Summarising')

        try:
            content = np.array2string(content, separator=', ')
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Summarize the following text. Include name, email, qualifications, work experience, skills and education. Remove newlines."},
                    {"role": "system", "content": content},
                ],
                stream=False,
            )
            summary = ""
            summary += completion.choices[0].message.content
        except Exception as e:
            print(e)

            # Save to file for debug
        with open('resumeCache.txt', 'a') as file:
            json.dump({"GPTout": summary}, file, indent=4)
            #json.dump({"content": content}, file, indent=4) # Debug: Compare input from files to output by GPT
        return summary

    def refresh_summary(self):
        # Save to file for debug
        with open("resumeCache.txt", "w") as file:
            file.truncate()

        # Path to local directory containing resumes
        directory = os.path.join((os.path.join(os.getcwd(), 'app')), 'files') #./app/files
        resumes = self.load_files(directory)
        resume_texts = [resume['text'] for resume in resumes]

        # Separate resume text into chunks to summarize
        chunks = np.array_split(resume_texts, 3) # Change this number to change number of threads used.
        
        # Process each chunk using multithreading
        data = ''
        with ThreadPoolExecutor(len(chunks)) as executor:
            data = executor.map(self.summarize, chunks)
        
        return data

    def start_request(self, message, data, conversation_history):
        """
        Process resumes and handle conversation with GPT.

        1. Loads files as text into {resumes}
        2. Summarise all resume content to optimise tokens sent. Stored in resumeCache.json.
        3. Send user message & summarised json to GPT for response.
        """

        # Get the response from GPT, add to conversation history.
        reply, message = self.gpt_request(self, message, data, conversation_history)
        conversation_history_update = ({"role": "user", "content": message}, {"role": "assistant", "content": reply})
        
        # Save the response to a JSON file
        with open('GPTout.json', 'w') as file:
            json.dump({"GPTout": reply}, file, indent=4)
        
        # Pretty print the final result
        with open('GPTout.json', 'r') as j:
            contents = json.loads(j.read())
        build_direction = "LEFT_TO_RIGHT"
        table_attributes = {"style": "width:100%"}
        # print(json2table.convert(contents, build_direction=build_direction, table_attributes=table_attributes))

        return conversation_history_update

    def user_start(self):
        """
        User interface for starting the program.
        """
        # Load resumeCache.txt data
        with open('resumeCache.txt') as f:
                data = f.readlines()

        # Loop forever
        stop = True
        conversation_history = []
        while stop:
            message = input('Enter prompt: ')
            conversation_history += self.start_request(message, data, conversation_history) # returns context
            
def dev_start():
    App = GPT(os.getenv('OPENAI_API_KEY'))
    # Check for latest resumes
    inp = input('Check all files? y/n: ')
    if inp in ('y', 'Y'):
        ResumesDownloader.download_all_files()

    # OpenAI API client + other initializations
    print('Waking up GPT...')
    load_dotenv()

    # Summarise resumes / files
    inp = input('Refresh summary table? [Might make reuslts more accurate, but will take longer] y/n: ')
    if inp in ('y', 'Y'):
        data = App.refresh_summary()
        print("Summary cache refreshed.")
    else:
        print('Loaded previous data.')
        with open('resumeCache.txt') as f:
            data = f.readlines()

    # Loop forever
    stop = True
    conversation_history = []
    while stop:
        #start_time = datetime.datetime.now() # debug runtime
        message = input('Enter prompt: ')
        conversation_history += App.start_request(message, data, conversation_history) # returns context

        #runtime = f'{datetime.datetime.now() - start_time}'
        #print(runtime) # Debug

if __name__ == "__main__":
    dev_start()