from aiogram.fsm.state import State, StatesGroup

class AddChannelState(StatesGroup):
    waiting_for_type = State()
    waiting_for_title = State()
    waiting_for_id = State()
    waiting_for_url = State()

class AddTaskState(StatesGroup):
    waiting_for_type = State()
    waiting_for_title = State()
    waiting_for_id = State()
    waiting_for_url = State()
    waiting_for_reward = State()

class SetReferralPriceState(StatesGroup):
    waiting_for_price = State()

class SetTaskPriceState(StatesGroup):
    waiting_for_price = State()

class SetCardState(StatesGroup):
    waiting_for_card_number = State()
    waiting_for_card_holder = State()

class SetVideoGuideState(StatesGroup):
    waiting_for_video = State()

class SetAdPostState(StatesGroup):
    waiting_for_content = State()
    waiting_for_button_choice = State()
    waiting_for_button_text = State()
    waiting_for_button_url = State()

class BroadcastState(StatesGroup):
    waiting_for_message = State()
    waiting_for_button_choice = State()
    waiting_for_button_text = State()
    waiting_for_button_url = State()
    waiting_for_confirm = State()

class SetAboutTextState(StatesGroup):
    waiting_for_text = State()

class SetHelpTextState(StatesGroup):
    waiting_for_text = State()
