"""initial migration

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    # books
    op.create_table(
        'books',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('author', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('isbn', sa.String(20), nullable=True),
        sa.Column('cover_url', sa.String(500), nullable=True),
        sa.Column('genre', sa.Enum(
            'fiction','non_fiction','fantasy','sci_fi','mystery','romance',
            'thriller','horror','biography','history','science','self_help',
            'children','poetry','other', name='bookgenre'
        ), nullable=False),
        sa.Column('published_year', sa.Integer(), nullable=True),
        sa.Column('language', sa.String(50), nullable=False, server_default='Ukrainian'),
        sa.Column('condition', sa.Enum('new','good','fair','poor', name='bookcondition'), nullable=False, server_default='good'),
        sa.Column('is_available_for_exchange', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_books_id', 'books', ['id'])
    op.create_index('ix_books_title', 'books', ['title'])
    op.create_index('ix_books_author', 'books', ['author'])
    op.create_unique_constraint('uq_books_isbn', 'books', ['isbn'])

    # reviews
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('book_id', sa.Integer(), sa.ForeignKey('books.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_reviews_id', 'reviews', ['id'])

    # exchanges
    op.create_table(
        'exchanges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('requester_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('offered_book_id', sa.Integer(), sa.ForeignKey('books.id'), nullable=False),
        sa.Column('requested_book_id', sa.Integer(), sa.ForeignKey('books.id'), nullable=False),
        sa.Column('status', sa.Enum('pending','accepted','completed','rejected','cancelled', name='exchangestatus'), nullable=False, server_default='pending'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_exchanges_id', 'exchanges', ['id'])

    # wishlist_items
    op.create_table(
        'wishlist_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('book_id', sa.Integer(), sa.ForeignKey('books.id'), nullable=False),
        sa.Column('added_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # messages
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exchange_id', sa.Integer(), sa.ForeignKey('exchanges.id'), nullable=False),
        sa.Column('sender_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_messages_id', 'messages', ['id'])


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('wishlist_items')
    op.drop_table('exchanges')
    op.drop_table('reviews')
    op.drop_table('books')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS bookgenre')
    op.execute('DROP TYPE IF EXISTS bookcondition')
    op.execute('DROP TYPE IF EXISTS exchangestatus')
