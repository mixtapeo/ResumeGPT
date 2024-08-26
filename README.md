# ResumeGPT
A GPT 4.0 Mini powered recommendation of top 5 candidates for a given list of requirements. Uses WildApricot to get resumes / bios, WildApricot does not provide files from API; we must utilise member ID's, match to file ID, get {base_url}/attachments/{file_id} for each member.
## Instructions:
### Pre-requisites:
Make sure python 3.12 is installed on os.

### I. Clone / download this Repo.
Run these commands in root folder:
py -3.12 -m venv .venv
pip install -r requirements.txt

### II. Make '.env' file.
1. Make a new file (can be anything) in root directory. Rename file (including extension of the file, make sure you are able to view the extensions) to '.env'.
2. Open with a text editor.
3. Put OpenAI API key, WildApricot API key, WildApricot Account number into .env file. </br>
3. Example of contents:<br /><br />
wildapiricot_api_key=<><br />
openai_api_key=<><br />
account_id=<><br /><br />

### III. Run GPT.py: 
Run main.py (the flask app), open index.html (./app/static), can now use.
Uses resumes & bios from ResumeDownloader.py, interface with OpenAI GPT 4.0-Turbo, prints result & saves into GPTout.json.<br /><br />

## III: Future TODOs:
Drawback: Look into batch translating. Some people are missing when using multithreading chat completions GPT for summarising. Also chat completions will be unreliable in the future. Avg tokens sent for summary are ~220K. Batch will be better.<br />

## App Flow:
<p align="center"> <img src="https://github.com/user-attachments/assets/44b8c8f5-0b43-445e-b432-4ebcfed9bf96" /> </p>
