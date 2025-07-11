# Frontend React (Vite)
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* ./* ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
# Copie des fichiers compilés
COPY --from=build /app/dist /usr/share/nginx/html
# Copie de la configuration SPA fallback
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
