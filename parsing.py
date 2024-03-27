import aiohttp
from bs4 import BeautifulSoup


async def get_food_data(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = []
            r = await response.text()
            soup = BeautifulSoup(r, 'html.parser')
            items = soup.find_all('div', class_='n-col-6 n-col-lg-4 n-col-xl-3 product_cart_container noload')
            for item in items:
                name = item.find('a', class_='product_name').text.strip()
                mass = item.find('div', class_='product_mass').text.strip()
                price = item.find('div', class_='price').text.strip()
                photo = f'https://pizza-italia.by{item.find('img')['src']}'
                data.append({
                    'name': name,
                    'mass': mass,
                    'price': price[:-4],
                    'photo': photo
                })
            return data


async def get_about_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://pizza-italia.by/about/') as response:
            r = await response.text()
            soup = BeautifulSoup(r, 'html.parser')
            items = soup.find_all('p')

            return '\n'.join(item.text.strip() for item in items if not item.text.strip().startswith('Доставка') and not item.text.strip().startswith('Мы'))


async def get_delivery_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://pizza-italia.by/about/delivery/') as response:
            r = await response.text()
            soup = BeautifulSoup(r, 'html.parser')
            item = soup.find('div', class_='contacts_text text_content')
            sentences = [x.strip() for x in item.text.split('\n') if x]
            return '{}\n\n- {}\n- {}\n\n{}'.format(*sentences)


async def get_payments_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://pizza-italia.by/about/payment/') as response:
            r = await response.text()
            soup = BeautifulSoup(r, 'html.parser')
            item = soup.find('div', class_='text_content')
            sentences = [x.strip() for x in item.text.split('\n') if x]
            return '{}\n\n- {}\n- {}\n\n{}'.format(*sentences)
