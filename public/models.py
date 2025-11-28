# همه مدل‌ها رو از فایل‌های جداگانه import می‌کنیم
from .models.product_model import Product,Tag,Categury,ProductImage
from .models.shoping_model import Order,Enrollment,Payment,Order_Item
from .models.user_model import CustomUser
from .models.course_model import Course
from .models.banner_model import Banner