from django.shortcuts import render
from django.views import View


class CalculatorView(View):

    def get(self, request):
        return render(request, 'practice/calculator.html')
