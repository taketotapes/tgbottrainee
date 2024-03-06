# import logging
# from datetime import datetime, timedelta
# from telegram.ext import Update, ReplyKeyboardMarkup, KeyboardButton
# from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler

import logging
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, ApplicationBuilder
from telegram import Update
import pickle


BOT_TOKEN = '6738032333:AAEMKV0vwD4LOf-cJh_No1Ub39sy7JeVfqw'
user_data = {}

COST_CATEGORIES = ['Продукти', 'Транспорт', 'Розваги', 'Житло', "Здоров'я", 'Інше']
INCOME_CATEGORIES = ['Зарпалата', 'Подарунок', 'Інше']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)




class Costs:
    def __init__(self, title: float, category: str, date: datetime):
        self.title = title
        self.category = category
        self.cost = '➖'
        self.date = date

    def __str__(self):
        if self.category:
            return f'{self.cost} {self.title} {self.category}'

    def __repr__(self):
        return self.__str__()


class Incomes:
    def __init__(self, title: float, category: str, date: datetime):
        self.title = title
        self.category = category
        self.income = '➕'
        self.date = date

    def __str__(self):
        if self.category:
            return f'{self.income} {self.title} {self.category}'

    def __repr__(self):
        return self.__str__()


def save_data(data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(data, file)


def load_data(filename):
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        return data
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f'Помилка під час завантаження даних з файлa: {e}')
        return {}


async def start(update: Update, context: CallbackContext) -> None:
    logging.info('Start clicked')
    await update.message.reply_text(
        'Вітаю у боті розрахунків доходів та витрат!\n'
        'Команди:\n'
        'Подивитися доступні категорії: /category_list\n'
        'Додати запис витрат та категорію: /add_cost\n'
        'Додати запис доходів та категорію: /add_income\n'
        'Витрати за місяць: /month_costs\n'
        'Витрати за тиждень: /week_costs\n'
        'Видалити запис: /remove_records\n'
    )


async def add_cost(update: Update, context: CallbackContext) -> None:
    """
    Format of add cost command
    /add_cost <cost sum> <category>
    """
    user_id = update.message.from_user.id
    cost_parts = " ".join(context.args).split("|")

    if len(cost_parts) < 2:
        await update.message.reply_text(
            'Будь ласка, вкажіть суму та категорію у форматі: Сума | Категорія')
        return

    cost_title = cost_parts[0].strip()

    if not cost_title:
        await update.message.reply_text("Сумма витрат не може бути пустою.")
        return

    category = cost_parts[1].strip()

    if not category:
        await update.message.reply_text("Категорія не може бути пустою.")
        return

    if not user_data.get(user_id):
        user_data[user_id] = []

    cost = Costs(cost_title, category, datetime.now())

    if cost_title:
        user_data[user_id].append(cost)
        await update.message.reply_text(f'Витрата {cost} успішно додана!')
    else:
        await update.message.reply_text("Сумма витрат не може бути пустою.")

    save_data(user_data, 'user_data.pkl')


async def category_list(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(f'Усі категорії {COST_CATEGORIES}')


async def add_income(update: Update, context: CallbackContext) -> None:
    """
    Format of add income command
    /add_income <income sum> | <category>
    """
    user_id = update.message.from_user.id
    income_parts = " ".join(context.args).split("|")
    income_title = income_parts[0].strip()

    if len(income_parts) < 2:
        await update.message.reply_text(
            'Будь ласка, вкажіть суму та категорію у форматі: Сума | Категорія')
        return

    if not income_title:
        await update.message.reply_text(
            'Сумма доходу не може бути пустою.')
        return

    category = income_parts[1].strip()

    if not user_data.get(user_id):
        user_data[user_id] = []

    income = Incomes(income_title, category, datetime.now())

    if income_title:
        user_data[user_id].append(income)
        await update.message.reply_text(f'Дохід {income} успішно доданий!')
    else:
        await update.message.reply_text('Сумма доходу не може бути пустою.')

    save_data(user_data, 'user_data.pkl')


async def show_all_costs(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id not in user_data or not user_data[user_id]:
        await update.message.reply_text('У Вас ще немає витрат.')
        return

    cost_text = "\n".join(map(str, user_data[user_id]))
    await update.message.reply_text(f'Ваші витрати:\n{cost_text}')


async def show_month_costs(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id not in user_data or not user_data[user_id]:
        await update.message.reply_text("У вас ще немає витрат.")
        return

    current_date = datetime.now()

    month_costs = [cost for cost in user_data[user_id] if cost.date.month == current_date.month]

    if not month_costs:
        await update.message.reply_text('У вас ще немаэ витрат за поточний місяць.')
        return

    cost_text = "\n".join(map(str, month_costs))
    await update.message.reply_text(f'Витрати за поточний місяць:\n{cost_text}')


async def show_week_costs(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id not in user_data or not user_data[user_id]:
        await update.message.reply_text("У вас ще немає витрат.")
        return

    current_date = datetime.now()

    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    week_costs = [cost for cost in user_data[user_id] if start_of_week <= cost.date <= end_of_week]

    if not week_costs:
        await update.message.reply_text('У Вас немає витрат за поточний тиждень')
        return

    cost_text = "\n".join(map(str, week_costs))
    await update.message.reply_text(f'Витрати за поточний тиждень:\n{cost_text}')


async def remove_records(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not user_data.get(user_id):
        await update.message.reply_text("У Вас немає записів для видалення.")
        return

    record_id = context.args[0] if context.args else None

    if not record_id or not record_id.isdigit():
        await update.message.reply_text('Будь ласка введіть коректний ідентифікатор.')
        return

    record_id = int(record_id)

    if 0 <= record_id < len(user_data[user_id]):
        delete_rec = user_data[user_id].pop(record_id)
        await update.message.reply_text(f'Запис {delete_rec} успішно видалено!')
    else:
        await update.message.reply_text('Неравильний ідентифікатор запису.')

    save_data(user_data, 'user_data.pkl')


user_data = load_data('user_data.pkl')


def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    logging.info('Application build successfully!')

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', start))
    app.add_handler(CommandHandler('add_cost', add_cost))
    app.add_handler(CommandHandler('add_income', add_income))
    app.add_handler(CommandHandler('category_list', category_list))
    app.add_handler(CommandHandler('month_costs', show_month_costs))
    app.add_handler(CommandHandler('week_costs', show_week_costs))
    app.add_handler(CommandHandler('remove_records', remove_records))
    app.run_polling()


if __name__ == '__main__':
    save_data(user_data, 'user_data.pkl')
    run()
