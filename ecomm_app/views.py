from django.shortcuts import render, HttpResponse,redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import Product, Cart,Order
from django.db.models import  Q 
import random
import razorpay
from django.core.mail import send_mail
# Create your views here.

def about(request):
    return HttpResponse("Hello from views file")

# def home(request):
#     return HttpResponse("<h1>Home page</h1>")

def edit(request,rid): #rid=4
    return HttpResponse("Id to be edited : "+ rid)

def addition(request,x,y):
    add=int(x)+int(y)
    print("Addition is:",add)
    return HttpResponse("Addition is:" + str(add))

class Simpleview(View):
    def get(self,request):
        return HttpResponse("Hello from class based views")
    
def hello(request):
    context={}
    context['greet']='Good evening, we are learning DTL'
    context['x']=100
    context['y']=20
    context['l']=[10,20,30,40,50]
    context['products']=[
        {'id':1,'name':'samsung','cat':'mobile','price':5000},
        {'id':2,'name':'jeans','cat':'clothes','price':1000},
        {'id':3,'name':'woodland office','cat':'shoes','price':800},
        {'id':4,'name':'tshirt','cat':'cltohes','price':1000},
        ]
    return render(request,'hello.html',context)

#---------- ekart project------------

def home(request):
    # print(request.user.id)
    #print(request.user.is_authenticated) #0
    p=Product.objects.filter(is_active=True)
    print(p)   # 5objects
    context={}
    context['products']=p 
    return render(request,'index.html',context)

def product_details(request,pid):
    p=Product.objects.filter(id=pid)
    context={}
    context['products']=p
    return render(request,'product_details.html',context)

def register(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        if uname=="" or upass=="" or ucpass=="":
            context['errmsg']="Fields cannot be Empty" 
        elif upass != ucpass:
            context['errmsg']="password and confirm password didn't match" 
        else:
            try:
                u=User.objects.create(password=upass,username=uname,email=uname)
                u.set_password(upass)
                u.save()
                context['success']="User Created Successfully,Please login"
            except Exception:
                context['errmsg']="Username already Exists !!"
        return render(request,'register.html',context)
    else:
        return render(request,'register.html')
    
def user_login(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        context={}
        if uname=="" or upass=="":
            context['errmsg']="Fields cannot be Empty" 
            return render(request,'login.html',context)
        else:
            u= authenticate(username=uname,password=upass)
            # print(u)
            if u is not None:
                login(request,u)   # start session- 2nd user
                return redirect('/')
            else:
                context['errmsg']="Username and Password is invalid" 
                return render(request,'login.html',context)           
    else:
        return render(request,'login.html')
    
def user_logout(request):
    logout(request)         # destroy session
    return redirect('/')

def catfilter(request,cv): #cv =1
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=Product.objects.filter(q1 & q2)  # 2 active objects
    context={}
    context['products']=p    #2 products
    return render(request,'index.html',context)

def sort(request,sv):
    if sv=='0':
        col='price'
    else:
        col='-price'
    p=Product.objects.filter(is_active=True).order_by(col)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=Product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p
    return render(request,'index.html',context)
    
def addtocart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        u=User.objects.filter(id=userid) #[user object(7)]
        p=Product.objects.filter(id=pid) #[product object(6)]
        #check product exist or not
        q1=Q(uid=u[0])     # userobject (7)
        q2=Q(pid=p[0])    # product object(6)
        c=Cart.objects.filter(q1 & q2)  #[]
        n=len(c)
        context={}
        if n==1:
            context['msg']="Product Already Exist in cart!!"
        else:
            c=Cart.objects.create(uid=u[0],pid=p[0])
            c.save()
            context['success']="Product Added succsussfully to Cart"
        context['products']=p    #[product object(6)]
        return render(request,'product_details.html',context)
        # return HttpResponse("product added successfully")
    else:
        return redirect('/login')
    
def viewcart(request):
    c=Cart.objects.filter(uid=request.user.id) #uid=7-fourthuser
    # print(c) #[cart object[7],cart object(8)]
    context={}
    context['data']=c
    n=len(c)
    s=0
    for i in c:
        # print(i.pid.price)
        s=s+i.pid.price * i.qty  # s=9500
    context['total']=s
    context['np']=n
    return render(request,'cart.html',context)

def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')

def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)
    # print(c) #queryset[ cart object(7)]
    # print(c[0].pid)
    # print(c[0].uid)
    # print(c[0].qty)
    if qv == '1':
        t=c[0].qty+1       # 2+1
        c.update(qty=t)
    else:
        if c[0].qty>1:
            t=c[0].qty-1       # 2+1
            c.update(qty=t)
    return redirect('/viewcart')

def placeorder(request):
    userid=request.user.id   #userid=7 - fourthuser
    c=Cart.objects.filter(uid=userid)
    # print(c)   #<QuerySet [<Cart: Cart object (7)>, <Cart: Cart object (8)>]>
    oid=random.randrange(1000,9999)
    print(oid)
    for x in c:
        o=Order.objects.create(order_id=oid,uid=x.uid,pid=x.pid,qty=x.qty)
        o.save()
        x.delete()
    o=Order.objects.filter(uid=request.user.id) #uid=7-fourthuser
    context={}
    context['data']=o
    n=len(o)
    s=0
    for i in o:
        s=s+i.pid.price * i.qty  # s=9500
    context['total']=s
    context['np']=n
    return render(request,'placeorder.html',context)
    # return HttpResponse("placed order successfully")

def makepayment(request):
    orders=Order.objects.filter(uid=request.user.id) #id=7
    context={}
    s=0
    for i in orders:
        s=s+i.pid.price * i.qty  # s=9500
        oid=i.order_id
    client = razorpay.Client(auth=("rzp_test_pjmfONoAV5hhRJ", "2qLFlWxOv0vaA1jxWEEHwbcA"))
    data = { "amount": s*100, "currency": "INR", "receipt": oid }
    payment = client.order.create(data=data) 
    print(payment)
    context['data']=payment
    return render(request,'pay.html',context)
    # return HttpResponse("In makepayment function")

def sendusermail(request):
    uemail=request.user.email #fourthuser@gmail.com
    msg="Order details are:"
    send_mail(
        "Ekart-Order Placed Successfully",
        msg,
        "dhanutdy15@gmail.com",
        [uemail],
        fail_silently=False,
    )
    return HttpResponse("Mail sent successfully")
