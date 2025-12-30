package config

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
)

// Settings contains all application configuration
type Settings struct {
	BotToken         string
	PostgresUser     string
	PostgresPassword string
	PostgresHost     string
	PostgresPort     string
	PostgresDB       string
	MeiliHost        string
	MeiliPort        string
	MeiliMasterKey   string
	MeiliEnv         string
	WebappURL        string
	AllowedOrigins   string
}

var AppSettings *Settings

// LoadSettings loads configuration from environment variables
func LoadSettings() (*Settings, error) {
	// Load .env file (ignore error if file doesn't exist)
	_ = godotenv.Load()

	settings := &Settings{
		BotToken:         getEnv("BOT_TOKEN", ""),
		PostgresUser:     getEnv("POSTGRES_USER", ""),
		PostgresPassword: getEnv("POSTGRES_PASSWORD", ""),
		PostgresHost:     getEnv("POSTGRES_HOST", "localhost"),
		PostgresPort:     getEnv("POSTGRES_PORT", "5432"),
		PostgresDB:       getEnv("POSTGRES_DB", ""),
		MeiliHost:        getEnv("MEILI_HOST", "meilisearch"),
		MeiliPort:        getEnv("MEILI_PORT", "7700"),
		MeiliMasterKey:   getEnv("MEILI_MASTER_KEY", ""),
		MeiliEnv:         getEnv("MEILI_ENV", "development"),
		WebappURL:        getEnv("WEBAPP_URL", "http://localhost:8000"),
		AllowedOrigins:   getEnv("ALLOWED_ORIGINS", "*"),
	}

	// Validate required fields
	if settings.BotToken == "" {
		return nil, fmt.Errorf("BOT_TOKEN is required")
	}

	AppSettings = settings
	return settings, nil
}

// GetDatabaseURL constructs PostgreSQL connection string
func (s *Settings) GetDatabaseURL() string {
	return fmt.Sprintf("postgres://%s:%s@%s:%s/%s?sslmode=disable",
		s.PostgresUser,
		s.PostgresPassword,
		s.PostgresHost,
		s.PostgresPort,
		s.PostgresDB,
	)
}

// GetMeiliSearchURL constructs MeiliSearch connection URL
func (s *Settings) GetMeiliSearchURL() string {
	return fmt.Sprintf("http://%s:%s", s.MeiliHost, s.MeiliPort)
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
