package main

import (
	"fmt"
	"log"
	"os"
	"time"

	"mdm-bot/internal/config"
	"mdm-bot/internal/database"
	"mdm-bot/internal/handlers"

	tele "gopkg.in/telebot.v4"
)

func setupLogging() {
	// Open log file
	logFile, err := os.OpenFile("mdm_bot.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		log.Printf("Warning: Could not open log file: %v", err)
		return
	}

	// Set output to both file and console
	log.SetOutput(logFile)
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)
}

func printBanner() {
	banner := `
███╗   ███╗██████╗ ███╗   ███╗    ██████╗  ██████╗ ████████╗
████╗ ████║██╔══██╗████╗ ████║    ██╔══██╗██╔═══██╗╚══██╔══╝
██╔████╔██║██║  ██║██╔████╔██║    ██████╔╝██║   ██║   ██║
██║╚██╔╝██║██║  ██║██║╚██╔╝██║    ██╔══██╗██║   ██║   ██║
██║ ╚═╝ ██║██████╔╝██║ ╚═╝ ██║    ██████╔╝╚██████╔╝   ██║
╚═╝     ╚═╝╚═════╝ ╚═╝     ╚═╝    ╚═════╝  ╚═════╝    ╚═╝
`
	fmt.Println(banner)
}

func main() {
	// Setup logging
	setupLogging()
	log.Println("Bot started")

	// Print banner
	printBanner()

	// Load configuration
	settings, err := config.LoadSettings()
	if err != nil {
		log.Fatalf("Failed to load settings: %v", err)
	}
	log.Println("Configuration loaded")

	// Initialize database
	db, err := database.InitDatabase(settings)
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}

	// Create tables
	if err := database.CreateTables(db); err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}

	// Create bot
	pref := tele.Settings{
		Token:  settings.BotToken,
		Poller: &tele.LongPoller{Timeout: 10 * time.Second},
	}

	bot, err := tele.NewBot(pref)
	if err != nil {
		log.Fatalf("Failed to create bot: %v", err)
	}

	// Register handlers
	bot.Handle("/start", handlers.HandleStart)
	bot.Handle("/hello", func(c tele.Context) error {
		return c.Send("Hello!")
	})

	// Start polling
	log.Println("Starting bot polling...")
	fmt.Println("Bot is running...")
	bot.Start()
}
