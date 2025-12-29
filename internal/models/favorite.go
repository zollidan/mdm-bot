package models

import "time"

// Favorite represents a user's favorite product
type Favorite struct {
	UserID      int64     `gorm:"primaryKey;column:user_id"`
	ProductID   int       `gorm:"primaryKey;column:product_id"`
	CreatedDate time.Time `gorm:"column:created_date;autoCreateTime"`

	// Relationships
	User    User    `gorm:"foreignKey:UserID;references:TelegramID"`
	Product Product `gorm:"foreignKey:ProductID"`
}

// TableName overrides the table name
func (Favorite) TableName() string {
	return "favorites"
}
