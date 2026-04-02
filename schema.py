import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal

    @field_validator("amount")
    @classmethod
    def positive_amount(cls, i_amount: Decimal) -> Decimal:
        if i_amount <= 0:
            raise ValueError("Amount must be positive")
        return i_amount


class WalletResponse(BaseModel):
    id: uuid.UUID
    balance: Decimal

    model_config = ConfigDict(from_attributes=True)


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wallet_uuid: uuid.UUID
    operation_type: OperationType
    amount: Decimal
    status: TransactionStatus
    created_at: datetime
