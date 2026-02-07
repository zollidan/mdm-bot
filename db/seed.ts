import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import * as dotenv from "dotenv";
import { users, products } from "./schema";

dotenv.config();

const pool = new Pool({
  connectionString:
    process.env.DATABASE_URL ||
    "postgresql://postgres:postgres@localhost:5432/mdm_bot",
});

const db = drizzle(pool);

async function seed() {
  console.log("🌱 Starting database seeding...");

  try {
    // Очистка существующих данных
    console.log("🗑️  Clearing existing data...");
    await db.delete(products);
    await db.delete(users);

    // Добавление пользователей
    console.log("👤 Adding users...");
    const insertedUsers = await db
      .insert(users)
      .values([
        {
          name: "Иван Иванов",
          email: "ivan@example.com",
        },
        {
          name: "Мария Петрова",
          email: "maria@example.com",
        },
        {
          name: "Алексей Сидоров",
          email: "alex@example.com",
        },
        {
          name: "Елена Смирнова",
          email: "elena@example.com",
        },
        {
          name: "Дмитрий Козлов",
          email: "dmitry@example.com",
        },
      ])
      .returning();

    console.log(`✅ Added ${insertedUsers.length} users`);

    // Добавление продуктов
    console.log("📦 Adding products...");
    const insertedProducts = await db
      .insert(products)
      .values([
        {
          name: "iPhone 15 Pro",
          description: "Последняя модель iPhone с процессором A17 Pro",
          price: 99990,
          stock: 25,
          isActive: true,
        },
        {
          name: "Samsung Galaxy S24",
          description: "Флагманский смартфон Samsung с AI функциями",
          price: 79990,
          stock: 30,
          isActive: true,
        },
        {
          name: "MacBook Air M3",
          description: "Тонкий и легкий ноутбук от Apple с чипом M3",
          price: 129990,
          stock: 15,
          isActive: true,
        },
        {
          name: "AirPods Pro 2",
          description: "Беспроводные наушники с активным шумоподавлением",
          price: 24990,
          stock: 50,
          isActive: true,
        },
        {
          name: "iPad Pro 12.9",
          description: "Мощный планшет для профессионалов",
          price: 109990,
          stock: 20,
          isActive: true,
        },
        {
          name: "Apple Watch Series 9",
          description: "Умные часы с расширенными функциями здоровья",
          price: 39990,
          stock: 35,
          isActive: true,
        },
        {
          name: "Sony WH-1000XM5",
          description: "Премиальные наушники с лучшим шумоподавлением",
          price: 29990,
          stock: 40,
          isActive: true,
        },
        {
          name: "Kindle Paperwhite",
          description: "Электронная книга с подсветкой экрана",
          price: 12990,
          stock: 60,
          isActive: true,
        },
        {
          name: "DJI Mini 3 Pro",
          description: "Компактный дрон с 4K камерой",
          price: 59990,
          stock: 10,
          isActive: true,
        },
        {
          name: "PlayStation 5",
          description: "Игровая консоль нового поколения",
          price: 54990,
          stock: 0,
          isActive: false,
        },
        {
          name: "Logitech MX Master 3S",
          description: "Эргономичная беспроводная мышь",
          price: 9990,
          stock: 45,
          isActive: true,
        },
        {
          name: "Samsung Galaxy Tab S9",
          description: "Планшет на Android с AMOLED экраном",
          price: 69990,
          stock: 18,
          isActive: true,
        },
        {
          name: "GoPro Hero 12",
          description: "Экшн-камера для экстремальных съемок",
          price: 44990,
          stock: 22,
          isActive: true,
        },
        {
          name: "Dyson V15 Detect",
          description: "Беспроводной пылесос с лазерной подсветкой",
          price: 59990,
          stock: 12,
          isActive: true,
        },
        {
          name: "Xiaomi Mi Band 8",
          description: "Доступный фитнес-браслет",
          price: 3990,
          stock: 100,
          isActive: true,
        },
      ])
      .returning();

    console.log(`✅ Added ${insertedProducts.length} products`);

    console.log("\n✨ Seeding completed successfully!");
    console.log(`📊 Summary:`);
    console.log(`   Users: ${insertedUsers.length}`);
    console.log(`   Products: ${insertedProducts.length}`);
  } catch (error) {
    console.error("❌ Error seeding database:", error);
    throw error;
  } finally {
    await pool.end();
  }
}

seed()
  .then(() => {
    console.log("👋 Done!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("💥 Failed to seed database:", error);
    process.exit(1);
  });
