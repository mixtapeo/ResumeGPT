from gpt import GPT
import os
from dotenv import load_dotenv
import time

load_dotenv()
gpt_instance = GPT(os.getenv('OPENAI_API'))
print('Started routine')
def update_files():
    gpt_instance.update_files()
    return "Files update started successfully"


def update_resumecache():
    gpt_instance.refresh_summary()
    return "Resume cache refreshed successfully"

update_files()
update_resumecache()