from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserProfile,Notification
from datetime import date
from .models import Complaint,ContactMessage
from .forms import ComplaintForm,NotificationForm
from django.db.models import Count
from django.utils import timezone
from .models import UserProfile, Flat, Complaint, Event,EventPayment, Maintenance
from django.contrib.admin.views.decorators import staff_member_required
from twilio.rest import Client
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .forms import CustomUserCreationForm, CustomLoginForm

def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            # Save phone in UserProfile (optional)
            phone = form.cleaned_data.get('phone')
            UserProfile.objects.create(user=user, phone=phone)

            # ----------------- SEND WELCOME SMS -----------------
            if phone:
                try:
                    phone_number = phone.strip()
                    if not phone_number.startswith('+'):
                        phone_number = '+91' + phone_number[-10:]
                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    client.messages.create(
                        body=f"Welcome {user.username}! Your account has been created successfully.",
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=phone_number
                    )
                    print(f"✅ SMS sent to {phone_number}")
                except Exception as e:
                    print(f"❌ Failed to send SMS to {phone_number}: {e}")

            # Auto-login user
            auth_user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            if auth_user:
                login(request, auth_user)
                return redirect("profile")
            else:
                messages.error(request, "Signup successful but login failed. Please login manually.")
                return redirect("login")
    else:
        form = CustomUserCreationForm()

    return render(request, "enroll/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username= form.cleaned_data['username']  # username or email
            password = form.cleaned_data['password']

            # Try login by username
            user = authenticate(username=username, password=password)

            # If username fails, try email
            if user is None:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user:
                login(request, user)

                # ----------------- SEND LOGIN SMS -----------------
                try:
                    profile = UserProfile.objects.get(user=user)
                    phone = profile.phone
                    if phone:
                        phone_number = phone.strip()
                        if not phone_number.startswith('+'):
                            phone_number = '+91' + phone_number[-10:]
                        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                        client.messages.create(
                            body=f"Hello {user.username}, you have successfully logged in to Digital Society.",
                            from_=settings.TWILIO_PHONE_NUMBER,
                            to=phone_number
                        )
                        print(f"✅ Login SMS sent to {phone_number}")
                except Exception as e:
                    print(f"❌ Login SMS failed: {e}")

                return redirect("profile")
            else:
                messages.error(request, "Invalid Username/Email or Password")
        else:
            messages.error(request, "Invalid input. Please try again.")
    else:
        form = CustomLoginForm()

    return render(request, "enroll/login.html", {"form": form})

@login_required
def profile_view(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, "enroll/profile.html", {"profile": profile})


def logout_view(request):
    logout(request)
    return redirect("login")


# @login_required
def home_view(request):
    if request.user.is_authenticated:
        total_members = User.objects.count()
        total_flats = Flat.objects.count()
        pending_complaints = Complaint.objects.filter(status="Pending").count()
        upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()
        pending_maintenance = Maintenance.objects.filter(status="Unpaid").count()
        
        # Unread notifications count
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()

        context = {
            'total_members': total_members,
            'total_flats': total_flats,
            'pending_complaints': pending_complaints,
            'upcoming_events': upcoming_events,
            'pending_maintenance': pending_maintenance,
            'unread_notifications': unread_notifications,
        }

        return render(request, 'enroll/home.html', context)
    else:
        return render(request, 'enroll/public/home_public.html')
    
@login_required
def profile_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    context = {
        'profile': profile
    }
    return render(request, 'enroll/profile.html', context)

@login_required
def settings_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    message = ""

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        image = request.FILES.get('profile_image')

        # Update username
        user.username = username
        user.save()

        # Update password
        if password and password == password2:
            user.set_password(password)
            user.save()
            message = "Settings updated successfully"
        elif password != password2 and password != "":
            message = "Passwords do not match"

        # Update profile image
        if image:
            profile.profile_image = image
            profile.save()

        return render(request, 'enroll/settings.html', {'message': message, 'profile': profile})

    return render(request, 'enroll/settings.html', {'profile': profile})

# public home
def public_home(request):
    return render(request, 'enroll/public/home_public.html')

def about_page(request):
    return render(request, 'enroll/public/about.html')

@csrf_exempt
def contact_page(request):
    return render(request, 'enroll/public/contact.html')

# complaint
@login_required
def complaint_add(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('complaint_list')
    else:
        form = ComplaintForm()
    return render(request, 'enroll/complaint_add.html', {'form': form})

@login_required
def complaint_list(request):
    complaints = Complaint.objects.filter(user=request.user)
    return render(request, 'enroll/complaint_list.html', {'complaints': complaints})

@login_required
def events_view(request):
    events = Event.objects.order_by('date')
    return render(request, 'enroll/events.html', {'events': events})

# Show User Maintenance Status (User View)
@login_required
def maintenance_view(request):
    records = Maintenance.objects.filter(user=request.user)
    return render(request, 'enroll/maintenance.html', {'records': records})

# --------------------------
# Admin Send Notification + SMS
# --------------------------
@staff_member_required
def send_notification(request):
    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save()

            # --- TWILIO CLIENT ---
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            # Filter users to send SMS
            if notification.user:
                user_profiles = UserProfile.objects.filter(
                    user=notification.user,
                    phone__isnull=False
                ).exclude(phone='')
            else:
                user_profiles = UserProfile.objects.exclude(phone__isnull=True).exclude(phone='')

            # --- SMS SENDING LOOP ---
            for profile in user_profiles:
                print("SENDING SMS TO USERS...")
                print(f"Sending to: {profile.phone}")

                try:
                    client.messages.create(
                        body=f"{notification.title}\n{notification.message}",
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=profile.phone
                    )
                    print("SMS SENT SUCCESS")
                except Exception as e:
                    print(f"SMS FAILED for {profile.user.username}: {e}")

            return redirect("send_notification")

    else:
        form = NotificationForm()

    notifications = Notification.objects.order_by('-created_at')[:10]

    return render(request, "enroll/send_notification.html", {
        "form": form,
        "notifications": notifications
    })


@login_required
def notifications_view(request):
    user_notifications = Notification.objects.filter(user=request.user)
    broadcast = Notification.objects.filter(user__isnull=True)

    notifications = (user_notifications | broadcast).order_by('-created_at')

    return render(request, "enroll/notifications.html", {
        "notifications": notifications
    })

@login_required
def mark_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
    except:
        pass

    return redirect("notifications")

@csrf_protect
def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message_text = request.POST.get("message", "").strip()

        if name and email and message_text:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                message=message_text
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
        else:
            messages.error(request, "Please fill all required fields.")

    return render(request, "enroll/contact_page.html")



from django.shortcuts import get_object_or_404
@login_required
def maintenance_payment(request, record_id):
    record = get_object_or_404(Maintenance, id=record_id, user=request.user)

    if record.status == "Paid":
        return redirect('maintenance')  # Already paid

    if request.method == "POST":
        method = request.POST.get("payment_method")

        if method in ["phonepe", "paytm", "razorpay", "gpay"]:
            # Here you would integrate actual payment gateway logic
            # For now, we simulate successful payment:

            record.status = "Paid"
            record.save()  # Update status in database

            return redirect('maintenance')  # Redirect after payment

    return render(request, "payments/maintenance_pay.html", {"record": record})


@login_required
def event_payments(request):
    records = EventPayment.objects.filter(user=request.user)
    return render(request, 'payments/event_list.html', {'records': records})

@login_required
def event_payment_pay(request, record_id):
    record = get_object_or_404(EventPayment, id=record_id, user=request.user)

    if record.status == "Paid":
        return redirect('event_payments')  # Already paid

    if request.method == "POST":
        method = request.POST.get("payment_method")
        if method in ["phonepe", "paytm", "razorpay", "gpay"]:
            record.status = "Paid"  # Must match choices
            record.payment_date = timezone.now()  # Optional: store payment time
            record.save()
            return redirect('event_payments')

    # Render page with payment method dropdown
    return render(request, "payments/event_pay.html", {"record": record})
@login_required
def donation_payment(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        method = request.POST.get("payment_method")

        if method == "phonepe":
            # Redirect to PhonePe payment page
            pass
        elif method == "paytm":
            # Redirect to Paytm payment page
            pass
        elif method == "razorpay":
            # Redirect to Razorpay payment page
            pass
        elif method == "gpay":
            # Redirect to GPay payment page
            pass

    return render(request, "payments/donation.html")
