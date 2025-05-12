import logging
from datetime import datetime, timedelta
from flask import current_app
from app import db, scheduler
from models import Thread, Post, Image
from mega_utils import mega_handler

logger = logging.getLogger(__name__)

def cleanup_old_threads():
    """
    Cleans up old threads and their associated posts and images
    based on age, upvotes, and views.
    """
    with current_app.app_context():
        try:
            logger.info("Starting thread cleanup task")
            
            # Get the maximum age threshold
            max_age_days = current_app.config.get('THREAD_MAX_AGE_DAYS', 120)
            age_threshold = datetime.utcnow() - timedelta(days=max_age_days)
            
            # Find old threads that have low activity
            old_threads = Thread.query.filter(
                Thread.created_at < age_threshold,
                Thread.sticky.is_(False),  # Don't delete sticky threads
                Thread.upvotes < 5,  # Low upvotes
                Thread.views < 100  # Low views
            ).all()
            
            logger.info(f"Found {len(old_threads)} old threads to clean up")
            
            for thread in old_threads:
                logger.info(f"Cleaning up thread {thread.id} from board /{thread.board.slug}/")
                
                # Get all posts in the thread
                posts = Post.query.filter_by(thread_id=thread.id).all()
                
                # Clean up images from all posts
                for post in posts:
                    images = Image.query.filter_by(post_id=post.id).all()
                    
                    for image in images:
                        # Delete from Mega.nz
                        if image.mega_url:
                            logger.info(f"Deleting image {image.id} from Mega.nz")
                            mega_handler.delete_file(image.mega_url)
                        
                        # Delete the image record
                        db.session.delete(image)
                    
                    # Delete the post
                    db.session.delete(post)
                
                # Delete the thread
                db.session.delete(thread)
            
            # Commit all deletions
            db.session.commit()
            logger.info("Thread cleanup task completed successfully")
            
        except Exception as e:
            logger.error(f"Error in thread cleanup task: {str(e)}")
            db.session.rollback()


def start_scheduler(scheduler):
    """
    Start the background scheduler with cleanup tasks
    """
    try:
        # Add the cleanup job to run at the specified interval
        interval_hours = current_app.config.get('THREAD_CLEANUP_INTERVAL_HOURS', 24)
        
        scheduler.add_job(
            cleanup_old_threads,
            'interval',
            hours=interval_hours,
            id='cleanup_old_threads',
            replace_existing=True
        )
        
        # Start the scheduler if it's not already running
        if not scheduler.running:
            scheduler.start()
            logger.info(f"Scheduler started. Thread cleanup will run every {interval_hours} hours.")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
