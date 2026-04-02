import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from handlers import change_balance, get_wallet
from schema import OperationRequest, TransactionResponse, WalletResponse

router = APIRouter(prefix="/api/v1/wallets")


@router.get("/{wallet_uuid}", response_model=WalletResponse)
async def get_wallet_balance(
    wallet_uuid: uuid.UUID,
    db: AsyncSession = Depends(get_session),
):
    return await get_wallet(db, wallet_uuid)


@router.post("/{wallet_uuid}/operation", response_model=TransactionResponse)
async def change_wallet_balancce(
    wallet_uuid: uuid.UUID,
    body: OperationRequest,
    db: AsyncSession = Depends(get_session),
):
    return await change_balance(db, wallet_uuid, body.operation_type, body.amount)
