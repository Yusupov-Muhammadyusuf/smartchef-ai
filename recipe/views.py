import os
import base64
import requests
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def main(request):
    return render(request, "main.html")

def generate_recipe(request):
    if request.method == "GET":
        saved_recipe = request.session.get("last_recipe")
        saved_image = request.session.get("last_image")

        if saved_recipe and saved_image:
            return render(request, "recipe.html", {
                "recipe": saved_recipe,
                "image_url": saved_image
            })
        
        return render(request, "main.html")

    if request.method == "POST" and request.FILES.get("ingredients_image"):
        image_file = request.FILES["ingredients_image"]
        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        image_url = fs.url(filename)
        image_path = fs.path(filename)

        with open(image_path, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode("utf-8")

        url = "https://models.inference.ai.azure.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GITHUB_TOKEN}"
        }

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a world-class professional chef. Analyze all the food ingredients gathered in the image. "
                        "Create the fastest and most delicious recipe possible from these items. The step-by-step instructions "
                        "must be incredibly clear, friendly, and simple. Respond strictly in English. "
                        "Format the output beautifully using bullet points, bold text, and appropriate emojis. "
                        "CRITICAL RULE: If the image does not contain any food ingredients or edible items, politely "
                        "inform the user that you can only generate recipes from food images, and ask them to upload a proper image."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Please look at these gathered ingredients and generate a great recipe."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                    ]
                }
            ],
            "model": "gpt-4o-mini",
            "temperature": 0.7
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            result_data = response.json()
            recipe_text = result_data["choices"][0]["message"]["content"]

            request.session["last_recipe"] = recipe_text
            request.session["last_image"] = image_url
        except Exception as e:
            print("Error details:", e)

            request.session["last_recipe"] = "Sorry, the chef encountered an error while analyzing your ingredients. Please try again!"
            request.session["last_image"] = image_url

        return redirect("generate_recipe")
    
    return redirect("generate_recipe")