package models

// Package models contains all database models for the MDM Bot application.
// This file serves as a central import point for all models.

// AllModels returns a slice of all model types for database migration
func AllModels() []interface{} {
	return []interface{}{
		&User{},
		&Product{},
		&Favorite{},
		&CartItem{},
		&Order{},
		&OrderItem{},
		&Review{},
	}
}
