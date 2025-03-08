import os
import pandas as pd
import logging
from datetime import datetime

#  Configuración de logs
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "data_preprocessor.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class DataPreprocessor:
    def __init__(self, df):
        self.df = df

    def clean_data(self):
        """Convierte las fechas a formato datetime y calcula los años operando, suspendido y reiniciado sin perder información relevante."""
        logging.info("🔹 Iniciando limpieza de datos...")

        try:
            #  Convertir RUC a string para evitar problemas de interpretación
            self.df["NUMERO_RUC"] = self.df["NUMERO_RUC"].astype(str)

            #  Crear nuevas columnas auxiliares para conservar valores "Sinreinicio" y "Vigente"
            self.df["ESTADO_REINICIO"] = self.df["FECHA_REINICIO_ACTIVIDADES"]
            self.df["ESTADO_SUSPENSION"] = self.df["FECHA_SUSPENSION_DEFINITIVA"]

            #  Identificar y almacenar los valores especiales antes de la conversión
            self.df.loc[self.df["FECHA_REINICIO_ACTIVIDADES"] == "Sinreinicio", "ESTADO_REINICIO"] = "Sinreinicio"
            self.df.loc[self.df["FECHA_SUSPENSION_DEFINITIVA"] == "Vigente", "ESTADO_SUSPENSION"] = "Vigente"

            #  Convertir las columnas de fecha a datetime (sin afectar las etiquetas)
            date_columns = ["FECHA_INICIO_ACTIVIDADES", "FECHA_SUSPENSION_DEFINITIVA", "FECHA_REINICIO_ACTIVIDADES"]
            for col in date_columns:
                self.df[col] = pd.to_datetime(self.df[col], errors="coerce")

            #  Calcular los años de operación, suspensión y reinicio
            hoy = datetime.now()

            def calcular_anios(fecha):
                if isinstance(fecha, datetime):  # Si es una fecha válida
                    return (hoy - fecha).days / 365
                return 0  # En caso de valores vacíos o NaT

            self.df["AÑOS_OPERANDO"] = self.df["FECHA_INICIO_ACTIVIDADES"].apply(calcular_anios)
            self.df["AÑOS_SUSPENDIDO"] = self.df["FECHA_SUSPENSION_DEFINITIVA"].apply(calcular_anios)
            self.df["AÑOS_REINICIADO"] = self.df["FECHA_REINICIO_ACTIVIDADES"].apply(calcular_anios)

            #  Convertir los valores a float para evitar errores en comparaciones
            self.df["AÑOS_OPERANDO"] = pd.to_numeric(self.df["AÑOS_OPERANDO"], errors="coerce").fillna(0)
            self.df["AÑOS_SUSPENDIDO"] = pd.to_numeric(self.df["AÑOS_SUSPENDIDO"], errors="coerce").fillna(0)
            self.df["AÑOS_REINICIADO"] = pd.to_numeric(self.df["AÑOS_REINICIADO"], errors="coerce").fillna(0)

            logging.info("Limpieza de datos completada correctamente.")

        except Exception as e:
            logging.error(f" Error durante la limpieza de datos: {e}")
            raise e

        return self.df

    def add_risk_variable(self):
        """Asigna un nivel de riesgo a cada empresa con base en las reglas proporcionadas."""

        def determinar_riesgo(row):
            try:
                anios_operando = float(row["AÑOS_OPERANDO"])
                anios_suspendido = float(row["AÑOS_SUSPENDIDO"])
                anios_reiniciado = float(row["AÑOS_REINICIADO"])
                estado = row["ESTADO_CONTRIBUYENTE"]
                obligado_contabilidad = row["OBLIGADO"] == "S"

                #  Nivel Super Bajo (0): Empresas activas sin suspensión ni reinicio
                if (
                        anios_operando > 0
                        and (pd.isna(row["ESTADO_REINICIO"]) or str(row["ESTADO_REINICIO"]).strip().lower() == "sinreinicio")
                        and ( pd.isna(row["ESTADO_SUSPENSION"]) or str(row["ESTADO_SUSPENSION"]).strip().lower() == "vigente")
                        and str(estado).strip().upper() == "ACTIVO"
                ):
                    return 0  # Super Bajo

                #  Nivel Bajo (1): Empresas con menos de 3 años operando o con suspensión corta
                if (
                    anios_operando < 3 and estado == "ACTIVO"
                    or (anios_suspendido < 1 and estado in ["ACTIVO"])
                    or (anios_operando < 3 and anios_suspendido < 1 and anios_reiniciado < 1 and estado in ["ACTIVO"])
                ):
                    return 1  # Bajo

                #  Nivel Medio (2): Empresas suspendidas entre 3 y 5 años, con actividad intermitente
                if (
                    3 < anios_operando <= 5
                    and estado in ["SUSPENDIDO", "PASIVO"]
                    and 3 < anios_suspendido <= 5
                    and (anios_reiniciado == 0 or anios_reiniciado < 2)
                ):
                    return 2  # Medio
                #  Nivel Alto (3): Empresas suspendidas más de 5 años, con historial de reinicios
                if (
                    4 <= anios_operando <= 7
                    and estado == "SUSPENDIDO"
                    and 5 <= anios_suspendido <= 10
                    and (anios_reiniciado == 0 or anios_reiniciado < 3)
                ):
                    return 3  # Alto

                #  Nivel Super Alto (4): Empresas con largo historial de suspensión y riesgo financiero
                if (
                    anios_operando > 8
                    and estado == "SUSPENDIDO"
                    and (anios_reiniciado == 0 or anios_reiniciado < 5)
                    and obligado_contabilidad
                ):
                    return 4  # Super Alto

                #  Si no cumple con ninguna condición, asignara riesgo medio
                return 2

            except ValueError as e:
                logging.warning(f" Error al determinar riesgo: {e}. Asignando nivel de riesgo medio por defecto.")
                return 2

        #  Aplicar la función a cada fila del DataFrame
        self.df["RIESGO"] = self.df.apply(determinar_riesgo, axis=1)

        #  Convertir la columna `RIESGO` en tipo entero para evitar errores en la Red Neuronal
        self.df["RIESGO"] = self.df["RIESGO"].astype(int)

        return self.df

