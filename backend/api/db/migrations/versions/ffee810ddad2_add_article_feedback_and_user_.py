"""add_article_feedback_and_user_preference_profile_tables

Revision ID: ffee810ddad2
Revises: ee97a9696601
Create Date: 2025-10-24 23:01:26.372785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffee810ddad2'
down_revision: Union[str, None] = 'ee97a9696601'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create article_feedback table for thumbs up/down tracking
    op.create_table(
        'article_feedback',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=False), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('article_id', sa.dialects.postgresql.UUID(as_uuid=False), sa.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('digest_id', sa.dialects.postgresql.UUID(as_uuid=False), sa.ForeignKey('digests.id', ondelete='CASCADE'), nullable=True),
        sa.Column('feedback_type', sa.String(20), nullable=False),
        sa.Column('feedback_text', sa.Text, nullable=True),
        sa.Column('feedback_source', sa.String(20), default='email'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("feedback_type IN ('thumbs_up', 'thumbs_down', 'not_relevant')", name='check_feedback_type'),
        sa.UniqueConstraint('user_id', 'article_id', 'digest_id', name='uq_user_article_digest_feedback')
    )

    # Create indexes for article_feedback
    op.create_index('idx_article_feedback_user', 'article_feedback', ['user_id', 'created_at'])
    op.create_index('idx_article_feedback_article', 'article_feedback', ['article_id'])
    op.create_index('idx_article_feedback_digest', 'article_feedback', ['digest_id'])
    op.create_index('idx_article_feedback_type', 'article_feedback', ['feedback_type'])

    # Create user_preference_profile table for learned preferences
    op.create_table(
        'user_preference_profile',
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=False), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('company_weights', sa.dialects.postgresql.JSONB, server_default='{}'),
        sa.Column('industry_weights', sa.dialects.postgresql.JSONB, server_default='{}'),
        sa.Column('topic_weights', sa.dialects.postgresql.JSONB, server_default='{}'),
        sa.Column('total_feedback_count', sa.Integer, default=0),
        sa.Column('positive_feedback_count', sa.Integer, default=0),
        sa.Column('negative_feedback_count', sa.Integer, default=0),
        sa.Column('avg_engagement_score', sa.DECIMAL(5, 2), default=0),
        sa.Column('last_updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now())
    )

    # Create user_engagement_metrics table
    op.create_table(
        'user_engagement_metrics',
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=False), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('total_emails_sent', sa.Integer, default=0),
        sa.Column('total_emails_opened', sa.Integer, default=0),
        sa.Column('total_links_clicked', sa.Integer, default=0),
        sa.Column('total_articles_clicked', sa.Integer, default=0),
        sa.Column('avg_articles_clicked_per_digest', sa.DECIMAL(5, 2), default=0),
        sa.Column('open_rate', sa.DECIMAL(5, 4), default=0),
        sa.Column('click_rate', sa.DECIMAL(5, 4), default=0),
        sa.Column('engagement_score', sa.DECIMAL(5, 2), default=0),
        sa.Column('avg_time_to_open_seconds', sa.Integer, default=0),
        sa.Column('last_calculated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now())
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('user_engagement_metrics')
    op.drop_table('user_preference_profile')

    # Drop indexes first
    op.drop_index('idx_article_feedback_type', 'article_feedback')
    op.drop_index('idx_article_feedback_digest', 'article_feedback')
    op.drop_index('idx_article_feedback_article', 'article_feedback')
    op.drop_index('idx_article_feedback_user', 'article_feedback')

    # Drop table
    op.drop_table('article_feedback')
