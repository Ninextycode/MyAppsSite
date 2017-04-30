from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie

import os
import io
import time
import json
import base64
from PIL import Image

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .forms import TextForm, FileForm
import MyAppsSite.settings as settings


import DjangoBacktester.evaluator as evaluator
import DjangoBacktester.datagraphs as datagraphs
# Create your views here.
import time


def response_for_wrong_request():
    return HttpResponse(json.dumps({"logs": "Wrong request"}), content_type="application/json")

def response_for_rendering_error():
    HttpResponse(json.dumps({"logs": "Error while rendering"}), content_type="application/json")

def evaluate_strategy(request):
    if request.is_ajax() and request.method == "POST":
        selected_shares = []
        try:
            selected_shares = json.loads(request.POST["selected_shares"])
            datagraphs.prepare_files(selected_shares, request.POST["start_date"], request.POST["end_date"])
        except Exception as e:
            response = \
                HttpResponse(json.dumps({"logs": "Error in history data "}), content_type="application/json")
            return response

        result = evaluator.evaluate(request.POST["strategy"], selected_shares)
        if result[0]:
            result[1]["LIQUIDATION VALUE"] = result[1]["lv"]
            result[1]["MONEY"] = result[1]["money"]
            del result[1]["lv"]
            del result[1]["money"]

            data = pd.DataFrame(result[1])
            data.to_csv(os.path.join(settings.MEDIA_ROOT, 'results.csv'))

            data["MONEY"] /= 100
            data["LIQUIDATION VALUE"] /= 100

            images = {}
            try:
                images = datagraphs.images_from_data(data)
            except Exception as e:
                response = response_for_rendering_error

            response =  \
                HttpResponse(json.dumps({"logs": "Success", "plots": images}),
                                 content_type="application/json")
        else:
            response =\
                HttpResponse(json.dumps({"logs": "Fail: " + result[1].__str__()}), content_type="application/json")

    else:
        response = response_for_wrong_request()

    return response


def get_shares_graphs(request):
    images = {}
    if request.is_ajax() and request.method == "POST":
        try:
            selected_shares = json.loads(request.POST["selected_shares"])
            images = datagraphs.get_graphs(selected_shares, request.POST["start_date"], request.POST["end_date"])
        except Exception as e:
            return response_for_rendering_error
        return HttpResponse(json.dumps(images), content_type = "application/json")
    else:
        return response_for_wrong_request()

@ensure_csrf_cookie
def write_form(request):
    print("123")
    files = os.listdir(settings.STATIC_ROOT)
    files = [x[:-4] for x in files if x[-3:] == "csv"]
    return render(request, 'write_form.html',
                  context={"shares": files})

def show_result(request):
    output = request.session.get("strategy_code", "")
    return render(request, 'output.html', {"output": output})
