### 1. Clone the Repository

```bash
git clone https://github.com/ivan-22-3-5/pet-store.git
cd pet-store
```

---

### 2. build docker images and run the containers using `docker-compose`

```bash
docker-compose up --build
```

---

### 3. Access the Application

Once running, the API/backend should be accessible at:

```
http://localhost:8000
```

The docs are available at:

```
http://localhost:8000/docs
```

---

## ⚙️ Configuration

You should define the following environment variables in a `.env` file:

POSTGRES_USER – The username for the PostgreSQL database.  
POSTGRES_DB – The name of the default PostgreSQL database to be created when the container starts.  
POSTGRES_PASSWORD – The password for the PostgreSQL user.

STATIC_PATH – Path to the folder where static files (specifically images) are stored and served from.

CELERY_BROKER_URL – The Redis connection URL used by Celery as the message broker (for task queuing).
CELERY_BACKEND_URL – The Redis connection URL used by Celery to store and retrieve task results.

TOKEN_SECRET_KEY – A secret key used for signing JWT tokens.  

STRIPE_SECRET_KEY – The private Stripe API key used by your backend to authenticate API requests to Stripe.  
STRIPE_WEBHOOK_SECRET – Secret used to verify the authenticity of incoming webhook events from Stripe.

GOOGLE_CLIENT_ID – The OAuth 2.0 client ID used to initiate login/authentication via Google.  
GOOGLE_CLIENT_SECRET – The client secret used to securely exchange the authorization code for access tokens.  
GOOGLE_REDIRECT_URL – The callback URL to which Google redirects users after successful authentication.  

SMTP_USERNAME – The email address used to authenticate with the SMTP server.  
SMTP_PASSWORD – The password (or app-specific password) used to authenticate with the SMTP server.  
SMTP_PORT – The port number used to send email over SMTP.  
SMTP_MAIL – The sender email address that appears in the “From” field of outgoing emails.  
SMTP_SERVER – The hostname or IP address of the SMTP server.  

Example `.env`:

```dotenv
# USED IN DOCKER COMPOSE
POSTGRES_USER=postgres
POSTGRES_DB=petstore_db
POSTGRES_PASSWORD=qwerty123

STATIC_PATH=static

CELERY_BROKER_URL=redis://redis_container:6379/0
CELERY_BACKEND_URL=redis://redis_container:6379/1

# SOLELY APP CONFIGURATION
TOKEN_SECRET_KEY=nbjk1examples809exampledfvbs9examplees8i903415examplefbsi9u35q24examplelvi90534

STRIPE_SECRET_KEY=sk_test_51RIsBexampleKrAxEkexamplePD57KTZexampleSvBpfexampleTnVwHexampleOTw00krstO
STRIPE_WEBHOOK_SECRET=whsec_a451example539examplee638example402examplec7b43examplea02bb20

GOOGLE_CLIENT_ID=123456789012-k40pexample2r25example0st1.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GODSXD-SO-XWRexampleRbDk-OoexampleC
GOOGLE_REDIRECT_URL=http://127.0.0.1:8000/auth/google/callback

SMTP_USERNAME=example@gmail.com
SMTP_PASSWORD=secret_password
SMTP_PORT=587
SMTP_MAIL=example@gmail.com
SMTP_SERVER=smtp.gmail.com
```

---

## 🛠️ Requirements

* Docker
* Docker Compose

---

