```
pc-shop/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── readme.md
├── filetree.md
│
├── pc_shop/                        # Project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                       # Users, roles, shipping addresses
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── decorators.py
│   ├── context_processors.py
│   └── migrations/
│
├── products/                       # Product catalog, categories, brands
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templatetags/
│   │   └── product_filters.py
│   └── migrations/
│
├── cart/                           # Shopping cart, coupon codes
│   ├── models.py
│   ├── views.py
│   ├── razorpay_views.py
│   ├── urls.py
│   ├── context_processors.py
│   └── migrations/
│
├── orders/                         # Order management, tracking
│   ├── models.py
│   ├── views.py
│   ├── razorpay_views.py
│   ├── urls.py
│   └── migrations/
│
├── payments/                       # Payment model, Razorpay integration
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── customization/                  # Custom PC builder (7-component)
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   └── migrations/
│
├── reviews/                        # Product reviews and ratings
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── migrations/
│
├── wishlist/                       # User wishlists
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── support/                        # Support tickets
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── notifications/                  # In-app notifications
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── context_processors.py
│   └── migrations/
│
├── chatbot/                        # Vex AI chatbot (Gemini-powered)
│   ├── views.py
│   ├── config.py
│   ├── models.py
│   ├── usage_stats.py
│   ├── urls.py
│   └── migrations/
│
├── admin_panel/                    # Admin dashboard
│   ├── middleware.py
│   ├── models.py
│   ├── urls.py
│   └── views/
│       ├── dashboard.py
│       ├── users.py
│       ├── staff.py
│       ├── products.py
│       ├── orders.py
│       ├── custom_builds.py
│       ├── categories.py
│       ├── brands.py
│       ├── reviews.py
│       ├── support.py
│       ├── analytics.py
│       ├── discounts.py
│       └── logs.py
│
├── staff_panel/                    # Staff dashboard
│   ├── middleware.py
│   ├── views.py
│   ├── urls.py
│   ├── static/
│   └── templates/
│
├── templates/                      # All HTML templates
│   ├── base.html
│   ├── home.html
│   ├── authentication/
│   ├── products/
│   ├── cart/
│   ├── orders/
│   ├── payments/
│   ├── customization/
│   ├── reviews/
│   ├── wishlist/
│   ├── support/
│   ├── notifications/
│   ├── admin_panel/
│   └── staff_panel/
│
├── static/                         # Source static files
│   ├── css/
│   │   ├── style.css
│   │   ├── admin.css
│   │   ├── staff.css
│   │   └── customization.css
│   └── js/
│       ├── main.js
│       ├── admin.js
│       ├── staff.js
│       ├── customization.js
│       └── pc-builder-recommendations.js
│
├── screenshots/                    # Project screenshots
│   ├── Screenshot .png
│   ├── Screenshot 1.png
│   └── Screenshot 2.png
│
└── Z DATA/                         # Dev data management scripts
    ├── manage_data.py
    └── clear_data.py
```
