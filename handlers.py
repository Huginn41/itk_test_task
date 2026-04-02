import uuid
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Wallet, Transaction, TransactionStatus
from schema import OperationType


async def get_wallet(db: AsyncSession, wallet_uuid: uuid.UUID) -> Wallet:
    result = await db.execute(
        select(Wallet).where(Wallet.id == wallet_uuid)
    )
    wallet = result.scalar_one_or_none()

    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return wallet


async def change_balance(
        db: AsyncSession,
        wallet_uuid: uuid.UUID,
        operation_type: OperationType,
        amount: Decimal,
) -> Transaction:
    result = await db.execute(
        select(Wallet).where(Wallet.id == wallet_uuid)
        .with_for_update()
    )
    wallet = result.scalar_one_or_none()

    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if operation_type == OperationType.DEPOSIT:
        wallet.balance += amount
    else:
        if wallet.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        wallet.balance -= amount

    transaction = Transaction(
        wallet_uuid=wallet_uuid,
        operation_type=operation_type,
        amount=amount,
        status=TransactionStatus.SUCCESS,
    )
    db.add(transaction)

    await db.flush()

    return transaction
