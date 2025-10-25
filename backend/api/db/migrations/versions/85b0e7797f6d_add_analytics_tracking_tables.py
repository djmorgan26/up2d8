"""add_analytics_tracking_tables

Revision ID: 85b0e7797f6d
Revises: ffee810ddad2
Create Date: 2025-10-25 16:26:16.466557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85b0e7797f6d'
down_revision: Union[str, None] = 'ffee810ddad2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Source Performance Analytics
    # Tracks aggregate metrics per source to understand which sources users engage with
    op.create_table(
        'source_analytics',
        sa.Column('source_id', sa.String(100), sa.ForeignKey('sources.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('total_articles_delivered', sa.Integer, default=0),
        sa.Column('total_positive_feedback', sa.Integer, default=0),
        sa.Column('total_negative_feedback', sa.Integer, default=0),
        sa.Column('total_clicks', sa.Integer, default=0),
        sa.Column('avg_relevance_score', sa.DECIMAL(5, 2), default=0),
        sa.Column('engagement_rate', sa.DECIMAL(5, 4), default=0),  # (positive + clicks) / delivered
        sa.Column('last_updated', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Company Performance Analytics
    # Tracks how users respond to content about specific companies
    op.create_table(
        'company_analytics',
        sa.Column('company_name', sa.String(255), primary_key=True),
        sa.Column('total_mentions', sa.Integer, default=0),
        sa.Column('total_positive_feedback', sa.Integer, default=0),
        sa.Column('total_negative_feedback', sa.Integer, default=0),
        sa.Column('total_users_interested', sa.Integer, default=0),
        sa.Column('sentiment_score', sa.DECIMAL(5, 2), default=0),  # positive / (positive + negative)
        sa.Column('popularity_score', sa.DECIMAL(10, 2), default=0),  # weighted score
        sa.Column('last_updated', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_company_popularity', 'company_analytics', ['popularity_score'])

    # Industry Performance Analytics
    # Tracks user engagement with different industry topics
    op.create_table(
        'industry_analytics',
        sa.Column('industry_name', sa.String(255), primary_key=True),
        sa.Column('total_mentions', sa.Integer, default=0),
        sa.Column('total_positive_feedback', sa.Integer, default=0),
        sa.Column('total_negative_feedback', sa.Integer, default=0),
        sa.Column('total_users_interested', sa.Integer, default=0),
        sa.Column('sentiment_score', sa.DECIMAL(5, 2), default=0),
        sa.Column('popularity_score', sa.DECIMAL(10, 2), default=0),
        sa.Column('last_updated', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_industry_popularity', 'industry_analytics', ['popularity_score'])

    # Content Performance Analytics
    # Tracks individual article performance for A/B testing and quality analysis
    op.create_table(
        'article_analytics',
        sa.Column('article_id', sa.dialects.postgresql.UUID(as_uuid=False), sa.ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('times_delivered', sa.Integer, default=0),
        sa.Column('unique_users_delivered', sa.Integer, default=0),
        sa.Column('positive_feedback_count', sa.Integer, default=0),
        sa.Column('negative_feedback_count', sa.Integer, default=0),
        sa.Column('click_count', sa.Integer, default=0),
        sa.Column('avg_relevance_score', sa.DECIMAL(5, 2), default=0),
        sa.Column('engagement_rate', sa.DECIMAL(5, 4), default=0),
        sa.Column('last_updated', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_article_engagement', 'article_analytics', ['engagement_rate'])

    # Daily Aggregated Analytics
    # Time-series data for trend analysis and growth tracking
    op.create_table(
        'daily_analytics',
        sa.Column('date', sa.Date, primary_key=True),
        sa.Column('total_digests_sent', sa.Integer, default=0),
        sa.Column('total_articles_delivered', sa.Integer, default=0),
        sa.Column('total_feedback_received', sa.Integer, default=0),
        sa.Column('total_positive_feedback', sa.Integer, default=0),
        sa.Column('total_negative_feedback', sa.Integer, default=0),
        sa.Column('total_clicks', sa.Integer, default=0),
        sa.Column('active_users', sa.Integer, default=0),
        sa.Column('avg_relevance_score', sa.DECIMAL(5, 2), default=0),
        sa.Column('overall_engagement_rate', sa.DECIMAL(5, 4), default=0),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # User Cohort Analytics
    # Track user segments for personalization insights
    op.create_table(
        'user_cohort_analytics',
        sa.Column('cohort_name', sa.String(100), primary_key=True),
        sa.Column('cohort_definition', sa.JSON),  # Criteria for this cohort
        sa.Column('total_users', sa.Integer, default=0),
        sa.Column('avg_feedback_count', sa.DECIMAL(10, 2), default=0),
        sa.Column('avg_engagement_rate', sa.DECIMAL(5, 4), default=0),
        sa.Column('top_companies', sa.JSON, default=[]),
        sa.Column('top_industries', sa.JSON, default=[]),
        sa.Column('top_sources', sa.JSON, default=[]),
        sa.Column('last_updated', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('user_cohort_analytics')
    op.drop_table('daily_analytics')
    op.drop_index('idx_article_engagement')
    op.drop_table('article_analytics')
    op.drop_index('idx_industry_popularity')
    op.drop_table('industry_analytics')
    op.drop_index('idx_company_popularity')
    op.drop_table('company_analytics')
    op.drop_table('source_analytics')
