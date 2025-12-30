package search

import (
	"encoding/json"
	"fmt"
	"log"
	"strconv"
	"time"

	"github.com/meilisearch/meilisearch-go"
	"gorm.io/gorm"

	"mdm-bot/internal/config"
	"mdm-bot/internal/models"
)

const IndexName = "products"

// Client wraps MeiliSearch client with application-specific logic
type Client struct {
	client   meilisearch.ServiceManager
	index    meilisearch.IndexManager
	settings *config.Settings
	db       *gorm.DB
}

// ProductDocument represents a product in MeiliSearch index
type ProductDocument struct {
	ID          int     `json:"id"`
	Name        string  `json:"name"`
	VendorCode  string  `json:"vendor_code"`
	Price       float64 `json:"price"`
	Vendor      string  `json:"vendor"`
	Model       string  `json:"model"`
	Description string  `json:"description"`
	Availability string `json:"availability"`
	IsBestseller bool   `json:"is_bestseller"`
}

// NewClient creates a new MeiliSearch client instance
func NewClient(settings *config.Settings, db *gorm.DB) (*Client, error) {
	meiliURL := config.AppSettings.GetMeiliSearchURL()

	// Create MeiliSearch client
	client := meilisearch.New(meiliURL, meilisearch.WithAPIKey(settings.MeiliMasterKey))

	// Get or create index
	index := client.Index(IndexName)

	c := &Client{
		client:   client,
		index:    index,
		settings: settings,
		db:       db,
	}

	log.Printf("MeiliSearch client initialized at %s", meiliURL)
	return c, nil
}

// InitIndex initializes and configures the products index
func (c *Client) InitIndex() error {
	log.Printf("Initializing MeiliSearch index '%s'...", IndexName)

	// Configure searchable attributes (fields to search in)
	searchableAttrs := []string{
		"name",
		"description",
		"vendor",
		"vendor_code",
		"model",
	}
	_, err := c.index.UpdateSearchableAttributes(&searchableAttrs)
	if err != nil {
		return fmt.Errorf("failed to update searchable attributes: %w", err)
	}

	// Configure filterable attributes (for filtering results)
	filterableAttrs := []string{
		"price",
		"availability",
		"vendor",
		"is_bestseller",
	}
	// Convert to []interface{} as required by the API
	filterableInterfaces := make([]interface{}, len(filterableAttrs))
	for i, v := range filterableAttrs {
		filterableInterfaces[i] = v
	}
	_, err = c.index.UpdateFilterableAttributes(&filterableInterfaces)
	if err != nil {
		return fmt.Errorf("failed to update filterable attributes: %w", err)
	}

	// Configure sortable attributes
	sortableAttrs := []string{"price"}
	_, err = c.index.UpdateSortableAttributes(&sortableAttrs)
	if err != nil {
		return fmt.Errorf("failed to update sortable attributes: %w", err)
	}

	// Configure typo tolerance
	typoTolerance := meilisearch.TypoTolerance{
		Enabled: true,
		MinWordSizeForTypos: meilisearch.MinWordSizeForTypos{
			OneTypo:  5,
			TwoTypos: 9,
		},
	}
	_, err = c.index.UpdateTypoTolerance(&typoTolerance)
	if err != nil {
		return fmt.Errorf("failed to update typo tolerance: %w", err)
	}

	log.Printf("Index '%s' configured successfully", IndexName)
	return nil
}

// SyncProducts synchronizes all products from PostgreSQL to MeiliSearch
func (c *Client) SyncProducts() error {
	log.Println("Starting product synchronization...")

	// Fetch all products from database
	var products []models.Product
	if err := c.db.Find(&products).Error; err != nil {
		return fmt.Errorf("failed to fetch products from database: %w", err)
	}

	if len(products) == 0 {
		log.Println("No products found in database")
		return nil
	}

	// Prepare documents for MeiliSearch
	documents := make([]ProductDocument, len(products))
	for i, product := range products {
		description := ""
		if product.Description != nil {
			description = *product.Description
		}
		documents[i] = ProductDocument{
			ID:           int(product.ID),
			Name:         product.Name,
			VendorCode:   product.VendorCode,
			Price:        product.Price,
			Vendor:       product.Vendor,
			Model:        product.Model,
			Description:  description,
			Availability: product.Availability,
			IsBestseller: product.IsBestseller,
		}
	}

	// Add documents to MeiliSearch
	task, err := c.index.AddDocuments(documents, nil)
	if err != nil {
		return fmt.Errorf("failed to add documents to MeiliSearch: %w", err)
	}

	log.Printf("Synced %d products to MeiliSearch. Task UID: %d", len(documents), task.TaskUID)

	// Wait for the task to complete (30 second timeout)
	_, err = c.client.WaitForTask(task.TaskUID, 30*time.Second)
	if err != nil {
		return fmt.Errorf("failed to wait for indexing task: %w", err)
	}

	log.Println("Product synchronization completed successfully")
	return nil
}

// SearchProducts searches for products and returns list of product IDs
func (c *Client) SearchProducts(query string, limit int64) ([]int, error) {
	if limit <= 0 {
		limit = 5
	}
	if limit > 100 {
		limit = 100
	}

	// Perform search
	searchRes, err := c.index.Search(query, &meilisearch.SearchRequest{
		Limit: limit,
		AttributesToRetrieve: []string{"id"},
	})
	if err != nil {
		return nil, fmt.Errorf("search failed: %w", err)
	}

	// Extract product IDs
	productIDs := make([]int, 0, len(searchRes.Hits))
	for _, hit := range searchRes.Hits {
		// Hit is map[string]json.RawMessage, extract and unmarshal id
		if idRaw, ok := hit["id"]; ok {
			var id interface{}
			if err := json.Unmarshal(idRaw, &id); err != nil {
				continue
			}

			// Handle both float64 (JSON number) and int
			switch v := id.(type) {
			case float64:
				productIDs = append(productIDs, int(v))
			case int:
				productIDs = append(productIDs, v)
			case string:
				if parsedID, err := strconv.Atoi(v); err == nil {
					productIDs = append(productIDs, parsedID)
				}
			}
		}
	}

	log.Printf("Search query '%s' returned %d results", query, len(productIDs))
	return productIDs, nil
}

// HealthCheck checks if MeiliSearch is healthy
func (c *Client) HealthCheck() (bool, error) {
	health, err := c.client.Health()
	if err != nil {
		return false, fmt.Errorf("health check failed: %w", err)
	}

	return health.Status == "available", nil
}

// AddProduct adds or updates a single product in the index
func (c *Client) AddProduct(product *models.Product) error {
	description := ""
	if product.Description != nil {
		description = *product.Description
	}

	doc := ProductDocument{
		ID:           int(product.ID),
		Name:         product.Name,
		VendorCode:   product.VendorCode,
		Price:        product.Price,
		Vendor:       product.Vendor,
		Model:        product.Model,
		Description:  description,
		Availability: product.Availability,
		IsBestseller: product.IsBestseller,
	}

	task, err := c.index.AddDocuments([]ProductDocument{doc}, nil)
	if err != nil {
		return fmt.Errorf("failed to add product to index: %w", err)
	}

	_, err = c.client.WaitForTask(task.TaskUID, 10*time.Second)
	if err != nil {
		return fmt.Errorf("failed to wait for indexing task: %w", err)
	}

	return nil
}

// DeleteProduct removes a product from the index
func (c *Client) DeleteProduct(productID int) error {
	task, err := c.index.DeleteDocument(strconv.Itoa(productID), nil)
	if err != nil {
		return fmt.Errorf("failed to delete product from index: %w", err)
	}

	_, err = c.client.WaitForTask(task.TaskUID, 10*time.Second)
	if err != nil {
		return fmt.Errorf("failed to wait for deletion task: %w", err)
	}

	return nil
}
