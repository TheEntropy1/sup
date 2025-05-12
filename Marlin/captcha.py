import os
import random
import string
import uuid
import logging
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import base64
from flask import Blueprint, request, jsonify
from app import db
from models import CaptchaToken

logger = logging.getLogger(__name__)

captcha_bp = Blueprint('captcha', __name__)

def generate_captcha_text(length=6):
    """Generate random captcha text"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_captcha_image(text):
    """Generate captcha image with given text"""
    # Create a blank image with a random background color
    width, height = 180, 60
    bg_color = (random.randint(230, 255), random.randint(230, 255), random.randint(230, 255))
    text_color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
    
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)
    
    # Add noise (dots)
    for _ in range(width * height // 20):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        color = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
        draw.point((x, y), fill=color)
    
    # Add text with random position jitters
    font_size = random.randint(26, 32)
    # Use a default font since we can't include a custom font file
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Calculate text size to center it
    text_width = width // 2
    text_height = height // 2
    
    # Draw each character with slight random rotation and position
    x_offset = 15
    for char in text:
        angle = random.randint(-15, 15)
        char_image = Image.new('RGBA', (30, 30), color=(0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_image)
        char_draw.text((5, 5), char, font=font, fill=text_color)
        
        # Rotate the character
        rotated_char = char_image.rotate(angle, resample=Image.BICUBIC, expand=0)
        
        # Paste onto main image
        y_pos = random.randint(10, height - 30)
        image.paste(rotated_char, (x_offset, y_pos), rotated_char)
        x_offset += random.randint(18, 25)
    
    # Add lines across the image
    for _ in range(random.randint(2, 4)):
        start_x = random.randint(0, width // 4)
        start_y = random.randint(0, height)
        end_x = random.randint(width // 4 * 3, width)
        end_y = random.randint(0, height)
        line_color = (random.randint(0, 150), random.randint(0, 150), random.randint(0, 150))
        draw.line([(start_x, start_y), (end_x, end_y)], fill=line_color, width=random.randint(1, 2))
    
    # Apply slight blur
    image = image.filter(ImageFilter.BLUR)
    
    # Convert to base64 string
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str


def create_captcha():
    """Create a new captcha and store in database"""
    # Generate random captcha text
    captcha_text = generate_captcha_text()
    
    # Generate token
    token = uuid.uuid4().hex
    
    # Create database record
    captcha_token = CaptchaToken(
        token=token,
        solution=captcha_text,
        used=False
    )
    db.session.add(captcha_token)
    db.session.commit()
    
    # Generate image
    captcha_image = generate_captcha_image(captcha_text)
    
    return {
        'token': token,
        'image': captcha_image
    }


def validate_captcha(token, solution):
    """Validate captcha solution"""
    if not token or not solution:
        return False
    
    # Find token in database
    captcha_token = CaptchaToken.query.filter_by(token=token, used=False).first()
    
    if not captcha_token:
        return False
    
    # Mark as used regardless of validation result
    captcha_token.used = True
    db.session.commit()
    
    # Validate solution (case-insensitive)
    return captcha_token.solution.upper() == solution.upper()


@captcha_bp.route('/captcha/generate', methods=['GET'])
def generate_captcha():
    """API endpoint to generate a new captcha"""
    try:
        captcha_data = create_captcha()
        return jsonify({
            'success': True,
            'token': captcha_data['token'],
            'image': captcha_data['image']
        })
    except Exception as e:
        logger.error(f"Error generating captcha: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate captcha'
        }), 500
