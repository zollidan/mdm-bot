package models

import "time"

// Review represents user reviews and feedback
type Review struct {
	ID          int       `gorm:"primaryKey;column:id"`
	UserID      int64     `gorm:"column:user_id"`
	UserText    string    `gorm:"column:user_text"`
	CreatedDate time.Time `gorm:"column:created_date;autoCreateTime"`

	// Relationships
	User User `gorm:"foreignKey:UserID;references:TelegramID"`
}

// TableName overrides the table name
func (Review) TableName() string {
	return "reviews"
}
