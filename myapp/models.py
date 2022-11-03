from django.db import models
from django.utils import timezone

# Create your models here.
class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.EmailField()
	mobile=models.PositiveIntegerField()
	password=models.CharField(max_length=100)
	usertype=models.CharField(max_length=100,default="user")
	address=models.TextField(default="")
	country=models.CharField(max_length=100,default="")
	state=models.CharField(max_length=100,default="")
	zipcode=models.PositiveIntegerField(default=0)
	city=models.CharField(max_length=100,default="")

	def __str__(self):
		return self.fname
class Product(models.Model):
	CHOICE=(
		("Men","Men"),
		("Women","Women"),
		("Kids","Kids")
		)
	seller=models.ForeignKey(User,on_delete=models.CASCADE)
	product_category=models.CharField(max_length=100,choices=CHOICE)
	product_name=models.CharField(max_length=100)
	product_price=models.PositiveIntegerField()
	product_desc=models.TextField()
	product_image=models.ImageField(upload_to="product_image/")


	def __str__(self):
		return self.seller.fname+"-"+self.product_name

class Wishlist(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	data=models.DateTimeField(default=timezone.now)

	def __strt__(self):
		return self.user.fname+"-"+self.product.product_name

class Cart(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	data=models.DateTimeField(default=timezone.now)
	product_qty=models.PositiveIntegerField()
	product_price=models.PositiveIntegerField()
	total_price=models.PositiveIntegerField()
	payment_status=models.BooleanField(default=False)

	def __strt__(self):
		return self.user.fname+"-"+self.product.product_name

class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions',on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)
