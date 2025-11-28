# views.py  (این فایل بیرون فولدر views قرار دارد)

# -------- User Views --------
from .views.user_views import (
    CustomUserViewSet,
    LogoutView,
)

# -------- Staff Views --------
from .views.staff_views import (
    staff_page,
    TeacherCourseViewSet,
    TeacherProductViewSet,
)

# -------- Product Views --------
from .views.product_views import (
    ProductViewSet,
)

# -------- Order Views --------
from .views.order_views import (
    OrderViewSet,
    OrderItemViewSet,
    PaymentViewSet,
    EnrollmentViewSet,
)

# -------- Course Views --------
from .views.course_views import (
    CourseViewSet,
)

# -------- Auth Views --------
from .views.auth_view import (
    RegisterView,
    CodeCheckR,
    CodeCheckL,
    verify_number,
    checklogin,
)

# -------- Auth Views --------
from .views.categury_views import (
    CateguryViewSet
    )
