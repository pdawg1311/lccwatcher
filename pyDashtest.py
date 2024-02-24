from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import joblib
import base64
import os
import time
import threading


class Files:
    
    def __init__(self):
        self.senderemail = "noreply@witron-monitoring.com"
        creds = Credentials.from_authorized_user_file("token.json")
        self.service = build("gmail", "v1", credentials=creds)
        self.threadStart = False

        


    def download_attachment(self,email_data,msg_id,filename):
        try:
            # Iterate through the parts of the message to find attachments
            for part in email_data['payload']['parts']:
                if part.get('filename'):
                    # Extract attachment data
                    if 'data' in part['body']:
                        attachment_data = base64.urlsafe_b64decode(part['body']['data'].encode('UTF-8'))
                        # Save attachment to file
                        with open(f"{filename}_{part.get('filename')}", 'wb') as f:
                            f.write(attachment_data)
                        #print(f"Attachment '{part['filename']}")
                        return
                    else:
                        att_id = part['body']['attachmentId']
                        att = self.service.users().messages().attachments().get(userId="me", messageId=msg_id,id=att_id).execute()
                        data = att['data']
                        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                        # Save attachment to file
                        with open(f"{filename}_{part.get('filename')}", 'wb') as f:
                            f.write(file_data)
                        #print(f"Attachment '{part['filename']}'")
                        return        
        except Exception as e:
            print(f"Error downloading attachment: {e}")


    

    def job(self,msg,time):
        try:
            time_interval = datetime.now(timezone.utc) - timedelta(hours=time)
            timestamp = int(time_interval.timestamp())
            msg_id = msg["id"]
            msg = self.service.users().messages().get(userId="me", id=msg_id, format="full").execute()
            # Get the timestamp of the email
            email_timestamp = int(msg["internalDate"])/1000  # Convert milliseconds to seconds

            self.service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()


            email_date = datetime.fromtimestamp(email_timestamp)
            formatted_email_date = email_date.strftime('%Y-%m-%d-%H-%M-%S')
            #print(f'THIS IS FORMATTED EMAIL DATE {formatted_email_date}')

            if email_timestamp < timestamp:
                self.service.users().messages().trash(userId='me',id=msg_id).execute()
             #   print(f"Deleted email with ID: {msg_id}")
            self.download_attachment(msg,msg_id,formatted_email_date)

        except Exception as e:
            print(f'Idk what happened but here {e}')

    def check_for_new_messages(self):
        while True:
            try:
                print('still alive')
                # Get a list of unread messages from the sender
                messages = self.service.users().messages().list(userId="me", q=f"from:{self.senderemail}", labelIds=['UNREAD']).execute()
                if "messages" in messages:
                    self.master()
                time.sleep(60)  # Check for new messages every minute
            except Exception as e:
                print(f"An error occurred while checking for new messages: {e}")



    def master(self):
        messages = self.service.users().messages().list(userId="me",q=f"from:{self.senderemail}").execute()
        print('UNREAD MESSAGES FOUND DOWNLOADING THREAD WORKING')
        files = [file for file in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), file)) and file.endswith('.csv')] 
        joblib.Parallel(n_jobs=12)(joblib.delayed(self.job)(i,3) for i in messages.get("messages", []))
        if self.threadStart == False:
            self.threadStart = True
            downloadingThread = threading.Thread(target=self.check_for_new_messages)
            downloadingThread.start()
        
        

        


# Iterate through each email

   