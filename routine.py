from gpt import GPT
import os
from dotenv import load_dotenv
import ResumesDownloader

load_dotenv()
gpt_instance = GPT(os.getenv('OPENAI_API'))
print('Started routine')

def update_files():
    print("Updating files from remote source...")
    #ResumesDownloader.download_all_files()
    return "Files update started successfully"

def update_resumecache():
    print('Refreshing resume cache...')

    App = GPT(os.getenv('OPENAI_API_KEY'))
    App.create_batch_summary()

    return "Resume cache refreshed successfully"

update_files()
update_resumecache()