from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from rest_framework import status
from users.permissions import IsAdmin, IsFinance, IsHR, IsUser
from typing import List

@api_view(['POST'])
def login(request) -> Response:

    email: str = request.data.get('email')
    phone_number: str = request.data.get('phone_number')
    password: str = request.data.get('password')

    if not email and not phone_number:
        return Response(
            {"error" : "Provide the right email or phone number"},
            status=status.HTTP_400_BAD_REQUEST
        )


    if email:
        user = user.objects.filter(email=email).first()
    elif phone_number:
        user = user.objects.filter(phone_number=phone_number).first()
    else:
        return Response(
            {"error" : "Provide email or phone number"},
            status=status.HTTP_400_BAD_REQUEST
        )

    #401 or 400?
    if not user.check_password(password):
        return Response(
            {"error" : "Password is inccorect"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if user.is_blocked:
        return Response(
            {"error" : "Account is blocked, contact admin"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token: dict[str,str] = generate_or_refresh_token(user)
    return Response(token)
    

@api_view(['POST'])
def register(request) -> Response:

    email: str = request.data.get('email')
    password: str = request.data.get('password')
    phone_number: str = request.data.get('phone_number')
    first_name: str = request.data.get('first_name')
    last_name: str = request.data.get('last_name')

    if User.objects.filter(email=email).exists():
        return Response(
            {"error" : "Email is linked to a different account"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(phone_number=phone_number).exists():
        return Response(
            {"error": "Phone number is linked to a different account"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not all([email, password, phone_number, first_name, last_name]):
        return Response(
            {"error" : "All fields should be filled"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        validate_password(password)
    ##better exceptions - custom
    except Exception as e:
        return Response(
            {"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
    
    user: User = User.objects.create_user(email=email, first_name=first_name, 
                                          last_name=last_name, phone_number=phone_number, 
                                          password=password, username=email)
    
    try:
        group, created = Group.objects.get_or_create(name='USER')
        user.groups.add(group)

    except Exception as e:
        #later more specific print and custom exception
        print(e)
    
    return Response({"message" : "The account was created successfully"},
                     status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request) -> Response:

    try:
        token: str = request.data.get("refresh")
        token: RefreshToken = RefreshToken(token)
        token.blacklist()
        
        return Response(
            {"message" : "Logged out"},status=status.HTTP_200_OK)
    
    except:

        return Response(
            {"error" : "Token incorrect"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request) -> Response:
    
    user: User = request.user

    old_password: str = request.data.get("old_password")
    new_password: str = request.data.get("new_password")

    if not old_password or not new_password:
        return Response(
            {"error" : "Enter old and new password"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        validate_password(new_password)
    ##better exceptions - custom
    except Exception as e:
        return Response(
            {"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    return Response(
        {"message" : "The password was changed successfully"},
        status=status.HTTP_200_OK
    )

def generate_or_refresh_token(user: User) -> dict[str, str]:
    refresh: RefreshToken = RefreshToken(user)

    return {
        "refresh" : str(refresh),
        "access" : str(refresh.access_token)
    }

@api_view(['POST'])
@permission_classes([IsAdmin, IsAuthenticated])
def create_user(request) -> Response:

    username: str = request.data.get("email")
    email: str = request.data.get("email")
    password: str = request.data.get("password")
    role:str = request.data.get("role", "USER")
    phone_number : str = request.data.get("phone_number")
    first_name: str = request.data.get("first_name")
    last_name: str = request.data.get("last_name")

    user: User = User.objects.create_user(
        username=username,email=email,
        password=password,role=role,
        first_name=first_name, last_name=last_name, 
        phone_number=phone_number
    )

    return Response({"message": "User created"}, 
                    status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAdmin, IsAuthenticated])
def delete_user(request, id):

    try:
        user = User.objects.get(id=id)
        user.delete()
        return Response(
            {"message": "User deleted"}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:

        return Response(
            {"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
@permission_classes([IsAdmin, IsAuthenticated])
def update_user(request, id) -> Response:

    try:
        user: User = User.objects.get(id=id)
        user.role = request.data.get("role", user.role)
        user.save()

        return Response(
            {"message": "User updated"}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(
            {"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
@permission_classes([IsAdmin, IsAuthenticated])
def update_position(request, id) -> Response:

    try:
        user: User = User.objects.get(id=id)
        user.position = request.data.get("position", user.position)
        user.save()

        return Response(
            {"message": "User updated"}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(
            {"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAdmin, IsAuthenticated])
def update_department(request, id) -> Response:

    try:
        user: User = User.objects.get(id=id)
        user.department = request.data.get("department", user.department)
        user.save()

        return Response(
            {"message": "User updated"}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(
            {"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PATCH'])
@permission_classes([IsAdmin, IsAuthenticated])
def block_user(request, id) -> Response:

    try:
        user: User = User.objects.get(id=id)
        user.is_blocked = True
        user.save()
    except User.DoesNotExist:
         return Response(
            {"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(
        {"message": "User blocked"}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAdmin, IsAuthenticated])
def unblock_user(request, id) -> Response:

    try:
        user: User = User.objects.get(id=id)
        user.is_blocked = False
        user.save()
    except User.DoesNotExist:
         return Response(
            {"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {"message": "User unblocked"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request) -> Response:

    first_name: str = request.query_params.get("first_name")
    last_name: str = request.query_params.get("last_name")

    users: List[User] = User.objects.all()

    if first_name:
        users = users.filter(first_name__icontains=first_name)
    if last_name:
        users = users.filter(last_name__icontains=last_name)

    data: dict = users.values("id", "email", "first_name", "last_name", "role", "phone_number")

    return Response(data)

#should we confine the visibility, so only people from HR can see people from HR?
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_role(request) -> Response:

    role: str = request.query_params.get("role")

    if not role:
        return Response(
            {"error": "Department is required"}, status=status.HTTP_400_BAD_REQUEST)

    users: List[User] = User.objects.filter(role=role)

    data: dict = users.values("id", "email", "first_name", "last_name", "role", "department")

    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_profile(request):

    user: User = request.user

    return Response({
        "full_name": f"{user.first_name} {user.last_name}",
        "role": user.role,
        "position": user.position,
        "department": user.department,
        "assigned_car_id": user.assigned_car_id,
    })