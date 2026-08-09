import asyncio
import socket

hosts = [
    "db.lnybjagetijsbhkmarwe.supabase.co",
    "aws-0-ap-south-1.pooler.supabase.com",
    "aws-0-us-east-1.pooler.supabase.com"
]

for h in hosts:
    try:
        ip = socket.gethostbyname(h)
        print(f"HOST: {h} -> RESOLVED IP: {ip}")
    except Exception as e:
        print(f"HOST: {h} -> DNS FAIL: {e}")
