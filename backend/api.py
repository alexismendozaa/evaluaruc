from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import fitz  # PyMuPDF para leer PDFs
import google.generativeai as genai
from predictions.predictor import Predictor

# Inicializar Flask
app = Flask(__name__)
CORS(app, origins=["http://3.227.55.144:4200"])  # Permitir peticiones solo desde el frontend

# Configurar API de Gemini AI con la clave de acceso
GEMINI_API_KEY = "AIzaSyBbRf1Aw0iffONA29mjpvQRGLRcJVeDOaM"
genai.configure(api_key=GEMINI_API_KEY)

# Definir rutas necesarias
model_dir = os.path.join(os.path.dirname(__file__), "models")
scaler_path = os.path.join(model_dir, "scaler.pkl")
graphics_dir = os.path.join(os.path.dirname(__file__), "graphics")
database_path = os.path.join(os.path.dirname(__file__), "database", "datos_procesados.csv")
PDFS_FOLDER_PATH = os.path.join(os.path.dirname(__file__), "backend", "resources")

# Cargar la base de datos
df_clean = pd.read_csv(database_path, dtype={"NUMERO_RUC": str})
# Inicializar el predictor
predictor = Predictor(df_clean, model_dir, scaler_path, graphics_dir)

def extract_text_from_pdf(pdf_path):
    """Extrae el texto de un archivo PDF."""
    try:
        with fitz.open(pdf_path) as pdf:
            text = ""
            for page in pdf:
                text += page.get_text("text") + "\n"
            return text
    except Exception as e:
        print(f"Error al leer el PDF: {str(e)}")
        return None

def extract_text_from_pdfs(folder_path):
    """Extrae y combina el texto de todos los archivos PDF en una carpeta."""
    all_text = ""
    try:
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".pdf"):
                pdf_path = os.path.join(folder_path, file_name)
                with fitz.open(pdf_path) as pdf:
                    for page in pdf:
                        all_text += page.get_text("text") + "\n"
        return all_text
    except Exception as e:
        print(f" {str(e)}")
        return None

# Cargar el contenido de todos los PDFs
sri_texts = extract_text_from_pdfs(PDFS_FOLDER_PATH)

@app.route("/predict", methods=["POST"])
def predict():
    """Recibe un RUC y devuelve la predicción del nivel de riesgo."""
    data = request.json
    ruc = data.get("ruc")

    if not ruc:
        return jsonify({"error": " Debes ingresar un RUC"}), 400

    resultado = predictor.predict(ruc)

    if "error" in resultado:
        return jsonify(resultado), 404

    return jsonify(resultado), 200


@app.route("/chatbot", methods=["POST"])
def chatbot():
    """
    Chatbot con Gemini: interactúa libremente y da consejos basados en el riesgo fiscal.
    """
    data = request.json
    ruc = data.get("ruc")
    risk_level = data.get("risk_level")
    user_message = data.get("user_message", "").strip().lower()  # Obtener mensaje del usuario

    if not ruc or risk_level is None:
        return jsonify({"error": "Se requiere el RUC y el nivel de riesgo."}), 400

    # 📌 **Consejos fiscales basados en nivel de riesgo**
    consejos_fiscales = {
        "Super Bajo": "Tu situación fiscal es excelente. Mantén registros claros y sigue presentando tus declaraciones puntualmente.",
        "Bajo": "Tienes un buen perfil fiscal, pero asegúrate de mantener un historial de pagos limpio y revisar tus deducciones.",
        "Medio": "Te recomendamos consultar con un contador para optimizar tu carga fiscal y evitar posibles riesgos.",
        "Alto": "Existe cierto riesgo. Revisa tu contabilidad con un experto y cumple con los plazos para evitar sanciones.",
        "Super Alto": "Alto riesgo fiscal. Es urgente que busques asesoría profesional para evitar sanciones y problemas legales."
    }

    # Si el usuario responde afirmativamente, dar consejos fiscales
    if user_message in ["sí", "si", "ok", "claro"]:
        respuesta = consejos_fiscales.get(risk_level, "No tengo información específica para tu caso.")

    else:
        prompt = f"""
        Aquí están las regulaciones del SRI sobre riesgos fiscales, basadas en documentos oficiales:

        {sri_texts}

        Un usuario con RUC {ruc} tiene un nivel de riesgo {risk_level}.
        El usuario pregunta: "{user_message}". 

        Si la pregunta está relacionada con riesgo fiscal, impuestos o normativas del SRI, responde de manera clara y útil. 
        Si la pregunta NO tiene relación con estos temas, responde con: "Solo puedo responder preguntas sobre riesgo fiscal y normativas del SRI."
        """

        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(prompt)
            respuesta = response.text if response else "No tengo información específica en este momento."

            # Si Gemini no sigue la restricción, filtrar manualmente
            if "solo puedo responder" in respuesta.lower():
                respuesta = "Solo puedo responder preguntas sobre riesgo fiscal y normativas del SRI."

        except Exception as e:
            respuesta = f"Error al generar respuesta: {str(e)}"

    return jsonify({"response": respuesta})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
