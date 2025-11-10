// Tab functionality
document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Update buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Update content
            tabContents.forEach(content => content.classList.remove('active'));
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
    
    // Upload form handling
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processForm(this, false);
        });
    }
    
    // Camera functionality
    let stream = null;
    const startCameraBtn = document.getElementById('start-camera');
    const captureBtn = document.getElementById('capture');
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    
    if (startCameraBtn) {
        startCameraBtn.addEventListener('click', startCamera);
    }
    
    if (captureBtn) {
        captureBtn.addEventListener('click', captureImage);
    }
});

function startCamera() {
    const video = document.getElementById('video');
    const startCameraBtn = document.getElementById('start-camera');
    
    if (stream) {
        // Stop camera
        stream.getTracks().forEach(track => track.stop());
        stream = null;
        video.srcObject = null;
        startCameraBtn.textContent = 'Start Camera';
        return;
    }
    
    navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        .then(function(localStream) {
            stream = localStream;
            video.srcObject = stream;
            startCameraBtn.textContent = 'Stop Camera';
        })
        .catch(function(err) {
            alert('Error accessing camera: ' + err.message);
        });
}

function captureImage() {
    if (!stream) {
        alert('Please start the camera first!');
        return;
    }
    
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const imageData = canvas.toDataURL('image/jpeg');
    processCameraForm(imageData);
}

function processCameraForm(imageData) {
    const form = document.getElementById('camera-form');
    const formData = new FormData();
    
    // Add form data
    formData.append('name', form.querySelector('[name="name"]').value || 'Anonymous');
    formData.append('email', form.querySelector('[name="email"]').value || '');
    formData.append('age_group', form.querySelector('[name="age_group"]').value);
    formData.append('gender', form.querySelector('[name="gender"]').value);
    formData.append('image_data', imageData);
    formData.append('is_online', 'true');
    
    detectEmotion(formData);
}

function processForm(form, isOnline) {
    const formData = new FormData(form);
    formData.append('is_online', isOnline ? 'true' : 'false');
    detectEmotion(formData);
}

function detectEmotion(formData) {
    const resultContainer = document.getElementById('result');
    const resultContent = document.getElementById('result-content');
    
    resultContent.innerHTML = '<p>Detecting emotion... Please wait.</p>';
    resultContainer.classList.remove('hidden');
    
    fetch('/detect', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            resultContent.innerHTML = `<p class="error">Error: ${data.error}</p>`;
            return;
        }
        
        resultContent.innerHTML = `
            <div class="detection-result">
                <h4>Emotion Detected: <span class="emotion ${data.emotion}">${data.emotion}</span></h4>
                <p>Confidence: ${(data.confidence * 100).toFixed(1)}%</p>
                ${data.image_path ? `<div class="result-image"><img src="${data.image_path}" alt="Result"></div>` : ''}
                <p><small>Session ID: ${data.session_id}</small></p>
            </div>
        `;
    })
    .catch(error => {
        resultContent.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    });
}