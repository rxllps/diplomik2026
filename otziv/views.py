from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction

from rooms.models import Room
from .models import Review

def add_review(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    
    if request.method == "POST":
        rating = request.POST.get('rating')
        text = request.POST.get('comment')
        
        if not rating or not text:
            messages.error(request, "Пожалуйста, заполните все поля.")
            return redirect('room_schedule', url_name=room.url_name)
            
        try:
            with transaction.atomic():
                # Check if user already has a review for this room
                review, created = Review.objects.get_or_create(
                    room=room,
                    user=request.user,
                    defaults={
                        'rating': rating,
                        'text': text,
                        'is_approved': False  # Will be approved by admin
                    }
                )
                
                if not created:
                    # Update existing review
                    review.rating = rating
                    review.text = text
                    review.is_approved = False
                    review.save()
                    
            messages.success(request, "Ваш отзыв успешно отправлен на модерацию!")
            
        except Exception as e:
            messages.error(request, "Произошла ошибка при сохранении отзыва.")
            
        return redirect('room_schedule', url_name=room.url_name)
    
    # For GET requests, redirect to room page
    return redirect('room_schedule', url_name=room.url_name)