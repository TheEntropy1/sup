import logging
from flask import Blueprint, render_template, redirect, url_for, request, current_app
from app import db
from models import Board, Thread, Post, Image

logger = logging.getLogger(__name__)

boards_bp = Blueprint('boards', __name__)

def create_default_boards():
    """Create default boards if they don't exist"""
    default_boards = [
        # Japanese Culture (excluding these as per requirements)
        # Modified board list based on the requirements
        
        # Creative
        {'name': 'Oekaki', 'slug': 'i', 'description': 'Oekaki', 'category': 'Creative', 'nsfw': False},
        {'name': 'Papercraft & Origami', 'slug': 'po', 'description': 'Papercraft & Origami', 'category': 'Creative', 'nsfw': False},
        {'name': 'Photography', 'slug': 'p', 'description': 'Photography', 'category': 'Creative', 'nsfw': False},
        {'name': 'Food & Cooking', 'slug': 'ck', 'description': 'Food & Cooking', 'category': 'Creative', 'nsfw': False},
        {'name': 'Artwork/Critique', 'slug': 'ic', 'description': 'Artwork/Critique', 'category': 'Creative', 'nsfw': False},
        {'name': 'Wallpapers/General', 'slug': 'wg', 'description': 'Wallpapers/General', 'category': 'Creative', 'nsfw': False},
        {'name': 'Literature', 'slug': 'lit', 'description': 'Literature', 'category': 'Creative', 'nsfw': False},
        {'name': 'Music', 'slug': 'mu', 'description': 'Music', 'category': 'Creative', 'nsfw': False},
        {'name': 'Fashion', 'slug': 'fa', 'description': 'Fashion', 'category': 'Creative', 'nsfw': False},
        {'name': '3DCG', 'slug': '3', 'description': '3DCG', 'category': 'Creative', 'nsfw': False},
        {'name': 'Graphic Design', 'slug': 'gd', 'description': 'Graphic Design', 'category': 'Creative', 'nsfw': False},
        {'name': 'Do-It-Yourself', 'slug': 'diy', 'description': 'Do-It-Yourself', 'category': 'Creative', 'nsfw': False},
        {'name': 'Worksafe GIF', 'slug': 'wsg', 'description': 'Worksafe GIF', 'category': 'Creative', 'nsfw': False},
        {'name': 'Quests', 'slug': 'qst', 'description': 'Quests', 'category': 'Creative', 'nsfw': False},
        
        # Interests
        {'name': 'Comics & Cartoons', 'slug': 'co', 'description': 'Comics & Cartoons', 'category': 'Interests', 'nsfw': False},
        {'name': 'Technology', 'slug': 'g', 'description': 'Technology', 'category': 'Interests', 'nsfw': False},
        {'name': 'Television & Film', 'slug': 'tv', 'description': 'Television & Film', 'category': 'Interests', 'nsfw': False},
        {'name': 'Weapons', 'slug': 'k', 'description': 'Weapons', 'category': 'Interests', 'nsfw': False},
        {'name': 'Auto', 'slug': 'o', 'description': 'Auto', 'category': 'Interests', 'nsfw': False},
        {'name': 'Animals & Nature', 'slug': 'an', 'description': 'Animals & Nature', 'category': 'Interests', 'nsfw': False},
        {'name': 'Traditional Games', 'slug': 'tg', 'description': 'Traditional Games', 'category': 'Interests', 'nsfw': False},
        {'name': 'Sports', 'slug': 'sp', 'description': 'Sports', 'category': 'Interests', 'nsfw': False},
        {'name': 'Extreme Sports', 'slug': 'xs', 'description': 'Extreme Sports', 'category': 'Interests', 'nsfw': False},
        {'name': 'Professional Wrestling', 'slug': 'pw', 'description': 'Professional Wrestling', 'category': 'Interests', 'nsfw': False},
        {'name': 'Science & Math', 'slug': 'sci', 'description': 'Science & Math', 'category': 'Interests', 'nsfw': False},
        {'name': 'History & Humanities', 'slug': 'his', 'description': 'History & Humanities', 'category': 'Interests', 'nsfw': False},
        {'name': 'International', 'slug': 'int', 'description': 'International', 'category': 'Interests', 'nsfw': False},
        {'name': 'Outdoors', 'slug': 'out', 'description': 'Outdoors', 'category': 'Interests', 'nsfw': False},
        {'name': 'Toys', 'slug': 'toy', 'description': 'Toys', 'category': 'Interests', 'nsfw': False},
        
        # Video Games
        {'name': 'Video Games', 'slug': 'v', 'description': 'Video Games', 'category': 'Video Games', 'nsfw': False},
        {'name': 'Video Game Generals', 'slug': 'vg', 'description': 'Video Game Generals', 'category': 'Video Games', 'nsfw': False},
        {'name': 'Video Games/Multiplayer', 'slug': 'vm', 'description': 'Video Games/Multiplayer', 'category': 'Video Games', 'nsfw': False},
        {'name': 'Video Games/Mobile', 'slug': 'vmg', 'description': 'Video Games/Mobile', 'category': 'Video Games', 'nsfw': False},
        {'name': 'Pokémon', 'slug': 'pkmn', 'description': 'Pokémon', 'category': 'Video Games', 'nsfw': False},
        {'name': 'Retro Games', 'slug': 'vr', 'description': 'Retro Games', 'category': 'Video Games', 'nsfw': False},
        {'name': 'Video Games/RPG', 'slug': 'vrpg', 'description': 'Video Games/RPG', 'category': 'Video Games', 'nsfw': False},
        {'name': 'Video Games/Strategy', 'slug': 'vst', 'description': 'Video Games/Strategy', 'category': 'Video Games', 'nsfw': False},
        
        # Other
        {'name': 'Business & Finance', 'slug': 'biz', 'description': 'Business & Finance', 'category': 'Other', 'nsfw': False},
        {'name': 'Travel', 'slug': 'trv', 'description': 'Travel', 'category': 'Other', 'nsfw': False},
        {'name': 'Fitness', 'slug': 'fit', 'description': 'Fitness', 'category': 'Other', 'nsfw': False},
        {'name': 'Paranormal', 'slug': 'x', 'description': 'Paranormal', 'category': 'Other', 'nsfw': False},
        {'name': 'Advice', 'slug': 'adv', 'description': 'Advice', 'category': 'Other', 'nsfw': False},
        {'name': 'LGBT', 'slug': 'lgbt', 'description': 'LGBT', 'category': 'Other', 'nsfw': False},
        {'name': 'Pony', 'slug': 'mlp', 'description': 'Pony', 'category': 'Other', 'nsfw': False},
        {'name': 'Current News', 'slug': 'news', 'description': 'Current News', 'category': 'Other', 'nsfw': False},
        {'name': 'Worksafe Requests', 'slug': 'wsr', 'description': 'Worksafe Requests', 'category': 'Other', 'nsfw': False},
        {'name': 'Very Important Posts', 'slug': 'vip', 'description': 'Very Important Posts', 'category': 'Other', 'nsfw': False},
        {'name': 'Random', 'slug': 'r', 'description': 'Random', 'category': 'Other', 'nsfw': False},
        {'name': 'ROBOT9001', 'slug': 'r9k', 'description': 'ROBOT9001', 'category': 'Other', 'nsfw': False},
        {'name': 'Politically Incorrect', 'slug': 'pol', 'description': 'Politically Incorrect', 'category': 'Other', 'nsfw': False},
        {'name': 'International/Random', 'slug': 'intl', 'description': 'International/Random', 'category': 'Other', 'nsfw': False},
        {'name': 'Cams & Meetups', 'slug': 'soc', 'description': 'Cams & Meetups', 'category': 'Other', 'nsfw': False},
        {'name': 'Virtual YouTubers', 'slug': 'vt', 'description': 'Virtual YouTubers', 'category': 'Other', 'nsfw': False},
        
        # Adult (NSFW)
        {'name': 'Sexy Beautiful Women', 'slug': 'sbw', 'description': 'Sexy Beautiful Women', 'category': 'Adult', 'nsfw': True},
        {'name': 'Hardcore', 'slug': 'hc', 'description': 'Hardcore', 'category': 'Adult', 'nsfw': True},
        {'name': 'Handsome Men', 'slug': 'hm', 'description': 'Handsome Men', 'category': 'Adult', 'nsfw': True},
        {'name': 'Hentai', 'slug': 'h', 'description': 'Hentai', 'category': 'Adult', 'nsfw': True},
        {'name': 'Ecchi', 'slug': 'e', 'description': 'Ecchi', 'category': 'Adult', 'nsfw': True},
        {'name': 'Yuri', 'slug': 'u', 'description': 'Yuri', 'category': 'Adult', 'nsfw': True},
        {'name': 'Hentai/Alternative', 'slug': 'd', 'description': 'Hentai/Alternative', 'category': 'Adult', 'nsfw': True},
        {'name': 'Yaoi', 'slug': 'y', 'description': 'Yaoi', 'category': 'Adult', 'nsfw': True},
        {'name': 'Torrents', 'slug': 't', 'description': 'Torrents', 'category': 'Adult', 'nsfw': True},
        {'name': 'High Resolution', 'slug': 'hr', 'description': 'High Resolution', 'category': 'Adult', 'nsfw': True},
        {'name': 'Adult GIF', 'slug': 'gif', 'description': 'Adult GIF', 'category': 'Adult', 'nsfw': True},
        {'name': 'Adult Cartoons', 'slug': 'aco', 'description': 'Adult Cartoons', 'category': 'Adult', 'nsfw': True},
        {'name': 'Adult Requests', 'slug': 'areq', 'description': 'Adult Requests', 'category': 'Adult', 'nsfw': True},
        
        # Custom boards as requested
        {'name': 'Russian Women', 'slug': 'rw', 'description': 'Russian Women', 'category': 'Custom', 'nsfw': False},
        {'name': 'Russian Beauty', 'slug': 'rb', 'description': 'Russian Beauty', 'category': 'Custom', 'nsfw': False},
        {'name': 'Pune', 'slug': 'pune', 'description': 'Pune', 'category': 'Custom', 'nsfw': False},
    ]
    
    # Check existing boards
    for board_info in default_boards:
        board = Board.query.filter_by(slug=board_info['slug']).first()
        if not board:
            logger.info(f"Creating board /{board_info['slug']}/ - {board_info['name']}")
            board = Board(
                name=board_info['name'],
                slug=board_info['slug'],
                description=board_info['description'],
                category=board_info['category'],
                nsfw=board_info['nsfw']
            )
            db.session.add(board)
    
    db.session.commit()
    logger.info("Default boards created successfully")


@boards_bp.route('/boards')
def index():
    # Get all boards grouped by category
    boards_by_category = {}
    
    all_boards = Board.query.order_by(Board.category, Board.name).all()
    
    for board in all_boards:
        if board.category not in boards_by_category:
            boards_by_category[board.category] = []
        boards_by_category[board.category].append(board)
    
    # Get popular threads for display on the home page
    popular_threads = Thread.query.order_by(Thread.upvotes.desc()).limit(10).all()
    
    return render_template(
        'index.html', 
        title='Marlin - Boards', 
        boards_by_category=boards_by_category,
        popular_threads=popular_threads
    )


@boards_bp.route('/<board_slug>/')
def view_board(board_slug):
    board = Board.query.filter_by(slug=board_slug).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Threads per page
    
    # Get threads with first post and image preloaded
    threads_query = Thread.query.filter_by(board_id=board.id)
    
    # Handle sorting
    sort = request.args.get('sort', 'bump')
    if sort == 'new':
        threads_query = threads_query.order_by(Thread.created_at.desc())
    elif sort == 'hot':
        threads_query = threads_query.order_by(Thread.upvotes.desc())
    else:  # Default 'bump' sort by activity
        threads_query = threads_query.order_by(Thread.sticky.desc(), Thread.updated_at.desc())
    
    # Get paginated threads
    threads_pagination = threads_query.paginate(page=page, per_page=per_page)
    
    # Get first post and image for each thread
    threads_data = []
    for thread in threads_pagination.items:
        first_post = Post.query.filter_by(thread_id=thread.id).order_by(Post.created_at).first()
        first_image = None
        if first_post:
            first_image = Image.query.filter_by(post_id=first_post.id).first()
        
        threads_data.append({
            'thread': thread,
            'first_post': first_post,
            'first_image': first_image,
            'reply_count': Post.query.filter_by(thread_id=thread.id).count() - 1  # Subtract OP
        })
    
    return render_template(
        'board.html',
        title=f'/{board.slug}/ - {board.name}',
        board=board,
        threads_data=threads_data,
        pagination=threads_pagination,
        sort=sort
    )
