from django.db.models import EmailField, CharField, UUIDField, DateField, BooleanField, IntegerField
from django.contrib.auth.models import PermissionsMixin, UserManager, AbstractUser
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models.fields import BooleanField
from django.forms import IntegerField
import uuid
from django.utils.translation import gettext_lazy as _

# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    email = EmailField(unique=True)
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    phone_number = CharField(max_length=10)
    password = CharField(max_length=255)
    uuid = UUIDField(default=uuid.uuid4, editable=False, unique=True)
    birth_date = DateField()
    is_teacher = BooleanField(default=True)
    is_admin = BooleanField(default=False)
    is_staff = BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    username_validator = UnicodeUsernameValidator()

    username = CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
         
    is_active = BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def has_perm(self, perm: str, obj=True) -> bool:
        return self.is_admin
    
    def has_module_perms(self, app_label: str) -> bool:
        return True
