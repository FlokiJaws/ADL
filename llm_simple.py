from google import genai
import google.generativeai as genai
import os 

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Erreur : La variable d'environnement GOOGLE_API_KEY n'est pas définie.")
    print("Veuillez la définir dans votre terminal avant de lancer le script.")
    exit()

model = genai.GenerativeModel("gemini-2.5-flash") 

response = model.generate_content(
    "Bonjour, quel temps fait-il a Limoges aujourd'hui ?",
)

print(response.text)