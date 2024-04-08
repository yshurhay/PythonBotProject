from info import info


def get_bonus_info(user_id):
    try:
        with open('bonus.txt', 'r', encoding='utf-8') as file:
            for line in file.readlines():
                user = int(line.split()[0])
                orders_count = int(line.split()[1])
                info['bonus'][user] = orders_count
                if user_id not in info['bonus']:
                    info['bonus'][user_id] = 0
    except FileNotFoundError or IndexError or KeyError:
        info['bonus'][user_id] = 0

    return info['bonus'][user_id]
