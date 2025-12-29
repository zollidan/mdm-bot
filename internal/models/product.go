package models

import "time"

// Product represents a store product catalog item
type Product struct {
	ID                   int       `gorm:"primaryKey;column:id"`
	URL                  string    `gorm:"column:url"`
	Name                 string    `gorm:"column:name"`
	VendorCode           string    `gorm:"column:vendor_code"`
	Price                float64   `gorm:"column:price"`
	CurrencyID           string    `gorm:"column:currency_id"`
	CategoryID           int       `gorm:"column:category_id"`
	Model                string    `gorm:"column:model"`
	Vendor               string    `gorm:"column:vendor"`
	Description          *string   `gorm:"column:description"`
	ManufacturerWarranty bool      `gorm:"column:manufacturer_warranty"`
	Image                string    `gorm:"column:image"`
	OptPrice             *float64  `gorm:"column:opt_price"`
	IsBestseller         bool      `gorm:"column:is_bestseller"`
	Unit                 string    `gorm:"column:unit"`
	USDPrice             *float64  `gorm:"column:usd_price"`
	Availability         string    `gorm:"column:availability"`
	Status               *string   `gorm:"column:status"`
	CreatedDate          time.Time `gorm:"column:created_date;autoCreateTime"`

	// Stock levels
	StockChashnikovo     *string `gorm:"column:stock_chashnikovo"`
	StockKantemirovskaya *string `gorm:"column:stock_kantemirovskaya"`
	StockSPB             *string `gorm:"column:stock_spb"`
	StockVoronezh        *string `gorm:"column:stock_voronezh"`
	StockKorolev         *string `gorm:"column:stock_korolev"`
	StockKrasnodar       *string `gorm:"column:stock_krasnodar"`
	StockKazan           *string `gorm:"column:stock_kazan"`
	StockOnline          *string `gorm:"column:stock_online"`

	// Belarus prices
	PriceBYNLegal  *float64 `gorm:"column:price_byn_legal"`
	PriceBYNRetail *float64 `gorm:"column:price_byn_retail"`

	// Relationships
	Favorites  []Favorite  `gorm:"foreignKey:ProductID"`
	CartItems  []CartItem  `gorm:"foreignKey:ProductID"`
	OrderItems []OrderItem `gorm:"foreignKey:ProductID"`
}

// TableName overrides the table name
func (Product) TableName() string {
	return "products"
}
