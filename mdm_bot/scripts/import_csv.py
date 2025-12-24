"""
CSV import script for products database
"""
import csv
import asyncio
from mdm_bot.core import Product, AsyncSessionFactory, create_tables


def convert_to_bool(value):
    """Convert various values to boolean"""
    if not value or value.lower() in ["", "0", "false", "нет", "no"]:
        return False
    return True


def extract_first_image(pictures):
    """Extract first image URL from list"""
    if not pictures:
        return None
    images = [img.strip() for img in pictures.split(',')]
    return images[0] if images else None


def map_availability(value):
    """Convert availability value to standardized format"""
    if not value or value.lower() not in ["есть", "да", "yes", "1", "true"]:
        return "нет"
    return "есть"


def check_if_bestseller(value):
    """Check if product is a bestseller"""
    return bool(value and value.strip())


async def process_csv(file_path):
    """Process CSV file and populate database"""
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=",")

        # Create database session
        async with AsyncSessionFactory() as session:
            for row in reader:
                # Convert price from string to float
                price = float(row.get('price', 0).replace(',', '.'))

                # Convert wholesale price
                opt_price_str = row.get('Цена ОПТ, RUR', '')
                opt_price = float(opt_price_str.replace(',', '.')) if opt_price_str else None

                # Convert USD price
                usd_price_str = row.get('Цена у.е.', '')
                usd_price = float(usd_price_str.replace(',', '.')) if usd_price_str else None

                # Convert Belarus prices
                price_byn_legal_str = row.get('Цена для ЮЛ (Бел. BYN.): Цена', '')
                price_byn_legal = float(price_byn_legal_str.replace(',', '.')) if price_byn_legal_str else None

                price_byn_retail_str = row.get('Цена для ФЛ (Бел. BYN.): Цена', '')
                price_byn_retail = float(price_byn_retail_str.replace(',', '.')) if price_byn_retail_str else None

                # Get first image
                image = extract_first_image(row.get('Pictures', ''))

                # Create product object
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
                    # Stock quantities
                    stock_chashnikovo=row.get('Количество на складе «Москва, Чашниково»', ''),
                    stock_kantemirovskaya=row.get('Количество на складе «Москва, Кантемировская»', ''),
                    stock_spb=row.get('Количество на складе «Санкт-Петербург»', ''),
                    stock_voronezh=row.get('Количество на складе «Воронеж»', ''),
                    stock_korolev=row.get('Количество на складе «Королёв»', ''),
                    stock_krasnodar=row.get('Количество на складе «Краснодар»', ''),
                    stock_kazan=row.get('Количество на складе «Казань»', ''),
                    stock_online=row.get('Количество на складе «Интернет-магазин»', ''),
                    # Belarus prices
                    price_byn_legal=price_byn_legal,
                    price_byn_retail=price_byn_retail
                )

                # Add product to session
                session.add(product)

            # Save changes to database
            await session.commit()
            print("Импорт данных завершен успешно!")


async def main():
    """Main entry point"""
    await create_tables()
    csv_path = "full_database.csv"  # Path to CSV file
    await process_csv(csv_path)


if __name__ == "__main__":
    asyncio.run(main())
