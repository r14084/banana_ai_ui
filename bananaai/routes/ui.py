from flask import Blueprint, render_template, send_from_directory, current_app
import os

ui_bp = Blueprint('ui', __name__)


@ui_bp.route('/')
def index():
    """Main UI page"""
    return render_template('index.html')


@ui_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    return send_from_directory(upload_folder, filename)


@ui_bp.route('/output/<filename>')
def generated_file(filename):
    """Serve generated image files"""
    output_folder = current_app.config.get('OUTPUT_FOLDER', 'output')
    return send_from_directory(output_folder, filename)