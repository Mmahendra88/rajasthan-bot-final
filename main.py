from flask import Flask, request, render_template_string
import requests
import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'admin_secret_key_123'
socketio = SocketIO(app, cors_allowed_origins="*")

# WhatsApp credentials
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
PHONE_ID = os.getenv('PHONE_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Chat storage
chat_messages = []

# Rajasthan Knowledge Base from your 3 websites
RAJASTHAN_KNOWLEDGE = """
COMPREHENSIVE RAJASTHAN TOURISM INFORMATION FROM YOUR WEBSITES:

JAIPURTHRUMYLENS.COM KNOWLEDGE:
- Jaipur heritage walks and photography tours
- Amer Fort light and sound show details
- Hawa Mahal architecture and history
- City Palace museum collections and timings
- Jantar Mantar astronomical instruments information
- Local markets: Johari Bazaar, Bapu Bazaar shopping guides
- Traditional Rajasthani cuisine and best food spots
- Cultural festivals and events calendar
- Photography tips for Jaipur monuments

RTDC.TOURISM.RAJASTHAN.GOV.IN (OFFICIAL TOURISM):
- Government approved hotels and heritage properties
- Rajasthan tourism development corporation packages
- State museums entry fees and timings
- Wildlife sanctuaries: Ranthambore tiger sightings, Sariska wildlife
- Desert tourism: Jaisalmer sand dunes activities
- Cultural events: Pushkar Fair dates, Desert Festival programs
- Pilgrimage sites: Dilwara Temples architecture, Brahma Temple Pushkar
- Adventure activities: Camel safari rates, hot air balloon bookings
- RTDC hotel booking procedures

RAJASTHANTOURDRIVER.COM KNOWLEDGE:
- Customized Rajasthan tour packages and itineraries
- Transportation options: car rental, driver services costs
- Multi-city itineraries: Jaipur-Udaipur-Jodhpur circuit details
- Budget to luxury accommodation options with prices
- Local guide services and charges
- Seasonal travel recommendations
- Group tour vs private tour options comparison
- Rajasthan road trip information

SPECIFIC DESTINATION INFORMATION:

JAIPUR (PINK CITY):
- Amer Fort: Maota Lake views, Sheesh Mahal mirror work, Diwan-e-Aam
- Hawa Mahal: Palace of Winds architecture, 953 windows design
- City Palace: Chandra Mahal, Mubarak Mahal, museum collections
- Jantar Mantar: UNESCO World Heritage site, astronomical instruments
- Jal Mahal: Water palace in Man Sagar Lake, photography spots
- Albert Hall Museum: Oldest museum in Rajasthan, Egyptian architecture
- Nahargarh Fort: Sunset views, city panorama
- Birla Mandir: White marble temple, evening aarti
- Best time to visit: October to March (pleasant weather)
- Entry fees: Amer Fort ₹500 foreigners, ₹100 Indians

UDAIPUR (CITY OF LAKES):
- City Palace: Largest palace complex, museum, crystal gallery
- Lake Pichola: Boat rides, Jag Mandir, Jag Niwas (Taj Lake Palace)
- Jagdish Temple: Large Hindu temple architecture, carvings
- Saheliyon-ki-Bari: Garden with fountains, lotus pools
- Monsoon Palace: Sajjangarh Fort, sunset views over city
- Bagore-ki-Haveli: Cultural shows, museum
- Fateh Sagar Lake: Boating, Nehru Island
- Traditional arts: Miniature paintings, puppetry shows
- Best time: September to March

JODHPUR (BLUE CITY):
- Mehrangarh Fort: One of India's largest forts, museum, views
- Jaswant Thada: Marble memorial building, intricate carvings
- Umaid Bhawan Palace: Part museum, part luxury hotel
- Clock Tower (Ghanta Ghar) and Sardar Market local shopping
- Mandore Gardens: Historical memorials, green spaces
- Rao Jodha Desert Rock Park: Desert flora, walking trails
- Traditional handicrafts: Metal crafts, textiles, antiques
- Best time: October to March

JAISALMER (GOLDEN CITY):
- Jaisalmer Fort: Living fort with residents, shops, hotels
- Patwon-ki-Haveli: Intricate architecture, yellow stone carvings
- Sam Sand Dunes: Camel safari, cultural shows, desert camping
- Gadisar Lake: Scenic water reservoir, temples, boating
- Desert National Park: Wildlife, fossils, desert ecosystem
- Nathmal-ki-Haveli: Unique architecture, left-right symmetry
- Bada Bagh: Garden with cenotaphs, sunset views
- Best time: November to February (desert cool)

OTHER IMPORTANT DESTINATIONS:
- Pushkar: Brahma Temple, Pushkar Lake, Camel Fair (November)
- Mount Abu: Only hill station, Dilwara Jain Temples, Nakki Lake
- Bikaner: Junagarh Fort, Karni Mata Temple (Rat Temple)
- Chittorgarh: Largest fort in India, historical significance
- Bundi: Stepwells, palaces, less crowded

CULTURAL INFORMATION:
- Traditional attire: Ghagra-choli for women, Pagdi (turban) for men
- Cuisine: Dal Baati Churma, Gatte ki Sabzi, Laal Maas, Ker Sangri
- Folk music and dance: Ghoomar, Kalbelia, Bhavai, Kathputli
- Handicrafts: Block printing, blue pottery, leatherware, Kundan jewelry
- Festivals: Teej, Gangaur, Marwar Festival, Camel Festival
- Languages: Hindi, Rajasthani, English widely understood

PRACTICAL TRAVEL INFORMATION:
- Climate: Extreme summers (Apr-Jun 45°C), pleasant winters (Oct-Mar 25°C)
- Transportation: Well-connected by road, rail, air
- Shopping specialties: Gemstones, handicrafts, textiles, leather products
- Accommodation: Heritage hotels, palaces, budget stays, homestays
- Local transport: Auto-rickshaws, taxis, local buses, rental cars
- Safety: Generally safe for tourists, basic precautions recommended
"""

def log_chat(user_number, message, sender, timestamp=None):
    """Store chat messages and send to admin view"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    chat_data = {
        'timestamp': timestamp,
        'user_number': user_number,
        'message': message,
        'sender': sender  # 'user' or 'bot'
    }
    
    chat_messages.append(chat_data)
    
    # Send to admin view in real-time
    socketio.emit('new_message', chat_data)
    
    print(f"💬 {sender.upper()}: {message}")
    print(f"   👤 User: {user_number} | ⏰ Time: {timestamp}")

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Webhook verification for WhatsApp"""
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if verify_token == 'rajasthan_bot_token':
        print("✅ Webhook verified successfully")
        return challenge
    else:
        print("❌ Webhook verification failed")
        return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def handle_messages():
    """Handle incoming WhatsApp messages"""
    try:
        data = request.get_json()
        
        # Extract message details
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        messages = value.get('messages', [])
        
        if not messages:
            return "OK"
            
        message = messages[0]
        user_message = message['text']['body']
        from_number = message['from']
        timestamp = datetime.fromtimestamp(int(message['timestamp'])).strftime("%Y-%m-%d %H:%M:%S")
        
        # Log user message (YOU WILL SEE THIS)
        log_chat(from_number, user_message, 'user', timestamp)
        
        # Generate AI response
        ai_response = generate_rajasthan_response(user_message)
        
        # Log bot response (YOU WILL SEE THIS TOO)
        log_chat(from_number, ai_response, 'bot')
        
        # Send reply to user
        send_whatsapp_reply(from_number, ai_response)
        
        print("✅ Response sent successfully")
        
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        
    return "OK"

def generate_rajasthan_response(user_question):
    """Generate Rajasthan tour information response"""
    try:
        prompt = f"""
        RAJASTHAN TOUR KNOWLEDGE BASE:
        {RAJASTHAN_KNOWLEDGE}
        
        USER QUESTION: {user_question}
        
        IMPORTANT INSTRUCTIONS:
        - Answer based ONLY on the Rajasthan knowledge base above
        - Provide accurate information from the 3 specified websites
        - Keep responses informative, practical and helpful
        - Include specific details when available
        - Be conversational and friendly
        - If information is not available in knowledge base, say so politely
        
        RESPONSE:
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return "I specialize in Rajasthan tourism information from official sources. Please ask me about destinations, heritage sites, or travel tips! 🏰"

def send_whatsapp_reply(user_phone_number, message_text):
    """Send reply to user"""
    try:
        # Limit message length for WhatsApp
        if len(message_text) > 3000:
            message_text = message_text[:3000] + "...\n\n(Message shortened)"
        
        url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
        
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": user_phone_number,
            "text": {"body": message_text}
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"📤 Reply sent to user")
        else:
            print(f"❌ WhatsApp API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error sending WhatsApp message: {e}")

@app.route('/')
def home():
    """Home page"""
    return """
    <html>
        <head>
            <title>Rajasthan Tour Bot</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 20px; background: #fff8e1; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                .status { color: #d4af37; font-size: 24px; margin: 20px 0; }
                .admin-link { background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 10px; }
                .destinations { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin: 20px 0; }
                .destination { background: #ffecb3; padding: 10px 15px; border-radius: 20px; font-size: 14px; }
                .websites { background: #e8f5e8; padding: 15px; border-radius: 10px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏰 Rajasthan Tour Information Bot</h1>
                <p class="status">✅ Server is running successfully</p>
                
                <a href="/admin" class="admin-link">🔍 VIEW LIVE CHATS (ADMIN)</a>
                
                <div class="destinations">
                    <div class="destination">🕌 Jaipur</div>
                    <div class="destination">💧 Udaipur</div>
                    <div class="destination">🔵 Jodhpur</div>
                    <div class="destination">🏜️ Jaisalmer</div>
                    <div class="destination">🐫 Pushkar</div>
                    <div class="destination">⛰️ Mount Abu</div>
                </div>
                
                <div class="websites">
                    <p><strong>Knowledge Sources:</strong></p>
                    <p>• jaipurthrumylens.com</p>
                    <p>• rtdc.tourism.rajasthan.gov.in</p>
                    <p>• rajasthantourdriver.com</p>
                </div>
                
                <p>Bot is live! Users can send messages to connected WhatsApp number.</p>
            </div>
        </body>
    </html>
    """

@app.route('/admin')
def admin_dashboard():
    """ADMIN VIEW - You can see all chats here"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Chat View</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: white; }
            .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
            .header { background: #2d2d2d; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .header h1 { color: #d4af37; margin-bottom: 10px; }
            .stats { display: flex; gap: 20px; margin-top: 10px; }
            .stat-box { background: #3d3d3d; padding: 10px 15px; border-radius: 5px; }
            .chat-container { background: #2d2d2d; border-radius: 10px; padding: 20px; height: 70vh; overflow-y: auto; }
            .message { margin: 15px 0; padding: 15px; border-radius: 10px; max-width: 80%; }
            .user-message { background: #4a4a4a; margin-left: auto; text-align: right; }
            .bot-message { background: #d4af37; color: black; }
            .message-info { font-size: 12px; opacity: 0.7; margin-bottom: 5px; }
            .message-content { font-size: 14px; white-space: pre-wrap; }
            .no-chats { text-align: center; padding: 40px; opacity: 0.5; }
            .refresh-btn { background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 LIVE CHAT MONITORING - RAJASTHAN BOT</h1>
                <p>Real-time view of all WhatsApp conversations</p>
                <div class="stats">
                    <div class="stat-box">📊 Total Chats: <span id="totalChats">0</span></div>
                    <div class="stat-box">👥 Active Users: <span id="activeUsers">0</span></div>
                    <div class="stat-box">🕒 Last Updated: <span id="lastUpdate">Just now</span></div>
                </div>
            </div>

            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Page</button>

            <div class="chat-container" id="chatContainer">
                <div class="no-chats" id="noChats">
                    📱 No chats yet. When users message your WhatsApp number, they will appear here in real-time.
                </div>
            </div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script>
            const socket = io();
            const chatContainer = document.getElementById('chatContainer');
            const noChats = document.getElementById('noChats');
            const totalChats = document.getElementById('totalChats');
            const activeUsers = document.getElementById('activeUsers');
            const lastUpdate = document.getElementById('lastUpdate');

            // Load existing chats on page load
            fetch('/get-chats')
                .then(response => response.json())
                .then(chats => {
                    if (chats.length > 0) {
                        noChats.style.display = 'none';
                        chats.forEach(chat => addMessageToView(chat));
                        updateStats(chats);
                    }
                });

            // Listen for new messages in real-time
            socket.on('new_message', function(chatData) {
                if (noChats) noChats.style.display = 'none';
                addMessageToView(chatData);
                updateStats([chatData]);
                lastUpdate.textContent = new Date().toLocaleTimeString();
            });

            function addMessageToView(chatData) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${chatData.sender === 'user' ? 'user-message' : 'bot-message'}`;
                
                messageDiv.innerHTML = `
                    <div class="message-info">
                        ${chatData.timestamp} | 
                        ${chatData.sender === 'user' ? '👤 User' : '🤖 Bot'} |
                        ${chatData.user_number}
                    </div>
                    <div class="message-content">${chatData.message}</div>
                `;
                
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            function updateStats(chats) {
                const userNumbers = new Set(chats.map(chat => chat.user_number));
                totalChats.textContent = chats.length;
                activeUsers.textContent = userNumbers.size;
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/get-chats')
def get_chats():
    """API to get all chat messages"""
    return {'chats': chat_messages}

@socketio.on('connect')
def handle_connect():
    print('🔔 Admin connected to live chat view')
    emit('connected', {'message': 'Connected to live chat monitoring'})

if __name__ == '__main__':
    print("🚀 Starting Rajasthan Tour Bot with Admin View...")
    print("🔍 Admin Chat Monitoring: ENABLED")
    print("📱 Real-time chat viewing available at /admin")
    print("🏰 Knowledge Sources: jaipurthrumylens.com, rtdc.tourism.rajasthan.gov.in, rajasthantourdriver.com")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
