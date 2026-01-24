from aiogram.fsm.state import State, StatesGroup

class Checkout(StatesGroup):
    name = State()
    phone = State()
    city = State()
    delivery_method = State()
    address = State()
    comment = State()
    confirm = State()
