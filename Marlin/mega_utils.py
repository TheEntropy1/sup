import os
import logging
import tempfile
import requests
import uuid
import json
from flask import current_app

logger = logging.getLogger(__name__)

class MegaHandler:
    def __init__(self):
        self.logged_in = False
        self.email = None
        self.password = None
    
    def login(self):
        """Login to Mega.nz using REST API"""
        try:
            self.email = current_app.config.get('MEGA_EMAIL')
            self.password = current_app.config.get('MEGA_PASSWORD')
            
            if not self.email or not self.password:
                logger.warning("Mega.nz credentials not provided")
                return False
            
            # For now, we'll use a local storage approach instead
            # This is placeholder for actual Mega.nz integration
            logger.info(f"Using local storage instead of Mega.nz")
            self.logged_in = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize storage handler: {str(e)}")
            return False
    
    def ensure_login(self):
        """Ensure login is active"""
        if not self.logged_in:
            return self.login()
        return True
    
    def upload_file(self, file_obj, filename):
        """
        Store a file and return URLs
        
        Args:
            file_obj: File-like object to upload
            filename: Name to give the file
            
        Returns:
            tuple: (file_id, public_url)
        """
        if not self.ensure_login():
            logger.error("Cannot upload file: Storage credentials not available")
            return None, None
        
        try:
            # Create a unique filename to avoid collisions
            unique_id = str(uuid.uuid4())
            extension = os.path.splitext(filename)[1].lower()
            file_id = f"{unique_id}{extension}"
            
            # Save file to static folder
            static_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(static_folder, exist_ok=True)
            
            file_path = os.path.join(static_folder, file_id)
            logger.info(f"Saving file to: {file_path}")
            
            file_obj.save(file_path)
            
            # Generate a public URL for embedding
            public_url = f"/static/uploads/{file_id}"
            
            logger.info(f"Successfully stored file: {public_url}")
            return file_id, public_url
        except Exception as e:
            logger.error(f"Error storing file: {str(e)}")
            return None, None
    
    def delete_file(self, file_id):
        """
        Delete a file
        
        Args:
            file_id: The file ID
            
        Returns:
            bool: Success or failure
        """
        try:
            static_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            file_path = os.path.join(static_folder, file_id)
            
            if os.path.exists(file_path):
                logger.info(f"Deleting file: {file_path}")
                os.remove(file_path)
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False

# Create a singleton instance
mega_handler = MegaHandler()