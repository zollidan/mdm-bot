package database

import (
	"fmt"
	"log"

	"mdm-bot/internal/config"
	"mdm-bot/internal/models"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

// InitDatabase initializes the database connection
func InitDatabase(settings *config.Settings) (*gorm.DB, error) {
	dsn := settings.GetDatabaseURL()

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	DB = db
	log.Println("Database connection established")
	return db, nil
}

// CreateTables creates all database tables
func CreateTables(db *gorm.DB) error {
	// AutoMigrate will create tables if they don't exist
	err := db.AutoMigrate(models.AllModels()...)
	if err != nil {
		return fmt.Errorf("failed to create tables: %w", err)
	}

	log.Println("Database tables created")
	return nil
}
