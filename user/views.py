import json, re, requests, hashlib
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.cache import cache

from user.models import users, chats
from items.models import Food
from user.forms import loginform, chatform

# Updated to match your FastAPI port
CHAT_API_URL = "http://127.0.0.1:8001/chat"
CLIP_API_URL = "http://127.0.0.1:8002/predict_food"

# ---------------- LOGIN ----------------
@never_cache
def log(request):
    form = loginform()
    if request.method == "POST":
        form = loginform(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['email'],
                password=form.cleaned_data['passcode']
            )
            if user:
                auth_login(request, user)
                return redirect(request.GET.get('next', 'home'))
            form.add_error(None, "Invalid credentials")
    return render(request, 'loginpage.html', {'form': form})

# ---------------- HOME ----------------
@never_cache
@login_required
def home(request):
    uzer = users.objects.get(user=request.user)
    prev = chats.objects.filter(name=uzer.name).order_by('count')[:20]
    return render(request, 'home.html', {'uzer': uzer, 'form': chatform(), 'previous_chats': prev})

# ---------------- CHAT ----------------
@csrf_exempt
@login_required
def start_chat(request):
    user_prompt = request.POST.get("prompt", "").strip()
    image_file = request.FILES.get("image")
    research_blocks = []

    # ---------- 1. IMAGE → CLIP ----------
    if image_file:
        try:
            image_file.seek(0)
            files = {'image': (image_file.name, image_file.read(), image_file.content_type)}
            resp = requests.post(CLIP_API_URL, files=files, timeout=5)
            data = resp.json()
            detected_food = data[0].get("food_name") if isinstance(data, list) else data.get("food_name")
            if not detected_food and "predictions" in data:
                detected_food = data["predictions"][0].get("food_name")
                
            if detected_food:
                user_prompt = f"{user_prompt} {detected_food.lower()}".strip()
        except Exception as e:
            print("CLIP error:", e)

    raw_prompt = user_prompt.lower()

    # ---------- 2. TWO STAGE SEARCH ----------
    if raw_prompt:
        words = [w for w in re.findall(r"[a-z]+", raw_prompt) if len(w) >= 3]
        if words:
            stage1_query = Q()
            for w in words:
                prefix = w[:-2] if len(w) > 3 else w
                stage1_query |= (Q(item__istartswith=prefix) | Q(variant__istartswith=prefix))

            candidates = Food.objects.filter(stage1_query).distinct()

            scored = []
            for f in candidates:
                score = 0
                item_text, var_text = (f.item or "").lower(), (f.variant or "").lower()
                for w in words:
                    if w in var_text: score += 3
                    elif w in item_text: score += 1
                if score > 0:
                    scored.append((score, f))

            scored.sort(key=lambda x: x[0], reverse=True)

            if scored:
                top_score = scored[0][0]
                top_items = [f for score, f in scored if score == top_score]

                items_text = [
                    f"ITEM: {f.item}\nVARIANT: {f.variant}\nMETHOD: {f.method}\n"
                    f"NUTRIENTS: {f.nutrients}\nBENEFITS: {f.benefits}\nHAZARDS: {f.hazards}\n"
                    f"VIDEO URL: {f.video_url or 'None'}\n"
                    f"SOURCE URL: {f.source_url or 'None'}\n"
                    f"IMAGE URL: {f.image_url or 'None'}"
                    for f in top_items
                ]
                
                research_blocks.append(
                    f"RANK: 1\nMATCH_SCORE: {top_score}\n" + 
                    "\n---\n".join(items_text)
                )

    res_data = "\n\n====================\n\n".join(research_blocks) if research_blocks else "No records found."

    # ---------- 3. PREPARE FASTAPI PAYLOAD ----------
    uzer = users.objects.get(user=request.user)
    # Get last 5 history items
    history_objs = chats.objects.filter(name=uzer.name).order_by('-count')[:5]
    history = [{"user": c.prompt, "bot": c.bot} for c in reversed(history_objs)]

    # This structure matches your ChatRequest BaseModel in FastAPI
    fastapi_payload = {
        "user_prompt": user_prompt,
        "research_data": res_data,
        "history": history
    }

    # Wrap for the Frontend
    response_payload = {
        "stream_url": CHAT_API_URL,
        "payload": fastapi_payload
    }

    cache.set(f"chat_{hashlib.md5(user_prompt.encode()).hexdigest()}", response_payload, 3600)
    return JsonResponse(response_payload)

# ---------------- SAVE CHAT ----------------
@csrf_exempt
@login_required
def save_chat_history(request):
    if request.method == "POST":
        uzer = users.objects.get(user=request.user)
        last = chats.objects.filter(name=uzer.name).order_by('-count').first()
        chats.objects.create(
            name=uzer.name,
            count=(last.count + 1 if last else 1),
            prompt=request.POST.get('prompt'),
            bot=request.POST.get('bot'),
            image=request.FILES.get('image')
        )
        return JsonResponse({'status': 'saved'})

# ---------------- UTILS ----------------
@login_required
def flush(request):
    uzer = users.objects.get(user=request.user)
    chats.objects.filter(name=uzer.name).delete()
    return redirect('home')

@login_required
def out(request):
    logout(request)
    return redirect('log')