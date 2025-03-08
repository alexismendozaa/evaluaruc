import os
import logging
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from processing.data_loader import DataLoader
from processing.data_preprocessor import DataPreprocessor
from models.model_trainer import ModelTrainer
from models.model_evaluator import ModelEvaluator
from models.model_selector import ModelSelector
from models.neural_network import NeuralNetworkTrainer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

#  Configuración de carpetas dentro de backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATABASE_DIR = os.path.join(BASE_DIR, "database")
GRAPHICS_DIR = os.path.join(BASE_DIR, "graphics")

# Crear directorios si no existen
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(GRAPHICS_DIR, exist_ok=True)

#  Configuración de logs
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "main.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info(" Iniciando el pipeline de procesamiento y entrenamiento...")
print(" Iniciando el pipeline de procesamiento y entrenamiento...")

# Cargar datos
data_loader = DataLoader(folder_path=DATABASE_DIR)
df_pandas = data_loader.load_data()

if df_pandas.empty:
    logging.error(" No se encontraron datos en la carpeta `database/`. Deteniendo ejecución.")
    print(" No se encontraron datos en `database/`. Deteniendo ejecución.")
    exit(1)

logging.info(f" Datos cargados correctamente. Total registros: {len(df_pandas)}")
print(f" Datos cargados correctamente. Total registros: {len(df_pandas)}")

# Preprocesamiento de datos
preprocessor = DataPreprocessor(df_pandas)
df_clean = preprocessor.clean_data()
df_clean = preprocessor.add_risk_variable()

# Guardar datos preprocesados
clean_data_path = os.path.join(DATABASE_DIR, "datos_procesados.csv")
df_clean.to_csv(clean_data_path, index=False)
logging.info(f" Datos limpios guardados en: {clean_data_path}")
print(f" Datos limpios guardados en: {clean_data_path}")

# 4Preparar datos para entrenamiento
X = df_clean[["AÑOS_OPERANDO", "AÑOS_SUSPENDIDO", "AÑOS_REINICIADO"]]
y = df_clean["RIESGO"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5️Normalizar características
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Guardar scaler
scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")
joblib.dump(scaler, scaler_path)

# Entrenar modelos tradicionales
trainer = ModelTrainer(X_train_scaled, y_train, MODEL_DIR)
trained_models = trainer.train_models()

# Validar si los modelos fueron entrenados correctamente
if not trained_models:
    logging.error("❌ No se entrenaron modelos correctamente. Deteniendo ejecución.")
    print("❌ No se entrenaron modelos correctamente. Revisa el proceso.")
    exit(1)

# Guardar modelos entrenados
for model_name, model in trained_models.items():
    model_filename = os.path.join(MODEL_DIR, f"{model_name}.pkl")
    joblib.dump(model, model_filename)
    print(f" Modelo {model_name} guardado en {model_filename}")

# Evaluación de modelos
metrics = {}
for model_name, model in trained_models.items():
    print(f"\n📊 Evaluando {model_name}...")
    metrics[model_name] = ModelEvaluator.evaluate(model, X_test_scaled, y_test)

# Mostrar métricas detalladas por modelo
for model_name, model_metrics in metrics.items():
    print(f"\n📊 Resultados detallados para {model_name}:")
    print(pd.DataFrame(model_metrics["category_metrics"]).T)

# Seleccionar el mejor modelo
best_model_name = ModelSelector.select_best_model(metrics)
print(f"\n Mejor modelo seleccionado: {best_model_name}")

# 🔹 **Guardar métricas de modelos en CSV**
metrics_csv_path = os.path.join(GRAPHICS_DIR, "metrics_comparison.csv")
metrics_df = pd.DataFrame(metrics).T
metrics_df.to_csv(metrics_csv_path)

# Generación de gráficos comparativos
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle("Comparación de Modelos de Machine Learning", fontsize=16)

#  Accuracy
axes[0, 0].bar(metrics_df.index, metrics_df["accuracy"], color="blue")
axes[0, 0].set_title("Accuracy")

#  Precision
axes[0, 1].bar(metrics_df.index, metrics_df["precision"], color="green")
axes[0, 1].set_title("Precision")

#  Recall
axes[0, 2].bar(metrics_df.index, metrics_df["recall"], color="red")
axes[0, 2].set_title("Recall")

#  F1 Score
axes[1, 0].bar(metrics_df.index, metrics_df["f1_score"], color="purple")
axes[1, 0].set_title("F1 Score")

#  MSE (Error Cuadrático Medio)
axes[1, 1].bar(metrics_df.index, metrics_df["mse"], color="orange")
axes[1, 1].set_title("Mean Squared Error (MSE)")

#  MAE (Error Absoluto Medio)
axes[1, 2].bar(metrics_df.index, metrics_df["mae"], color="brown")
axes[1, 2].set_title("Mean Absolute Error (MAE)")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(os.path.join(GRAPHICS_DIR, "model_comparison.png"))
plt.show()

logging.info(" Modelos evaluados y gráfico generado.")
print(" Modelos evaluados y gráfico generado.")

# Gráficos de precisión por categoría de riesgo
for model_name, model_metrics in metrics.items():
    print(f"\n📊 Generando gráfico de métricas por categoría para {model_name}...")
    ModelEvaluator.plot_category_metrics(model_metrics, model_name)

# 🔹 **Mostrar gráfico de MSE y MAE por modelo**
print("\n Generando gráfico de MSE y MAE por modelo...")
ModelEvaluator.plot_error_metrics(metrics)

# Entrenamiento de Red Neuronal
print("\n🧠 Entrenando Red Neuronal...")
nn_trainer = NeuralNetworkTrainer(input_dim=X_train_scaled.shape[1], model_dir=MODEL_DIR)
nn_trainer.train(X_train_scaled, y_train, X_test_scaled, y_test)

logging.info("Entrenamiento de Red Neuronal completado.")
print(" Entrenamiento de Red Neuronal completado.")

print("\n Proceso completado con éxito.")
