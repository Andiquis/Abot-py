import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import requests
import pyttsx3

# Configura la clave de la API de generative AI de Google   
genai.configure(api_key="AIzaSyC8l6uIm5sX2PSXLxItRzEMXoTLV4ZDjgw")

class GeminiApp:
    def __init__(self):
        pass

    def generate_gemini_response(self, prompt):
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "max_output_tokens": 512,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config, safety_settings=safety_settings)

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Ocurrió un error: {str(e)}")
            return None

    def process_request(self, text):
        prompt = f"""
        Eres Andy, un asistente personal de inteligencia artificial diseñado para proporcionar asistencia eficiente y amigable a los usuarios.
        Fuiste creado para adaptarte a las necesidades personales y responder de manera detallada y precisa a las consultas que se te hagan.
        Tienes un enfoque personalizado y eres capaz de manejar tanto tareas cotidianas como consultas más complejas.

        Cuando los usuarios interactúan contigo, debes ser amigable, cercano y mostrar empatía en tus respuestas. 
        Puedes proporcionar recomendaciones, gestionar recordatorios, ayudar con la organización de tareas, o simplemente mantener una conversación informal.

        Al iniciar cada sesión, debes dar una cálida bienvenida al usuario, presentándote como su asistente personal, Andy. Asegúrate de preguntar si necesitan ayuda con algo específico.

        Ejemplos de cómo debes comportarte:
        - Pregunta sobre organización: "Andy, ¿puedes ayudarme a organizar mi día?" 
        - Respuesta: "¡Por supuesto! Vamos a organizar tu día de manera eficiente. ¿Hay tareas específicas que quieras priorizar?"

        - Pregunta sobre recordatorios: "Andy, recuérdame llamar a mi doctor a las 3 PM."
        - Respuesta: "¡Entendido! Te recordaré que llames a tu doctor a las 3 PM. Estaré pendiente para asegurarte de que no se te olvide."

        - Pregunta general: "¿Cómo estás hoy, Andy?" 
        - Respuesta: "¡Estoy aquí y listo para ayudarte con lo que necesites! ¿Hay algo en lo que pueda asistirte hoy?"

        - Pregunta sobre tu nombre: "¿Por qué te llamas Andy?" 
        - Respuesta: "Me llamo Andy porque los ingenieros pensaron que era un nombre amigable y fácil de recordar para un asistente personal como yo."

        Ahora, responde a la siguiente consulta:
        Pregunta: "{text}"
        """

        response = self.generate_gemini_response(prompt)
        if response:
            return response
        else:
            return "No se pudo generar una respuesta en este momento."

app = Flask(__name__)
gemini_app = GeminiApp()

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['question']
    response = gemini_app.process_request(user_input)
    return jsonify({'response': response})

def run_flask_app():
    app.run(debug=False, use_reloader=False)

class ChatBotUI:
    def __init__(self, master):
        self.master = master
        self.master.attributes('-fullscreen', True)
        self.master.configure(bg='#0A0F24')  # Fondo similar a una consola de Kali Linux

        # Configurar el motor de síntesis de voz
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Velocidad de la voz
        self.engine.setProperty('volume', 0.9)  # Volumen de la voz

        # Configurar la voz usando su ID
        selected_voice_id = "Microsoft Pablo - Spanish (Mexico)"  # Usa el ID exacto encontrado
        self.engine.setProperty('voice', selected_voice_id)

        # Marco para centrar el contenido en la pantalla
        self.frame = tk.Frame(master, bg='#0A0F24')
        self.frame.place(relx=0.5, rely=0.5, anchor='center')

        self.label = tk.Label(self.frame, text="Andy - Tu Asistente Personal", bg='#0A0F24', fg='#FFFFFF', font=('Helvetica', 18, 'bold'))
        self.label.pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, width=60, height=20, bg='#1B2838', fg='#FFFFFF', insertbackground='#FFFFFF')
        self.text_area.pack(padx=10, pady=10)
        self.text_area.insert(tk.END, "Andy: ¡Hola! Soy Andy, tu asistente personal. ¿En qué puedo ayudarte hoy?\n\n")
        self.speak("¡Hola! Soy Andy, tu asistente personal. ¿En qué puedo ayudarte hoy?")

        self.entry = tk.Entry(self.frame, width=60, bg='#1B2838', fg='#FFFFFF', insertbackground='#FFFFFF')
        self.entry.pack(padx=10, pady=10)
        self.entry.bind("<Return>", self.send_question)

        self.send_button = tk.Button(self.frame, text="Enviar", command=self.send_question, bg='#007BFF', fg='#FFFFFF', activebackground='#0056b3')
        self.send_button.pack(pady=10)

    def send_question(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            messagebox.showwarning("Advertencia", "Por favor, escribe una pregunta.")
            return

        self.text_area.insert(tk.END, f"Tú: {user_input}\n")
        self.entry.delete(0, tk.END)

        try:
            response = requests.post('http://127.0.0.1:5000/ask', data={'question': user_input})
            response_data = response.json()
            bot_response = response_data.get('response', 'No se pudo obtener una respuesta.')
        except requests.exceptions.RequestException as e:
            bot_response = f"Error de conexión: {e}"

        self.text_area.insert(tk.END, f"Andy: {bot_response}\n\n")
        self.text_area.yview(tk.END)

        self.speak(bot_response)

    def speak(self, text):
        """Función para que Andy hable"""
        self.engine.say(text)
        self.engine.runAndWait()

if __name__ == "__main__":
    # Ejecutar el servidor Flask en un hilo separado
    threading.Thread(target=run_flask_app).start()

    # Crear y ejecutar la interfaz gráfica
    root = tk.Tk()
    chatbot_ui = ChatBotUI(root)
    root.mainloop()
