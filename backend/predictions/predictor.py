import joblib
import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

class Predictor:
    def __init__(self, df, model_dir, scaler_path, graphics_dir):
        """
        Inicializa la clase Predictor.

        :param df: DataFrame con los datos de empresas.
        :param model_dir: Ruta donde están guardados los modelos entrenados.
        :param scaler_path: Ruta del archivo `scaler.pkl` para normalización.
        :param graphics_dir: Ruta donde se guardan los gráficos.
        """
        self.df = df
        self.model_dir = model_dir
        self.scaler = joblib.load(scaler_path)  # Cargar scaler
        self.graphics_dir = graphics_dir

        # Cargar el modelo de Red Neuronal
        self.nn_model_path = os.path.join(model_dir, "neural_network.h5")
        if os.path.exists(self.nn_model_path):
            self.nn_model = load_model(self.nn_model_path)
        else:
            raise FileNotFoundError(f"❌ Modelo de Red Neuronal no encontrado en {self.nn_model_path}")

    def predict(self, ruc):
        """
        Predice el nivel de riesgo de una empresa usando la Red Neuronal.

        :param ruc: Número de RUC a evaluar.
        :return: Resultado de la predicción y datos adicionales.
        """
        empresa = self.df[self.df["NUMERO_RUC"] == str(ruc)]

        if empresa.empty:
            return {"error": f"⚠️ RUC {ruc} no encontrado en la base de datos."}

        # Extraer características y normalizarlas
        X_input = empresa[["AÑOS_OPERANDO", "AÑOS_SUSPENDIDO", "AÑOS_REINICIADO"]].values
        X_scaled = self.scaler.transform(X_input)

        # Predicción
        prediction = self.nn_model.predict(X_scaled)
        predicted_class = np.argmax(prediction, axis=1)[0]

        # Mapeo de los 5 niveles de riesgo
        risk_levels = {
            0: "Super Bajo",
            1: "Bajo",
            2: "Medio",
            3: "Alto",
            4: "Super Alto"
        }
        risk_level = risk_levels.get(predicted_class, "Desconocido")

        # Obtener la razón social de la empresa
        razon_social = empresa["RAZON_SOCIAL"].values[0] if "RAZON_SOCIAL" in empresa.columns else "No disponible"

        # Cargar la gráfica de comparación de modelos
        graph_path = os.path.join(self.graphics_dir, "model_comparison.png")

        return {
            "ruc": ruc,
            "razon_social": razon_social,
            "riesgo": risk_level,
            "grafica_modelos": graph_path,
            "fechas": empresa[["FECHA_INICIO_ACTIVIDADES", "ESTADO_REINICIO", "ESTADO_SUSPENSION"]].to_dict("records")
        }

# 🔹 Simulación de `main.py` en `Predictor.py`
if __name__ == "__main__":
    # Definir rutas necesarias
    model_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    scaler_path = os.path.join(model_dir, "scaler.pkl")
    graphics_dir = os.path.join(os.path.dirname(__file__), "..", "graphics")

    # ✅ Usar la ruta absoluta corregida
    database_path = os.path.join(os.path.dirname(__file__), "..", "database", "datos_procesados.csv")
    database_path = os.path.abspath(database_path)  # Convertir a ruta absoluta

    # Cargar la base de datos con los RUCs disponibles
    df_clean = pd.read_csv(database_path, dtype={"NUMERO_RUC": str})

    # Inicializar predictor
    predictor = Predictor(df_clean, model_dir, scaler_path, graphics_dir)

    print("\n🔮 Predicción usando la Red Neuronal:")

    while True:
        # Pedir RUC al usuario
        ruc_prueba = input("\n🔍 Ingresa un RUC para predecir (o escribe 'salir' para terminar): ").strip()

        # Verificar si el usuario quiere salir
        if ruc_prueba.lower() == "salir":
            print("✅ Saliendo del programa.")
            break

        # Hacer la predicción
        resultado = predictor.predict(ruc_prueba)

        # Verificar si hubo error (RUC no encontrado)
        if "error" in resultado:
            print(resultado["error"])
            continue

        # Mostrar el resultado en consola tal como lo hacía `main.py`
        print("\n🔍 Predicción del modelo de Red Neuronal:")
        print(f"📌 RUC: {resultado['ruc']}")
        print(f"🏢 Razón Social: {resultado['razon_social']}")
        print(f"📊 Nivel de Riesgo: {resultado['riesgo']}")
        print(f"📅 Fechas Asociadas: {resultado['fechas']}")
        print(f"📈 Gráfica Comparativa de Modelos: {resultado['grafica_modelos']}")
