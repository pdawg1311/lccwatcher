import time
import requests
class Stopwatch:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        if self.start_time is not None:
            self.end_time = time.time()
        else:
            print("Stopwatch was not started.")

    def elapsed_time(self):
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        else:
            print("Stopwatch has not been started and stopped.")



class teamSender:

    def __init__(self,message_to_send):

        teams_webhook_url = 'https://witronde.webhook.office.com/webhookb2/5a1f72a4-8bf7-466c-80a4-d4504e1af9aa@8fdab2dd-d5f1-4619-97ff-8b1b243d712e/IncomingWebhook/b4208b1ad34e4ecba095d8e637c2a976/23eb86b9-fb71-4f08-bc31-30374fbc2e42'
        self.send_teams_message(teams_webhook_url, message_to_send)


    def send_teams_message(self,webhook_url, message):
        headers = {"Content-Type": "application/json"}


         # Split the message at the first ":"
        parts = message.split(":", 1)
        
        # Format the first part in bold
        bold_part = f"**{parts[0]}**"
        
        # Reconstruct the message with the bold part and the rest of the message
        formatted_message = f"{bold_part}:{parts[1]}" if len(parts) > 1 else bold_part

        payload = {
            "text": formatted_message
        }

        response = requests.post(webhook_url, json=payload, headers=headers)

        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")

    


