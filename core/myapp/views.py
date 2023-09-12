from django.shortcuts import render, redirect
import requests

from django.views import View  
from myapp.models import*
from datetime import datetime
from django.http import HttpResponse
from django.core.mail import send_mail
import math, random
from django.contrib import messages

    
class register(View):
    """view for register a new user."""
    
    def get(self, request):
        return render(request, "register.html")
    
    def post(self, request):
        error_msg = None
        PostData = request.POST
        name = PostData.get('name')
        dob = PostData.get('dob')
        dob2 =datetime.strptime(PostData.get('dob'), '%Y-%m-%d')
        today = datetime.now().date()
        age = today.year - dob2.year
        ph = PostData.get('ph')
        email = PostData.get('email')
        about = PostData.get('about')
        userid = random.randint(1001, 9999)
        
        
        if (not ph) and len(ph) < 10:
            error_msg = "phone number required or should be 10 digit !"
            
        if len(about)<5 and (not about):
            error_msg = "about must be at least 5 long"
        
        if not error_msg:
            user = Customer(userid=userid, name=name, dob=dob, ph=ph, age=age, email=email,about=about)
            user.save()
            request.session['email'] = email
            request.session['phone'] = ph
        context = {'user': user}
        return render(request, "welcomepage.html", context=context)
    
  
def generateOTP() :
    """function to generate otp."""
    
    digits = "0123456789"
    OTP = ""
    for i in range(4) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def send_otp(request):
    """view function to send a otp."""
    
    phone = int(request.session.get('phone'))
    email=request.session.get('email')
    print(email, phone)
    o=generateOTP()
    request.session['otp'] = o
    print('otp is ',o)
    
    
    """send otp code for mobile"""
    url = 'https://www.fast2sms.com/dev/bulkV2'
    message = o
    numbers = phone
    payload = f'sender_id=TXTIND&message={message}&route=v3&language=english&numbers={numbers}'
    headers = {
    'authorization': "xoiObB7WLa4GvY0uPZ6J9KmS1kXQCA2MeRhpzfTHN5sy8dctVDo5mkyeX9CRJxBKzu8M7FZ0stfh2gdi",
    'Content-Type': "application/x-www-form-urlencoded"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)
    
    
    """send otp code for mail"""
    htmlgen =  f'<p> OTP: <strong>{o}</strong></p>'
    send_mail('OTP request',o,'email',[email], fail_silently=False, html_message=htmlgen)
    
    return render(request, "otp.html", {'email': email, 'phone': phone})

 
def otp_verification(request):
    """View function for otp verification."""
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
    if otp == request.session["otp"]:
        messages.info(request,'signed in successfully...')
        email=request.session.get('email')
        user = Customer.objects.get(email=email)
        return render(request,"userdetails.html",{'user': user})
    else:
        messages.error(request,'otp does not match')
        return render(request,"otp.html")
        
    
def decision(request):
    """Decision after manual verification."""
    
    if request.method == 'POST':  
        decision = request.POST.get('decision')
        email = request.session.get('email')
        user = Customer.objects.get(email=email)
        
        """send success mail when accepted"""
        if decision == 'Accept':
            message = f"Registered successfully . Your user ID: {user.id}. Password: password"
            html_content = f"<p>Registered successfully <strong>{user.id}</strong><br>Password is: password</p>"

            send_mail(
                subject='Registration Successful',
                message=message,
                from_email='email', 
                recipient_list=[email],
                fail_silently=False,
                html_message=html_content,
            )
            
            """send rejection mail when rejected."""
        elif decision == 'Reject':
            htmlgen = f'<p>Application rejected! Please edit your application.</p>'
            
            send_mail(
                subject='Application Rejected',
                message="Application rejected! Edit your application.",
                from_email='email', 
                recipient_list=[email],
                fail_silently=False,
                html_message=htmlgen,
            )
        return HttpResponse("Successfully processed")
    else:
        # Handle cases where the request method is not POST
        return HttpResponse("Invalid request method")
    
    
