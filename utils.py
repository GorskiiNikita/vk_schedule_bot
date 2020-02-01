from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_custom_keyboard(buttons):
    keyboard = VkKeyboard()
    for btn in buttons:
        keyboard.add_button(btn, color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
    return keyboard.get_keyboard()
