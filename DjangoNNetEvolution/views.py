from django.shortcuts import render_to_response

# Create your views here.

def main_view(request):
    return render_to_response('main_nnev.html')

