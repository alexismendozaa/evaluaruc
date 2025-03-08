import os
import pandas as pd
import logging

# Configuración de logs
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "data_loader.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class DataLoader:
    def __init__(self, folder_path="database/"):
        self.folder_path = folder_path

    def load_data(self):
        if not os.path.exists(self.folder_path):
            logging.error(f"❌ Carpeta de datos no encontrada: {self.folder_path}")
            raise FileNotFoundError(f"No se encontró la carpeta: {self.folder_path}")

        all_files = [f for f in os.listdir(self.folder_path) if f.endswith(".xlsx")]
        if not all_files:
            logging.warning("⚠️ No se encontraron archivos Excel en la carpeta de datos.")
            return pd.DataFrame()

        all_dfs = []
        for file in all_files:
            file_path = os.path.join(self.folder_path, file)
            try:
                df = pd.read_excel(file_path, dtype={"NUMERO_RUC": str})
                df["PROVINCIA"] = file.replace(".xlsx", "")
                all_dfs.append(df)
                logging.info(f"📂 Archivo cargado correctamente: {file_path}")
            except Exception as e:
                logging.error(f"❌ Error cargando {file_path}: {e}")

        return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
