from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from rest_framework import status

@api_view(['GET'])
def get_users(request):
    return Response([
        {"id": 1, "name": "Arek"}
    ])

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
    
    user: User = None

    if email:
        user = user.objects.filter(email=email).first()
    elif phone_number:
        user = user.objects.filter(phone_number=phone_number).first()

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
                                          lastname=last_name, phone_number=phone_number, 
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
        "access" : str(refresh.acces_token)
    }

@api_view(['POST'])
@permission_classes([IsAdmin])
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
@permission_classes([IsAdmin])
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
@permission_classes([IsAdmin])
def update_user(request, id) -> Response:

    try:

        user: User = User.objects.get(id=id)
        user.role = request.data.get("role", user.role)

        user.save()

        return Response({"message": "User updated"})

    except User.DoesNotExist:
        return Response({"error": "User not found"})