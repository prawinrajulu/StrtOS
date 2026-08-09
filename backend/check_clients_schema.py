import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name='clients' ORDER BY ordinal_position;"))
        rows = res.fetchall()
        print("COLUMNS IN SUPABASE 'clients' TABLE:")
        for r in rows:
            print(f" - {r[0]}: {r[1]} (nullable: {r[2]})")

if __name__ == "__main__":
    asyncio.run(check())
