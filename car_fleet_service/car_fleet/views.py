from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_car_fleet(request):
    return Response([
        {"id": 1, "name": "Laptop"}
    ])