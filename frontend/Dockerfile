# Étape de build
FROM node:18.20.3 AS build
WORKDIR /app

# Installation des dépendances système requises
RUN apt-get update && apt-get install -y python3 make g++

# Copie des fichiers de dépendances d'abord pour meilleure mise en cache
COPY package*.json ./

# Installation des dépendances avec nettoyage du cache npm
RUN npm cache clean --force && \
    rm -rf node_modules && \
    rm -f package-lock.json && \
    npm install --legacy-peer-deps

# Copie du code source
COPY . .

# Build de l'application avec Vite
ENV NODE_OPTIONS=--openssl-legacy-provider
RUN npm run build

# Étape de production
FROM nginx:alpine

# Copie des fichiers compilés
COPY --from=build /app/dist /usr/share/nginx/html

# Configuration Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exposition du port 80
EXPOSE 80

# Démarrage de Nginx
CMD ["nginx", "-g", "daemon off;"]
