from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_custom_keyboard(buttons):
    keyboard = VkKeyboard()
    for i in range(len(buttons)):
        if i == 0:
            keyboard.add_button(buttons[i], color=VkKeyboardColor.PRIMARY)
            continue
        keyboard.add_line()
        keyboard.add_button(buttons[i], color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()
