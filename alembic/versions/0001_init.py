from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gin;")

    op.create_table('users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(120), nullable=False),
        sa.Column('language', sa.String(8), nullable=False, server_default='en'),
        sa.Column('timezone', sa.String(64), nullable=False, server_default='Europe/Amsterdam'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('profile', postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    )

    op.create_table('listings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('game', sa.String(32), nullable=False, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('region', sa.String(64)),
        sa.Column('server', sa.String(128)),
        sa.Column('language', sa.String(8), nullable=False, index=True),
        sa.Column('playstyle', sa.String(32)),
        sa.Column('voice', sa.String(32)),
        sa.Column('availability', sa.String(128)),
        sa.Column('team_need', postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('tags', postgresql.ARRAY(sa.String(32)), nullable=False, server_default='{}'),
        sa.Column('game_specific', postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    op.create_index('ix_listings_tags_gin', 'listings', ['tags'], postgresql_using='gin')
    op.create_index('ix_listings_game_specific_gin', 'listings', ['game_specific'], postgresql_using='gin')
    op.create_index('ix_listings_title_trgm', 'listings', [sa.text('title gin_trgm_ops')], postgresql_using='gin')

    op.create_table('messages',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('listing_id', sa.Integer, sa.ForeignKey('listings.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('sender_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('receiver_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    op.create_table('reports',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('reporter_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('listing_id', sa.Integer, sa.ForeignKey('listings.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('message_id', sa.Integer, sa.ForeignKey('messages.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('reason', sa.String(64), nullable=False),
        sa.Column('details', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='open')
    )

    op.create_table('likes',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('listing_id', sa.Integer, sa.ForeignKey('listings.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('user_id','listing_id', name='uq_like')
    )

def downgrade():
    op.drop_table('likes')
    op.drop_table('reports')
    op.drop_table('messages')
    op.drop_index('ix_listings_title_trgm', table_name='listings')
    op.drop_index('ix_listings_game_specific_gin', table_name='listings')
    op.drop_index('ix_listings_tags_gin', table_name='listings')
    op.drop_table('listings')
    op.drop_table('users')
