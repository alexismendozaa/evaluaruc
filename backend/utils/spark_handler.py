from pyspark.sql import SparkSession

class SparkHandler:
    """
    Clase para manejar la inicialización de Apache Spark y convertir DataFrames de Pandas a Spark.
    """
    def __init__(self):
        """
        Inicializa una sesión de Spark con un nombre específico.
        """
        self.spark = SparkSession.builder.appName("EvalúaRUC").getOrCreate()

    def to_spark_dataframe(self, pandas_df):
        """
        Convierte un DataFrame de Pandas a un DataFrame de Spark.

        :param pandas_df: DataFrame de Pandas
        :return: DataFrame de Spark
        """
        return self.spark.createDataFrame(pandas_df)
