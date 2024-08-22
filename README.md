# ResumeGPT
A GPT 4.0 Mini powered recommendation of top 5 candidates for a given list of requirements. Uses WildApricot to get resumes / bios, WildApricot does not provide files from API; we must utilise member ID's, match to file ID, get {base_url}/attachments/{file_id} for each member.
## Instructions:
### Pre-requisites:
Make sure python 3.12 is installed on os

### I. Clone / download this Repo.
Run these commands in root folder:
py -3.12 -m venv .venv
pip install -r requirements.txt

### II. Make '.env' file.
1. Make a new file (can be anything). Rename file (including extension of the file, make sure you are able to view the extensions) to '.env'.
2. Open with a text editor.
3. Put OpenAI API key, WildApricot API key, WildApricot Account number into .env file. </br>
3. Example of contents:<br /><br />
wildapiricot_api_key=<><br />
openai_api_key=<><br />
account_id=<><br /><br />

## III. Run these in order:
### 1. Run WaApi.py: 
Get outputfile.json with full contact list (has info about membership, address, phone number, name, etc.).<br />
### 2. Run OutputfileCleaner.py: 
Cleans outputfile of credential info, and invalid users (dont work at/for company anymore).<br />
### 3. Run ResumeDownloader.py: 
Downloads resumes of valid members using OutputfileCleaner.py's cleaned_outpufile.json.<br />
### 4. Run GPT.py: 
Uses resumes & bios from ResumeDownloader.py, interface with OpenAI GPT 4.0-Turbo, prints result & saves into GPTout.json.<br /><br />

## III: Future TODOs:
### TODO:
1. [DONE] Check if contact is still at Company or not. If not, dont download resume. -> by using cleaned outputfile.<br />
2. [Fixed: Processed chunks of files, summarised each at the end] Currently only using bios, not resume. Resume needs a lot more tokens (openAI) rate limit.<br />
3. Found some useless / random pdfs as well, which arent 'resumes' just references or slides of companies. Try to run a check somehow using WaApi's 'GetInfo' function and see if valid name type stuff.<br />
4. Copying latest files from WildApricot "SiteUploads" to local directory: Try to make it update once every 6 hours in live build under a different file.<br />
5. [Can be done docx library] Extracting data from DOCX resume files by converting to PDF or straight to txt.<br />
6. Main.py with GUI to execute all the required files automagically.
