from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from .models import Sweet, Order, Profile
from .forms import ProfileForm, OrderForm
import logging

# Create your views here.

logger = logging.getLogger(__name__)

# 首頁產品呈現
def index(request):
    sweets = Sweet.objects.all()
    return render(request, 'buy/index.html', {'sweets': sweets})

# 用戶註冊
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save(commit=False)
            user.email = profile_form.cleaned_data.get('email')
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
        profile_form = ProfileForm()
    return render(request, 'buy/register.html', {'form': form, 'profile_form': profile_form})

# 登入
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'buy/login.html', {'form': form})

# 登出
@login_required
def user_logout(request):
    logout(request)
    return redirect('index')

@login_required(login_url='/login/')
def order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = OrderForm()
    return render(request, 'buy/order.html', {'form': form})

# 訂單
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'buy/order_history.html', {'orders': orders})

@login_required
def order_confirmation(request, order_id):
    try:
        orders= Order.objects.filter(user=request.user, status='Pending')
        total_price = sum(order.sweet.price * order.quantity for order in orders)
        if request.method == 'POST':
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                new_order = order_form.save(commit=False)
                new_order.user = request.user
                new_order.status = 'Pending'
                new_order.save()
                return redirect('order_confirmation', order_id=new_order.id)
    except ObjectDoesNotExist:
        logger.error("Order does not exsist.")
        return redirect('index')
    
    order_totals = []
    for order in orders:
        order_total = order.sweet.price * order.quantity
        order_totals.append(
            {'order': order,
             'order_total': order_total}
        )

    return render(request, 'buy/order_confirmation.html', 
                  {'orders': order_totals,
                   'total_price': total_price,
                   'order_form': OrderForm(),
                   'order_id': order_id}
                   )

@login_required
def order_confirm(request, order_id):
    try:
        orders= Order.objects.filter(user=request.user, status='Pending')
        total_price = sum(order.sweet.price * order.quantity for order in orders)
        try:
            # Send confirmation email
            send_mail(
                'Order Confirmation',
                f'Thank you for your order, {request.user.username}. You have ordered the following items:\n\n' + '\n'.join([f'{order.quantity} x {order.sweet.name}' for order in orders]) + f'\n\nTotal price: ${total_price:.2f}.',
                'your-email@gmail.com',  # Replace with your actual email address
                [request.user.email],
                fail_silently=False,
            )
            orders.update(status='Confirmed')
            return redirect('order_history')
        except Exception as e:
            logger.error(f"Error sending email: {e}")
    except ObjectDoesNotExist:
        logger.error("Order does not exsist.")
    return redirect('index')

@login_required
def order_increase(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='Pending')
    order.quantity += 1
    order.save()
    return redirect('order_confirmation', order_id=order.id)

@login_required
def order_decrease(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='Pending')
    if order.quantity > 1:
        order.quantity -= 1
        order.save()
    return redirect('order_confirmation', order_id=order.id)

@login_required
def order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='Pending')
    order.delete()
    return redirect('order_confirmation', order_id=order.id)

@login_required
def add_item_to_order(request, order_id):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.user = request.user
            new_order.status = 'Pending'
            new_order.save()
    return redirect('order_confirmation', order_id=order_id)