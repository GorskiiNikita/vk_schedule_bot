from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_custom_keyboard(buttons):
    keyboard = VkKeyboard()
    for i in range(len(buttons)):
        if i == 0:
            keyboard.add_button(buttons[i], color=VkKeyboardColor.PRIMARY)
            continue
        keyboard.add_line()

        # костыль
        if buttons[i] == 'Заказать работу':
            keyboard.add_button(buttons[i], color=VkKeyboardColor.POSITIVE)
            continue
        elif buttons[i] == 'На главную':
            keyboard.add_button(buttons[i], color=VkKeyboardColor.NEGATIVE)
            continue

        keyboard.add_button(buttons[i], color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def today_is_holiday(date, holidays):
    if date.strftime('%d.%m.%Y') in holidays.data:
        return True
    return False





