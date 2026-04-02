from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils import timezone
from django.db.models import Q
from django.db.models import Avg

from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

from .models import UserProfile, Shop, Category, Complaint, Feedback, Request, Rating, Payment


# ==========================================
# 1. AUTHENTICATION & PUBLIC VIEWS
# ==========================================

def home(request):
    return render(request, 'index.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            request.session['user_id'] = user.id

            # Redirect based on Group
            if user.groups.filter(name='shop').exists():
                try:
                    shop = Shop.objects.get(USER=user)
                    request.session['shop_id'] = shop.id
                    if shop.status == 'approved':
                        return redirect('shop_home')
                    else:
                        messages.error(request, 'Account pending approval')
                        return redirect('login')
                except Shop.DoesNotExist:
                    messages.error(request, 'Shop profile not found')
                    return redirect('login')

            elif user.groups.filter(name='user').exists():
                return redirect('user_home')
            elif user.is_superuser:
                return redirect('admin_home')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    return render(request, 'login.html')


@never_cache
def logout_view(request):
    auth_logout(request)
    request.session.flush()  # Completely clears session data & cookies
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

# def register_shop(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         shop_name = request.POST['shop_name']
#         owner_name = request.POST['owner_name']
#         email = request.POST['email']
#         phone = request.POST['phone']
#
#         # Capabilities
#         shop_type_val = request.POST['shop_type']
#         equipment = request.POST['equipment']
#         materials = request.POST['materials']
#         city = request.POST['city']
#         turnaround = request.POST['turnaround']
#         proof_type = request.POST['proof_type']
#
#         if 'proof_file' in request.FILES:
#             proof_file = request.FILES['proof_file']
#         else:
#             proof_file = None
#
#         if User.objects.filter(username=username).exists():
#             messages.error(request, 'Shop ID already exists')
#             return redirect('register_shop')
#
#         # Create User & Shop
#         user = User.objects.create_user(username=username, password=password, email=email, first_name=shop_name)
#         user.save()
#
#         group, _ = Group.objects.get_or_create(name='shop')
#         user.groups.add(group)
#
#         Shop.objects.create(
#             USER=user,
#             shop_name=shop_name,
#             owner_name=owner_name,
#             email=email,
#             phone=phone,
#             place=city,
#             shop_type=shop_type_val,
#             equipment=equipment,
#             materials=materials,
#             turnaround_time=turnaround,
#             proof_type=proof_type,
#             proof_file=proof_file,
#             status='pending'
#         )
#         messages.success(request, 'Shop registered! Wait for approval.')
#         return redirect('login')
#
#     categories = Category.objects.all()
#     return render(request, 'register_shop.html', {'categories': categories})

def register_shop(request):
    if request.method == 'POST':
        # 1. Use .get() to avoid MultiValueDictKeyError crash
        username = request.POST.get('username')
        password = request.POST.get('password')
        shop_name = request.POST.get('shop_name')
        owner_name = request.POST.get('owner_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Dropdowns/Selects might be None if not picked
        shop_type_val = request.POST.get('shop_type')
        proof_type = request.POST.get('proof_type')

        # Optional fields
        equipment = request.POST.get('equipment')
        materials = request.POST.get('materials')
        city = request.POST.get('city')
        turnaround = request.POST.get('turnaround')

        # 2. Server-Side Validation Check
        # If critical fields are missing, stop here.
        if not username or not password or not shop_type_val or not proof_type:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'register_shop.html', {'categories': Category.objects.all()})

        # 3. Check if Username Exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'register_shop.html', {'categories': Category.objects.all()})

        # 4. Create User
        user = User.objects.create_user(username=username, password=password, email=email, first_name=shop_name)

        # Add to Group
        group, _ = Group.objects.get_or_create(name='shop')
        user.groups.add(group)

        # Handle File safely
        proof_file = request.FILES.get('proof_file')

        # 5. Create Shop Profile
        Shop.objects.create(
            USER=user,
            shop_name=shop_name,
            owner_name=owner_name,
            email=email,
            phone=phone,
            place=city,
            shop_type=shop_type_val,
            equipment=equipment,
            materials=materials,
            turnaround_time=turnaround,
            proof_type=proof_type,
            proof_file=proof_file,
            status='pending'
        )

        messages.success(request, 'Shop registered! Wait for Admin approval.')
        return redirect('login')

    # GET Request
    categories = Category.objects.all()
    return render(request, 'register_shop.html', {'categories': categories})


def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        user_type = request.POST['user_type']
        city = request.POST['city']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register_user')

        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name,
                                        last_name=last_name)
        user.save()

        group, _ = Group.objects.get_or_create(name='user')
        user.groups.add(group)

        UserProfile.objects.create(
            USER=user,
            phone=phone,
            place=city,
            user_type_interest=user_type
        )
        messages.success(request, 'User registered! Please login.')
        return redirect('login')

    return render(request, 'register_user.html')



def forgot_password(request):
    # 1. Handle Form Submission
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        new_pass = request.POST['new_password']
        confirm_pass = request.POST['confirm_password']

        try:
            # 2. Verify User Exists
            user = User.objects.get(username=username, email=email)

            # 3. Security Restriction: No Admins Allowed
            if user.is_superuser:
                messages.error(request, "Administrative accounts cannot reset passwords here. Contact system support.")
                return redirect('forgot_password')

            # 4. Validate Passwords Match
            if new_pass == confirm_pass:
                # 5. Set New Password (Hashes it automatically)
                user.set_password(new_pass)
                user.save()
                messages.success(request, "Password updated successfully! You can now login.")
                return redirect('login')
            else:
                messages.error(request, "New passwords do not match.")
                return redirect('forgot_password')

        except User.DoesNotExist:
            # 6. Handle Invalid User/Email combo
            messages.error(request, "No account found with that Username and Email combination.")
            return redirect('forgot_password')

    # 7. Render Page for GET Request
    return render(request, 'forgot_password.html')


# ==========================================
# 2. ADMIN VIEWS
# ==========================================

# def admin_home(request):
#     return render(request, 'admin.html')


@never_cache
@login_required(login_url='login')
def admin_home(request):
    # Fetch real-time counts for the dashboard
    pending_shops_count = Shop.objects.filter(status='pending').count()
    unresolved_complaints_count = Complaint.objects.exclude(status='Resolved').count()
    pending_requests_count = Request.objects.filter(status='Pending').count()

    context = {
        'pending_shops_count': pending_shops_count,
        'unresolved_complaints_count': unresolved_complaints_count,
        'pending_requests_count': pending_requests_count,
    }
    return render(request, 'admin.html', context)

def registered_shops(request):
    shops = Shop.objects.filter(status='pending')
    return render(request, 'registered_shops.html', {'shops': shops})


def approved_shops(request):
    shops = Shop.objects.filter(status='approved')
    return render(request, 'approved_shops.html', {'shops': shops})


def registered_users(request):
    users = User.objects.filter(groups__name='user').select_related('userprofile')
    return render(request, 'registered_users.html', {'users': users})


def approve_shop(request, id):
    shop = Shop.objects.get(id=id)
    shop.status = 'approved'
    shop.save()
    messages.success(request, f'{shop.shop_name} approved.')
    return redirect('registered_shops')


def reject_shop(request, id):
    shop = Shop.objects.get(id=id)
    shop.status = 'rejected'
    shop.save()
    messages.error(request, f'{shop.shop_name} rejected.')
    return redirect('registered_shops')


def manage_category(request):
    if request.method == "POST":
        category_name = request.POST.get('category_name')
        if category_name:
            if Category.objects.filter(category_name=category_name).exists():
                messages.error(request, 'Category already exists.')
            else:
                Category.objects.create(category_name=category_name)
                messages.success(request, 'Category added.')
        else:
            messages.error(request, 'Name cannot be empty.')
        return redirect('manage_category')

    categories = Category.objects.all()
    return render(request, 'manage_category.html', {'categories': categories})


def delete_category(request, id):
    try:
        Category.objects.get(id=id).delete()
        messages.success(request, 'Category deleted.')
    except Category.DoesNotExist:
        messages.error(request, 'Category not found.')
    return redirect('manage_category')


# --- Admin Complaint Handling ---

def view_complaint(request):
    complaints = Complaint.objects.all().order_by('-date')
    return render(request, 'view_complaint.html', {'complaints': complaints})


def reply_complaint(request):
    if request.method == "POST":
        complaint_id = request.POST.get('complaint_id')
        reply_text = request.POST.get('reply_text')
        try:
            complaint = Complaint.objects.get(id=complaint_id)

            current_history = complaint.reply if complaint.reply else ""
            timestamp = timezone.now().strftime("%d-%b-%Y")  # Date Only
            new_message = f"[{timestamp}] Admin: {reply_text}"

            if current_history:
                complaint.reply = f"{current_history}\n\n{new_message}"
            else:
                complaint.reply = new_message

            complaint.status = 'Resolved'
            complaint.save()
            messages.success(request, 'Reply added.')
        except Complaint.DoesNotExist:
            messages.error(request, 'Complaint not found.')
    return redirect('view_complaint')


# UPDATE view_feedback (Admin) to include Ratings
def view_feedback(request):
    # 1. Fetch both QuerySets
    general_feedbacks = Feedback.objects.all()
    product_ratings = Rating.objects.all()

    # 2. Combine and Sort by Date (Newest First)
    # We use a lambda function to sort by the 'date' attribute of each object
    combined_reviews = sorted(
        list(general_feedbacks) + list(product_ratings),
        key=lambda x: x.date,
        reverse=True
    )

    # 3. Pass the single combined list to the template
    return render(request, 'view_feedback.html', {
        'reviews': combined_reviews
    })


# --- Admin View Requests & Orders ---

def view_requests(request):
    """
    Displays ALL requests (Pending, Rejected, Accepted, etc.)
    Admin can see the flow of demand.
    """
    requests_list = Request.objects.all().select_related('USER__USER', 'SHOP').order_by('-created_at')
    return render(request, 'view_requests.html', {'requests': requests_list})


def view_orders(request):
    """
    Displays ONLY active orders (Status is NOT Pending).
    These are requests that have been Accepted/Paid/Printing etc.
    """
    orders_list = Request.objects.exclude(status='Pending').select_related('USER__USER', 'SHOP').order_by('-created_at')
    return render(request, 'view_orders.html', {'orders': orders_list})


# ==========================================
# 3. USER VIEWS (Complaints & Feedback & REQUESTS)
# ==========================================


@never_cache
@login_required(login_url='login')
def user_home(request):
    # 1. Fetch Approved Shops for Marketplace
    shops = Shop.objects.filter(status='approved')

    # CALCULATE RATINGS FOR EACH SHOP ---
    for shop in shops:
        # We look at all Ratings where the Request -> Shop matches the current shop
        # We aggregate the 'rating' field to find the Average
        data = Rating.objects.filter(REQUEST__SHOP=shop).aggregate(avg=Avg('rating'))

        # We count how many ratings exist to show (e.g., "12 reviews")
        count = Rating.objects.filter(REQUEST__SHOP=shop).count()

        # We attach these temporary attributes to the shop object
        shop.average_rating = data['avg']
        shop.review_count = count
        # -------------------------------------------------

    # 2. Fetch My Requests History
    try:
        user_profile = UserProfile.objects.get(USER=request.user)
        my_requests = Request.objects.filter(USER=user_profile).order_by('-created_at')
        my_payments = Payment.objects.filter(REQUEST__USER=user_profile).order_by('-payment_date')
    except UserProfile.DoesNotExist:
        my_requests = []
        my_payments = []

    # 3. Existing Data
    complaints = Complaint.objects.filter(USER=request.user).order_by('-date')
    feedbacks = Feedback.objects.filter(USER=request.user).order_by('-date')

    context = {
        'shops': shops,  # Needed for Marketplace Cards
        'my_requests': my_requests,  # Needed for Activity Tab
        'payments': my_payments,
        'complaints': complaints,
        'feedbacks': feedbacks
    }
    return render(request, 'user_page.html', context)


# --- Submit Print Request ---
def submit_print_request(request):
    if request.method == "POST":
        try:
            user_profile = UserProfile.objects.get(USER=request.user)
            shop_id = request.POST.get('shop_select')
            shop_obj = Shop.objects.get(id=shop_id)

            # Handle File Upload
            if 'model_file' in request.FILES:
                file = request.FILES['model_file']
            else:
                messages.error(request, "Please attach a 3D file.")
                return redirect('user_home')

            # Create Request
            Request.objects.create(
                USER=user_profile,
                SHOP=shop_obj,
                model_file=file,
                description=request.POST.get('description', 'No notes provided'),
                delivery_address=request.POST.get('delivery_address'),
                status='Pending'
            )
            messages.success(request, 'Request sent successfully!')
        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect('user_home')
    return redirect('user_home')


def process_payment(request):
    if request.method == "POST":
        req_id = request.POST.get('req_id')
        dummy_card = request.POST.get('card_number')  # Just for show

        try:
            req_obj = Request.objects.get(id=req_id)

            # 1. Create the Payment Record
            Payment.objects.create(
                REQUEST=req_obj,
                amount=req_obj.amount,
                status='Success'
            )

            # 2. Update Request Status
            req_obj.status = 'Paid'
            req_obj.save()

            messages.success(request, f"Payment of ${req_obj.amount} successful! Shop notified.")

        except Request.DoesNotExist:
            messages.error(request, "Order not found.")

    return redirect('user_home')


# -- User Complaint --
def user_sent_complaint(request):
    shops = Shop.objects.filter(status='approved')
    return render(request, 'user_sent_complaint.html', {'shops': shops})


def submit_user_complaint(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        ctype = request.POST.get('complaint_type')
        shop_id = request.POST.get('shop_id')

        shop_obj = None
        if ctype == 'Shop' and shop_id:
            shop_obj = Shop.objects.get(id=shop_id)

        Complaint.objects.create(
            USER=request.user,
            SHOP=shop_obj,
            complaint_type=ctype,
            title=title,
            description=description,
            status='Pending'
        )
        messages.success(request, 'Complaint submitted successfully.')
        return redirect('user_home')
    return redirect('user_home')


# -- User Feedback --
def user_sent_feedback(request):
    shops = Shop.objects.filter(status='approved')
    return render(request, 'user_sent_feedback.html', {'shops': shops})


def submit_user_feedback(request):
    if request.method == "POST":
        target = request.POST.get('feedback_target')
        shop_obj = None
        if target != 'platform':
            try:
                shop_obj = Shop.objects.get(id=target)
            except Shop.DoesNotExist:
                messages.error(request, "Selected shop not found.")
                return redirect('user_home')

        Feedback.objects.create(
            USER=request.user,
            SHOP=shop_obj,
            rating=request.POST.get('rating'),
            description=request.POST.get('description')
        )
        messages.success(request, 'Feedback submitted successfully.')
        return redirect('user_home')
    return redirect('user_home')


# NEW function to handle User Rating submission
def submit_product_rating(request):
    if request.method == "POST":
        req_id = request.POST.get('req_id')
        rating_val = request.POST.get('rating')
        comment = request.POST.get('description')

        try:
            req_obj = Request.objects.get(id=req_id)

            # Security: Ensure only the owner can rate
            if req_obj.USER.USER != request.user:
                messages.error(request, "Unauthorized.")
                return redirect('user_home')

            Rating.objects.create(
                REQUEST=req_obj,
                rating=rating_val,
                description=comment
            )
            messages.success(request, 'Product rating submitted!')
        except Request.DoesNotExist:
            messages.error(request, 'Order not found.')

    return redirect('user_home')


# ==========================================
# 4. SHOP VIEWS (Complaints & Feedback & REQUESTS)
# ==========================================


@never_cache
@login_required(login_url='login')
def shop_home(request):
    try:
        current_shop = Shop.objects.get(USER=request.user)
    except Shop.DoesNotExist:
        messages.error(request, "Shop profile not found.")
        return redirect('login')

    # 1. Fetch Orders & Requests
    incoming_requests = Request.objects.filter(SHOP=current_shop, status='Pending').order_by('-created_at')
    active_orders = Request.objects.filter(SHOP=current_shop).exclude(status='Pending').order_by('-created_at')

    # 2. Fetch Complaints
    sent_complaints = Complaint.objects.filter(SHOP=current_shop, complaint_type='Platform').order_by('-date')
    received_complaints = Complaint.objects.filter(SHOP=current_shop, complaint_type='Shop').order_by('-date')

    # 3. FETCH REVIEWS (The Fix)
    # A. Product Ratings (Review attached to a specific order)
    product_ratings = Rating.objects.filter(REQUEST__SHOP=current_shop).order_by('-date')

    # B. General Feedback (Direct shop reviews from "Give Feedback" button) << NEW LINE
    general_feedback = Feedback.objects.filter(SHOP=current_shop).order_by('-date')

    categories = Category.objects.all()

    context = {
        'incoming_requests': incoming_requests,
        'active_orders': active_orders,
        'sent_complaints': sent_complaints,
        'received_complaints': received_complaints,

        # Pass BOTH lists to the template
        'product_reviews': product_ratings,
        'general_reviews': general_feedback,

        'categories': categories,
    }
    return render(request, 'shop_page.html', context)

# --- NEW: Update Request Status (Accept/Reject) ---
def update_request_status(request):
    if request.method == "POST":
        req_id = request.POST.get('req_id')
        action = request.POST.get('action')  # 'accept' or 'reject'

        try:
            req_obj = Request.objects.get(id=req_id)

            if action == 'accept':
                price = request.POST.get('price')
                req_obj.status = 'Accepted'
                req_obj.amount = price
                req_obj.save()
                messages.success(request, f'Quote of ${price} sent to user.')

            elif action == 'reject':
                reason = request.POST.get('reason')
                req_obj.status = 'Rejected'
                # Append rejection reason to description for user visibility
                req_obj.description += f" [REJECT REASON: {reason}]"
                req_obj.save()
                messages.error(request, 'Request rejected.')

        except Request.DoesNotExist:
            messages.error(request, 'Request ID not found.')

    return redirect('shop_home')


# --- Full Page for Customer Complaints ---
def user_complaints_toshop(request):
    try:
        current_shop = Shop.objects.get(USER=request.user)
        received_complaints = Complaint.objects.filter(
            SHOP=current_shop,
            complaint_type='Shop'
        ).order_by('-date')
        return render(request, 'user_complaints_toshop.html', {'received_complaints': received_complaints})
    except Shop.DoesNotExist:
        messages.error(request, "Shop error.")
        return redirect('shop_home')


# --- Handle Reply to Customer ---
def reply_customer_complaint(request):
    if request.method == "POST":
        complaint_id = request.POST.get('complaint_id')
        reply_text = request.POST.get('reply_text')

        try:
            complaint = Complaint.objects.get(id=complaint_id)
            if complaint.SHOP.USER != request.user:
                messages.error(request, "Unauthorized.")
                return redirect('user_complaints_toshop')

            current_history = complaint.reply if complaint.reply else ""
            timestamp = timezone.now().strftime("%d-%b-%Y")  # Date Only
            new_message = f"[{timestamp}] {complaint.SHOP.shop_name}: {reply_text}"

            if current_history:
                complaint.reply = f"{current_history}\n\n{new_message}"
            else:
                complaint.reply = new_message

            complaint.status = 'Resolved'
            complaint.save()
            messages.success(request, 'Reply sent.')
        except Complaint.DoesNotExist:
            messages.error(request, 'Error finding complaint.')

    return redirect('user_complaints_toshop')


# --- Shop Reporting Issue TO ADMIN ---
def shop_sent_complaint(request):
    return render(request, 'shop_sent_complaint.html')


def submit_shop_complaint(request):
    if request.method == "POST":
        try:
            current_shop = Shop.objects.get(USER=request.user)
            Complaint.objects.create(
                USER=request.user,
                complaint_type='Platform',
                SHOP=current_shop,
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                status='Pending'
            )
            messages.success(request, 'Issue reported to Admin.')
        except Shop.DoesNotExist:
            messages.error(request, 'Error: Shop profile not found.')

        return redirect('shop_home')

    return redirect('shop_home')


# -- Shop Feedback --
def shop_sent_feedback(request):
    return render(request, 'shop_sent_feedback.html')


def submit_shop_feedback(request):
    if request.method == "POST":
        Feedback.objects.create(
            USER=request.user,
            SHOP=None,
            rating=request.POST.get('rating'),
            description=request.POST.get('description')
        )
        messages.success(request, 'Feedback sent to Admin.')
        return redirect('shop_home')
    return redirect('shop_home')


# --- NEW: Update Order Progress (Shop Dashboard) ---
# def update_order_progress(request):
#     if request.method == "POST":
#         req_id = request.POST.get('req_id')
#         new_status = request.POST.get('status')
#
#         try:
#             # Fetch the order
#             order = Request.objects.get(id=req_id)
#
#             # Security: Ensure the logged-in shop owns this order
#             if order.SHOP.USER != request.user:
#                 messages.error(request, "Unauthorized action.")
#                 return redirect('shop_home')
#
#             # Update Status
#             order.status = new_status
#             order.save()
#             messages.success(request, f'Order #{order.id} updated to {new_status}.')
#
#         except Request.DoesNotExist:
#             messages.error(request, 'Order not found.')
#
#     return redirect('shop_home')

def update_order_progress(request):
    if request.method == "POST":
        req_id = request.POST.get('req_id')
        new_status = request.POST.get('status')

        try:
            # Fetch the order
            order = Request.objects.get(id=req_id)

            # Security: Ensure the logged-in shop owns this order
            if order.SHOP.USER != request.user:
                messages.error(request, "Unauthorized action.")
                return redirect('shop_home')

            # ====================================================
            # GUARD 1: PREVENT SKIPPING PAYMENT
            # ====================================================
            # If shop tries to set status to Printing, Ready, Dispatched, or Delivered...
            restricted_statuses = ['Printing', 'Ready', 'Dispatched', 'Delivered']

            if new_status in restricted_statuses:
                # ...we MUST check if the user has paid.
                # We check if a Payment object exists for this request.
                has_paid = Payment.objects.filter(REQUEST=order).exists()

                if not has_paid:
                    messages.error(request,
                                   f"Action Blocked: User has NOT paid yet. You cannot move to '{new_status}'.")
                    return redirect('shop_home')

            # ====================================================
            # GUARD 2: PREVENT BACKWARD MOVEMENT
            # ====================================================
            # If current status is 'Dispatched', only allow 'Delivered'.
            if order.status == 'Dispatched':
                if new_status != 'Delivered':
                    messages.error(request, "Action Blocked: Item is already Dispatched. You cannot revert status.")
                    return redirect('shop_home')

            # If current status is 'Delivered', block ALL changes.
            if order.status == 'Delivered':
                messages.error(request, "Action Blocked: Order is already Delivered. No further changes allowed.")
                return redirect('shop_home')

            # ====================================================
            # SAVE CHANGES
            # ====================================================
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} updated to {new_status}.')

        except Request.DoesNotExist:
            messages.error(request, 'Order not found.')

    return redirect('shop_home')


# ==========================================
# 5. PROFILE MANAGEMENT
# ==========================================

def update_user_profile(request):
    if request.method == "POST":
        user = request.user
        try:
            profile = UserProfile.objects.get(USER=user)

            # Update Auth Data
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()

            # Update Profile Data
            profile.phone = request.POST.get('phone')
            profile.place = request.POST.get('city')
            profile.user_type_interest = request.POST.get('user_type')
            profile.save()

            messages.success(request, "Profile updated successfully.")
        except UserProfile.DoesNotExist:
            messages.error(request, "Profile not found.")

    return redirect('user_home')


def update_shop_profile(request):
    if request.method == "POST":
        user = request.user
        try:
            shop = Shop.objects.get(USER=user)

            # Update Auth Data
            user.first_name = request.POST.get('shop_name')
            user.email = request.POST.get('email')
            user.save()

            # Update Shop Data
            shop.shop_name = request.POST.get('shop_name')
            shop.owner_name = request.POST.get('owner_name')
            shop.email = request.POST.get('email')
            shop.phone = request.POST.get('phone')
            shop.place = request.POST.get('city')
            shop.shop_type = request.POST.get('shop_type')
            shop.equipment = request.POST.get('equipment')
            shop.materials = request.POST.get('materials')
            shop.turnaround_time = request.POST.get('turnaround')
            shop.save()

            messages.success(request, "Shop details updated.")
        except Shop.DoesNotExist:
            messages.error(request, "Shop profile not found.")

    return redirect('shop_home')


def update_admin_profile(request):
    if request.method == "POST":
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, "Admin profile updated.")

    return redirect('admin_home')






# ========================================================================CORE=============================================================================
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import subprocess
import sys
import os
import time
import requests

# Global variable to track if Gradio is running
gradio_process = None


def gen3d(request):
    global gradio_process
    try:
        # Check if Gradio is already running
        if gradio_process is None or gradio_process.poll() is not None:
            # path to your gradio_app.py inside TripoSR folder
            script_path = os.path.join(os.path.dirname(__file__), "TripoSR/gradio_app.py")
            script_path = os.path.abspath(script_path)

            # Run gradio app in a separate background process
            gradio_process = subprocess.Popen([sys.executable, script_path, "--listen", "--port", "7878"])

        # Render loading page
        return render(request, "loading.html")
    except Exception as e:
        return HttpResponse(f"<h3>Error launching Gradio App:</h3><pre>{e}</pre>")


def check_gradio_status(request):
    """API endpoint to check if Gradio is ready"""
    try:
        response = requests.get("http://127.0.0.1:7878", timeout=2)
        if response.status_code == 200:
            return JsonResponse({"status": "ready", "url": "http://127.0.0.1:7878"})
    except:
        pass

    return JsonResponse({"status": "loading"})