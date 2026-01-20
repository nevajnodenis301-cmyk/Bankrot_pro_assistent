import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    """Test health endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_create_case(client: AsyncClient):
    """Test case creation"""
    case_data = {
        "full_name": "Иванов Иван Иванович",
        "total_debt": 500000.00,
        "telegram_user_id": 12345678,
    }

    response = await client.post("/api/cases", json=case_data)
    assert response.status_code == 201

    data = response.json()
    assert data["full_name"] == case_data["full_name"]
    assert data["case_number"].startswith("BP-")
    assert data["status"] == "new"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_cases(client: AsyncClient):
    """Test getting list of cases"""
    # Create test case first
    case_data = {
        "full_name": "Петров Петр Петрович",
        "total_debt": 300000.00,
    }
    await client.post("/api/cases", json=case_data)

    # Get all cases
    response = await client.get("/api/cases")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_case_by_id(client: AsyncClient):
    """Test getting case by ID"""
    # Create test case
    case_data = {
        "full_name": "Сидоров Сидор Сидорович",
        "total_debt": 750000.00,
    }
    create_response = await client.post("/api/cases", json=case_data)
    case_id = create_response.json()["id"]

    # Get case by ID
    response = await client.get(f"/api/cases/{case_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == case_id
    assert data["full_name"] == case_data["full_name"]


@pytest.mark.asyncio
async def test_get_case_public(client: AsyncClient):
    """Test getting public case data"""
    # Create test case with confidential data
    case_data = {"full_name": "Федоров Федор Федорович", "total_debt": 400000.00}
    create_response = await client.post("/api/cases", json=case_data)
    case_id = create_response.json()["id"]

    # Update with confidential data
    update_data = {
        "passport_series": "1234",
        "passport_number": "567890",
        "inn": "123456789012",
    }
    await client.put(f"/api/cases/{case_id}", json=update_data)

    # Get public data (should not include passport, INN)
    response = await client.get(f"/api/cases/{case_id}/public")
    assert response.status_code == 200

    data = response.json()
    assert "passport_series" not in data
    assert "passport_number" not in data
    assert "inn" not in data
    assert data["full_name"] == case_data["full_name"]


@pytest.mark.asyncio
async def test_update_case(client: AsyncClient):
    """Test updating case"""
    # Create test case
    case_data = {"full_name": "Александров Александр Александрович", "total_debt": 600000.00}
    create_response = await client.post("/api/cases", json=case_data)
    case_id = create_response.json()["id"]

    # Update case
    update_data = {
        "status": "in_progress",
        "phone": "+79001234567",
        "email": "test@example.com",
    }
    response = await client.put(f"/api/cases/{case_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "in_progress"
    assert data["phone"] == "+79001234567"
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_delete_case(client: AsyncClient):
    """Test deleting case"""
    # Create test case
    case_data = {"full_name": "Николаев Николай Николаевич", "total_debt": 200000.00}
    create_response = await client.post("/api/cases", json=case_data)
    case_id = create_response.json()["id"]

    # Delete case
    response = await client.delete(f"/api/cases/{case_id}")
    assert response.status_code == 204

    # Verify deletion
    get_response = await client.get(f"/api/cases/{case_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_add_creditor(client: AsyncClient):
    """Test adding creditor to case"""
    # Create test case
    case_data = {"full_name": "Михайлов Михаил Михайлович", "total_debt": 450000.00}
    create_response = await client.post("/api/cases", json=case_data)
    case_id = create_response.json()["id"]

    # Add creditor
    creditor_data = {
        "name": "ПАО Сбербанк",
        "creditor_type": "bank",
        "debt_amount": 300000.00,
        "debt_type": "credit",
    }
    response = await client.post(f"/api/creditors/{case_id}", json=creditor_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == creditor_data["name"]
    assert data["creditor_type"] == "bank"


@pytest.mark.asyncio
async def test_filter_cases_by_telegram_user(client: AsyncClient):
    """Test filtering cases by Telegram user ID"""
    telegram_user_id = 99999999

    # Create test case with telegram_user_id
    case_data = {
        "full_name": "Дмитриев Дмитрий Дмитриевич",
        "total_debt": 350000.00,
        "telegram_user_id": telegram_user_id,
    }
    await client.post("/api/cases", json=case_data)

    # Get cases for this user
    response = await client.get(f"/api/cases?telegram_user_id={telegram_user_id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0
    # Note: Public endpoint doesn't return telegram_user_id, but filters correctly
