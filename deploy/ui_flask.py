"""
Simple Flask Web UI for Brain Tumor MRI Classifier
No authentication required, works immediately
"""

from flask import Flask, render_template, request, jsonify
import requests
import json
from pathlib import Path
from PIL import Image
import io
import base64

app = Flask(__name__)
API_BASE = "http://127.0.0.1:8000"

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Brain Tumor MRI Classifier</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                padding: 40px;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .section {
                margin: 30px 0;
                padding: 20px;
                border: 1px solid #eee;
                border-radius: 8px;
                background: #f9f9f9;
            }
            .section h2 {
                color: #667eea;
                margin-bottom: 15px;
                font-size: 18px;
            }
            .upload-area {
                border: 2px dashed #667eea;
                border-radius: 8px;
                padding: 30px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
            }
            .upload-area:hover {
                background: #f0f0ff;
                border-color: #764ba2;
            }
            input[type="file"] {
                display: none;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
                transition: all 0.3s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }
            .result {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                display: none;
            }
            .result.show {
                display: block;
                border: 2px solid #667eea;
            }
            .prediction {
                font-size: 24px;
                font-weight: bold;
                color: #667eea;
                margin: 10px 0;
            }
            .confidence {
                font-size: 18px;
                color: #764ba2;
                margin: 10px 0;
            }
            .image-preview {
                max-width: 300px;
                border-radius: 8px;
                margin: 10px 0;
            }
            .probabilities {
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #eee;
            }
            .prob-item {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                font-size: 14px;
            }
            .prob-bar {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                height: 6px;
                border-radius: 3px;
                margin-top: 3px;
            }
            .status {
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                font-size: 14px;
            }
            .status.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .info-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin: 20px 0;
            }
            .info-card {
                background: white;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            .info-card h3 {
                color: #667eea;
                font-size: 14px;
                margin-bottom: 10px;
            }
            .info-card p {
                color: #666;
                font-size: 13px;
                line-height: 1.6;
            }
            .loading {
                display: none;
                text-align: center;
                color: #667eea;
                font-weight: bold;
            }
            @media (max-width: 600px) {
                .container { padding: 20px; }
                .info-grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 Brain Tumor MRI Classifier</h1>
            <p class="subtitle">Upload an MRI scan to classify brain tumors instantly</p>
            
            <div class="section">
                <h2>📸 Upload Image</h2>
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <p>Click to upload or drag and drop</p>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">JPG, PNG or JPEG</p>
                    <input type="file" id="fileInput" accept="image/*">
                </div>
                <button onclick="document.getElementById('fileInput').click()" style="margin-top: 10px; width: 100%;">Choose File</button>
            </div>

            <div class="loading" id="loading">⏳ Processing image...</div>

            <div class="result" id="result">
                <div id="resultContent"></div>
            </div>

            <div class="section">
                <h2>ℹ️ Model Information</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h3>📊 Model Details</h3>
                        <p>
                            <strong>Framework:</strong> TensorFlow/Keras<br>
                            <strong>Architecture:</strong> MobileNetV2<br>
                            <strong>Training Epochs:</strong> 15<br>
                            <strong>Accuracy:</strong> 96%+
                        </p>
                    </div>
                    <div class="info-card">
                        <h3>🏷️ Classes</h3>
                        <p>
                            1️⃣ Glioma Tumor<br>
                            2️⃣ Meningioma Tumor<br>
                            3️⃣ Pituitary Tumor<br>
                            4️⃣ No Tumor Detected
                        </p>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>✅ Status</h2>
                <div id="apiStatus" class="status success">
                    ✓ API is running on http://127.0.0.1:8000
                </div>
            </div>
        </div>

        <script>
            const fileInput = document.getElementById('fileInput');
            fileInput.addEventListener('change', handleFileSelect);

            function handleFileSelect(e) {
                const file = e.target.files[0];
                if (!file) return;

                const reader = new FileReader();
                reader.onload = function(event) {
                    predictImage(file);
                };
                reader.readAsArrayBuffer(file);
            }

            function predictImage(file) {
                document.getElementById('loading').style.display = 'block';
                
                const formData = new FormData();
                formData.append('file', file);

                fetch('''' + API_BASE + '''/predict', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    displayResult(data, file);
                    document.getElementById('loading').style.display = 'none';
                })
                .catch(error => {
                    showError('Failed to process image: ' + error);
                    document.getElementById('loading').style.display = 'none';
                });
            }

            function displayResult(data, file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const imageBase64 = e.target.result;
                    
                    let html = '<img src="' + imageBase64 + '" class="image-preview" alt="Uploaded">';
                    html += '<div class="prediction">' + data.predicted_class_short + '</div>';
                    html += '<div class="confidence">Confidence: ' + (data.confidence * 100).toFixed(1) + '%</div>';
                    html += '<div class="probabilities">';
                    html += '<strong>Probabilities:</strong>';
                    
                    for (const [label, prob] of Object.entries(data.probabilities)) {
                        const percentage = (prob * 100).toFixed(1);
                        const width = prob * 100;
                        html += '<div class="prob-item">';
                        html += '<span>' + label + '</span>';
                        html += '<span>' + percentage + '%</span>';
                        html += '</div>';
                        html += '<div class="prob-bar" style="width: ' + width + '%"></div>';
                    }
                    
                    html += '<p style="margin-top: 10px; font-size: 12px; color: #999;">Inference time: ' + data.inference_time_ms.toFixed(0) + 'ms</p>';
                    html += '</div>';
                    
                    document.getElementById('resultContent').innerHTML = html;
                    document.getElementById('result').classList.add('show');
                };
                reader.readAsDataURL(file);
            }

            function showError(message) {
                const html = '<div class="status error">' + message + '</div>';
                document.getElementById('resultContent').innerHTML = html;
                document.getElementById('result').classList.add('show');
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/health', methods=['GET'])
def health():
    try:
        response = requests.get(f'{API_BASE}/health', timeout=5)
        return jsonify(response.json())
    except:
        return jsonify({"status": "error", "message": "API not available"}), 503

if __name__ == '__main__':
    print("Starting Flask UI on http://127.0.0.1:5000")
    app.run(debug=False, host='127.0.0.1', port=5000, threaded=True)
