# PC Shop — Django E-Commerce Platform

PC Shop is a Django-based online store built specifically for PC hardware. Customers can browse and buy pre-built PCs or individual components, or use the custom PC builder to pick their own CPU, GPU, RAM, and more — the system checks compatibility and sends the build through an approval and assembly workflow before delivery.

Payments go through Razorpay, supporting UPI, cards, net banking, and cash on delivery for both regular orders and custom builds. A built-in AI chatbot called Vex AI (powered by Google Gemini) helps users with component selection, compatibility questions, and build advice.

Access is split across three roles — customers shop on the storefront, staff manage builds and support tickets, and admins get a full dashboard covering users, products, orders, analytics, and discounts. Supporting features include a cart with coupon codes, product reviews, wishlists, a support ticket system, and in-app notifications for order and build updates.

---

## Features

- Product catalog with categories, brands, and discount codes
- Shopping cart with coupon support (percentage & fixed)
- Order management with status tracking
- Custom PC builder — select components, validate compatibility, track assembly
- Razorpay payment gateway (orders & custom builds)
- Vex AI chatbot powered by Google Gemini with API key fallback and response caching
- Product reviews and ratings
- Wishlist management
- Support ticket system with staff assignment
- In-app notifications (order updates, build approvals, support)
- Role-based access: Customer, Staff, Admin — each with separate login and dashboard
- Admin panel: users, products, orders, builds, discounts, analytics
- Staff panel: build management, support tickets

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.0.1, Django REST Framework |
| Database | MySQL |
| Frontend | Bootstrap 5, crispy-forms |
| Payments | Razorpay |
| AI Chatbot | Google Gemini API (`gemini-2.5-flash`) |
| Image Processing | Pillow |
| Production Server | Gunicorn + WhiteNoise |

---

## Project Structure

> Full file tree: [filetree.md](filetree.md)

```
pc_shop/          # Django project settings & root URLs
accounts/         # Custom user model, roles, shipping addresses
products/         # Products, categories, brands, discounts
cart/             # Cart, cart items, coupon application
orders/           # Orders and order items
payments/         # Payment model, Razorpay integration
customization/    # Custom PC builder (7-component selection)
reviews/          # Product reviews (1 per user per product)
wishlist/         # User wishlists
support/          # Support tickets and responses
notifications/    # In-app notification system
admin_panel/      # Admin dashboard and management views
staff_panel/      # Staff dashboard
chatbot/          # Vex AI chatbot (Gemini-powered)
```

---

## Screenshots

![Screenshot](screenshots/Screenshot%20.png)

![Screenshot 1](screenshots/Screenshot%201.png)

![Screenshot 2](screenshots/Screenshot%202.png)

---

## Setup

### Prerequisites

- Python 3.10+
- MySQL
- pip

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd pc_shop
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True

# MySQL
DB_NAME=pc_shop
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Razorpay (https://razorpay.com)
RAZORPAY_KEY_ID=rzp_test_YOUR_KEY_ID
RAZORPAY_KEY_SECRET=YOUR_KEY_SECRET

# Google Gemini AI (https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your_primary_key
GEMINI_API_KEY_BACKUP=your_backup_key
GEMINI_API_KEY_BACKUP_2=your_second_backup_key
```

### 3. Create the database

```sql
CREATE DATABASE pc_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Run migrations and start

```bash
python manage.py collectstatic
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## User Roles

| Role | Login URL | Dashboard |
|---|---|---|
| Customer | `/accounts/login/` | Product store |
| Staff | `/accounts/staff-login/` | `/staff/dashboard/` |
| Admin | `/accounts/admin-login/` | `/admin/dashboard/` |

Create roles via the Django shell if needed:

```python
from accounts.models import Role
Role.objects.get_or_create(name='customer')
Role.objects.get_or_create(name='staff')
Role.objects.get_or_create(name='admin')
```

---

## Key URLs

```
/                        # Product listing (home)
/products/               # Product catalog
/cart/                   # Shopping cart
/orders/                 # Order history
/customization/          # Custom PC builder
/support/                # Support tickets
/wishlist/               # Wishlist
/notifications/          # Notifications
/chatbot/                # Vex AI chatbot (login required)
/admin/dashboard/        # Admin panel
/staff/dashboard/        # Staff panel
/django-admin/           # Django built-in admin
```

---

## Custom PC Builder

Users can configure a PC with 7 components: CPU, Motherboard, RAM, GPU, Storage, Case, and PSU. The system validates Intel/AMD compatibility and tracks the build through a full lifecycle:

```
pending → approved → paid → in_progress → assembling → testing → shipping → delivered
```

A configurable service charge (default ₹1500) is added on top of component costs. Admins can approve/reject builds and assign them to staff members.

---

## Vex AI Chatbot

The chatbot uses Google Gemini (`gemini-2.5-flash`) and is configured in `chatbot/config.py`:

- Supports up to 3 API keys with automatic fallback on quota exhaustion
- Response caching (1 hour default) to reduce API calls
- Rate limiting (disabled by default, configurable)
- Focused on PC components, custom builds, and compatibility advice

---

## Payment Flow

Razorpay handles payments for both standard orders and custom PC builds. Supported methods: Credit Card, Debit Card, UPI, Net Banking, Cash on Delivery.

Set your Razorpay keys in `.env`. Use test keys (`rzp_test_...`) during development.

---

## Production Notes

- Set `DEBUG=False` and configure a strong `SECRET_KEY`

- Use Gunicorn: `gunicorn pc_shop.wsgi:application`
- Switch `EMAIL_BACKEND` in settings to an SMTP backend for real email delivery
- Restrict `ALLOWED_HOSTS` to your actual domain
