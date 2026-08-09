import asyncio
import asyncpg

async def check_local_pg():
    try:
        conn = await asyncpg.connect(user="postgres", password="postgres", database="postgres", host="localhost", port=5432)
        print("LOCAL POSTGRESQL IS ONLINE!")
        await conn.execute("CREATE DATABASE strtos_db;")
        print("DATABASE strtos_db CREATED!")
        await conn.close()
    except Exception as e:
        print("Local PG status:", type(e), e)

if __name__ == "__main__":
    asyncio.run(check_local_pg())
