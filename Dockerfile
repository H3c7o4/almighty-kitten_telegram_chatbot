# Utilisation de l'image python officielle
FROM python:3.8

# Mise à jour du système et installation des dépendances
RUN apt-get update && apt-get install -y \
    python3-pip \
    git

# Copie de vos fichiers locaux dans le conteneur
COPY . /app

# Définition du répertoire de travail
WORKDIR /app

# Installation des dépendances Python
RUN pip install --upgrade pip
RUN pip install python-telegram-bot google-generativeai requests

# Commande par défaut à exécuter lors du démarrage du conteneur
CMD ["python3", "main.py"]
