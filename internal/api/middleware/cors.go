package middleware

import (
	"strings"

	"github.com/go-chi/cors"
	"mdm-bot/internal/config"
)

// CORSMiddleware returns configured CORS middleware
func CORSMiddleware(settings *config.Settings) *cors.Cors {
	allowedOrigins := []string{"*"}

	// Read from settings
	if settings.AllowedOrigins != "" && settings.AllowedOrigins != "*" {
		allowedOrigins = strings.Split(settings.AllowedOrigins, ",")
	}

	return cors.New(cors.Options{
		AllowedOrigins:   allowedOrigins,
		AllowedMethods:   []string{"GET", "POST", "OPTIONS"},
		AllowedHeaders:   []string{"Content-Type", "Authorization"},
		AllowCredentials: true,
		MaxAge:           3600,
	})
}
