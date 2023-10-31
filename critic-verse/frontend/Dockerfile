FROM node:20 AS build

WORKDIR /app

COPY package*.json ./

COPY . .

RUN npm install

RUN npm run build

# Serve Application using Nginx Server
FROM nginx:alpine

COPY --from=build /app/dist/critic-verse/ /usr/share/nginx/html

EXPOSE 80
