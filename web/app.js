// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const cameraBtn = document.getElementById('cameraBtn');
const previewImage = document.getElementById('previewImage');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const resultContent = document.getElementById('resultContent');
const lineOptions = document.querySelectorAll('.line-option');
const cameraModal = document.getElementById('cameraModal');
const cameraVideo = document.getElementById('cameraVideo');
const cameraCanvas = document.getElementById('cameraCanvas');
const captureBtn = document.getElementById('captureBtn');
const closeCameraBtn = document.getElementById('closeCameraBtn');

// Global variables
let selectedLine = 'life';
let currentFile = null;
let cameraStream = null;

// Initialize event listeners
function initializeEventListeners() {
    // Upload area events
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadBtn.addEventListener('click', () => fileInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    });

    // Line selection events
    lineOptions.forEach(option => {
        option.addEventListener('click', () => {
            lineOptions.forEach(opt => opt.classList.remove('selected'));
            option.classList.add('selected');
            selectedLine = option.dataset.line;
        });
    });

    // Camera functionality
    cameraBtn.addEventListener('click', openCamera);
    closeCameraBtn.addEventListener('click', closeCamera);
    captureBtn.addEventListener('click', capturePhoto);

    // Analyze button
    analyzeBtn.addEventListener('click', analyzeHand);
}

// File handling functions
function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showAlert('Vui lòng chọn file ảnh!', 'error');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showAlert('File quá lớn! Vui lòng chọn ảnh dưới 10MB.', 'error');
        return;
    }

    currentFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewImage.style.display = 'block';
        analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

// Camera functions
async function openCamera() {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            } 
        });
        cameraVideo.srcObject = cameraStream;
        cameraModal.style.display = 'flex';
    } catch (error) {
        showAlert('Không thể mở camera: ' + error.message, 'error');
    }
}

function closeCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    cameraModal.style.display = 'none';
}

function capturePhoto() {
    const canvas = cameraCanvas;
    const context = canvas.getContext('2d');
    
    canvas.width = cameraVideo.videoWidth;
    canvas.height = cameraVideo.videoHeight;
    
    context.drawImage(cameraVideo, 0, 0);
    
    canvas.toBlob((blob) => {
        const file = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' });
        handleFile(file);
        closeCamera();
    }, 'image/jpeg', 0.8);
}

// Analysis functions
async function analyzeHand() {
    if (!currentFile) return;

    showLoading(true);

    try {
        // Simulate API call with realistic delay
        await simulateAnalysis();
        
        const predictions = generatePrediction(selectedLine);
        displayResults(predictions);
    } catch (error) {
        showAlert('Có lỗi xảy ra trong quá trình phân tích: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function simulateAnalysis() {
    return new Promise(resolve => {
        const delay = 2000 + Math.random() * 2000; // 2-4 seconds
        setTimeout(resolve, delay);
    });
}

function generatePrediction(lineType) {
    const predictions = {
        life: {
            title: '🌱 Đường Sống - Sức Khỏe & Tuổi Thọ',
            confidence: Math.random() * 20 + 75,
            content: [
                'Bạn có một đường sống khá rõ nét và dài, báo hiệu sức khỏe tốt và tuổi thọ cao.',
                'Giai đoạn 30-40 tuổi sẽ là thời kỳ phát triển mạnh về sức khỏe.',
                'Nên chú ý đến việc tập thể dục đều đặn và ăn uống lành mạnh.',
                'Tuổi thọ dự kiến khoảng 75-85 tuổi với chất lượng cuộc sống tốt.',
                'Hệ miễn dịch của bạn khá tốt, ít khi mắc bệnh nặng.',
                'Có dấu hiệu của một cuộc sống năng động và khỏe mạnh.',
                'Cần tránh stress và áp lực công việc quá mức.',
                'Thể chất bạn phù hợp với các môn thể thao ngoài trời.'
            ]
        },
        heart: {
            title: '❤️ Đường Tình - Tình Yêu & Cảm Xúc',
            confidence: Math.random() * 15 + 80,
            content: [
                'Đường cảm xúc của bạn khá phức tạp, cho thấy một tâm hồn giàu cảm xúc.',
                'Bạn sẽ trải qua 2-3 mối tình nghiêm túc trong đời.',
                'Tuổi 25-30 là thời điểm tìm được tình yêu đích thực.',
                'Cuộc hôn nhân của bạn sẽ hạnh phúc và bền vững.',
                'Cần học cách kiểm soát cảm xúc để tránh những quyết định nóng vội.',
                'Gia đình sẽ là nguồn hạnh phúc lớn nhất trong cuộc đời bạn.',
                'Tình yêu đầu đời sẽ để lại dấu ấn sâu đậm.',
                'Bạn có xu hướng yêu sâu đậm và chung thủy.',
                'Khả năng cao sẽ có một cuộc hôn nhân hạnh phúc và nhiều con.'
            ]
        },
        head: {
            title: '🧠 Đường Trí - Trí Tuệ & Sự Nghiệp',
            confidence: Math.random() * 25 + 70,
            content: [
                'Bạn có trí tuệ tốt và khả năng phân tích logic cao.',
                'Sự nghiệp sẽ có bước phát triển vượt bậc ở tuổi 35.',
                'Phù hợp với các ngành liên quan đến công nghệ, tài chính hoặc giáo dục.',
                'Có khả năng lãnh đạo tốt và được đồng nghiệp tôn trọng.',
                'Thu nhập sẽ tăng đều đặn qua từng năm.',
                'Khả năng sáng tạo và đổi mới sẽ mang lại thành công lớn.',
                'Trí nhớ của bạn khá tốt, thích hợp học hỏi suốt đời.',
                'Có tài kinh doanh và khả năng nhìn xa trông rộng.',
                'Tuổi trung niên sẽ đạt được thành tựu cao trong sự nghiệp.'
            ]
        },
        fate: {
            title: '🌟 Đường Vận Mệnh - Số Phận & Tương Lai',
            confidence: Math.random() * 30 + 65,
            content: [
                'Vận mệnh của bạn có nhiều thăng trầm nhưng tổng thể là tích cực.',
                'Giai đoạn 28-35 tuổi sẽ có những cơ hội lớn thay đổi cuộc đời.',
                'May mắn sẽ đến với bạn vào những thời điểm bạn ít mong đợi nhất.',
                'Gia đình và bạn bè sẽ là nguồn hỗ trợ lớn trong cuộc đời.',
                'Hãy tin tưởng vào trực giác của mình, nó thường đúng.',
                'Tuổi già sẽ được tận hưởng thành quả của sự nỗ lực bền bỉ.',
                'Có khả năng đạt được địa vị xã hội cao và được nhiều người kính trọng.',
                'Số phận bạn gắn liền với việc giúp đỡ người khác.',
                'Con đường thành công của bạn sẽ không phẳng lặng nhưng đáng giá.',
                'Có duyên với tài lộc và sẽ không lo thiếu thốn về vật chất.'
            ]
        }
    };

    // Chọn ngẫu nhiên 1 câu duy nhất từ mảng content
    const predictionData = predictions[lineType];
    const randomIndex = Math.floor(Math.random() * predictionData.content.length);
    
    return {
        title: predictionData.title,
        confidence: predictionData.confidence,
        content: predictionData.content[randomIndex] // Chỉ trả về 1 câu
    };
}

function displayResults(prediction) {
    const adviceTexts = [
        'Hãy nhớ rằng tương lai được tạo nên bởi những hành động của bạn hôm nay.',
        'Sử dụng những thông tin này như một nguồn cảm hứng tích cực để phát triển bản thân!',
        'Tương lai luôn có thể thay đổi tùy thuộc vào nỗ lực và quyết tâm của bạn.',
        'Hãy tận dụng những điểm mạnh và cải thiện những điểm yếu để có cuộc sống tốt hơn.'
    ];
    
    const randomAdvice = adviceTexts[Math.floor(Math.random() * adviceTexts.length)];

    resultContent.innerHTML = `
        <div class="prediction-card">
            <h4 class="prediction-title">${prediction.title}</h4>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${prediction.confidence}%"></div>
            </div>
            <p style="text-align: right; font-size: 0.9rem; margin-bottom: 15px; opacity: 0.8;">
                Độ tin cậy: ${prediction.confidence.toFixed(1)}%
            </p>
            <div class="prediction-text" style="margin-bottom: 15px; font-size: 1.1rem; line-height: 1.8; padding: 15px; background: rgba(255, 255, 255, 0.05); border-radius: 10px;">
                ${prediction.content}
            </div>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background: rgba(255, 216, 155, 0.1); border-radius: 10px; border: 1px solid rgba(255, 216, 155, 0.3);">
            <h5 style="color: #ffd89b; margin-bottom: 10px;">🔮 Lời khuyên từ AI:</h5>
            <p style="font-style: italic; opacity: 0.9;">
                ${randomAdvice}
            </p>
        </div>
        
        <div style="margin-top: 15px; text-align: center;">
            <button class="btn" id="newPredictionBtn" onclick="analyzeHand()" style="background: linear-gradient(45deg, #ff9a9e, #fecfef);">
                🎲 Dự đoán khác
            </button>
        </div>
    `;
}

// Utility functions
function showLoading(show) {
    if (show) {
        loading.style.display = 'block';
        resultContent.style.display = 'none';
    } else {
        loading.style.display = 'none';
        resultContent.style.display = 'block';
    }
}

function showAlert(message, type = 'info') {
    // Simple alert for now - can be enhanced with custom modal
    alert(message);
}

// Animation functions
function initializeAnimations() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200);
    });
}

// API integration (for future use)
async function callPredictionAPI(file, lineType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('line_type', lineType);

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    initializeAnimations();
    
    // Set initial result content
    resultContent.style.display = 'block';
});

// Handle page visibility change to clean up camera
document.addEventListener('visibilitychange', () => {
    if (document.hidden && cameraStream) {
        closeCamera();
    }
});

// Handle window resize
window.addEventListener('resize', () => {
    // Handle responsive behavior if needed
});

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        handleFile,
        generatePrediction,
        showLoading,
        initializeEventListeners
    };
}