import logging
from datetime import date

from rest_framework import serializers

from .models import Leave, Employee


logger = logging.getLogger(__name__)


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = "__all__"
        # Ensure employee is set from the request context, not the client
        read_only_fields = ["employee"]

    list_display = ("leave_type", "start_date", "end_date", "reason", "status")
    search_fields = ("leave_type", "reason", "status")
    list_filter = ("start_date", "end_date", "leave_type", "status")

    def validate(self, data):
        """Custom validation to ensure that the end date is not before the start date and that the start date is not in the past."""
        logger.debug(
            "Validating leave for %(employee)s: %(start)s -> %(end)s (%(type)s)",
            {
                "employee": getattr(data.get("employee"), "id", None),
                "start": data.get("start_date"),
                "end": data.get("end_date"),
                "type": data.get("leave_type"),
            },
        )

        if data["end_date"] < data["start_date"]:
            raise serializers.ValidationError("End date cannot be before start date.")
        if data["start_date"] < date.today():
            raise serializers.ValidationError("Start date cannot be in the past.")

        leave_type = data.get("leave_type")
        document = data.get("supporting_document")

        leaves_requiring_document = ["SICK", "STUDY"]

        if leave_type in leaves_requiring_document and not document:
            raise serializers.ValidationError(
                f"{leave_type} leave requires a supporting document."
            )
        logger.info(
            "Leave validation successful for type=%s start=%s end=%s",
            leave_type,
            data.get("start_date"),
            data.get("end_date"),
        )
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}, min_length=8
    )

    class Meta:
        model = Employee
        fields = [
            "first_name",
            "last_name",
            "email",
            "employee_department",
            "employee_position",
            "phone_number",
            "employee_role",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Create a new employee instance with the provided validated data."""
        password = validated_data.pop("password")

        # Ensure a unique username is always set. Since the custom user model
        # still inherits from AbstractUser, the "username" field is required
        # and must be unique. If we don't populate it, multiple users will end
        # up with the default empty string and the database will raise a
        # UNIQUE constraint error (500 response) on the second registration.
        if "username" not in validated_data or not validated_data.get("username"):
            base_username = (validated_data.get("email") or "").split("@")[0] or "user"
            username = base_username
            suffix = 1
            while Employee.objects.filter(username=username).exists():
                username = f"{base_username}{suffix}"
                suffix += 1
            validated_data["username"] = username

        logger.info(
            "Creating employee account for email=%s department=%s position=%s role=%s",
            validated_data.get("email"),
            validated_data.get("employee_department"),
            validated_data.get("employee_position"),
            validated_data.get("employee_role"),
        )

        employee = Employee(**validated_data)
        employee.set_password(password)  # Hash the password before saving
        employee.save()
        logger.info(
            "Employee created with id=%s username=%s", employee.id, employee.username
        )
        return employee


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}, min_length=8
    )
