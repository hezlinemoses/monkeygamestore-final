# monkeygamestore

An e-commerce application build with python django for purchasing games. It comes with an admin panel for managing users, coupons, offers, products and categories.

## Tech stack
 - Django
 - PostgreSQL
 - rq-scheduler(redis queue/background task)

## Features
### Admin panel
 - Dashboard
 - Product management - add, edit, disable, delete games
 - Multiple images and description via django formset, image cropping implemented with cropper.js
 - Category management - basic CURD operation, sub-categories
 - Games can have mutliple categories
 - Coupon management - basic CURD operations, scheduling of coupons using rq-scheduler
 - Coupon for specific order from user, purchase limit etc can be created. Options to set expiry date depending on demands can be created.
 - Offer management - basic CURD operations, scheduling of offers, category wide offer and Product specific offers.
 - Sales report - monthly, weekly reports can be generated and downloaded for further use.
### User side
- Guest cart
- Login with OTP using twilio, email registration and login
- Profile management for users to edit profile details
- Multiple address can be saved for easier use
- Coupons applicable for specific user will be highlighed in cart menu
- Wallet for refunding money when order is cancelled by user
- Payment with Paypal and razorpay integrated

## Other
 - Dockerzied all componenets before hosting in aws
 - Supervisord for running multiple proccesses within docker container
 - Hosted in aws and utilized nginx for loadbalancing and serving static content
 - Used django's signals for various tasks and would never recommend to use it again. Creates additional complexity which can be avoided by not using it!!!
 - Coupons and offers can be scheduled further into future which may not be a good choice
