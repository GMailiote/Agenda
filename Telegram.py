import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class TokenForm(StatesGroup):
    token = State()


class Telegram:
    employees_data_list = []

    def __init__(self, TOKEN):
        self.bot = Bot(TOKEN)

    def start(self):
        storage = MemoryStorage()
        dp = Dispatcher(self.bot, storage=storage)

        @dp.message_handler(commands=['cadastrar'])
        async def cadastro(message: types.Message):
            employee_id = str(message.from_id)

            with open('Code\\data\\tokens_employees.txt', 'r', encoding='utf8') as file:
                header_list = file.readline().splitlines()[0].split(':')
                lines = file.read().splitlines()
                self.employees_data_list = [dict(zip(header_list, employees_register_data.split(':'))) for employees_register_data in lines]

            registered_employees_id_and_name_dict = {employee_data_list['id']: employee_data_list['name'] for employee_data_list in self.employees_data_list if employee_data_list['id'] != 'unused'}
            if employee_id in registered_employees_id_and_name_dict.keys():
                await message.answer(f'Você já está cadastrado, {registered_employees_id_and_name_dict[employee_id]}.')
                return None

            await TokenForm.token.set()
            await message.answer(f'Informe o seu token de cadastro:')


        @dp.message_handler(state='*', commands=['cancelar'])
        async def cancel_handler(message: types.Message, state: FSMContext):
            """Allow user to cancel action via /cancel command"""

            current_state = await state.get_state()
            if current_state is None:
                # User is not in any state, ignoring
                return

            # Cancel state and inform user about it
            await state.finish()
            await message.reply('Cadastro cancelado.')


        @dp.message_handler(state=TokenForm.token)
        async def finalizar_cadastro(message: types.Message, state: FSMContext):
            """Process user name"""

            # Finish our conversation
            await state.finish()

            employee_token = message.text
            for employee_data in self.employees_data_list:
                if employee_token == employee_data['token']:
                    employee_data['id'] = message.from_id
                    await message.reply(f"Token validado!")
                    await message.answer(f"Bem-vindo à Cris Eletrônicos, {employee_data['name']}.")
                    return
            
            await message.reply(f"Token não existente.")

        executor.start_polling(dp)
        
if __name__ == '__main__':
    """ asyncio.run(test()) """
    hieo = None
    with open('Code\\data\\tokens_employees.txt', 'r', encoding='utf8') as file:
        header_list = file.readline().splitlines()[0].split(':')
        lines = file.readlines()
        employees_data_list = [dict(zip(header_list, employees_register_data.split(':'))) for employees_register_data in lines]
        print(employees_data_list)
