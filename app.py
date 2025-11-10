from flask import Flask, render_template, request, jsonify
import sqlite3
import cv2
import numpy as np
from PIL import Image
import base64
import io
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('emotion_detection.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS detections
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  name TEXT,
                  email TEXT,
                  age_group TEXT,
                  gender TEXT,
                  emotion TEXT,
                  confidence REAL,
                  image_path TEXT,
                  is_online BOOLEAN,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_db()

class EmotionDetector:
    def __init__(self):
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
    
    def detect_emotion(self, image):
        # For demo purposes - returns random emotion
        import random
        emotion_idx = random.randint(0, len(self.emotions)-1)
        confidence = round(random.uniform(0.7, 0.95), 2)
        return self.emotions[emotion_idx], confidence

detector = EmotionDetector()

def save_detection(data):
    conn = sqlite3.connect('emotion_detection.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO detections 
                (session_id, name, email, age_group, gender, emotion, confidence, image_path, is_online)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
             (data['session_id'], data['name'], data['email'], data['age_group'],
              data['gender'], data['emotion'], data['confidence'], 
              data['image_path'], data['is_online']))
    
    conn.commit()
    conn.close()

def get_recent_detections(limit=20):
    conn = sqlite3.connect('emotion_detection.db')
    c = conn.cursor()
    c.execute('SELECT * FROM detections ORDER BY timestamp DESC LIMIT ?', (limit,))
    results = c.fetchall()
    conn.close()
    return results

def get_statistics():
    conn = sqlite3.connect('emotion_detection.db')
    c = conn.cursor()
    c.execute('SELECT emotion, COUNT(*), AVG(confidence) FROM detections GROUP BY emotion')
    stats = c.fetchall()
    conn.close()
    return stats

@app.route('/')
def index():
    return render_template('template.html')

@app.route('/detect', methods=['POST'])
def detect_emotion():
    try:
        session_id = str(uuid.uuid4())[:8]
        
        # Get form data
        name = request.form.get('name', 'Anonymous')
        email = request.form.get('email', '')
        age_group = request.form.get('age_group', 'Not specified')
        gender = request.form.get('gender', 'Not specified')
        is_online = request.form.get('is_online', 'false') == 'true'
        
        image = None
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                img = Image.open(file.stream)
                image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Handle webcam capture
        elif 'image_data' in request.form:
            image_data = request.form['image_data']
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(image_bytes))
            image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        if image is None:
            return jsonify({'error': 'No image provided'})
        
        # Detect emotion
        emotion, confidence = detector.detect_emotion(image)
        
        # Save image (in production, consider using cloud storage)
        uploads_dir = 'static/uploads'
        os.makedirs(uploads_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{uploads_dir}/{session_id}_{timestamp}.jpg"
        cv2.imwrite(image_filename, image)
        
        # Save to database
        detection_data = {
            'session_id': session_id,
            'name': name,
            'email': email,
            'age_group': age_group,
            'gender': gender,
            'emotion': emotion,
            'confidence': confidence,
            'image_path': image_filename,
            'is_online': is_online
        }
        save_detection(detection_data)
        
        return jsonify({
            'success': True,
            'emotion': emotion,
            'confidence': confidence,
            'image_path': image_filename,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/results')
def results():
    detections = get_recent_detections()
    return render_template('results.html', detections=detections)

@app.route('/statistics')
def statistics():
    stats = get_statistics()
    total_detections = len(get_recent_detections(1000))
    return render_template('statistics.html', stats=stats, total_detections=total_detections)

@app.route('/api/detections')
def api_detections():
    detections = get_recent_detections(50)
    result = []
    for det in detections:
        result.append({
            'name': det[2],
            'emotion': det[6],
            'confidence': det[7],
            'timestamp': det[10],
            'is_online': det[9]
        })
    return jsonify(result)

# Health check endpoint for Render
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # For production, use environment variable for port
    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port, debug=False)
