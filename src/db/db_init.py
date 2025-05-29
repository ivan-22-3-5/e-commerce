from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from src.db import models


# TODO: add support for ukrainian language
async def create_product_fulltext_index(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                    AND indexname = 'idx_product_tsv'
                ) THEN
                    CREATE INDEX idx_product_tsv
                    ON products
                    USING gin(to_tsvector('english', title || ' ' || description));
                END IF;
            END
            $$;
        """))


async def create_models(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


async def init_db(engine: AsyncEngine):
    await create_models(engine)
    await create_product_fulltext_index(engine)
