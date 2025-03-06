FROM node:14 as build-stage

WORKDIR /app

# Copy package.json and package-lock.json
COPY DonorDashUI/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY DonorDashUI/ .

# Build the application
RUN npm run build

# Production stage
FROM nginx:stable-alpine as production-stage

# Copy the build output from the build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# NGINX config will be mounted as a volume in docker-compose

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
