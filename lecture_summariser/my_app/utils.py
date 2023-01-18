from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import whisper
import uuid
import openai


async def transcribe_and_summarise(video):
    fn = f"{uuid.uuid4().hex}.mp4"
    fs = FileSystemStorage()
    fs.save(fn, video)
    transcript = transcribe(fn)
    fs.delete(fn)
    summary = summarise(transcript)
    return [transcript, summary]


def transcribe(fn):
    model = whisper.load_model("tiny.en")
    result = model.transcribe(os.path.join(settings.MEDIA_ROOT, fn), verbose=True)
    transcript = result["text"]
    return transcript


def make_prompt(transcript, count=None):
    prompt = f"summarise the following transcript of a lecture, provide the summary in point form"
    if count:
        prompt += f", this is the part {count} of the transcript"
    prompt += f":\n\n{transcript}"
    return prompt


def summarise(transcript):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = make_prompt(transcript=transcript)
    try:
        summary = openai.Completion.create(engine="text-davinci-003", prompt=prompt,)[
            "choices"
        ][0]["text"].replace("\n", "NEWLINE")
    except openai.error.InvalidRequestError as e:
        print(e)
        summary = ""
        half = len(transcript) // 2
        prompts = [
            make_prompt(transcript=transcript[half:], count=1),
            make_prompt(transcript=transcript[:half], count=2),
        ]

        # fs_idxs = [i for i, _ in enumerate(transcript) if _ == "."]
        # count = 0
        # prev = 0
        # for fs_idx in fs_idxs:
        #     if fs_idx % 16000 == 0:
        #         cut = transcript[prev:fs_idx]
        #         prev = fs_idx
        #         count += 1
        #         prompt = f"summarise the following transcript of a lecture, provide the summary in point form, this is the part {count} of the transcript:\n\n{cut}"
        #         prompts.append(prompt)
        # summary = ""
        for prompt in prompts:
            summary += openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
            )["choices"][0]["text"].replace("\n", "NEWLINE")
    return summary
