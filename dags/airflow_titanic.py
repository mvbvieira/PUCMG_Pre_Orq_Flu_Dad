from airflow.decorators import dag, task
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql import functions as f

TARGET_DIR = "/opt/storage_data/data/"
TARGET_FILE = "titanic.csv"
SOURCE_FILE = "https://raw.githubusercontent.com/neylsoncrepalde/titanic_data_with_semicolon/main/titanic.csv"


default_args = {
    'owner': "Marcos Vieira",
    "depends_on_past": False,
    'start_date': datetime (2022, 10, 9)
}

@dag(default_args=default_args, schedule_interval=None, catchup=False, tags=["Titanic"])

def airflow_titanic():
    spark = SparkSession.builder.getOrCreate()

    also_run_this = BashOperator(
        task_id='also_run_this',
        bash_command="curl -L -o" + TARGET_DIR + TARGET_FILE + " " + SOURCE_FILE
    )
    
    @task
    def aggregation_dataframe(target_dir, target_file):
        df = (
            spark
            .read
            .format("csv")
            .option("delimiter", ";")
            .option("header", True)
            .load(target_dir + target_file)
        )

        (
            df
            .groupBy('Sex', 'Pclass')
            .agg(
                f.count('Sex').alias('Contagem')
            ).show()
        )

        (
            df
            .groupBy('Sex', 'Pclass')
            .agg(
                f.mean('Fare').alias('Tarifa')
            ).show()
        )

        (
            df
            .withColumn("soma", f.col("SibSp") + f.col("Parch"))
            .groupBy('Sex', 'Pclass')
            .agg(
                f.count('soma').alias('SibSp + Parch')
            ).show()
        )

        df_aggregation = (
            df
            .withColumn("soma", f.col("SibSp") + f.col("Parch"))
            .groupBy('Sex', 'Pclass')
            .agg(
                f.count('Sex').alias('Contagem'),
                f.mean('Fare').alias('Tarifa'),
                f.count('soma').alias('SibSp + Parch')
            )
        )

        df_aggregation.show()

        (
            df_aggregation
            .write
            .mode("overwrite")
            .format("csv")
            .option("header", True)
            .option("delimiter", ";")
            .save(TARGET_DIR + "tabela_unica.csv")
        )

    execute_airflow_titanic_2 = TriggerDagRunOperator(
        task_id="execute_airflow_titanic_2",
        trigger_dag_id="airflow_titanic_2"
    )

    inicio = DummyOperator(task_id="inicio")
    fim = DummyOperator(task_id="fim")

    inicio >> also_run_this >> aggregation_dataframe(TARGET_DIR, TARGET_FILE) >> execute_airflow_titanic_2 >> fim


execucao = airflow_titanic()