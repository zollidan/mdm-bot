package models

import "time"

// User represents a Telegram user profile
type User struct {
	TelegramID  int64     `gorm:"primaryKey;column:telegram_id"`
	Username    *string   `gorm:"column:username"`
	Name        string    `gorm:"column:name"`
	PhoneNumber string    `gorm:"column:phone_number"`
	Address     string    `gorm:"column:address"`
	CreatedDate time.Time `gorm:"column:created_date;autoCreateTime"`
}

// TableName overrides the table name
func (User) TableName() string {
	return "users"
}
