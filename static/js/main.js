// Main JavaScript for Banana AI Prompt Expander

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const uploadForm = document.getElementById('uploadForm');
    const promptForm = document.getElementById('promptForm');
    const imageFile1 = document.getElementById('imageFile1');
    const imageFile2 = document.getElementById('imageFile2');
    const fileName1 = document.getElementById('fileName1');
    const fileName2 = document.getElementById('fileName2');
    const imagePreview1 = document.getElementById('imagePreview1');
    const imagePreview2 = document.getElementById('imagePreview2');
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

    let uploadedFile1Url = null;
    let uploadedFile1Name = null;
    let uploadedFile2Url = null;
    let uploadedFile2Name = null;

    // CSRF Token
    function getCSRFToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    // File upload handling for first image
    imageFile1.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            fileName1.textContent = file.name;
            
            // Preview image with thumbnail
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview1.innerHTML = `<img src="${e.target.result}" alt="Preview 1" class="thumbnail">`;
            };
            reader.readAsDataURL(file);

            // Upload file
            uploadFile(file, 1);
        } else {
            fileName1.textContent = 'ยังไม่ได้เลือกไฟล์';
            imagePreview1.innerHTML = '';
        }
    });
    
    // File upload handling for second image
    imageFile2.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            fileName2.textContent = file.name;
            
            // Preview image with thumbnail
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview2.innerHTML = `<img src="${e.target.result}" alt="Preview 2" class="thumbnail">`;
            };
            reader.readAsDataURL(file);

            // Upload file
            uploadFile(file, 2);
        } else {
            fileName2.textContent = 'ยังไม่ได้เลือกไฟล์';
            imagePreview2.innerHTML = '';
        }
    });

    // Upload file to server
    async function uploadFile(file, imageNumber) {
        const formData = new FormData();
        formData.append('image_file', file);
        formData.append('image_number', imageNumber);

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
                if (imageNumber === 1) {
                    uploadedFile1Url = data.url;
                    uploadedFile1Name = data.filename;
                } else {
                    uploadedFile2Url = data.url;
                    uploadedFile2Name = data.filename;
                }
                showMessage(`ไฟล์รูปที่ ${imageNumber} อัปโหลดสำเร็จ`, 'success');
            } else {
                showError(data.error || 'เกิดข้อผิดพลาดในการอัปโหลด');
            }
        } catch (error) {
            showError('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์');
        }
    }

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

    // Form submission
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
        document.querySelector('.btn-text').style.display = 'none';
        document.querySelector('.btn-loading').style.display = 'inline-block';

        try {
            const response = await fetch('/api/assist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    prompt: prompt,
                    aspect_ratio: aspectRatio
                })
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
            document.querySelector('.btn-text').style.display = 'inline-block';
            document.querySelector('.btn-loading').style.display = 'none';
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
            if (uploadedFile1Name) {
                referenceImages.push(uploadedFile1Name);
            }
            if (uploadedFile2Name) {
                referenceImages.push(uploadedFile2Name);
            }
            if (referenceImages.length > 0) {
                requestData.reference_images = referenceImages;
            }

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

    // Clear all (including uploaded image)
    function clearAll() {
        // Clear form
        userPrompt.value = '';
        charCount.textContent = '0';
        negativePrompt.value = '';
        guidanceScale.value = 7.5;
        guidanceValue.textContent = '7.5';
        inferenceSteps.value = 20;
        stepsValue.textContent = '20';
        
        // Clear uploaded images
        uploadedFile1Url = null;
        uploadedFile1Name = null;
        uploadedFile2Url = null;
        uploadedFile2Name = null;
        imagePreview1.innerHTML = '';
        imagePreview2.innerHTML = '';
        fileName1.textContent = 'ยังไม่ได้เลือกไฟล์';
        fileName2.textContent = 'ยังไม่ได้เลือกไฟล์';
        imageFile1.value = '';
        imageFile2.value = '';
        
        // Clear results
        resultSection.style.display = 'none';
        expandedPrompt.textContent = '';
        generatedSection.style.display = 'none';
    }

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