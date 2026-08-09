import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

# Using pooler host with tenant prefix syntax for Supabase Connection Pooler
url = "postgresql+asyncpg://postgres.lnybjagetijsbhkmarwe:prawin%4020061@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

async def test():
    print("Testing Pooler Connection:", url)
    try:
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            print("SUCCESS! Connected to Supabase PostgreSQL via Pooler!")
    except Exception as e:
        print("Connection status:", type(e), e)

if __name__ == "__main__":
    asyncio.run(test())
