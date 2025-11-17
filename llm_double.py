import google.generativeai as genai
import os
import time 

# --- 1. Configuration (silencieuse) ---
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Erreur : La variable d'environnement GOOGLE_API_KEY n'est pas définie.")
    print("Veuillez la définir dans votre terminal avant de lancer le script.")
    exit()

# --- 2. Définir les Modèles ---

model_a = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    system_instruction="Tu es 'Sherlock', un détective logique et analytique. Tu parles à 'Watson'. Sois bref."
)
model_b = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    system_instruction="Tu es 'Watson', le partenaire enthousiaste de Sherlock. Tu t'émerveilles de ses déductions."
)

# --- 3. La boucle de conversation ---
message_actuel = "Watson, un nouveau mystère nous attend : La disparition du diamant bleu."
nombre_de_tours = 3 

print(f"🕵️‍♂️ Sherlock (Sujet) : {message_actuel}\n")

try:
    for tour in range(nombre_de_tours):
        
        # 1. Sherlock (A) parle
        time.sleep(3) # Pause nécessaire pour le quota de l'API
        response_a = model_a.generate_content(message_actuel)
        reponse_texte_a = response_a.text
        
        # Affichage de la réponse de A
        print(f"🕵️‍♂️ Sherlock : {reponse_texte_a}\n")
        message_actuel = reponse_texte_a
        
        # 2. Watson (B) répond
        time.sleep(3) # Pause nécessaire pour le quota de l'API
        response_b = model_b.generate_content(message_actuel)
        reponse_texte_b = response_b.text
        
        # Affichage de la réponse de B
        print(f"👨‍⚕️ Watson : {reponse_texte_b}\n")
        message_actuel = reponse_texte_b

except Exception as e:
    print(f"\nUne erreur est survenue pendant le chat : {e}")
