#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/root/bankrot_bot/api')
os.chdir('/root/bankrot_bot/api')
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://bankrot:bankrot@localhost:5432/bankrot'

import asyncio
from database import async_session_maker
from sqlalchemy import select
from models import Case

async def check_cases():
    async with async_session_maker() as session:
        result = await session.execute(select(Case).limit(5))
        cases = result.scalars().all()
        
        if cases:
            print(f"✅ Found {len(cases)} test case(s):\n")
            for case in cases:
                print(f"  • {case.case_number} - {case.full_name}")
                print(f"    Status: {case.status}")
                print(f"    Total debt: {case.total_debt}")
                print()
        else:
            print("❌ No cases found in database")
            print("   You'll need to create a test case first")

if __name__ == "__main__":
    asyncio.run(check_cases())
