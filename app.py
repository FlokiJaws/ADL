from flask import Flask, render_template, request, jsonify, Response
import json
import time
from llama_cpp import Llama

# --- Global Model Loading ---
# This loads the model once when the application starts.
print("Loading the local Mistral model...")
try:
    llm = Llama(
        model_path="mistral-7b-instruct-v0.2.Q4_K_M.gguf",  
        n_ctx=2048,
        n_gpu_layers=0,
        verbose=False,
        chat_format="mistral-instruct" 
    )
    print("Local model loaded successfully.")
except Exception as e:
    print(f"Error loading the model: {e}")
    llm = None

# Initialise l'application Flask
app = Flask(__name__, static_folder='static', template_folder='static')

# --- Routes de l'application ---
@app.route('/')
def index():
    return render_template('index.html')

def generate_debate(topic):
    if not llm:
        message = {"speaker": "Erreur", "message": "Le modèle local n'a pas pu être chargé. Vérifiez les logs du serveur."}
        yield f"data: {json.dumps(message)}\n\n"
        return

    try:
        # Le "system prompt" est maintenant géré directement dans la liste des messages
        optimist_instruction = f"Tu es 'L'Optimiste'. Ton rôle est de défendre le sujet '{topic}' en mettant en avant tous les aspects positifs, les opportunités et les bénéfices. Sois concis, percutant, persuasif et ne dépasse pas 4 phrases. Utilise un ton positif. Réponds toujours à l'argument précédent de ton interlocuteur. Si l'autre te convainc, commence ta réponse par 'CONSENSUS:' et explique pourquoi tu as changé d'avis."
        sceptic_instruction = f"Tu es 'Le Sceptique'. Ton rôle est de critiquer le sujet '{topic}' en soulevant les doutes, les risques, les inconvénients et les défis. Sois concis, percutant, réaliste et ne dépasse pas 4 phrases. Utilise un ton interrogatif ou prudent. Réponds toujours à l'argument précédent de ton interlocuteur. Si l'autre te convainc, commence ta réponse par 'CONSENSUS:' et explique pourquoi tu as changé d'avis."

        # Premier message pour lancer le débat
        current_argument = f"Commençons le débat sur : '{topic}'. Je suis convaincu que ce sujet présente de nombreux avantages. Mon premier argument est..."
        
        max_tours = 15
        
        # L'historique des messages est une liste de dictionnaires
        history_optimist = [{"role": "system", "content": optimist_instruction}]
        history_sceptic = [{"role": "system", "content": sceptic_instruction}]

        for tour in range(max_tours):
            # --- Tour de l'Optimiste ---
            history_optimist.append({"role": "user", "content": current_argument})
            
            full_response_optimist = ""
            for chunk in llm.create_chat_completion(messages=history_optimist, max_tokens=150, stop=["</s>"], stream=True):
                delta = chunk['choices'][0]['delta']
                if 'content' in delta:
                    full_response_optimist += delta['content']

            text_optimist = full_response_optimist.strip()
            history_optimist.append({"role": "assistant", "content": text_optimist})

            if text_optimist.strip().startswith("CONSENSUS:"):
                message = {"speaker": "Optimiste", "message": text_optimist}
                yield f"data: {json.dumps(message)}\n\n"
                consensus_message = {"speaker": "Consensus", "message": f"L'Optimiste a été convaincu par le Sceptique. La conclusion est contre le sujet '{topic}'."}
                yield f"data: {json.dumps(consensus_message)}\n\n"
                break

            message = {"speaker": "Optimiste", "message": text_optimist}
            yield f"data: {json.dumps(message)}\n\n"
            time.sleep(1)
            current_argument = text_optimist

            # --- Tour du Sceptique ---
            history_sceptic.append({"role": "user", "content": current_argument})
            
            full_response_sceptic = ""
            for chunk in llm.create_chat_completion(messages=history_sceptic, max_tokens=150, stop=["</s>"], stream=True):
                delta = chunk['choices'][0]['delta']
                if 'content' in delta:
                    full_response_sceptic += delta['content']
            
            text_sceptic = full_response_sceptic.strip()
            history_sceptic.append({"role": "assistant", "content": text_sceptic})

            if text_sceptic.strip().startswith("CONSENSUS:"):
                message = {"speaker": "Sceptique", "message": text_sceptic}
                yield f"data: {json.dumps(message)}\n\n"
                consensus_message = {"speaker": "Consensus", "message": f"Le Sceptique a été convaincu par l'Optimiste. La conclusion est en faveur du sujet '{topic}'."}
                yield f"data: {json.dumps(consensus_message)}\n\n"
                break

            message = {"speaker": "Sceptique", "message": text_sceptic}
            yield f"data: {json.dumps(message)}\n\n"
            time.sleep(1)
            current_argument = text_sceptic
        
        else:
            final_message = {"speaker": "Modérateur", "message": f"Le débat sur '{topic}' est terminé sans consensus après {max_tours} tours."}
            yield f"data: {json.dumps(final_message)}\n\n"

    except Exception as e:
        message = {"speaker": "Erreur", "message": f"Une erreur est survenue lors de la génération : {e}"}
        yield f"data: {json.dumps(message)}\n\n"

@app.route('/debate', methods=['POST'])
def debate():
    data = request.get_json()
    topic = data.get('topic', '').strip()

    if not topic:
        return jsonify({"error": "Le sujet du débat est manquant."}), 400

    return Response(generate_debate(topic), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
