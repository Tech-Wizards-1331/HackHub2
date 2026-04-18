from django.shortcuts import render

from accounts.decorators import role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('volunteer')
def home(request):
	return render(request, 'volunteers/home.html')
