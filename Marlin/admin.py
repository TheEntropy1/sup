import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from models import User, Board, Thread, Post, Image
from forms import BoardForm, ModerateThreadForm, ModeratePostForm
from mega_utils import mega_handler

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

# Admin authentication check
@admin_bp.before_request
def check_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('You do not have permission to access the admin area', 'danger')
        return redirect(url_for('boards.index'))


@admin_bp.route('/')
@login_required
def index():
    return render_template('admin/index.html', title='Admin Dashboard')


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Get statistics for dashboard
    total_users = User.query.count()
    total_boards = Board.query.count()
    total_threads = Thread.query.count()
    total_posts = Post.query.count()
    
    # Get recent threads
    recent_threads = Thread.query.order_by(Thread.created_at.desc()).limit(10).all()
    
    # Get popular threads
    popular_threads = Thread.query.order_by(Thread.upvotes.desc()).limit(10).all()
    
    return render_template(
        'admin/dashboard.html',
        title='Admin Dashboard',
        total_users=total_users,
        total_boards=total_boards,
        total_threads=total_threads,
        total_posts=total_posts,
        recent_threads=recent_threads,
        popular_threads=popular_threads
    )


@admin_bp.route('/boards')
@login_required
def boards():
    all_boards = Board.query.order_by(Board.category, Board.name).all()
    return render_template('admin/boards.html', title='Manage Boards', boards=all_boards)


@admin_bp.route('/boards/new', methods=['GET', 'POST'])
@login_required
def new_board():
    form = BoardForm()
    if form.validate_on_submit():
        # Check if board slug already exists
        existing_board = Board.query.filter_by(slug=form.slug.data).first()
        if existing_board:
            flash(f'Board with slug /{form.slug.data}/ already exists', 'danger')
            return redirect(url_for('admin.new_board'))
        
        # Create new board
        board = Board(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data,
            category=form.category.data,
            nsfw=form.nsfw.data
        )
        
        db.session.add(board)
        db.session.commit()
        
        flash(f'Board /{form.slug.data}/ created successfully', 'success')
        return redirect(url_for('admin.boards'))
    
    return render_template('admin/board_form.html', title='Create Board', form=form)


@admin_bp.route('/boards/edit/<int:board_id>', methods=['GET', 'POST'])
@login_required
def edit_board(board_id):
    board = Board.query.get_or_404(board_id)
    form = BoardForm(obj=board)
    
    if form.validate_on_submit():
        # Check slug conflicts only if slug changed
        if form.slug.data != board.slug:
            existing_board = Board.query.filter_by(slug=form.slug.data).first()
            if existing_board:
                flash(f'Board with slug /{form.slug.data}/ already exists', 'danger')
                return redirect(url_for('admin.edit_board', board_id=board_id))
        
        # Update board
        board.name = form.name.data
        board.slug = form.slug.data
        board.description = form.description.data
        board.category = form.category.data
        board.nsfw = form.nsfw.data
        
        db.session.commit()
        
        flash(f'Board /{form.slug.data}/ updated successfully', 'success')
        return redirect(url_for('admin.boards'))
    
    return render_template('admin/board_form.html', title='Edit Board', form=form, board=board)


@admin_bp.route('/boards/delete/<int:board_id>', methods=['POST'])
@login_required
def delete_board(board_id):
    board = Board.query.get_or_404(board_id)
    
    # Get all threads in the board
    threads = Thread.query.filter_by(board_id=board.id).all()
    
    # Delete all images from Mega.nz
    for thread in threads:
        posts = Post.query.filter_by(thread_id=thread.id).all()
        for post in posts:
            images = Image.query.filter_by(post_id=post.id).all()
            for image in images:
                if image.mega_url:
                    mega_handler.delete_file(image.mega_url)
    
    # The database cascade will handle deleting threads, posts, and images
    db.session.delete(board)
    db.session.commit()
    
    flash(f'Board {board.name} deleted successfully', 'success')
    return redirect(url_for('admin.boards'))


@admin_bp.route('/moderate/thread/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def moderate_thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    form = ModerateThreadForm(obj=thread)
    
    if form.validate_on_submit():
        if form.delete.data:
            # Delete all images from Mega.nz
            posts = Post.query.filter_by(thread_id=thread.id).all()
            for post in posts:
                images = Image.query.filter_by(post_id=post.id).all()
                for image in images:
                    if image.mega_url:
                        mega_handler.delete_file(image.mega_url)
            
            # Delete the thread
            db.session.delete(thread)
            db.session.commit()
            
            flash(f'Thread {thread_id} deleted successfully', 'success')
            return redirect(url_for('boards.view_board', board_slug=thread.board.slug))
        else:
            # Update thread properties
            thread.sticky = form.sticky.data
            thread.locked = form.locked.data
            
            db.session.commit()
            
            flash(f'Thread {thread_id} updated successfully', 'success')
            return redirect(url_for('threads.view_thread', board_slug=thread.board.slug, thread_id=thread.id))
    
    return render_template('admin/moderate_thread.html', title='Moderate Thread', form=form, thread=thread)


@admin_bp.route('/moderate/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def moderate_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = ModeratePostForm()
    
    if form.validate_on_submit():
        if form.delete.data:
            # Delete all images from Mega.nz
            images = Image.query.filter_by(post_id=post.id).all()
            for image in images:
                if image.mega_url:
                    mega_handler.delete_file(image.mega_url)
            
            # Get thread info before deleting the post
            thread_id = post.thread_id
            board_slug = post.thread.board.slug
            
            # Delete the post
            db.session.delete(post)
            db.session.commit()
            
            flash(f'Post {post_id} deleted successfully', 'success')
            return redirect(url_for('threads.view_thread', board_slug=board_slug, thread_id=thread_id))
    
    return render_template('admin/moderate_post.html', title='Moderate Post', form=form, post=post)


@admin_bp.route('/users')
@login_required
def users():
    all_users = User.query.order_by(User.username).all()
    return render_template('admin/users.html', title='Manage Users', users=all_users)


@admin_bp.route('/users/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow removing admin status from yourself
    if user.id == current_user.id:
        flash('You cannot remove your own admin privileges', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} for {user.username}', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} deleted successfully', 'success')
    return redirect(url_for('admin.users'))
