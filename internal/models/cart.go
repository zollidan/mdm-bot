package models

import "time"

// CartItem represents a shopping cart item
type CartItem struct {
	ID          int       `gorm:"primaryKey;column:id"`
	UserID      int64     `gorm:"column:user_id"`
	ProductID   int       `gorm:"column:product_id"`
	Quantity    int       `gorm:"column:quantity;default:1"`
	AddedDate   time.Time `gorm:"column:added_date;autoCreateTime"`
	CreatedDate time.Time `gorm:"column:created_date;autoCreateTime"`

	// Relationships
	User    User    `gorm:"foreignKey:UserID;references:TelegramID"`
	Product Product `gorm:"foreignKey:ProductID"`
}

// TableName overrides the table name
func (CartItem) TableName() string {
	return "cart_items"
}
