from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    select_group = State()
    select_teacher = State()
    specify_teacher = State()
