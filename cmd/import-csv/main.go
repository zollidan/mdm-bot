package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	"mdm-bot/internal/config"
	"mdm-bot/internal/database"
	"mdm-bot/internal/models"

	"gorm.io/gorm"
)

// convertToBool converts various string values to boolean
func convertToBool(value string) bool {
	value = strings.ToLower(strings.TrimSpace(value))
	if value == "" || value == "0" || value == "false" || value == "нет" || value == "no" {
		return false
	}
	return true
}

// extractFirstImage extracts first image URL from comma-separated list
func extractFirstImage(pictures string) string {
	if pictures == "" {
		return ""
	}
	images := strings.Split(pictures, ",")
	if len(images) > 0 {
		return strings.TrimSpace(images[0])
	}
	return ""
}

// mapAvailability converts availability value to standardized format
func mapAvailability(value string) string {
	value = strings.ToLower(strings.TrimSpace(value))
	if value == "есть" || value == "да" || value == "yes" || value == "1" || value == "true" {
		return "есть"
	}
	return "нет"
}

// checkIfBestseller checks if product is a bestseller
func checkIfBestseller(value string) bool {
	return strings.TrimSpace(value) != ""
}

// parseFloat parses string to float64, replacing commas with dots
func parseFloat(value string) (float64, error) {
	if value == "" {
		return 0, fmt.Errorf("empty value")
	}
	value = strings.ReplaceAll(strings.TrimSpace(value), ",", ".")
	return strconv.ParseFloat(value, 64)
}

// parseFloatPtr parses string to *float64, returns nil if empty or invalid
func parseFloatPtr(value string) *float64 {
	if value == "" {
		return nil
	}
	f, err := parseFloat(value)
	if err != nil {
		return nil
	}
	return &f
}

// stringPtr returns pointer to string, or nil if empty
func stringPtr(value string) *string {
	if value == "" {
		return nil
	}
	return &value
}

// processCSV reads CSV file and imports products to database
func processCSV(filePath string, db *gorm.DB) error {
	file, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("failed to open CSV file: %w", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	reader.Comma = ','
	reader.LazyQuotes = true
	reader.FieldsPerRecord = -1 // Allow variable number of fields

	// Read header
	headers, err := reader.Read()
	if err != nil {
		return fmt.Errorf("failed to read CSV header: %w", err)
	}

	// Create header index map
	headerMap := make(map[string]int)
	for i, header := range headers {
		headerMap[strings.TrimSpace(header)] = i
	}

	// Helper to get value by header name
	getValue := func(row []string, headerName string) string {
		if idx, ok := headerMap[headerName]; ok && idx < len(row) {
			return strings.TrimSpace(row[idx])
		}
		return ""
	}

	products := []models.Product{}
	lineNum := 1

	// Read all rows
	for {
		lineNum++
		row, err := reader.Read()
		if err != nil {
			if err.Error() == "EOF" {
				break
			}
			log.Printf("Warning: error reading line %d: %v", lineNum, err)
			continue
		}

		// Parse price (required field)
		price, err := parseFloat(getValue(row, "price"))
		if err != nil {
			log.Printf("Warning: skipping line %d, invalid price: %v", lineNum, err)
			continue
		}

		// Parse category ID
		categoryID := 0
		if catIDStr := getValue(row, "categoryId"); catIDStr != "" {
			if cat, err := strconv.Atoi(catIDStr); err == nil {
				categoryID = cat
			}
		}

		// Create product
		product := models.Product{
			URL:                  getValue(row, "url"),
			Name:                 getValue(row, "name"),
			VendorCode:           getValue(row, "vendorCode"),
			Price:                price,
			CurrencyID:           getValue(row, "currencyId"),
			CategoryID:           categoryID,
			Model:                getValue(row, "model"),
			Vendor:               getValue(row, "vendor"),
			Description:          stringPtr(getValue(row, "description")),
			ManufacturerWarranty: convertToBool(getValue(row, "manufacturer warranty")),
			Image:                extractFirstImage(getValue(row, "Pictures")),
			OptPrice:             parseFloatPtr(getValue(row, "Цена ОПТ, RUR")),
			IsBestseller:         checkIfBestseller(getValue(row, "Хит продаж")),
			Unit:                 getValue(row, "Единица измерения"),
			USDPrice:             parseFloatPtr(getValue(row, "Цена у.е.")),
			Availability:         mapAvailability(getValue(row, "Наличие")),
			Status:               stringPtr(getValue(row, "Статус товара")),

			// Stock levels
			StockChashnikovo:     stringPtr(getValue(row, "Количество на складе «Москва, Чашниково»")),
			StockKantemirovskaya: stringPtr(getValue(row, "Количество на складе «Москва, Кантемировская»")),
			StockSPB:             stringPtr(getValue(row, "Количество на складе «Санкт-Петербург»")),
			StockVoronezh:        stringPtr(getValue(row, "Количество на складе «Воронеж»")),
			StockKorolev:         stringPtr(getValue(row, "Количество на складе «Королёв»")),
			StockKrasnodar:       stringPtr(getValue(row, "Количество на складе «Краснодар»")),
			StockKazan:           stringPtr(getValue(row, "Количество на складе «Казань»")),
			StockOnline:          stringPtr(getValue(row, "Количество на складе «Интернет-магазин»")),

			// Belarus prices
			PriceBYNLegal:  parseFloatPtr(getValue(row, "Цена для ЮЛ (Бел. BYN.): Цена")),
			PriceBYNRetail: parseFloatPtr(getValue(row, "Цена для ФЛ (Бел. BYN.): Цена")),
		}

		// Set default unit if empty
		if product.Unit == "" {
			product.Unit = "шт"
		}

		// Set default currency if empty
		if product.CurrencyID == "" {
			product.CurrencyID = "RUR"
		}

		products = append(products, product)

		// Batch insert every 100 products to avoid memory issues
		if len(products) >= 100 {
			if err := db.Create(&products).Error; err != nil {
				return fmt.Errorf("failed to insert products batch: %w", err)
			}
			log.Printf("Imported %d products (batch)", len(products))
			products = []models.Product{}
		}
	}

	// Insert remaining products
	if len(products) > 0 {
		if err := db.Create(&products).Error; err != nil {
			return fmt.Errorf("failed to insert final products batch: %w", err)
		}
		log.Printf("Imported %d products (final batch)", len(products))
	}

	log.Println("Импорт данных завершен успешно!")
	return nil
}

func main() {
	// Parse command-line flags
	csvPath := flag.String("file", "full_database.csv", "Path to CSV file")
	createTables := flag.Bool("create-tables", false, "Create database tables before import")
	flag.Parse()

	// Load configuration
	settings, err := config.LoadSettings()
	if err != nil {
		log.Fatalf("Failed to load settings: %v", err)
	}

	// Initialize database
	db, err := database.InitDatabase(settings)
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}

	// Create tables if requested
	if *createTables {
		if err := database.CreateTables(db); err != nil {
			log.Fatalf("Failed to create tables: %v", err)
		}
	}

	// Process CSV file
	log.Printf("Starting CSV import from: %s", *csvPath)
	if err := processCSV(*csvPath, db); err != nil {
		log.Fatalf("Failed to process CSV: %v", err)
	}

	log.Println("Import completed successfully!")
}
