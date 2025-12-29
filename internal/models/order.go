package models

import "time"

// Order represents a user order
type Order struct {
	ID             int       `gorm:"primaryKey;column:id"`
	UserID         int64     `gorm:"column:user_id"`
	TotalSum       float64   `gorm:"column:total_sum"`
	Status         string    `gorm:"column:status;default:processing"`
	DeliveryMethod *string   `gorm:"column:delivery_method"`
	PaymentMethod  *string   `gorm:"column:payment_method"`
	TrackingNumber *string   `gorm:"column:tracking_number"`
	OrderDate      time.Time `gorm:"column:order_date;autoCreateTime"`
	CreatedDate    time.Time `gorm:"column:created_date;autoCreateTime"`

	// Relationships
	User       User        `gorm:"foreignKey:UserID;references:TelegramID"`
	OrderItems []OrderItem `gorm:"foreignKey:OrderID"`
}

// TableName overrides the table name
func (Order) TableName() string {
	return "orders"
}

// OrderItem represents an item in an order
type OrderItem struct {
	ID          int       `gorm:"primaryKey;column:id"`
	OrderID     int       `gorm:"column:order_id"`
	ProductID   int       `gorm:"column:product_id"`
	Quantity    int       `gorm:"column:quantity"`
	Price       float64   `gorm:"column:price"`
	CreatedDate time.Time `gorm:"column:created_date;autoCreateTime"`

	// Relationships
	Order   Order   `gorm:"foreignKey:OrderID"`
	Product Product `gorm:"foreignKey:ProductID"`
}

// TableName overrides the table name
func (OrderItem) TableName() string {
	return "order_items"
}
