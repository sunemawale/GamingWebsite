from django.shortcuts import render, redirect
from .models import Product, Order , OrderItem
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import re
import uuid
from django.conf import settings
from django.shortcuts import redirect
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt





# ================= Home Page =================
def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'STATIC_VERSION': 1
    })

# ================= Product Detail =================
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'store/product_detail.html', {
        'product': product,
        'STATIC_VERSION': 1
    })

# ================= Add to Cart =================
@login_required
def add_to_cart(request, id):
    cart = request.session.get('cart', {})

    # increase quantity if already exists
    if str(id) in cart:
        cart[str(id)] += 1
    else:
        cart[str(id)] = 1

    request.session['cart'] = cart
    return redirect('cart') 

# ================= Cart Page =================
def cart(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for key, value in cart.items():
        product = Product.objects.get(id=key)
        product.quantity = value
        product.total_price = product.price * value
        total += product.total_price
        products.append(product)

    return render(request, 'store/cart.html', {
        'products': products,
        'total': total
    })

# ================= Remove / Update Quantity =================

def remove_from_cart(request, id):
    cart = request.session.get('cart', {})
    if str(id) in cart:
        del cart[str(id)]
    request.session['cart'] = cart
    return redirect('cart')


def increase_quantity(request, id):
    cart = request.session.get('cart', {})
    if str(id) in cart:
        cart[str(id)] += 1
    request.session['cart'] = cart
    return redirect('/cart/')


def decrease_quantity(request, id):
    cart = request.session.get('cart', {})
    if str(id) in cart:
        cart[str(id)] -= 1
        if cart[str(id)] <= 0:
            del cart[str(id)]
    request.session['cart'] = cart
    return redirect('/cart/')

# ================= Checkout =================
@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        phone = request.POST['phone']

        # calculate total
        total = 0
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            total += product.price * quantity

        # save order
        order = Order.objects.create(
            user=request.user,  # link order to logged-in user
            name=name,
            address=address,
            phone=phone,
            total_amount=total
        )

        # ================= Add this part =================
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )
        # ==================================================

        # clear cart
        request.session['cart'] = {}

        return render(request, 'store/success.html', {'order': order})

    return render(request, 'store/checkout.html', {'cart': cart})


# def help_support(request):
#     return render(request, 'store/help.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # ================= EMPTY CHECK =================
        if not username or not email or not password or not confirm_password:
            messages.error(request, "All fields are required")
            return redirect('register')

        # ================= USERNAME VALIDATION =================
        if len(username) < 3:
            messages.error(request, "Username must be at least 3 characters")
            return redirect('register')

        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        # ================= EMAIL VALIDATION =================
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        # ================= PASSWORD VALIDATION =================
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return redirect('register')

        # At least one number
        if not re.search(r'\d', password):
            messages.error(request, "Password must contain at least one number")
            return redirect('register')

        # At least one letter
        if not re.search(r'[A-Za-z]', password):
            messages.error(request, "Password must contain at least one letter")
            return redirect('register')

        # Match confirm password
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        # ================= CREATE USER =================
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, 'store/register.html')



def user_login(request):
    if request.method == 'POST':
        email = request.POST['email'].strip()
        password = request.POST['password']

        if not email or not password:
            messages.error(request, "All fields are required")
            return redirect('login')

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username  # Django still needs username internally

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password")
                return redirect('login')

        except User.DoesNotExist:
            messages.error(request, "Email not found")
            return redirect('login')

    return render(request, 'store/login.html')


def user_logout(request):
    logout(request)
    return redirect('/')



@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')

    for order in orders:
        for item in order.orderitem_set.all():
            item.subtotal = item.product.price * item.quantity

    return render(request, 'store/my_orders.html', {'orders': orders})

def myproduct(request):
    products = Product.objects.all()
    return render(request, 'store/myproduct.html', {'products': products})

def about(request):
    return render(request, 'store/about.html')



@csrf_exempt
def khalti_verify(request):
    if request.method == "POST":
        data = json.loads(request.body)

        token = data.get("token")
        amount = data.get("amount")
        order_id = data.get("order_id")  # important (you should send this from frontend)

        url = "https://khalti.com/api/v2/payment/verify/"

        payload = {
            "token": token,
            "amount": amount
        }

        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}"
        }

        response = requests.post(url, data=payload, headers=headers)
        result = response.json()

        # ✅ SUCCESS CASE
        if response.status_code == 200 and result.get("idx"):
            
            # update order in database
            order = Order.objects.get(id=order_id)
            order.paid = True   # (you must add this field in model)
            order.payment_method = "Khalti"
            order.save()

            return JsonResponse({
                "status": "success",
                "message": "Payment verified successfully"
            })

        # ❌ FAILED CASE
        return JsonResponse({
            "status": "failed",
            "message": "Payment verification failed"
        })

