package schemas

// ProductResponse represents a product in API responses
type ProductResponse struct {
	ID          int     `json:"id"`
	Name        string  `json:"name"`
	Price       float64 `json:"price"`
	Image       *string `json:"image,omitempty"`
	VendorCode  *string `json:"vendor_code,omitempty"`
	Description *string `json:"description,omitempty"`
}

// ProductsListResponse represents paginated product list
type ProductsListResponse struct {
	Items      []ProductResponse `json:"items"`
	Total      int               `json:"total"`
	Page       int               `json:"page"`
	Limit      int               `json:"limit"`
	TotalPages int               `json:"total_pages"`
}

// SearchResponse represents search results
type SearchResponse struct {
	Items []ProductResponse `json:"items"`
	Total int               `json:"total"`
	Query string            `json:"query"`
}

// HealthResponse represents health check response
type HealthResponse struct {
	Status  string `json:"status"`
	Service string `json:"service"`
}

// ErrorResponse represents API error response
type ErrorResponse struct {
	Error  string `json:"error"`
	Detail string `json:"detail,omitempty"`
}
