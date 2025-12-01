import csv
import asyncio
from models import Base, Product
from database import AsyncSessionFactory, create_tables

def convert_to_bool(value):
    """Преобразует различные значения в булевое значение"""
    if not value or value.lower() in ["", "0", "false", "нет", "no"]:
        return False
    return True

def extract_first_image(pictures):
    """Извлекает URL первой картинки из списка"""
    if not pictures:
        return None
    images = [img.strip() for img in pictures.split(',')]
    return images[0] if images else None

def map_availability(value):
    """Преобразует значение наличия в стандартизированный формат"""
    if not value or value.lower() not in ["есть", "да", "yes", "1", "true"]:
        return "нет"
    return "есть"

def check_if_bestseller(value):
    """Проверяет, является ли товар хитом продаж"""
    return bool(value and value.strip()) 

async def process_csv(file_path):
    """Обрабатывает CSV файл и заполняет базу данных"""
    with open(file_path, 'r', encoding='utf-8') as file:
        # Используем delimiter ',' для full_database.csv
        reader = csv.DictReader(file, delimiter=",")
        
        # Создаем сессию для работы с базой данных
        async with AsyncSessionFactory() as session:
            for row in reader:
                # Преобразуем цену из строки в число с плавающей точкой
                price = float(row.get('price', 0).replace(',', '.'))
                
                # Преобразуем оптовую цену
                opt_price_str = row.get('Цена ОПТ, RUR', '')
                opt_price = float(opt_price_str.replace(',', '.')) if opt_price_str else None
                
                # Преобразуем цену в долларах
                usd_price_str = row.get('Цена у.е.', '')
                usd_price = float(usd_price_str.replace(',', '.')) if usd_price_str else None

                # Преобразуем цены для Беларуси
                price_byn_legal_str = row.get('Цена для ЮЛ (Бел. BYN.): Цена', '')
                price_byn_legal = float(price_byn_legal_str.replace(',', '.')) if price_byn_legal_str else None

                price_byn_retail_str = row.get('Цена для ФЛ (Бел. BYN.): Цена', '')
                price_byn_retail = float(price_byn_retail_str.replace(',', '.')) if price_byn_retail_str else None

                # Получаем первую картинку
                image = extract_first_image(row.get('Pictures', ''))
                
                # Создаем объект товара
                product = Product(
                    url=row.get('url', ''),
                    name=row.get('name', ''),
                    vendor_code=row.get('vendorCode', ''),
                    price=price,
                    currency_id=row.get('currencyId', 'RUR'),
                    category_id=int(row.get('categoryId', 0)),
                    model=row.get('model', ''),
                    vendor=row.get('vendor', ''),
                    description=row.get('description', ''),
                    manufacturer_warranty=convert_to_bool(row.get('manufacturer warranty', '')),
                    image=image,
                    opt_price=opt_price,
                    is_bestseller=check_if_bestseller(row.get('Хит продаж', '')),
                    unit=row.get('Единица измерения', 'шт'),
                    usd_price=usd_price,
                    availability=map_availability(row.get('Наличие', '')),
                    status=row.get('Статус товара', ''),
                    # Складские остатки
                    stock_chashnikovo=row.get('Количество на складе «Москва, Чашниково»', ''),
                    stock_kantemirovskaya=row.get('Количество на складе «Москва, Кантемировская»', ''),
                    stock_spb=row.get('Количество на складе «Санкт-Петербург»', ''),
                    stock_voronezh=row.get('Количество на складе «Воронеж»', ''),
                    stock_korolev=row.get('Количество на складе «Королёв»', ''),
                    stock_krasnodar=row.get('Количество на складе «Краснодар»', ''),
                    stock_kazan=row.get('Количество на складе «Казань»', ''),
                    stock_online=row.get('Количество на складе «Интернет-магазин»', ''),
                    # Цены для Беларуси
                    price_byn_legal=price_byn_legal,
                    price_byn_retail=price_byn_retail
                )
                
                # Добавляем товар в сессию
                session.add(product)
            
            # Сохраняем изменения в базе данных
            await session.commit()
            print("Импорт данных завершен успешно!")

async def main():
    await create_tables()
    csv_path = "full_database.csv"  # Путь к CSV файлу
    await process_csv(csv_path)

if __name__ == "__main__":
    asyncio.run(main())
