FROM node:20-alpine

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 4321

# Comando por defecto
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
