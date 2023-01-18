from django.shortcuts import render
from django.http import HttpResponse
from .utils import transcribe_and_summarise
import asyncio

# Create your views here.
def home(request):
    return render(request, "my_app/home.html")


async def upload(request):
    if request.method == "POST":
        video = request.FILES["video"]
        task = asyncio.ensure_future(transcribe_and_summarise(video))
        transcript, summary = await asyncio.wait_for(task, None)
        response = HttpResponse()
        response["transcript"] = transcript
        response["summary"] = summary
        return response
