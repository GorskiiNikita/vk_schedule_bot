from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def add_keyboard():
    keyboard = VkKeyboard()
    keyboard.add_button('Где пара?', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Какие сегодня пары?', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Какие завтра пары?', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Когда на учёбу?', color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


