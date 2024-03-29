from info import info


def get_bonus_info():
    try:
        with open('bonus.txt', 'r', encoding='utf-8') as file:
            for line in file.readlines():
                user_id = int(line.split()[0])
                orders_count = int(line.split()[1])
                info['bonus'][user_id] = orders_count
    except FileNotFoundError or IndexError:
        info['bonus'][user_id] = 0

    return info['bonus'][user_id]
