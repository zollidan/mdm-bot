package handlers

import (
	"math"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/render"
	"gorm.io/gorm"

	"mdm-bot/internal/models"
	"mdm-bot/internal/schemas"
)

// ProductHandler handles product-related requests
type ProductHandler struct {
	db *gorm.DB
}

// NewProductHandler creates a new product handler
func NewProductHandler(db *gorm.DB) *ProductHandler {
	return &ProductHandler{db: db}
}

// GetProducts returns paginated list of products
// GET /api/products?page=1&limit=20
func (h *ProductHandler) GetProducts(w http.ResponseWriter, r *http.Request) {
	// Parse query parameters
	page, _ := strconv.Atoi(r.URL.Query().Get("page"))
	if page < 1 {
		page = 1
	}

	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	if limit < 1 || limit > 100 {
		limit = 20
	}

	// Count total products
	var total int64
	if err := h.db.Model(&models.Product{}).Count(&total).Error; err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		render.JSON(w, r, schemas.ErrorResponse{
			Error:  "Database error",
			Detail: err.Error(),
		})
		return
	}

	// Calculate pagination
	totalPages := int(math.Ceil(float64(total) / float64(limit)))
	offset := (page - 1) * limit

	// Get products for current page
	var products []models.Product
	if err := h.db.Order("id").Offset(offset).Limit(limit).Find(&products).Error; err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		render.JSON(w, r, schemas.ErrorResponse{
			Error:  "Database error",
			Detail: err.Error(),
		})
		return
	}

	// Convert to response DTOs
	items := make([]schemas.ProductResponse, len(products))
	for i, p := range products {
		items[i] = schemas.ProductResponse{
			ID:          p.ID,
			Name:        p.Name,
			Price:       p.Price,
			Image:       &p.Image,
			VendorCode:  &p.VendorCode,
			Description: p.Description,
		}
	}

	response := schemas.ProductsListResponse{
		Items:      items,
		Total:      int(total),
		Page:       page,
		Limit:      limit,
		TotalPages: totalPages,
	}

	render.JSON(w, r, response)
}

// GetProduct returns a specific product by ID
// GET /api/products/{id}
func (h *ProductHandler) GetProduct(w http.ResponseWriter, r *http.Request) {
	productIDStr := chi.URLParam(r, "id")
	productID, err := strconv.Atoi(productIDStr)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		render.JSON(w, r, schemas.ErrorResponse{
			Error:  "Invalid product ID",
			Detail: "Product ID must be a number",
		})
		return
	}

	var product models.Product
	if err := h.db.First(&product, productID).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			w.WriteHeader(http.StatusNotFound)
			render.JSON(w, r, schemas.ErrorResponse{
				Error:  "Product not found",
				Detail: "Товар не найден",
			})
			return
		}

		w.WriteHeader(http.StatusInternalServerError)
		render.JSON(w, r, schemas.ErrorResponse{
			Error:  "Database error",
			Detail: err.Error(),
		})
		return
	}

	response := schemas.ProductResponse{
		ID:          product.ID,
		Name:        product.Name,
		Price:       product.Price,
		Image:       &product.Image,
		VendorCode:  &product.VendorCode,
		Description: product.Description,
	}

	render.JSON(w, r, response)
}

// SearchProducts searches for products
// GET /api/search?q=query&limit=20
func (h *ProductHandler) SearchProducts(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")
	if query == "" {
		w.WriteHeader(http.StatusBadRequest)
		render.JSON(w, r, schemas.ErrorResponse{
			Error:  "Query parameter required",
			Detail: "Parameter 'q' is required",
		})
		return
	}

	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	if limit < 1 || limit > 100 {
		limit = 20
	}

	// Simple search by name or vendor code
	// TODO: Integrate with MeiliSearch for better search
	var products []models.Product
	searchPattern := "%" + query + "%"
	err := h.db.
		Where("name ILIKE ? OR vendor_code ILIKE ?", searchPattern, searchPattern).
		Limit(limit).
		Find(&products).Error

	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		render.JSON(w, r, schemas.ErrorResponse{
			Error:  "Search error",
			Detail: err.Error(),
		})
		return
	}

	// Convert to response DTOs
	items := make([]schemas.ProductResponse, len(products))
	for i, p := range products {
		items[i] = schemas.ProductResponse{
			ID:          p.ID,
			Name:        p.Name,
			Price:       p.Price,
			Image:       &p.Image,
			VendorCode:  &p.VendorCode,
			Description: p.Description,
		}
	}

	response := schemas.SearchResponse{
		Items: items,
		Total: len(items),
		Query: query,
	}

	render.JSON(w, r, response)
}
