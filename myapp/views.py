from django.shortcuts import render, redirect
from .models import User,Product,Wishlist,Cart,Transaction
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import send_mail
import random


# Create your views here.
def validate_email(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}

	return JsonResponse(data)

def index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=="user":
			return render(request,'index.html')
		else:
			return render(request,'seller_index.html')
	except:
		return render(request,'index.html')
def product_list(request):
	products=Product.objects.all()
	return render(request,'product-list.html',{"products":products})
def product_detail(request,pk):
	wishlist_flag=False
	cart_flag=False
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	try:
		Wishlist.objects.get(user=user,product=product)
		wishlist_flag=True
	except:
		pass
	try:
		Cart.objects.get(user=user,product=product,payment_status=False)
		cart_flag=True
	except:
		pass
	return render(request,'product-detail.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})
def cart(request):
	net_price=0
	shipping=100
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		net_price=net_price+i.total_price
	checkout_price=net_price+shipping
	request.session['cart_count']=len(carts)
	return render(request,'cart.html',{'carts':carts,'net_price':net_price,'shipping':shipping,'checkout_price':checkout_price})
def checkout(request):
	user=User.objects.get(email=request.session['email'])
	checkout_price=request.POST['checkout_price']
	return render(request,'checkout.html',{'user':user,'checkout_price':checkout_price})
def my_account(request):
	return render(request,'my-account.html')
def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'wishlist.html',{'wishlists':wishlists})
	
def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'],password=request.POST['password'])
			request.session['email']=user.email
			request.session['fname']=user.fname
			wishlists=Wishlist.objects.filter(user=user)
			request.session['wishlist_count']=len(wishlists)
			carts=Cart.objects.filter(user=user,payment_status=False)
			request.session['cart_count']=len(carts)
			if user.usertype=="user":
				return render(request,'index.html')
			else:
				return render(request,'seller_index.html')
		except:
			msg2="email or password incorrect"
			return render(request,'login.html',{'msg2':msg2})
	else:
		return render(request,'login.html')

def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			otp=random.randint(1000,9999)
			subject = 'OTP for Forgot password'
			message = 'Your OTP for forgot password is'+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email, ]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'otp.html',{'email':user.email,'otp':otp})
		except:
			msg="email does not exists"
			return render(request,'forgot_password.html',{'msg':msg})

	else:
		return render(request,'forgot_password.html')

def verify_otp(request):
	otp=request.POST['otp']
	uotp=request.POST['uotp']
	email=request.POST['email']

	if otp==uotp:
		return render(request,'new_password.html',{'email':email})
	else:
		msg="Invalid OTP"
		return render(request,'otp.html',{'email':email,'otp':otp,'msg':msg})

def new_password(request):
	email=request.POST['email']
	np=request.POST['new_password']
	cnp=request.POST['cnew_password']
	
	if np==cnp:
		user=User.objects.get(email=email)
		user.password=np
		user.save()
		msg="password update successfully"
		return render(request,'login.html',{'msg':msg})
	else:
		msg:"nrw password and confirm new password does not matched"
		return render(request,'new_password.html',{'email':email,'msg':msg})



def contact(request):
	return render(request,'contact.html')
def signup(request):
	try:
		User.objects.get(email=request.POST['email'])
		msg1="Email already Exist"
		return render(request,'login.html',{'msg1':msg1})
	except:
		if request.POST['password']==request.POST['cpassword']:
			User.objects.create(
				fname=request.POST['fname'],
				lname=request.POST['lname'],
				email=request.POST['email'],
				mobile=request.POST['mobile'],
				password= request.POST['password'],
				usertype=request.POST['usertype']
				)
			msg2="User signup sucessfully"
			return render(request,'login.html',{'msg2':msg2})
		else:
			msg1="password and confirm password does not matched"
			return render(request,'login.html',{'msg1':msg1})


def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password==request.POST['new_password']
				user.save()
				return redirect('logout')
				
			else:
				msg="new password and confirm new password does not matched"
				return render(request,'change_password.html',{'msg':msg})
		else:
			msg="old password does not matched"
			return render(request,'change_password.html',{'msg':msg})
	else:
		return render(request,'change_password.html')
def seller_change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password==request.POST['new_password']
				user.save()
				del request.session['email']
				del request.session['fname']
				msg2="password change successfully"
				return render(request,'login.html',{'msg2':msg2})
			else:
				msg="new password and confirm new password does not matched"
				return render(request,'seller_change_password.html',{'msg':msg})
		else:
			msg="old password does not matched"
			return render(request,'seller_change_password.html',{'msg':msg})
	else:
		return render(request,'seller_change_password.html')

def seller_index(request):
	return render(request,'seller_index.html')
def seller_add_product(request):
	if request.method=="POST":
		seller=User.objects.get(email=request.session['email'])
		Product.objects.create(
			seller=seller,
			product_category=request.POST['product_category'],
			product_name=request.POST['product_name'],
			product_price=request.POST['product_price'],
			product_desc=request.POST['product_desc'],
			product_image=request.FILES['product_image']
			)
		msg="product add sucessfully"
		return render(request,'seller_add_product.html',{'msg':msg})
	else:
		return render(request,'seller_add_product.html')

def seller_view_product(request):
	seller=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=seller)
	return render(request,'seller_view_product.html',{'products':products})
def seller_product_detail(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller_product_detail.html',{'product':product})
def seller_edit_product(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_category=request.POST['product_category']
		product.product_name=request.POST['product_name']
		product.product_desc=request.POST['product_desc']
		product.product_price=request.POST['product_price']
		try:
			product.product_image=request.FILES['product_image']
		except:
			pass
			product.save()
			msg="product edit sucessfully"
			return render(request,'seller_edit_product.html',{'product':product,'msg':msg})
	else:	
		return render(request,'seller_edit_product.html',{'product':product})
def seller_delete_product(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('seller_view_product')

def add_to_wishlist(request,pk):
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	wishlist=Wishlist.objects.create(user=user,product=product)
	msg="product add to wishlist"
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'wishlist.html',{'msg':msg,'wishlists':wishlists})
def remove_from_wishlist(request,pk):
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('wishlist')
def add_to_cart(request,pk):
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	product_qty=1
	product_price=product.product_price
	total_price=product.product_price
	Cart.objects.create(user=user,product=product,product_qty=product_qty,product_price=product_price,total_price=total_price)
	return redirect('cart')

def remove_from_cart(request,pk):
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')

def change_qty(request,pk):
	cart=Cart.objects.get(pk=pk)
	product_qty=int(request.POST['product_qty'])
	cart.product_qty=product_qty
	cart.total_price=product_qty*cart.product_price
	cart.save()
	return redirect('cart')

def initiate_payment(request):
    user=User.objects.get(email=request.session['email'])
    try:
       
        amount = int(request.POST['amount'])
        
    except:
        return render(request, 'payments/pay.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user, amount=amount)
    transaction.save()

    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()
    carts=Cart.objects.filter(user=user,payment_status=False)
    for i in carts:
    	i.payment_status=True
    	i.save()
    carts=Cart.objects.filter(user=user,payment_status=False)
    request.session['cart_count']=len(carts)

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=True)
	return render(request,'myorder.html',{'carts':carts})