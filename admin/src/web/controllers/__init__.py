#from .user import user_bp
from .user.user_management import user_management_bp
from .auth import auth_bp

__all__ = ['user_management_bp', 'auth_bp']