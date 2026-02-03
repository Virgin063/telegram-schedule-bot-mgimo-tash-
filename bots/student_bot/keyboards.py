"""
Клавиатуры для студенческого бота
"""
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура бота"""
    keyboard = [
        ["📅 Сегодня", "➡️ Завтра"],
        ["📆 Неделя", "⚙️ Настройки"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_settings_keyboard(
    morning: bool,
    before_class: bool,
    changes: bool
) -> InlineKeyboardMarkup:
    """
    Клавиатура настроек
    
    Args:
        morning: утренние уведомления
        before_class: уведомления за 15 мин
        changes: уведомления об изменениях
        
    Returns:
        InlineKeyboardMarkup: клавиатура
    """
    morning_text = "✅" if morning else "❌"
    before_class_text = "✅" if before_class else "❌"
    changes_text = "✅" if changes else "❌"
    
    keyboard = [
        [InlineKeyboardButton(
            f"{morning_text} Утренние уведомления",
            callback_data="toggle_morning"
        )],
        [InlineKeyboardButton(
            f"{before_class_text} За 15 минут до пары",
            callback_data="toggle_before_class"
        )],
        [InlineKeyboardButton(
            f"{changes_text} Об изменениях расписания",
            callback_data="toggle_changes"
        )],
        [InlineKeyboardButton(
            "🔙 Назад",
            callback_data="back_to_main"
        )]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_group_selection_keyboard(groups: list) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора группы
    
    Args:
        groups: список групп
        
    Returns:
        InlineKeyboardMarkup: клавиатура
    """
    keyboard = []
    
    for group in groups:
        keyboard.append([
            InlineKeyboardButton(group, callback_data=f"select_group_{group}")
        ])
    
    return InlineKeyboardMarkup(keyboard)
