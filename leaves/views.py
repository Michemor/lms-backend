import logging

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Leave
from .serializers import (
    LeaveSerializer,
    RegistrationSerializer,
    UpdatePasswordSerializer,
)

logger = logging.getLogger(__name__)

Employee = get_user_model()
class LeaveListCreateView(generics.ListCreateAPIView):
    """
    View to list all leave requests for the authenticated user and to create new leave requests.

    Args:
        generics (ListCreateAPIView): Provides GET and POST handlers for listing and creating leave requests.

    Returns:
        A list of leave requests for the authenticated user on GET request, and the created leave request on POST request.
    """
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the leaves for the currently authenticated user."""
        user = self.request.user

        # HR and Manager can see all leave requests
        if user.employee_role in ['HR', 'MANAGER']:
                logger.info(
                    "User id=%s role=%s requested all leave records",
                    user.id,
                    user.employee_role,
                )
                return Leave.objects.all()  
        
        queryset = Leave.objects.filter(employee=self.request.user)
        logger.info(
            "User id=%s role=%s requested own leave records count=%s",
            user.id,
            user.employee_role,
            queryset.count(),
        )
        return queryset
    
    def perform_create(self, serializer):
        """Associate the new leave request with the currently authenticated user."""
        leave = serializer.save(employee=self.request.user)
        logger.info(
            "Leave created id=%s for user id=%s type=%s start=%s end=%s",
            leave.id,
            self.request.user.id,
            leave.leave_type,
            leave.start_date,
            leave.end_date,
        )

class LeaveDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a specific leave request.

    Args:
        generics (RetrieveUpdateDestroyAPIView): Provides GET, PUT, PATCH, and DELETE handlers for a specific leave request.
    
    Returns:
        The leave request details on GET request, the updated leave request on PUT/PATCH request,
        and a success message on DELETE request.
    """
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the leaves for the currently authenticated user."""
        user = self.request.user
        if user.employee_role in ['HR', 'MANAGER']:
            logger.info(
                "User id=%s role=%s requested detail list of all leaves",
                user.id,
                user.employee_role,
            )
            return Leave.objects.all()
        
        queryset = Leave.objects.filter(employee=self.request.user)
        logger.info(
            "User id=%s role=%s requested detail list of own leaves count=%s",
            user.id,
            user.employee_role,
            queryset.count(),
        )
        return queryset

class RegistrationView(generics.CreateAPIView):
    """
    View to handle user registration.

    Args:
        generics (CreateAPIView): Provides a POST handler for creating new user accounts.

    Returns:
        The created user account details on successful registration.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    queryset = Employee.objects.all()

    def create(self, request, *args, **kwargs):
        # Do not log the raw password; only log non-sensitive fields.
        logger.info(
            "Registration attempt for email=%s department=%s position=%s role=%s",
            request.data.get("email"),
            request.data.get("employee_department"),
            request.data.get("employee_position"),
            request.data.get("employee_role"),
        )
        response = super().create(request, *args, **kwargs)
        logger.info(
            "Registration success for email=%s status_code=%s",
            request.data.get("email"),
            response.status_code,
        )
        return response

class UpdatePasswordView(generics.UpdateAPIView):
    """
    View to handle password updates for authenticated users.

    Args:
        generics (UpdateAPIView): Provides a PUT handler for updating the user's password.

    Returns:
        A success message on successful password update, or an error message on failure.
    """
    serializer_class = UpdatePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the currently authenticated user."""
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Handle the password update process, including validation of the old password and setting the new password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        logger.info("Password update attempt for user id=%s", user.id)

        if not user.check_password(old_password):
            logger.warning("Password update failed for user id=%s: wrong password", user.id)
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        logger.info("Password updated successfully for user id=%s", user.id)

        return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
    