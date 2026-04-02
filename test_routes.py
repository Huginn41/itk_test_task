import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app
from models import OperationType, Transaction, TransactionStatus


class TestGetWallet:

    @pytest.fixture
    def client(self):
        with TestClient(app) as test_client:
            yield test_client

    def test_invalid_uuid(self, client):
        response = client.get("/api/v1/wallets/invalid-uuid")
        assert response.status_code == 422

    def test_get_wallet_not_found(self, client):
        with patch("routes.get_wallet", new_callable=AsyncMock) as mock:
            mock.side_effect = HTTPException(status_code=404, detail="Wallet not found")
            response = client.get(f"/api/v1/wallets/{uuid.uuid4()}")
            assert response.status_code == 404
            assert response.json()["detail"] == "Wallet not found"

    def test_get_wallet_success(self, client):
        wallet_id = uuid.uuid4()
        mock_wallet = AsyncMock()
        mock_wallet.id = wallet_id
        mock_wallet.balance = Decimal("500.00")

        with patch(
            "routes.get_wallet", new_callable=AsyncMock, return_value=mock_wallet
        ):
            response = client.get(f"/api/v1/wallets/{wallet_id}")
            assert response.status_code == 200
            assert response.json()["balance"] == "500.00"


class TestWalletOperation:

    @pytest.fixture
    def client(self):
        with TestClient(app) as test_client:
            yield test_client

    def test_invalid_uuid(self, client):
        response = client.post(
            "/api/v1/wallets/invalid-uuid/operation",
            json={"operation_type": "DEPOSIT", "amount": "100.00"},
        )
        assert response.status_code == 422

    def test_negative_amount(self, client):
        response = client.post(
            f"/api/v1/wallets/{uuid.uuid4()}/operation",
            json={"operation_type": "DEPOSIT", "amount": "-100.00"},
        )
        assert response.status_code == 422

    def test_zero_amount(self, client):
        response = client.post(
            f"/api/v1/wallets/{uuid.uuid4()}/operation",
            json={"operation_type": "DEPOSIT", "amount": "0"},
        )
        assert response.status_code == 422

    def test_invalid_operation_type(self, client):
        response = client.post(
            f"/api/v1/wallets/{uuid.uuid4()}/operation",
            json={"operation_type": "INVALID", "amount": "100.00"},
        )
        assert response.status_code == 422

    def test_deposit_success(self, client):
        wallet_id = uuid.uuid4()
        mock_transaction = Transaction(
            id=uuid.uuid4(),
            wallet_uuid=wallet_id,
            operation_type=OperationType.DEPOSIT,
            amount=Decimal("200.00"),
            status=TransactionStatus.SUCCESS,
            created_at=datetime.now(timezone.utc),
        )

        with patch(
            "routes.change_balance",
            new_callable=AsyncMock,
            return_value=mock_transaction,
        ):
            response = client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "DEPOSIT", "amount": "200.00"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "SUCCESS"
            assert data["operation_type"] == "DEPOSIT"
            assert data["amount"] == "200.00"

    def test_withdraw_success(self, client):
        wallet_id = uuid.uuid4()
        mock_transaction = Transaction(
            id=uuid.uuid4(),
            wallet_uuid=wallet_id,
            operation_type=OperationType.WITHDRAW,
            amount=Decimal("100.00"),
            status=TransactionStatus.SUCCESS,
            created_at=datetime.now(timezone.utc),
        )

        with patch(
            "routes.change_balance",
            new_callable=AsyncMock,
            return_value=mock_transaction,
        ):
            response = client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "WITHDRAW", "amount": "100.00"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "SUCCESS"
            assert data["operation_type"] == "WITHDRAW"

    def test_withdraw_insufficient(self, client):
        with patch("routes.change_balance", new_callable=AsyncMock) as mock:
            mock.side_effect = HTTPException(
                status_code=400, detail="Insufficient funds"
            )
            response = client.post(
                f"/api/v1/wallets/{uuid.uuid4()}/operation",
                json={"operation_type": "WITHDRAW", "amount": "9999.00"},
            )
            assert response.status_code == 400
            assert response.json()["detail"] == "Insufficient funds"

    def test_wallet_not_found(self, client):
        with patch("routes.change_balance", new_callable=AsyncMock) as mock:
            mock.side_effect = HTTPException(status_code=404, detail="Wallet not found")
            response = client.post(
                f"/api/v1/wallets/{uuid.uuid4()}/operation",
                json={"operation_type": "DEPOSIT", "amount": "100.00"},
            )
            assert response.status_code == 404
