package api

import (
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/render"
	"gorm.io/gorm"

	"mdm-bot/internal/api/handlers"
	customMiddleware "mdm-bot/internal/api/middleware"
	"mdm-bot/internal/config"
)

// Server represents the API server
type Server struct {
	router   *chi.Mux
	db       *gorm.DB
	settings *config.Settings
}

// NewServer creates a new API server instance
func NewServer(db *gorm.DB, settings *config.Settings) *Server {
	s := &Server{
		router:   chi.NewRouter(),
		db:       db,
		settings: settings,
	}

	s.setupMiddleware()
	s.setupRoutes()

	return s
}

// setupMiddleware configures middleware stack
func (s *Server) setupMiddleware() {
	// Standard chi middleware
	s.router.Use(middleware.RequestID)
	s.router.Use(middleware.RealIP)
	s.router.Use(customMiddleware.Logger)
	s.router.Use(middleware.Recoverer)
	s.router.Use(middleware.Heartbeat("/health"))

	// CORS middleware
	s.router.Use(customMiddleware.CORSMiddleware(s.settings).Handler)

	// Set JSON content type
	s.router.Use(render.SetContentType(render.ContentTypeJSON))
}

// setupRoutes configures all API routes
func (s *Server) setupRoutes() {
	// Initialize handlers
	productHandler := handlers.NewProductHandler(s.db)

	// API routes
	s.router.Route("/api", func(r chi.Router) {
		// Product routes
		r.Get("/products", productHandler.GetProducts)
		r.Get("/products/{id}", productHandler.GetProduct)

		// Search
		r.Get("/search", productHandler.SearchProducts)
	})

	// Root endpoint
	s.router.Get("/", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("MDM Bot API is running"))
	})
}

// Start starts the HTTP server
func (s *Server) Start(port string) error {
	addr := ":" + port
	log.Printf("Starting API server on %s", addr)
	return http.ListenAndServe(addr, s.router)
}

// Router returns the chi router instance (useful for testing)
func (s *Server) Router() *chi.Mux {
	return s.router
}
