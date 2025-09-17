// Main JavaScript for Banana AI Prompt Expander

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const uploadContainer = document.getElementById('uploadContainer');
    const addImageBtn = document.getElementById('addImageBtn');
    const promptForm = document.getElementById('promptForm');
    const userPrompt = document.getElementById('userPrompt');
    const charCount = document.getElementById('charCount');
    const assistBtn = document.getElementById('assistBtn');
    const generateBtn = document.getElementById('generateBtn');
    const resultSection = document.getElementById('resultSection');
    const expandedPrompt = document.getElementById('expandedPrompt');
    const copyBtn = document.getElementById('copyBtn');
    const clearBtn = document.getElementById('clearBtn');
    const copyNotification = document.getElementById('copyNotification');
    const errorDisplay = document.getElementById('errorDisplay');
    
    // Advanced options
    const advancedToggle = document.getElementById('advancedToggle');
    const advancedPanel = document.getElementById('advancedPanel');
    const negativePrompt = document.getElementById('negativePrompt');
    const guidanceScale = document.getElementById('guidanceScale');
    const guidanceValue = document.getElementById('guidanceValue');
    const inferenceSteps = document.getElementById('inferenceSteps');
    const stepsValue = document.getElementById('stepsValue');
    
    // Generated image elements
    const generatedSection = document.getElementById('generatedSection');
    const generatedImg = document.getElementById('generatedImg');
    const generatedFilename = document.getElementById('generatedFilename');
    const generatedSize = document.getElementById('generatedSize');
    const generatedSeed = document.getElementById('generatedSeed');
    const downloadBtn = document.getElementById('downloadBtn');
    const clearGeneratedBtn = document.getElementById('clearGeneratedBtn');

    // Store uploaded files
    let uploadedFiles = {};
    let imageCounter = 0;

    // CSRF Token
    function getCSRFToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    // Create new upload item
    function createUploadItem() {
        imageCounter++;
        const itemId = `upload-${imageCounter}`;
        
        const uploadItem = document.createElement('div');
        uploadItem.className = 'upload-item';
        uploadItem.id = itemId;
        uploadItem.innerHTML = `
            <button type="button" class="remove-btn" data-id="${itemId}">×</button>
            <input type="file" id="file-${itemId}" accept="image/*">
            <label for="file-${itemId}" class="upload-label">
                <div class="upload-preview">
                    <div class="upload-placeholder">
                        <div style="font-size: 32px;">📷</div>
                        <div>คลิกหรือลากรูปมาวาง</div>
                    </div>
                </div>
            </label>
        `;
        
        // Add event listeners
        const fileInput = uploadItem.querySelector(`#file-${itemId}`);
        const removeBtn = uploadItem.querySelector('.remove-btn');
        
        // File input change event
        fileInput.addEventListener('change', function(e) {
            handleFileSelect(e, itemId);
        });
        
        // Remove button click event
        removeBtn.addEventListener('click', function() {
            removeUploadItem(itemId);
        });
        
        // Drag and drop events
        uploadItem.addEventListener('dragover', handleDragOver);
        uploadItem.addEventListener('dragleave', handleDragLeave);
        uploadItem.addEventListener('drop', function(e) {
            handleDrop(e, itemId);
        });
        
        uploadContainer.appendChild(uploadItem);
    }

    // Handle file selection
    function handleFileSelect(e, itemId) {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            processFile(file, itemId);
        }
    }
    
    // Process and preview file
    function processFile(file, itemId) {
        const uploadItem = document.getElementById(itemId);
        const preview = uploadItem.querySelector('.upload-preview');

        // Clean up previous preview URL if it exists
        if (uploadItem.dataset.previewUrl) {
            URL.revokeObjectURL(uploadItem.dataset.previewUrl);
            delete uploadItem.dataset.previewUrl;
        }

        // Create an object URL so the user sees an instant preview
        const objectUrl = URL.createObjectURL(file);
        uploadItem.dataset.previewUrl = objectUrl;

        const img = document.createElement('img');
        img.src = objectUrl;
        img.alt = 'Preview';
        img.style.maxWidth = '100%';
        img.style.maxHeight = '150px';
        img.style.objectFit = 'contain';
        img.onload = function() {
            URL.revokeObjectURL(objectUrl);
            delete uploadItem.dataset.previewUrl;
        };
        img.onerror = function() {
            URL.revokeObjectURL(objectUrl);
            delete uploadItem.dataset.previewUrl;
            preview.innerHTML = '<div class="upload-placeholder">ไม่สามารถแสดงตัวอย่างรูปนี้ได้</div>';
        };

        preview.innerHTML = '';
        preview.appendChild(img);
        uploadItem.classList.add('has-image');

        // Upload file
        uploadFile(file, itemId);
    }
    
    // Drag and drop handlers
    function handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.add('drag-over');
    }
    
    function handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('drag-over');
    }
    
    function handleDrop(e, itemId) {
        e.preventDefault();
        e.stopPropagation();
        
        const uploadItem = document.getElementById(itemId);
        uploadItem.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            processFile(files[0], itemId);
        }
    }

    // Remove upload item
    function removeUploadItem(itemId) {
        const uploadItem = document.getElementById(itemId);
        if (uploadItem) {
            if (uploadItem.dataset.previewUrl) {
                URL.revokeObjectURL(uploadItem.dataset.previewUrl);
                delete uploadItem.dataset.previewUrl;
            }
            uploadItem.remove();
            delete uploadedFiles[itemId];
        }
    }

    // Upload file to server
    async function uploadFile(file, itemId) {
        const formData = new FormData();
        formData.append('image_file', file);
        formData.append('image_id', itemId);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                uploadedFiles[itemId] = {
                    url: data.url,
                    filename: data.filename
                };
                showMessage(`รูปภาพอัปโหลดสำเร็จ`, 'success');
            } else {
                showError(data.error || 'เกิดข้อผิดพลาดในการอัปโหลด');
                removeUploadItem(itemId);
            }
        } catch (error) {
            showError('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์');
            removeUploadItem(itemId);
        }
    }

    // Add image button click
    addImageBtn.addEventListener('click', function() {
        createUploadItem();
    });

    // Initialize with one upload slot
    createUploadItem();

    // Advanced options toggle
    advancedToggle.addEventListener('click', function() {
        if (advancedPanel.style.display === 'none') {
            advancedPanel.style.display = 'block';
            this.textContent = '⚙️ ซ่อนตัวเลือกขั้นสูง';
        } else {
            advancedPanel.style.display = 'none';
            this.textContent = '⚙️ ตัวเลือกขั้นสูง';
        }
    });

    // Range input updates
    guidanceScale.addEventListener('input', function() {
        guidanceValue.textContent = this.value;
    });

    inferenceSteps.addEventListener('input', function() {
        stepsValue.textContent = this.value;
    });

    // Character count
    userPrompt.addEventListener('input', function() {
        const count = this.value.length;
        charCount.textContent = count;
        
        if (count > 1800) {
            charCount.style.color = 'var(--error-color)';
        } else {
            charCount.style.color = 'var(--text-secondary)';
        }
    });

    // Form submission for AI Assist
    promptForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const prompt = userPrompt.value.trim();
        const aspectRatio = document.querySelector('input[name="aspect_ratio"]:checked').value;

        if (!prompt) {
            showError('กรุณาใส่ prompt');
            return;
        }

        // Show loading state
        assistBtn.disabled = true;
        assistBtn.querySelector('.btn-text').style.display = 'none';
        assistBtn.querySelector('.btn-loading').style.display = 'inline-block';

        try {
            // Prepare request data with image references
            const requestData = {
                prompt: prompt,
                aspect_ratio: aspectRatio
            };

            // Add uploaded image references if available
            const imageReferences = [];
            for (const [id, fileData] of Object.entries(uploadedFiles)) {
                if (fileData.filename) {
                    imageReferences.push(fileData.filename);
                }
            }
            if (imageReferences.length > 0) {
                requestData.reference_images = imageReferences;
            }

            const response = await fetch('/api/assist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (response.ok) {
                displayResult(data.expanded);
                if (data.cached) {
                    showMessage('ใช้ผลลัพธ์จาก cache', 'info');
                }
            } else if (response.status === 429) {
                const retryAfter = Math.ceil(data.retry_after || 60);
                showError(`คุณส่งคำขอบ่อยเกินไป กรุณารอ ${retryAfter} วินาที`);
            } else {
                showError(data.error || 'เกิดข้อผิดพลาดในการประมวลผล');
            }
        } catch (error) {
            showError('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์');
        } finally {
            // Reset loading state
            assistBtn.disabled = false;
            assistBtn.querySelector('.btn-text').style.display = 'inline-block';
            assistBtn.querySelector('.btn-loading').style.display = 'none';
        }
    });

    // Display result
    function displayResult(expanded) {
        expandedPrompt.textContent = expanded;
        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Copy to clipboard
    copyBtn.addEventListener('click', async function() {
        const text = expandedPrompt.textContent;
        
        try {
            await navigator.clipboard.writeText(text);
            copyNotification.style.display = 'block';
            setTimeout(() => {
                copyNotification.style.display = 'none';
            }, 2000);
        } catch (err) {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            
            copyNotification.style.display = 'block';
            setTimeout(() => {
                copyNotification.style.display = 'none';
            }, 2000);
        }
    });

    // Generate image button
    generateBtn.addEventListener('click', async function() {
        const prompt = userPrompt.value.trim();
        const aspectRatio = document.querySelector('input[name="aspect_ratio"]:checked').value;

        if (!prompt) {
            showError('กรุณาใส่ prompt');
            return;
        }

        // Show loading state
        generateBtn.disabled = true;
        generateBtn.querySelector('.btn-text').style.display = 'none';
        generateBtn.querySelector('.btn-loading').style.display = 'inline-block';

        try {
            const requestData = {
                prompt: prompt,
                aspect_ratio: aspectRatio,
                negative_prompt: negativePrompt.value.trim(),
                guidance_scale: parseFloat(guidanceScale.value),
                num_inference_steps: parseInt(inferenceSteps.value)
            };

            // Add reference images if uploaded
            const referenceImages = [];
            for (const [id, fileData] of Object.entries(uploadedFiles)) {
                if (fileData.filename) {
                    referenceImages.push(fileData.filename);
                }
            }
            if (referenceImages.length > 0) {
                requestData.reference_images = referenceImages;
            }

            console.log('Sending generate request with aspect ratio:', aspectRatio);

            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (response.ok) {
                displayGeneratedImage(data);
                showMessage('รูปภาพถูกสร้างเรียบร้อยแล้ว!', 'success');
            } else if (response.status === 429) {
                const retryAfter = Math.ceil(data.retry_after || 60);
                showError(`คุณส่งคำขอบ่อยเกินไป กรุณารอ ${retryAfter} วินาที`);
            } else {
                showError(data.error || 'เกิดข้อผิดพลาดในการสร้างรูปภาพ');
            }
        } catch (error) {
            showError('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์');
        } finally {
            // Reset loading state
            generateBtn.disabled = false;
            generateBtn.querySelector('.btn-text').style.display = 'inline-block';
            generateBtn.querySelector('.btn-loading').style.display = 'none';
        }
    });

    // Display generated image
    function displayGeneratedImage(data) {
        generatedImg.src = data.url;
        generatedFilename.textContent = data.filename;
        generatedSize.textContent = `${data.width} x ${data.height}`;
        generatedSeed.textContent = data.seed || 'N/A';
        downloadBtn.href = data.url;
        downloadBtn.download = data.filename;
        
        generatedSection.style.display = 'block';
        generatedSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Clear generated image
    clearGeneratedBtn.addEventListener('click', function() {
        generatedSection.style.display = 'none';
        generatedImg.src = '';
        generatedFilename.textContent = '-';
        generatedSize.textContent = '-';
        generatedSeed.textContent = '-';
    });

    // Clear results
    clearBtn.addEventListener('click', function() {
        resultSection.style.display = 'none';
        expandedPrompt.textContent = '';
        userPrompt.value = '';
        charCount.textContent = '0';
    });

    // Show error message
    function showError(message) {
        errorDisplay.textContent = '❌ ' + message;
        errorDisplay.style.display = 'block';
        setTimeout(() => {
            errorDisplay.style.display = 'none';
        }, 5000);
    }

    // Show success/info message
    function showMessage(message, type = 'success') {
        const icon = type === 'success' ? '✅' : 'ℹ️';
        errorDisplay.textContent = `${icon} ${message}`;
        errorDisplay.style.display = 'block';
        errorDisplay.style.background = type === 'success' 
            ? 'rgba(0, 200, 83, 0.1)' 
            : 'rgba(33, 150, 243, 0.1)';
        errorDisplay.style.borderColor = type === 'success' 
            ? 'var(--success-color)' 
            : '#2196F3';
        errorDisplay.style.color = type === 'success' 
            ? 'var(--success-color)' 
            : '#2196F3';
        
        setTimeout(() => {
            errorDisplay.style.display = 'none';
            errorDisplay.style.background = '';
            errorDisplay.style.borderColor = '';
            errorDisplay.style.color = '';
        }, 3000);
    }
});
