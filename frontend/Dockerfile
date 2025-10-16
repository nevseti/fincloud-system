FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Copy only required static assets
COPY index.html ./
COPY login.html ./
COPY dashboard.html ./
COPY style.css ./
COPY app.js ./
COPY auth.js ./
COPY finance.js ./

# Simple runtime config injection support (optional)
# You can provide /docker-entrypoint.d script in compose to write window.ENV

EXPOSE 80

# Healthcheck for nginx static server
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -q -O - http://127.0.0.1/ > /dev/null 2>&1 || exit 1


