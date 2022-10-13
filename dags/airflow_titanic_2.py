from airflow.decorators import dag, task
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql import functions as f

TARGET_DIR = "/opt/storage_data/data/"


default_args = {
    'owner': "Marcos Vieira",
    "depends_on_past": False,
    'start_date': datetime (2022, 10, 9)
}

@dag(default_args=default_args, schedule_interval="@once", catchup=False, tags=["Titanic"])

def airflow_titanic_2():
    spark = SparkSession.builder.getOrCreate()
    
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

        df_aggregation = (
            df
            .groupBy('Contagem', 'Tarifa', 'SibSp + Parch')
            .agg(
                f.mean('Contagem').alias('Contagem'),
                f.mean('Tarifa').alias('Tarifa'),
                f.mean('SibSp + Parch').alias('SibSp + Parch')
            )
        )

        df_aggregation.show()

    inicio = DummyOperator(task_id="inicio")
    fim = DummyOperator(task_id="fim")

    inicio >> aggregation_dataframe(TARGET_DIR, "tabela_unica.csv") >> fim


execucao = airflow_titanic_2()