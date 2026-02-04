from aiogram.fsm.state import State, StatesGroup


class CheckoutStates(StatesGroup):
    name = State()
    phone = State()
    city = State()
    delivery = State()
    address = State()
    comment = State()
    edit_field = State()  # generic editing state


class AdminCategoryStates(StatesGroup):
    create_name = State()
    rename = State()


class AdminProductStates(StatesGroup):
    create_title = State()
    create_description = State()
    create_price = State()
    create_category = State()
    create_stock = State()
    create_is_active = State()
    create_photo = State()

    edit_field = State()
    edit_value = State()
    wait_photo = State()
