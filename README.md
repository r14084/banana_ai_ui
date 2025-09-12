# 🍌 Banana AI Prompt Expander

A Flask web application that helps users upload 1-2 reference images, expand prompts using AI, and generate high-quality images using Google's Gemini 2.5 Flash Image Preview model.

## ✨ Features

- 📸 **Multi-Reference Images**: Upload 1-2 reference images with thumbnail previews
- 🖼️ **Smart Image Combination**: AI intelligently combines multiple reference images
- 🤖 **AI-Powered Expansion**: Uses Gemini 2.5 Flash to intelligently expand prompts
- 🎨 **Image Generation**: Generate images using Gemini 2.5 Flash Image Preview model
- 📐 **Aspect Ratio Support**: Choose between 9:16 (Portrait) and 16:9 (Landscape)
- ⚙️ **Advanced Controls**: Adjustable guidance scale, inference steps, and negative prompts
- ⚡ **Smart Caching**: Caches frequent prompts for faster responses
- 💾 **Image Management**: Automatically saves generated images to output folder
- 🛡️ **Security**: Rate limiting, CSRF protection, and input validation
- 📊 **Health Monitoring**: Built-in health check endpoints
- 🎨 **Modern UI**: Responsive design with smooth animations and hover effects

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (used for both prompt expansion and image generation)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd banana-ai
```

2. **Create virtual environment**
```bash
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment**
```bash
cp .env.example .env
```

Edit `.env` file and add your API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
SECRET_KEY=your_secret_key_here
```

5. **Run the application**
```bash
python app.py
```

The application will start at `http://127.0.0.1:8000`

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