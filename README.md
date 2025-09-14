# 🍌 Banana AI Prompt Expander

**แอปพลิเคชั่น AI สำหรับขยายความ Prompt และสร้างภาพด้วย Google Gemini API**

เว็บแอปพลิเคชั่นที่ช่วยขยายความ prompt สั้น ๆ ให้เป็นคำอธิบายที่ละเอียดและครบถ้วน เพื่อใช้สร้างภาพที่มีคุณภาพสูงขึ้น พร้อมกับการสนับสนุนรูปภาพอ้างอิงไม่จำกัดจำนวนและการปรับแต่งการสร้างภาพขั้นสูง

## ✨ คุณสมบัติหลัก

### 🎨 AI Prompt Expansion
- **ขยายความ Style เท่านั้น**: ไม่เพิ่มวัตถุหรือคนใหม่ เน้นขยายสไตล์ภาพ
- **รองรับภาษาไทย**: UI และคำแนะนำเป็นภาษาไทย
- **Google Gemini API**: ใช้ Gemini 2.0 Flash สำหรับความแม่นยำสูง
- **Smart Caching**: แคชผลลัพธ์สำหรับการเข้าถึงที่รวดเร็ว

### 📸 Image Reference System
- **Upload ไม่จำกัด**: เพิ่มรูปอ้างอิงได้ไม่จำกัดจำนวนด้วยปุ่ม +
- **Drag & Drop**: ลากวางรูปภาพได้สะดวก
- **Preview System**: แสดงตัวอย่างภาพทันที
- **Remove Function**: ลบรูปที่ไม่ต้องการด้วยปุ่ม × สีแดง

### 🎛️ Advanced Controls
- **Aspect Ratio**: 9:16 (Portrait) หรือ 16:9 (Landscape)
- **Guidance Scale**: ควบคุมการทำตาม prompt (1-20)
- **Inference Steps**: ควบคุมคุณภาพและความละเอียด (1-100)
- **Negative Prompt**: ระบุสิ่งที่ไม่ต้องการในภาพ

### 🌙 Modern UI
- **Dark Theme**: ธีมมืดที่สบายตา
- **Thai Font**: ใช้ Noto Sans Thai ดูสวยงาม
- **Responsive**: รองรับทุกขนาดหน้าจอ
- **Smooth Animations**: เอฟเฟกต์การเคลื่อนไหวที่นุ่มนวล

### 🛡️ Security & Performance
- **Rate Limiting**: จำกัดการใช้งาน API
- **CSRF Protection**: ป้องกันการโจมตี
- **Input Validation**: ตรวจสอบข้อมูลนำเข้า
- **Health Monitoring**: ตรวจสอบสถานะระบบ

## 📋 ความต้องการของระบบ

- **Python**: 3.8 หรือสูงกว่า
- **Google Gemini API Key**: สำหรับใช้งาน AI
- **ระบบปฏิบัติการ**: Windows, macOS, Linux

## 🚀 วิธีติดตั้ง

### 1. Clone โปรเจค
```bash
git clone [repository-url]
cd banana_ai_ui
```

### 2. สร้าง Virtual Environment
```bash
# สร้าง virtual environment
python -m venv .venv

# เปิดใช้งาน virtual environment
# สำหรับ Windows
.venv\Scripts\activate

# สำหรับ macOS/Linux
source .venv/bin/activate
```

### 3. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 4. ตั้งค่า Environment Variables
แก้ไขไฟล์ `.env`:
```env
# Google Gemini API Key (จำเป็น)
GEMINI_API_KEY=your_api_key_here

# การตั้งค่า Flask
SECRET_KEY=your_secret_key_here
MAX_CONTENT_MB=20

# การตั้งค่าโมเดล
LLM_MODEL=gemini-2.5-flash
BANANA_MODEL=gemini-2.5-flash-image-preview

# โฟลเดอร์
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=output
LOG_FOLDER=logs

# Rate Limiting
RATE_LIMIT_ASSIST=10
RATE_LIMIT_UPLOAD=5

# Cache
CACHE_TTL=3600
CACHE_MAX_SIZE=100
```

### 5. รันแอปพลิเคชั่น
```bash
python app.py
```

เปิดเบราว์เซอร์ไปที่: `http://localhost:8000`

## 📁 Project Structure

```
banana-ai/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── bananaai/              # Application package
│   ├── config.py          # Configuration management
│   ├── middleware/        # Security, rate limiting, error handling
│   ├── services/          # Business logic (LLM, caching)
│   ├── utils/             # Utilities (validation, logging)
│   └── routes/            # API and UI routes
├── templates/             # HTML templates
├── static/                # CSS and JavaScript
├── tests/                 # Test suite
└── uploads/               # User uploaded files
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `LLM_MODEL` | Model for prompt expansion | gemini-2.5-flash |
| `BANANA_MODEL` | Model for image generation | gemini-2.5-flash-image-preview |
| `SECRET_KEY` | Flask secret key | dev-key-change-in-production |
| `UPLOAD_FOLDER` | Directory for uploads | uploads |
| `OUTPUT_FOLDER` | Directory for generated images | output |
| `LOG_FOLDER` | Directory for logs | logs |
| `MAX_CONTENT_MB` | Max upload size (MB) | 20 |
| `RATE_LIMIT_ASSIST` | Rate limit for /assist (per min) | 10 |
| `RATE_LIMIT_UPLOAD` | Rate limit for /upload (per min) | 5 |
| `CACHE_TTL` | Cache time-to-live (seconds) | 3600 |
| `FILE_CLEANUP_HOURS` | File retention period (hours) | 24 |

## 📡 API Endpoints

### POST `/api/assist`
Expand prompt using AI

**Request:**
```json
{
  "prompt": "beautiful sunset over mountains",
  "aspect_ratio": "16:9"
}
```

**Response:**
```json
{
  "expanded": "Detailed expanded prompt...",
  "cached": false
}
```

### POST `/api/generate`
Generate image using Gemini 2.5 Flash Image Preview

**Request:**
```json
{
  "prompt": "beautiful sunset over mountains",
  "aspect_ratio": "16:9",
  "negative_prompt": "blurry, bad quality",
  "guidance_scale": 7.5,
  "num_inference_steps": 20,
  "reference_images": ["uploaded_image1.jpg", "uploaded_image2.jpg"]
}
```

**Response:**
```json
{
  "success": true,
  "filename": "20240112_143022_sunset_16x9.png",
  "url": "/output/20240112_143022_sunset_16x9.png",
  "width": 1820,
  "height": 1024,
  "seed": 123456789,
  "message": "Image generated successfully"
}
```

### POST `/api/upload`
Upload reference image file

**Request:** multipart/form-data with `image_file` and `image_number` fields

**Response:**
```json
{
  "filename": "20240112_143022_image.jpg",
  "url": "/uploads/20240112_143022_image.jpg",
  "message": "File uploaded successfully"
}
```

**Usage:**
- Upload 1 reference image: AI uses it as primary reference
- Upload 2 reference images: AI combines both for more complex generation
- Thumbnails automatically generated for preview (150x150px)

### GET `/health/check`
Health status check

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1704123456.789,
  "version": "1.0.0",
  "uptime": 3600
}
```

## 🧪 Testing

### Run Tests
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=bananaai --cov-report=html

# Run specific test file
pytest tests/test_api.py
```

### Code Quality
```bash
# Format code
black .

# Check code style
flake8 .
```

## 🛡️ Security Features

- **Rate Limiting**: Prevents API abuse with configurable limits
- **CSRF Protection**: Protects against cross-site request forgery
- **Input Validation**: Validates all user inputs
- **File Type Checking**: Only allows safe image formats
- **Filename Sanitization**: Prevents directory traversal attacks
- **Security Headers**: Adds X-Frame-Options, CSP, etc.

## 🚦 Development

### Local Development
```bash
# Run in debug mode
python app.py

# The app runs on http://127.0.0.1:8000
```

### Adding New Features

1. Create service in `bananaai/services/`
2. Add route in appropriate blueprint
3. Add tests in `tests/`
4. Update configuration if needed

### Monitoring

Check application health:
```bash
curl http://127.0.0.1:8000/health/check
```

Check readiness:
```bash
curl http://127.0.0.1:8000/health/ready
```

Get statistics:
```bash
curl http://127.0.0.1:8000/health/stats
```

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

**Missing API Key**
- Make sure `.env` file exists and contains `GEMINI_API_KEY`

**Import Errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Port Already in Use**
- Change port in `app.py` or kill the process using port 8000

**File Upload Issues**
- Check that `uploads/` directory exists
- Verify file size is under the limit (default 20MB)
- Ensure image formats are supported (JPG, PNG, GIF)
- Try uploading one image at a time if both uploads fail

**Multiple Reference Images**
- Only image 1 is required, image 2 is optional
- Both images will be combined by AI if provided
- Thumbnails should appear immediately after upload
- Check browser console for JavaScript errors if thumbnails don't show

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using Flask and Google Gemini 2.5 Flash

## 🆕 What's New in v2.0

### 🖼️ Multiple Reference Images Support
- **Upload 1-2 Images**: Choose between single or dual reference images
- **Smart Combination**: AI intelligently blends multiple references
- **Thumbnail Previews**: 150x150px thumbnails with hover effects
- **Flexible Usage**: Works with 0, 1, or 2 reference images

### 🎨 Enhanced UI/UX
- Separate upload sections for each reference image
- Real-time thumbnail generation
- Improved file handling and validation
- Better visual feedback for multi-image uploads

### ⚙️ Technical Improvements
- Updated API to handle multiple reference images
- Enhanced Banana AI client for multi-image processing
- Improved error handling and logging
- Better file management and cleanup
