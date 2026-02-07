"""
Alert Service for GLOF Prediction System.
Handles SMS notifications and location-based evacuation guidance.
"""
import geopy.distance
from typing import List, Dict, Tuple, Optional
from config import settings


def generate_map_link(coordinates: Tuple[float, float]) -> str:
    """Generate Google Maps link for given coordinates."""
    latitude, longitude = coordinates
    return f"https://www.google.com/maps?q={latitude},{longitude}"


def find_nearest_safe_location(current_coordinates: Tuple[float, float]) -> Optional[Dict]:
    """
    Find the nearest safe evacuation location.
    
    Args:
        current_coordinates: Tuple of (latitude, longitude)
        
    Returns:
        Dictionary with name, coordinates, and distance of nearest location.
    """
    min_distance = float('inf')
    nearest_location = None
    
    for location in settings.SAFE_LOCATIONS:
        distance = geopy.distance.geodesic(
            current_coordinates, 
            location["coordinates"]
        ).km
        
        if distance < min_distance:
            min_distance = distance
            nearest_location = {
                **location,
                "distance_km": round(distance, 2)
            }
    
    return nearest_location


def send_sms_alert(
    message: str,
    current_coordinates: Tuple[float, float],
    phone_numbers: List[str] = None
) -> Dict:
    """
    Send SMS alert via Twilio.
    
    Args:
        message: Alert message to send
        current_coordinates: Current risk location coordinates
        phone_numbers: List of phone numbers to send to (defaults to configured numbers)
        
    Returns:
        Dictionary with status and details
    """
    if phone_numbers is None:
        phone_numbers = settings.ALERT_PHONE_NUMBERS
    
    if not phone_numbers:
        return {"success": False, "error": "No phone numbers configured"}
    
    # Check if Twilio is configured
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        return {"success": False, "error": "Twilio credentials not configured"}
    
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Get nearest safe location
        nearest_location = find_nearest_safe_location(current_coordinates)
        
        # Build full message
        current_map_link = generate_map_link(current_coordinates)
        full_message = f"{message}\nRisk Location: {current_coordinates}\nView on Map: {current_map_link}"
        
        if nearest_location:
            safe_map_link = generate_map_link(nearest_location["coordinates"])
            full_message += (
                f"\n\nNearest Safe Location: {nearest_location['name']}\n"
                f"Distance: {nearest_location['distance_km']} km\n"
                f"Evacuation Map: {safe_map_link}"
            )
        
        # Send to all numbers
        sent_count = 0
        errors = []
        
        for number in phone_numbers:
            try:
                client.messages.create(
                    body=full_message,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=number
                )
                sent_count += 1
            except Exception as e:
                errors.append(f"{number}: {str(e)}")
        
        return {
            "success": True,
            "sent_count": sent_count,
            "total_recipients": len(phone_numbers),
            "errors": errors if errors else None,
            "nearest_safe_location": nearest_location
        }
        
    except ImportError:
        return {"success": False, "error": "Twilio library not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def prepare_alert_data(probability: float, coordinates: Tuple[float, float]) -> Dict:
    """
    Prepare alert data without sending SMS (for preview/testing).
    
    Args:
        probability: GLOF probability percentage
        coordinates: Risk location coordinates
        
    Returns:
        Dictionary with alert information
    """
    nearest_location = find_nearest_safe_location(coordinates)
    
    return {
        "probability": probability,
        "risk_location": {
            "coordinates": coordinates,
            "map_link": generate_map_link(coordinates)
        },
        "nearest_safe_location": {
            "name": nearest_location["name"],
            "coordinates": nearest_location["coordinates"],
            "distance_km": nearest_location["distance_km"],
            "map_link": generate_map_link(nearest_location["coordinates"])
        } if nearest_location else None,
        "configured_recipients": len(settings.ALERT_PHONE_NUMBERS)
    }
