import requests
import base64
import os
import xml.etree.ElementTree as ET
import time

class WildApricotAPI:
    def __init__(self, api_key, account_id):
        self.api_key = api_key
        self.account_id = account_id
        self.base_url = f'https://api.wildapricot.org/v2.3/accounts/{account_id}'
        self.token_url = 'https://oauth.wildapricot.org/auth/token'
        self.access_token = self.get_access_token()

    def get_access_token(self):
        encoded_api_key = base64.b64encode(f"APIKEY:{self.api_key}".encode()).decode()
        headers = {
            'Authorization': f'Basic {encoded_api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = 'grant_type=client_credentials&scope=auto&obtain_refresh_token=true'

        response = requests.post(self.token_url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            raise Exception(f"Failed to retrieve token: {response.content}")

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

    def extract_file_ids(self, xml_file_path):
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        ns = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}
        file_ids = []

        for row in root.findall('.//ss:Row', ns)[1:]:
            cells = row.findall('ss:Cell', ns)
            resume_file_ids = cells[32].find('ss:Data', ns).text.split(',') if len(cells) > 32 and cells[32].find('ss:Data', ns).text else []
            bio_file_ids = cells[31].find('ss:Data', ns).text.split(',') if len(cells) > 31 and cells[31].find('ss:Data', ns).text else []

            if resume_file_ids is not None and bio_file_ids is not None:
                file_ids.append({
                    'Resume': resume_file_ids,
                    'Bio': bio_file_ids
                })

        return file_ids

    def download_attachment(self, file_id, folder_path):
        try:
            url = f'{self.base_url}/attachments/{file_id}'
            response = requests.get(url, headers=self.get_headers())
            #print(f'Trying {file_id}') # Debug
            if response.status_code == 200:
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                file_name = f'{file_id}.pdf'

                if file_name not in folder_path:
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, 'wb') as file:
                        file.write(response.content)
                    # print(f'File saved as {file_path}') # Debug

                else:
                    print("Skipped. File already exists.")
        except:
            raise

def download_all_files():
    account_id = '322042'
    api_key = os.environ.get('wildapiricot_api_key')
    api = WildApricotAPI(api_key, account_id)
    local_path = os.path.join(os.getcwd(), 'files')
    xml_file_path = 'Members.xml'

    file_ids = api.extract_file_ids(xml_file_path)

    ratelimitThrottle = True # If file is skipped, do not wait 1 second.

    print('Will take a while...')
    for file_id_set in file_ids:
        if ratelimitThrottle == True:
            time.sleep(1) # Theres some kind of rate limit on WildApricot, though they don't disclose it.
        for resume_id in file_id_set['Resume']:
            resume_file = os.path.join(local_path, resume_id.strip() + '.pdf')
            if not os.path.exists(resume_file):
                api.download_attachment(resume_id.strip(), local_path)
                ratelimitThrottle=True
            else:
                ratelimitThrottle=False

        for bio_id in file_id_set['Bio']:
            bio_file = os.path.join(local_path, bio_id.strip() + '.pdf')
            if not os.path.exists(bio_file):
                api.download_attachment(bio_id.strip(), local_path)
                ratelimitThrottle=True
            else:
                ratelimitThrottle=False
    print('DONE!')
            
if __name__ == "__main__":
    download_all_files()