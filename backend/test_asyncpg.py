import asyncio
import asyncpg

async def test():
    # Test connecting directly via IP with custom SNI hostname
    print("Testing asyncpg direct IP connection...")
    try:
        conn = await asyncpg.connect(
            user="postgres.lnybjagetijsbhkmarwe",
            password="prawin@20061",
            database="postgres",
            host="65.0.195.55",
            port=6543,
            server_settings={"application_name": "strtos_test"}
        )
        print("SUCCESSFULLY CONNECTED TO SUPABASE POSTGRESQL!")
        await conn.close()
    except Exception as e:
        print("Error:", type(e), e)

if __name__ == "__main__":
    asyncio.run(test())
