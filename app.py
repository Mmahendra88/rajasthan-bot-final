from flask import Flask, request, render_template, jsonify, Response
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

# Admin Authentication - YE CHANGE KARNA
ADMIN_USERNAME = "rajasthan_admin"
ADMIN_PASSWORD = "Jaipur@123_Udaipur#2024"  # Strong password set karo

# Global variable to store chats
chat_history = []

def check_admin_auth():
    auth = request.authorization
    if not auth or auth.username != ADMIN_USERNAME or auth.password != ADMIN_PASSWORD:
        return False
    return True

@app.route('/')
def home():
    return "Rajasthan Tour Bot is Live! 🎉"

@app.route('/admin')
def admin_page():
    if not check_admin_auth():
        return Response(
            'Admin Login Required', 401,
            {'WWW-Authenticate': 'Basic realm="Admin Login Required"'})
    return render_template('admin.html', chats=chat_history)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if verify_token == 'rajasthan_bot_token':
            return challenge
        return 'Verification failed', 403
    
    # POST request handling
    data = request.get_json()
    print("Received webhook data:", data)
    
    if 'entry' in data:
        for entry in data['entry']:
            for change in entry.get('changes', []):
                if 'messages' in change['value']:
                    for message in change['value']['messages']:
                        handle_message(message)
    
    return 'OK', 200

def handle_message(message):
    user_message = message.get('text', {}).get('body', '').lower()
    user_number = message.get('from', '')
    
    print(f"Received message from {user_number}: {user_message}")
    
    # Store in chat history
    chat_data = {
        'user': user_number,
        'message': user_message,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    chat_history.append(chat_data)
    
    # Keep only last 100 messages
    if len(chat_history) > 100:
        chat_history.pop(0)
    
    # Send auto-reply
    reply_text = "Namaste! Main Rajasthan Tour Bot hu. Aapka swagat hai! 🎉"
    
    if 'jaipur' in user_message:
        reply_text = "Jaipur - The Pink City! 🌸 Famous for: Hawa Mahal, Amer Fort, City Palace, Jantar Mantar. Best time to visit: October-March."
    elif 'udaipur' in user_message:
        reply_text = "Udaipur - The City of Lakes! 🏞️ Famous for: Lake Pichola, City Palace, Jag Mandir, Saheliyon Ki Bari. Romantic destination!"
    elif 'jodhpur' in user_message:
        reply_text = "Jodhpur - The Blue City! 🔵 Famous for: Mehrangarh Fort, Umaid Bhawan Palace, Jaswant Thada. Don't miss the local markets!"
    elif 'culture' in user_message or 'heritage' in user_message:
        reply_text = "Rajasthan Culture: 🎭 Traditional dance: Ghoomar, Music: Manganiyar, Food: Dal Baati Churma, Festivals: Pushkar Fair, Desert Festival!"
    
    send_message(user_number, reply_text)

def send_message(to, message):
    access_token = os.environ.get('ACCESS_TOKEN')
    phone_id = os.environ.get('PHONE_ID')
    
    if not access_token or not phone_id:
        print("ERROR: ACCESS_TOKEN or PHONE_ID not set")
        return
    
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Message sent to {to}: {response.status_code}")
        
        # Store bot reply in chat history
        bot_reply = {
            'user': 'BOT',
            'message': message,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        chat_history.append(bot_reply)
        
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
