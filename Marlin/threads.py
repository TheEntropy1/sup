import logging
import uuid
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db
from models import Board, Thread, Post, Image, Vote
from forms import NewThreadForm, ReplyForm
from captcha import validate_captcha
from mega_utils import mega_handler

logger = logging.getLogger(__name__)

threads_bp = Blueprint('threads', __name__)


@threads_bp.route('/<board_slug>/thread/<int:thread_id>')
def view_thread(board_slug, thread_id):
    board = Board.query.filter_by(slug=board_slug).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, board_id=board.id).first_or_404()
    
    # Increment view counter
    thread.views += 1
    db.session.commit()
    
    # Get all posts in the thread with images
    posts = Post.query.filter_by(thread_id=thread.id).order_by(Post.created_at).all()
    
    # Get images for all posts
    posts_with_images = []
    for post in posts:
        images = Image.query.filter_by(post_id=post.id).all()
        posts_with_images.append({
            'post': post,
            'images': images
        })
    
    # Create reply form
    form = ReplyForm()
    
    return render_template(
        'thread.html',
        title=f'/{board.slug}/ - {thread.subject or "Thread #" + str(thread.id)}',
        board=board,
        thread=thread,
        posts_with_images=posts_with_images,
        form=form
    )


@threads_bp.route('/<board_slug>/new', methods=['GET', 'POST'])
def new_thread(board_slug):
    board = Board.query.filter_by(slug=board_slug).first_or_404()
    form = NewThreadForm()
    
    if form.validate_on_submit():
        # Validate captcha
        if not validate_captcha(form.captcha_token.data, form.captcha_solution.data):
            flash('Invalid captcha. Please try again.', 'danger')
            return redirect(url_for('threads.new_thread', board_slug=board_slug))
        
        # Create new thread
        thread = Thread(
            subject=form.subject.data,
            board_id=board.id
        )
        db.session.add(thread)
        db.session.flush()  # Get the thread ID
        
        # Create initial post (OP)
        post = Post(
            content=form.content.data,
            thread_id=thread.id,
            user_id=current_user.id if current_user.is_authenticated else None,
            poster_name="Anonymous"
        )
        db.session.add(post)
        db.session.flush()  # Get the post ID
        
        # Handle image upload if provided
        if form.image.data:
            try:
                # Generate unique filename
                original_filename = secure_filename(form.image.data.filename)
                file_ext = os.path.splitext(original_filename)[1]
                new_filename = f"{uuid.uuid4().hex}{file_ext}"
                
                # Upload to Mega.nz
                mega_url, public_url = mega_handler.upload_file(form.image.data, new_filename)
                
                if mega_url and public_url:
                    # Create image record
                    image = Image(
                        filename=new_filename,
                        mega_url=mega_url,
                        public_url=public_url,
                        post_id=post.id
                    )
                    db.session.add(image)
                else:
                    flash('Failed to upload image. Thread created without image.', 'warning')
            except Exception as e:
                logger.error(f"Error uploading image: {str(e)}")
                flash('Error uploading image. Thread created without image.', 'warning')
        
        # Commit all changes
        db.session.commit()
        
        flash('Thread created successfully!', 'success')
        return redirect(url_for('threads.view_thread', board_slug=board_slug, thread_id=thread.id))
    
    return render_template(
        'post_form.html',
        title=f'New Thread - /{board.slug}/',
        board=board,
        form=form,
        is_new_thread=True
    )


@threads_bp.route('/<board_slug>/thread/<int:thread_id>/reply', methods=['POST'])
def reply(board_slug, thread_id):
    board = Board.query.filter_by(slug=board_slug).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, board_id=board.id).first_or_404()
    
    # Check if thread is locked
    if thread.locked:
        flash('This thread is locked. You cannot reply.', 'danger')
        return redirect(url_for('threads.view_thread', board_slug=board_slug, thread_id=thread_id))
    
    form = ReplyForm()
    
    if form.validate_on_submit():
        # Validate captcha
        if not validate_captcha(form.captcha_token.data, form.captcha_solution.data):
            flash('Invalid captcha. Please try again.', 'danger')
            return redirect(url_for('threads.view_thread', board_slug=board_slug, thread_id=thread_id))
        
        # Create reply post
        post = Post(
            content=form.content.data,
            thread_id=thread.id,
            user_id=current_user.id if current_user.is_authenticated else None,
            poster_name="Anonymous"
        )
        db.session.add(post)
        db.session.flush()  # Get the post ID
        
        # Handle image upload if provided
        if form.image.data:
            try:
                # Generate unique filename
                original_filename = secure_filename(form.image.data.filename)
                file_ext = os.path.splitext(original_filename)[1]
                new_filename = f"{uuid.uuid4().hex}{file_ext}"
                
                # Upload to Mega.nz
                mega_url, public_url = mega_handler.upload_file(form.image.data, new_filename)
                
                if mega_url and public_url:
                    # Create image record
                    image = Image(
                        filename=new_filename,
                        mega_url=mega_url,
                        public_url=public_url,
                        post_id=post.id
                    )
                    db.session.add(image)
                else:
                    flash('Failed to upload image. Reply posted without image.', 'warning')
            except Exception as e:
                logger.error(f"Error uploading image: {str(e)}")
                flash('Error uploading image. Reply posted without image.', 'warning')
        
        # Update thread's updated_at timestamp (bump)
        thread.updated_at = datetime.utcnow()
        
        # Commit all changes
        db.session.commit()
        
        flash('Reply posted successfully!', 'success')
        return redirect(url_for('threads.view_thread', board_slug=board_slug, thread_id=thread_id))
    
    # If form validation fails, return to thread page with errors
    return redirect(url_for('threads.view_thread', board_slug=board_slug, thread_id=thread_id))


@threads_bp.route('/<board_slug>/thread/<int:thread_id>/upvote', methods=['POST'])
@login_required
def upvote_thread(board_slug, thread_id):
    board = Board.query.filter_by(slug=board_slug).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, board_id=board.id).first_or_404()
    
    # Check if user already voted
    existing_vote = Vote.query.filter_by(
        user_id=current_user.id,
        thread_id=thread.id
    ).first()
    
    if existing_vote:
        flash('You have already voted on this thread.', 'info')
    else:
        # Create new vote
        vote = Vote(
            user_id=current_user.id,
            thread_id=thread.id
        )
        db.session.add(vote)
        
        # Increment thread upvotes
        thread.upvotes += 1
        db.session.commit()
        
        flash('Thread upvoted!', 'success')
    
    return redirect(url_for('threads.view_thread', board_slug=board_slug, thread_id=thread_id))


@threads_bp.route('/<board_slug>/thread/<int:thread_id>/post/<int:post_id>/upvote', methods=['POST'])
@login_required
def upvote_post(board_slug, thread_id, post_id):
    board = Board.query.filter_by(slug=board_slug).first_or_404()
    thread = Thread.query.filter_by(id=thread_id, board_id=board.id).first_or_404()
    post = Post.query.filter_by(id=post_id, thread_id=thread.id).first_or_404()
    
    # Check if user already voted
    existing_vote = Vote.query.filter_by(
        user_id=current_user.id,
        post_id=post.id
    ).first()
    
    if existing_vote:
        flash('You have already voted on this post.', 'info')
    else:
        # Create new vote
        vote = Vote(
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(vote)
        
        # Increment post upvotes
        post.upvotes += 1
        db.session.commit()
        
        flash('Post upvoted!', 'success')
    
    return redirect(url_for('threads.view_thread', board_slug=board_slug, thread_id=thread_id))
