#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/root/bankrot_bot/api')
os.chdir('/root/bankrot_bot/api')
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://bankrot:bankrot@localhost:5432/bankrot'

import asyncio
from database import async_session_maker
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models import Case
from services.document_service import generate_bankruptcy_petition

async def test_generate():
    async with async_session_maker() as session:
        # Get a case with all relationships loaded
        result = await session.execute(
            select(Case)
            .options(
                selectinload(Case.creditors),
                selectinload(Case.debts),
                selectinload(Case.children),
                selectinload(Case.income_records),
                selectinload(Case.properties),
                selectinload(Case.transactions)
            )
            .limit(1)
        )
        case = result.scalar_one_or_none()
        
        if not case:
            print("❌ No cases found")
            return
        
        print(f"📄 Generating document for: {case.full_name}")
        print(f"   Case: {case.case_number}")
        
        try:
            buffer = generate_bankruptcy_petition(case)
            
            # Save to file for testing
            output_path = f"/root/bankrot_bot/generated/test_petition_{case.case_number}.docx"
            with open(output_path, 'wb') as f:
                f.write(buffer.getvalue())
            
            print(f"✅ Document generated successfully!")
            print(f"   Saved to: {output_path}")
            print(f"   Size: {len(buffer.getvalue())} bytes")
            
        except Exception as e:
            print(f"❌ Error generating document: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generate())
