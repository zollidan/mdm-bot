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
        # Используем delimiter ';' так как CSV файл использует точку с запятой
        reader = csv.DictReader(file, delimiter=";")
        
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
                    status=row.get('Статус товара', '')
                )
                
                # Добавляем товар в сессию
                session.add(product)
            
            # Сохраняем изменения в базе данных
            await session.commit()
            print("Импорт данных завершен успешно!")

async def main():
    await create_tables()
    csv_path = "old_db_lite.csv"  # Путь к CSV файлу
    await process_csv(csv_path)

if __name__ == "__main__":
    asyncio.run(main())
