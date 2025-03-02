from fastapi import APIRouter, status

from src.constraints import confirmed_email_required
from src.crud import addresses
from src.schemas.address import AddressOut, AddressIn, AddressUpdate
from src.schemas.message import Message
from src.deps import cur_user_dependency, db_dependency
from src.custom_exceptions import ResourceDoesNotExistError, NotEnoughRightsError

router = APIRouter(
    prefix='/addresses',
    tags=['addresses']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=AddressOut)
@confirmed_email_required
async def create_address(user: cur_user_dependency, address: AddressIn, db: db_dependency):
    return await addresses.create(address, user.id, db)


@router.patch('/{address_id}', status_code=status.HTTP_200_OK, response_model=Message)
async def update_address(address_id: int, address_update: AddressUpdate, user: cur_user_dependency, db: db_dependency):
    if (address := await addresses.get_by_id(address_id, db)) is None:
        raise ResourceDoesNotExistError("Address with the given id does not exist")
    if address.user_id != user.id:
        raise NotEnoughRightsError("User is not the address owner")
    await addresses.update(address_id, address_update, db)
    return Message(message="The address updated")


@router.delete('/{address_id}', status_code=status.HTTP_200_OK, response_model=Message)
async def delete_address(address_id: int, user: cur_user_dependency, db: db_dependency):
    if (address := await addresses.get_by_id(address_id, db)) is None:
        raise ResourceDoesNotExistError("Address with the given id does not exist")
    if address.user_id != user.id:
        raise NotEnoughRightsError("User is not the address owner")
    await addresses.delete(address_id, db)
    return Message(message="The address deleted")

