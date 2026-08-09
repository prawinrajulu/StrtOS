import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

# Pooler URL for Supabase project wwarebryzujdzrjiyjfb
pooler_url = "postgresql+asyncpg://postgres.wwarebryzujdzrjiyjfb:pprawin48%402006@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

async def test():
    print("Testing Supabase Connection Pooler:", pooler_url)
    try:
        engine = create_async_engine(pooler_url)
        async with engine.connect() as conn:
            print("SUCCESS! CONNECTED TO SUPABASE POSTGRESQL!")
    except Exception as e:
        print("Connection status:", type(e), e)

if __name__ == "__main__":
    asyncio.run(test())
