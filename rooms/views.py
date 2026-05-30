from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.db import transaction
from django.db.models import Q

from .models import Room, TimeSlot, Booking, ServicePackage, Payment
from .forms import BookingForm

def rooms_home(request):
    today = timezone.localdate()
    rooms = Room.objects.filter(is_active=True)
    slots = (TimeSlot.objects
              .filter(date=today, room__is_active=True)
              .select_related("room", "booking"))
    return render(request, "rooms/rooms_home.html", {
        "rooms": rooms,
        "slots": slots,
        "today": today,
    })

def room_schedule(request, url_name):
    room  = get_object_or_404(Room, url_name=url_name, is_active=True)
    today = timezone.localdate()
    slots = (TimeSlot.objects
             .filter(room=room, date__gte=today)
             .select_related("booking")
             .order_by("date", "start_time"))
    reviews = room.reviews.filter(is_approved=True)[:5]
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"]
    return render(request, "rooms/room_schedule.html", {
        "room": room,
        "slots": slots,
        "reviews": reviews,
        "avg_rating": avg_rating if avg_rating is not None else 0,
    })

def upcoming(request):
    rooms = Room.objects.filter(is_active=True).annotate(
        avg_rating=Case(
            When(reviews__rating__isnull=False, then=Avg("reviews__rating")),
            default=Value(0),
        )
    )
    return render(request, "rooms/upcoming.html", {"rooms": rooms})

def price(request):
    packages = ServicePackage.objects.filter(is_active=True).order_by("price")
    rooms    = Room.objects.filter(is_active=True)
    return render(request, "rooms/price.html", {"packages": packages, "rooms": rooms})

def my_karaoke(request):
    return render(request, "rooms/my_karaoke.html")
def reports(request):
    if not request.user.is_staff:
        return redirect("rooms_home")
    from django.db.models import Sum, Count
    today = timezone.localdate()
    stats = {
        "total_bookings": Booking.objects.count(),
        "confirmed":      Booking.objects.filter(status="confirmed").count(),
        "revenue":        Payment.objects.filter(status="paid")
                                         .aggregate(s=Sum("amount"))["s"] or 0,
        "today_slots":    TimeSlot.objects.filter(date=today, is_booked=True).count(),
        "by_room": (Room.objects
                    .filter(is_active=True)
                    .annotate(cnt=Count("slots__booking"),
                              rev=Sum("slots__booking__payment__amount"))),
    }
    return render(request, "rooms/reports.html", {"stats": stats})
@login_required
def book_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, pk=slot_id, is_booked=False)
    packages = ServicePackage.objects.filter(is_active=True)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.slot = slot
            try:
                with transaction.atomic():
                    booking.save()
                    
                    # Create payment record
                    payment = Payment.objects.create(
                        booking=booking,
                        amount=booking.total_price,
                        method=form.cleaned_data.get("payment_method", "online"),
                        status="pending"
                    )
                    
                    # Mark slot as booked
                    slot.is_booked = True
                    slot.save()
                    
                messages.success(request, f"Бронирование #{booking.pk} создано! Ожидайте оплаты.")
                
                # Redirect to payment page
                return redirect('payment_page', booking_id=booking.pk)
                
            except IntegrityError:
                messages.error(request, "Слот уже забронирован")
                return JsonResponse({"ok": False, "errors": "Слот уже забронирован"}, status=409)
            
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    else:
        form = BookingForm(initial={"slot": slot})

    return render(request, "rooms/book_slot.html", {
        "form": form, "slot": slot, "packages": packages
    })
@login_required
def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    payment = get_object_or_404(Payment, booking=booking)
    
    if request.method == "POST":
        # Process payment confirmation
        action = request.POST.get('action')
        
        if action == "pay":
            with transaction.atomic():
                # Mark payment as paid
                payment.status = "paid"
                payment.paid_at = timezone.now()
                payment.save()
                
                # Update booking status
                booking.status = "confirmed"
                booking.save()
                
            messages.success(request, f"Оплата бронирования #{booking.pk} прошла успешно!")
            return redirect('cabinet')
            
        elif action == "cancel":
            with transaction.atomic():
                # Cancel the booking
                booking.status = "cancelled"
                booking.save()
                
                # Free the slot
                booking.slot.is_booked = False
                booking.slot.save()
                
                # Update payment status
                payment.status = "failed"
                payment.save()
                
            messages.info(request, "Бронирование отменено.")
            return redirect('cabinet')

    return render(request, "rooms/payment.html", {
        "booking": booking,
        "payment": payment
    })
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    # Only allow cancellation if booking is pending or confirmed
    if booking.status in ("pending", "confirmed"):
        with transaction.atomic():
            # If booking is confirmed, we should refund if paid
            if booking.status == "confirmed" and hasattr(booking, 'payment'):
                payment = booking.payment
                if payment.status == "paid":
                    # In a real system, we would process a refund here
                    payment.status = "refunded"
                    payment.save()
                    messages.info(request, "Вам будет возвращена оплата.")
                
            # Cancel booking and free slot
            booking.status = "cancelled"
            booking.save()
            
            booking.slot.is_booked = False
            booking.slot.save()
            
        messages.info(request, "Бронирование отменено.")
        
    return redirect("cabinet")
@login_required
def cabinet(request):
    bookings = (Booking.objects
                .filter(user=request.user)
                .select_related("slot__room", "package", "payment")
                .order_by("-created_at"))
    return render(request, "rooms/cabinet.html", {"bookings": bookings})