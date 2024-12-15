from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import ScheduledTrigger, APITrigger
from django.core.exceptions import ValidationError


def validate_scheduled_trigger_data(name, scheduled_time, interval_option, interval_time):
    """Validate the data for scheduled trigger."""
    if not name or not scheduled_time:
        raise ValidationError("Trigger name and scheduled time are required.")
    if interval_option == "fixed_interval" and not interval_time:
        raise ValidationError("Interval time is required when the interval option is fixed_interval.")


def create_scheduled_trigger(name, scheduled_time, interval_option, interval_time):
    """Create a scheduled trigger."""
    # Validate data
    validate_scheduled_trigger_data(name, scheduled_time, interval_option, interval_time)

    # Create the scheduled trigger
    scheduled_trigger = ScheduledTrigger(
        name=name,
        scheduled_time=scheduled_time,
        interval_option=interval_option,
        interval_time=interval_time if interval_option == "fixed_interval" else None
    )
    scheduled_trigger.save()


def validate_api_trigger_data(name, endpoint, payload):
    """Validate the data for API trigger."""
    if not name or not endpoint or not payload:
        raise ValidationError("Trigger name, endpoint, and payload are required.")


def create_api_trigger(name, endpoint, payload):
    """Create an API trigger."""
    # Validate data
    validate_api_trigger_data(name, endpoint, payload)

    # Create the API trigger
    api_trigger = APITrigger(
        name=name,
        endpoint=endpoint,
        payload=payload
    )
    api_trigger.save()


def index(request):
    """
    Basic UI to create triggers and view logs.
    """
    if request.method == "POST":
        trigger_type = request.POST.get("trigger_type", "").lower()

        try:
            # For Scheduled trigger
            if trigger_type == "scheduled":
                name = request.POST.get("name", "")
                scheduled_time = request.POST.get("time", "")
                interval_option = request.POST.get("interval_option", "")
                interval_time = request.POST.get("interval_time", "")
                create_scheduled_trigger(name, scheduled_time, interval_option, interval_time)
                return redirect("index")  # Redirect back to the index page

            # For API trigger
            elif trigger_type == "api":
                name = request.POST.get("name", "")
                endpoint = request.POST.get("endpoint", "")
                payload = request.POST.get("payload", "")
                create_api_trigger(name, endpoint, payload)
                return redirect("index")  # Redirect back to the index page

            else:
                return JsonResponse({"error": "Invalid trigger type."}, status=400)

        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, "index.html")

