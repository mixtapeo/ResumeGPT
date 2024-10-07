
# ResumeGPT

A GPT 4.0 Mini-powered chatbot that processes and summarizes resumes, integrated with WildApricot to pull and manage member data. It is deployed on an AWS EC2 Ubuntu instance with a Flask web server, managed using Gunicorn and Nginx.

## Features

- Summarizes resumes from WildApricot.
- Deployable on AWS / Azure / Heroku with an iframe embed to WildApricot as custom HTML.
- Fully managed on AWS EC2 Ubuntu with Nginx and Gunicorn.

## Installation
### Option I: Local environment.

### I. Clone / Download the Repository

Run these commands in the root folder:

```bash
git clone https://github.com/mixtapeo/ResumeGPT
cd ResumeGPT
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### II. Create `.env` File

1. Create a new file named `.env` in the root directory.
2. Add the following environment variables:

```text
wildapiricot_api_key=<YOUR_WILDAPRICOOT_API_KEY>
openai_api_key=<YOUR_OPENAI_API_KEY>
account_id=<YOUR_ACCOUNT_ID>
```

### III. Run the Flask App

Run `app.py`:

```bash
python3 app.py
```

Then go to the IP program is running at (usually 127.0.0.1).

## Option II: Running on AWS EC2.
### Pre-requisites:
1. **Make an Instance:** Ubuntu, type t3a.medium recommended, select a key pair, allow HTTP / S trafic.
2. Once made, under security, add **inbound rule** for port 5000, on 0.0.0.0
3. **Connect** to Amazon Elastic IP to get a public IP
   
### Setting Up a New Instance

1. **Update the system and install Python virtual environment:**

   ```bash
   sudo apt-get update
   sudo apt-get install python3-venv
   ```

2. **Clone the repository and set up the environment:**

   ```bash
   cd /home/ubuntu
   git clone https://github.com/mixtapeo/ResumeGPT
   cd ResumeGPT
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

3. **Create `.env` File:**

   ```bash
   cat >> .env
   # Add the 3 environment variables, then Ctrl+C to exit
   ```

4. **Test Gunicorn:**

   ```bash
   gunicorn -b 0.0.0.0:5000 app:app
   # Ctrl+C to exit
   ```

5. **Set up Gunicorn as a systemd service:**

   ```bash
   sudo vi /etc/systemd/system/app.service
   ```

   Edit the file with the following content:

   ```text
   [Unit]
   Description=Gunicorn instance for a resume gpt app
   After=network.target
   [Service]
   User=ubuntu
   Group=www-data
   WorkingDirectory=/home/ubuntu/ResumeGPT
   ExecStart=/home/ubuntu/ResumeGPT/venv/bin/gunicorn -b localhost:5000 wsgi:app
   Restart=always
   [Install]
   WantedBy=multi-user.target
   ```

   Save by pressing `Esc` -> `:` -> `wq!`

6. **Start and enable the service:**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start app
   sudo systemctl enable app
   ```

7. **Check if it's working:**

   ```bash
   curl localhost:5000
   ```

8. **Install and configure Nginx:**

   ```bash
   sudo apt-get install nginx
   sudo systemctl start nginx
   sudo systemctl enable nginx
   ```

9. **Edit the Nginx server configuration:**

   ```bash
   sudo vi /etc/nginx/sites-available/default
   ```

   Modify it to include:

   ```text
   upstream flaskapp{
       server localhost:5000;
   }

   location / {
          proxy_pass http://flaskapp;
          proxy_http_version 1.1;
          proxy_set_header Upgrade $http_upgrade;
          proxy_set_header Connection keep-alive;
          proxy_set_header Host $host;
          proxy_cache_bypass $http_upgrade;
        }
   ```

   Save by pressing `Esc` -> `:` -> `wq!`

10. **Check Nginx configuration validity:**

    ```bash
    sudo nginx -t
    ```

11. **Restart Nginx and Gunicorn to apply changes:**

    ```bash
    sudo systemctl restart nginx
    pkill gunicorn
    ```

12. **Allow port 5000 through the firewall:**

    ```bash
    sudo ufw allow 5000/tcp
    ```

    Your EC2 virtual machine web app should now be accessible and working!

### Setting Up a Cron Job

To maintain routine tasks:

1. **Download resumes, delete invalid/corrupt files, and summarize:**

   Make sure the `Members.xml` file is in the root directory (`/home/ResumeGPT`).

   Example command to upload from Windows:

   ```bash
   scp -i newkey.pem Members.xml ubuntu@ec2-15-222-60-90.ca-central-1.compute.amazonaws.com:/home/ubuntu/
   Or just use WinSCP (easy, recommended).
   ```

2. **Set up the cron job:**

   ```bash
   crontab -e
   ```

   Add the following line:

   ```bash
   * 6 * * * cd /home/ubuntu/ResumeGPT; source venv/bin/activate; python3 routine.py
   ```

   Check status with:

   ```bash
   systemctl status cron

   And should be working when you run this:
   crontab -l | grep -v '^#' | cut -f 6- -d ' ' | while read CMD; do eval $CMD; done
   ```

## Updating the Application

To update the application with the latest code from the repository:

1. Deactivate the virtual environment:

   ```bash
   deactivate
   ```

2. Remove the existing directory:

   ```bash
   cd ..
   rm -rf ResumeGPT
   ```

3. Clone the repository again:

   ```bash
   git clone https://github.com/mixtapeo/ResumeGPT
   cd ResumeGPT
   ```

4. Set up the environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

5. Run the application:

   ```bash
   python3 app.py
   ```

## Debugging

To collect running logs:

```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Learnings / Tech used:

- **nginx:** Nginx is used as a reverse proxy to handle client connections, manage static files, and forward dynamic requests to Gunicorn. This improves the security, performance, and scalability.
- **gunicorn:** Gunicorn serves as the WSGI HTTP server that handles incoming requests to your Flask application. It forks multiple worker processes to manage these requests concurrently, making it a critical component in a production environment.
- **CORS**
- **CRON**
- **Ubuntu**
- **AWS EC2**
- **AWS Elastic IP Addresses**
- **HTML**
- **JavaScript**
- **Python**
- **OpenAI API: Batch requests, Chat completions**
- **WildApricot API**
- **Amazon Machine Images (AMI)**
- **SSH**
  
## App Flows
### Current Web App Flow.
Look at older flow below if using in local environment.
<p align="center">
  <img src ="https://github.com/user-attachments/assets/e05fb2b8-429c-442b-9b45-1c57a5be5b41" />
</p>

### [old, initial draw up proposal]
<p align="center">
  <img src="https://github.com/user-attachments/assets/44b8c8f5-0b43-445e-b432-4ebcfed9bf96" />
</p>

## App Flow:
<p align="center"> <img src="https://github.com/user-attachments/assets/44b8c8f5-0b43-445e-b432-4ebcfed9bf96" /> </p>
