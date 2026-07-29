# syntax=docker/dockerfile:1

# --------------------------------------------------------------------------
# Development: Angular CLI dev server with live reload, code mounted as a
# volume so edits on the host are picked up immediately.
# --------------------------------------------------------------------------
FROM node:22-alpine AS development

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 4200

CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--port", "4200", "--poll", "2000"]

# --------------------------------------------------------------------------
# Build: compiles the production bundle
# --------------------------------------------------------------------------
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npx ng build --configuration production

# --------------------------------------------------------------------------
# Production: static bundle served by nginx
# --------------------------------------------------------------------------
FROM nginx:1.27-alpine AS production

COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
