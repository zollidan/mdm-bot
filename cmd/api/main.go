package main

import (
	"fmt"
	"log"
	"os"

	"mdm-bot/internal/api"
	"mdm-bot/internal/config"
	"mdm-bot/internal/database"
	"mdm-bot/internal/search"
)

func printAPIBanner() {
	banner := `
╔═══════════════════════════════════════╗
║       MDM BOT API SERVER              ║
║       FastAPI → Go Migration          ║
╚═══════════════════════════════════════╝
`
	fmt.Println(banner)
}

func main() {
	// Print banner
	printAPIBanner()

	// Load configuration
	settings, err := config.LoadSettings()
	if err != nil {
		log.Fatalf("Failed to load settings: %v", err)
	}
	log.Println("Configuration loaded")

	// Initialize database using shared database package
	db, err := database.InitDatabase(settings)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Auto-migrate database schema
	log.Println("Running database migrations...")
	if err := database.CreateTables(db); err != nil {
		log.Fatalf("Failed to migrate database: %v", err)
	}
	log.Println("Database migrations completed successfully")

	// Initialize MeiliSearch client
	log.Println("Initializing MeiliSearch client...")
	meiliClient, err := search.NewClient(settings, db)
	if err != nil {
		log.Fatalf("Failed to create MeiliSearch client: %v", err)
	}

	// Configure MeiliSearch index
	if err := meiliClient.InitIndex(); err != nil {
		log.Fatalf("Failed to initialize MeiliSearch index: %v", err)
	}

	// Check MeiliSearch health
	healthy, err := meiliClient.HealthCheck()
	if err != nil {
		log.Printf("Warning: MeiliSearch health check failed: %v", err)
	} else if healthy {
		log.Println("MeiliSearch is healthy and ready")
	}

	// Sync products to MeiliSearch
	log.Println("Syncing products to MeiliSearch...")
	if err := meiliClient.SyncProducts(); err != nil {
		log.Printf("Warning: Failed to sync products to MeiliSearch: %v", err)
		log.Println("Continuing without search functionality...")
	} else {
		log.Println("Products synced successfully")
	}

	// Get port from environment or use default
	port := os.Getenv("API_PORT")
	if port == "" {
		port = "8000"
	}

	// Create and start API server
	server := api.NewServer(db, settings, meiliClient)
	log.Printf("Starting MDM Bot API server on port %s...", port)

	if err := server.Start(port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
