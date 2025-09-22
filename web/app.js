// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const cameraBtn = document.getElementById('cameraBtn');
const previewContainer = document.getElementById('previewContainer');
const previewImage = document.getElementById('previewImage');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const resultContent = document.getElementById('resultContent');
const lineItems = document.querySelectorAll('.line-item');
const cameraModal = document.getElementById('cameraModal');
const cameraVideo = document.getElementById('cameraVideo');
const cameraCanvas = document.getElementById('cameraCanvas');
const captureBtn = document.getElementById('captureBtn');
const closeCameraBtn = document.getElementById('closeCameraBtn');

// Global State
let selectedLine = 'life';
let currentFile = null;
let cameraStream = null;

// Event Listeners
function initializeEventListeners() {
    // Upload Events
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadBtn.addEventListener('click', () => fileInput.click());

    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);

    // Line Selection
    lineItems.forEach(item => {
        item.addEventListener('click', () => selectLine(item));
    });

    // Camera
    cameraBtn.addEventListener('click', openCamera);
    closeCameraBtn.addEventListener('click', closeCamera);
    captureBtn.addEventListener('click', capturePhoto);

    // Analysis
    analyzeBtn.addEventListener('click', analyzeHand);

    // Modal Click Outside
    cameraModal.addEventListener('click', (e) => {
        if (e.target === cameraModal) closeCamera();
    });
}

// File Handling
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

function handleFileSelect(e) {
    if (e.target.files[0]) {
        processFile(e.target.files[0]);
    }
}

function processFile(file) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
        showNotification('Vui lòng chọn file ảnh hợp lệ!', 'error');
        return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
        showNotification('File quá lớn! Vui lòng chọn ảnh dưới 10MB.', 'error');
        return;
    }

    currentFile = file;
    displayImagePreview(file);
    analyzeBtn.disabled = false;
}

function displayImagePreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewContainer.style.display = 'block';
        
        // Add smooth reveal animation
        previewContainer.style.opacity = '0';
        previewContainer.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            previewContainer.style.transition = 'all 0.5s ease';
            previewContainer.style.opacity = '1';
            previewContainer.style.transform = 'translateY(0)';
        }, 100);
    };
    reader.readAsDataURL(file);
}

// Line Selection
function selectLine(selectedItem) {
    lineItems.forEach(item => item.classList.remove('selected'));
    selectedItem.classList.add('selected');
    selectedLine = selectedItem.dataset.line;
    
    // Add subtle animation
    selectedItem.style.transform = 'scale(0.98)';
    setTimeout(() => {
        selectedItem.style.transform = 'scale(1)';
    }, 150);
}

// Camera Functions
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
        
        // Animate modal entrance
        const wrapper = cameraModal.querySelector('.camera-wrapper');
        wrapper.style.transform = 'scale(0.9) translateY(20px)';
        wrapper.style.opacity = '0';
        
        setTimeout(() => {
            wrapper.style.transition = 'all 0.3s ease';
            wrapper.style.transform = 'scale(1) translateY(0)';
            wrapper.style.opacity = '1';
        }, 100);
        
    } catch (error) {
        showNotification('Không thể mở camera: ' + error.message, 'error');
    }
}

function closeCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    
    const wrapper = cameraModal.querySelector('.camera-wrapper');
    wrapper.style.transform = 'scale(0.9) translateY(20px)';
    wrapper.style.opacity = '0';
    
    setTimeout(() => {
        cameraModal.style.display = 'none';
        wrapper.style.transition = 'none';
    }, 300);
}

function capturePhoto() {
    const canvas = cameraCanvas;
    const context = canvas.getContext('2d');
    
    canvas.width = cameraVideo.videoWidth;
    canvas.height = cameraVideo.videoHeight;
    
    context.drawImage(cameraVideo, 0, 0);
    
    canvas.toBlob((blob) => {
        const file = new File([blob], 'palm-photo.jpg', { type: 'image/jpeg' });
        processFile(file);
        closeCamera();
    }, 'image/jpeg', 0.9);
}

// Analysis Functions
async function analyzeHand() {
    if (!currentFile) return;

    showLoadingState(true);
    
    try {
        // Simulate analysis with realistic delay
        await simulateAnalysis();
        const prediction = generatePrediction(selectedLine);
        displayPrediction(prediction);
    } catch (error) {
        showNotification('Có lỗi xảy ra trong quá trình phân tích: ' + error.message, 'error');
    } finally {
        showLoadingState(false);
    }
}

function simulateAnalysis() {
    return new Promise(resolve => {
        const delay = 2500 + Math.random() * 2000; // 2.5-4.5 seconds
        setTimeout(resolve, delay);
    });
}

function generatePrediction(lineType) {
    const predictions = {
        life: {
            title: '🌿 Đường Sống - Sức Khỏe & Tuổi Thọ',
            confidence: Math.random() * 20 + 78,
            insights: [
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
            title: '💖 Đường Tình - Tình Yêu & Cảm Xúc',
            confidence: Math.random() * 15 + 82,
            insights: [
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
            confidence: Math.random() * 25 + 72,
            insights: [
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
            title: '⭐ Đường Vận Mệnh - Số Phận & Tương Lai',
            confidence: Math.random() * 30 + 68,
            insights: [
                'Vận mệnh của bạn có nhiều thăng trầm nhưng tổng thể là tích cực.',
                'Giai đoạn 28-35 tuổi sẽ có những cơ hội lớn thay đổi cuộc đời.',
                'May mắn sẽ đến với bạn vào những thời điểm bạn ít mong đợi nhất.',
                'Gia đình và bạn bè sẽ là nguồn hỗ trợ lớn trong cuộc đời.',
                'Hãy tin tương vào trực giác của mình, nó thường đúng.',
                'Tuổi già sẽ được tận hưởng thành quả của sự nỗ lực bền bỉ.',
                'Có khả năng đạt được địa vị xã hội cao và được nhiều người kính trọng.',
                'Số phận bạn gắn liền với việc giúp đỡ người khác.',
                'Con đường thành công của bạn sẽ không phẳng lặng nhưng đáng giá.',
                'Có duyên với tài lộc và sẽ không lo thiếu thốn về vật chất.'
            ]
        }
    };

    const predictionData = predictions[lineType];
    const randomInsight = predictionData.insights[Math.floor(Math.random() * predictionData.insights.length)];
    
    return {
        title: predictionData.title,
        confidence: predictionData.confidence,
        insight: randomInsight
    };
}

function displayPrediction(prediction) {
    const adviceTexts = [
        'Hãy nhớ rằng tương lai được tạo nên bởi những hành động của bạn hôm nay.',
        'Sử dụng những thông tin này như một nguồn cảm hứng tích cực để phát triển bản thân!',
        'Tương lai luôn có thể thay đổi tùy thuộc vào nỗ lực và quyết tâm của bạn.',
        'Hãy tận dụng những điểm mạnh và cải thiện những điểm yếu để có cuộc sống tốt hơn.',
        'Tin tưởng vào bản thân và theo đuổi những ước mơ của mình.',
        'Mỗi thách thức đều là cơ hội để bạn trở nên mạnh mẽ hơn.'
    ];
    
    const randomAdvice = adviceTexts[Math.floor(Math.random() * adviceTexts.length)];

    resultContent.innerHTML = `
        <div class="prediction-card">
            <h3 class="prediction-title">${prediction.title}</h3>
            
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: 0%"></div>
            </div>
            <p style="text-align: right; font-size: 0.9rem; margin-bottom: 1.5rem; color: #6b7280;">
                Độ tin cậy: <strong>${prediction.confidence.toFixed(1)}%</strong>
            </p>
            
            <div class="prediction-text">
                ${prediction.insight}
            </div>
        </div>
        
        <div style="background: linear-gradient(135deg, #10b98120 0%, #059669 20); border: 1px solid #d1fae5; border-radius: 12px; padding: 1.5rem; margin-top: 1.5rem;">
            <h4 style="color: #065f46; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem;">
                <span>✨</span> Lời khuyên từ AI
            </h4>
            <p style="color: #047857; font-style: italic; line-height: 1.6; margin: 0;">
                ${randomAdvice}
            </p>
        </div>
        
        <div style="text-align: center; margin-top: 1.5rem;">
            <button class="btn btn-primary" onclick="analyzeHand()" style="background: linear-gradient(135deg, #8b5cf6, #a855f7); box-shadow: 0 4px 14px rgba(139, 92, 246, 0.3);">
                <span class="btn-icon">🔮</span>
                Dự đoán mới
            </button>
        </div>
    `;
    
    // Animate confidence bar
    setTimeout(() => {
        const confidenceFill = document.querySelector('.confidence-fill');
        if (confidenceFill) {
            confidenceFill.style.width = prediction.confidence.toFixed(1) + '%';
        }
    }, 500);
}

// UI State Management
function showLoadingState(show) {
    if (show) {
        loading.style.display = 'block';
        resultContent.style.display = 'none';
        
        // Animate loading entrance
        loading.style.opacity = '0';
        loading.style.transform = 'translateY(20px)';
        setTimeout(() => {
            loading.style.transition = 'all 0.5s ease';
            loading.style.opacity = '1';
            loading.style.transform = 'translateY(0)';
        }, 100);
    } else {
        loading.style.opacity = '0';
        setTimeout(() => {
            loading.style.display = 'none';
            resultContent.style.display = 'block';
            
            // Animate results entrance
            resultContent.style.opacity = '0';
            resultContent.style.transform = 'translateY(20px)';
            setTimeout(() => {
                resultContent.style.transition = 'all 0.5s ease';
                resultContent.style.opacity = '1';
                resultContent.style.transform = 'translateY(0)';
            }, 100);
        }, 500);
    }
}

// Notification System
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${type === 'error' ? '⚠️' : 'ℹ️'}</span>
            <span class="notification-message">${message}</span>
        </div>
    `;
    
    // Add notification styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#fef2f2' : '#eff6ff'};
        color: ${type === 'error' ? '#dc2626' : '#1d4ed8'};
        border: 1px solid ${type === 'error' ? '#fecaca' : '#bfdbfe'};
        border-radius: 12px;
        padding: 1rem 1.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        z-index: 1001;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 4000);
}

// Smooth Animations
function initializeAnimations() {
    const cards = document.querySelectorAll('.upload-card, .results-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        setTimeout(() => {
            card.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200 + 300);
    });
}

// Lifecycle Management
function handleVisibilityChange() {
    if (document.hidden && cameraStream) {
        closeCamera();
    }
}

function handleWindowResize() {
    // Handle responsive adjustments if needed
    if (window.innerWidth < 768 && cameraStream) {
        // Adjust camera settings for mobile if needed
    }
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    initializeAnimations();
    
    // Set initial state
    showLoadingState(false);
    
    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
});

// Event Listeners for Lifecycle
document.addEventListener('visibilitychange', handleVisibilityChange);
window.addEventListener('resize', handleWindowResize);

// Keyboard Navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && cameraModal.style.display === 'flex') {
        closeCamera();
    }
});

// Export for testing (Node.js environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        processFile,
        generatePrediction,
        showLoadingState,
        selectLine
    };
}