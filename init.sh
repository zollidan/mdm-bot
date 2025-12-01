#!/bin/bash

# Проверка на запуск от root
if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен быть запущен с правами root (sudo)"
   exit 1
fi

echo "Начинаем первоначальную настройку сервера..."

apt update && apt upgrade -y

echo "Система обновлена."

apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update

apt install -y docker-ce docker-ce-cli containerd.io


# Вроде бы само запускается но если что раскомментировать
# systemctl enable docker
# systemctl start docker

echo "Docker установлен и запущен."

# Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

echo "Docker Compose установлен."

echo "Настройка завершена!"

systemctl status docker

# Experemental mb mb...
docker run hello-world
