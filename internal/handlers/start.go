package handlers

import (
	"fmt"
	"log"

	"mdm-bot/internal/config"
	"mdm-bot/internal/database"
	"mdm-bot/internal/models"

	tele "gopkg.in/telebot.v4"
	"gorm.io/gorm"
)

// HandleStart handles the /start command
// Creates or updates user in database and sends Mini App link
func HandleStart(c tele.Context) error {
	userID := c.Sender().ID
	username := c.Sender().Username
	fullName := fmt.Sprintf("%s %s", c.Sender().FirstName, c.Sender().LastName)
	if fullName == " " {
		fullName = c.Sender().FirstName
	}

	log.Printf("User %d started the bot", userID)

	// Find or create user
	var user models.User
	result := database.DB.Where("telegram_id = ?", userID).First(&user)

	if result.Error == gorm.ErrRecordNotFound {
		// Create new user
		user = models.User{
			TelegramID:  userID,
			Username:    &username,
			Name:        fullName,
			PhoneNumber: "",
			Address:     "",
		}
		if err := database.DB.Create(&user).Error; err != nil {
			log.Printf("Error creating user %d: %v", userID, err)
			return c.Send("Произошла ошибка при создании профиля")
		}
		log.Printf("New user %d created", userID)
	} else if result.Error != nil {
		log.Printf("Error querying user %d: %v", userID, result.Error)
		return c.Send("Произошла ошибка при получении данных")
	} else {
		// Update username if changed
		if user.Username == nil || *user.Username != username {
			user.Username = &username
			if err := database.DB.Save(&user).Error; err != nil {
				log.Printf("Error updating user %d: %v", userID, err)
			}
		}
		log.Printf("Existing user %d returned", userID)
	}

	// Create Mini App button
	webappButton := tele.InlineButton{
		Text: "🛍️ Открыть каталог",
		WebApp: &tele.WebApp{
			URL: config.AppSettings.WebappURL,
		},
	}

	keyboard := &tele.ReplyMarkup{
		InlineKeyboard: [][]tele.InlineButton{
			{webappButton},
		},
	}

	welcomeMessage := fmt.Sprintf(
		"👋 Привет, %s!\n\n"+
			"Добро пожаловать в MDM Bot — ваш магазин в Telegram!\n\n"+
			"🔹 Просматривайте каталог товаров\n"+
			"🔹 Добавляйте товары в корзину\n"+
			"🔹 Оформляйте заказы\n\n"+
			"Нажмите кнопку ниже, чтобы открыть каталог 👇",
		fullName,
	)

	return c.Send(welcomeMessage, keyboard)
}
