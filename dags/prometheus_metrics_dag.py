from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import time
import random

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Pushgateway URL (Kubernetes service)
PUSHGATEWAY_URL = "http://pushgateway-prometheus-pushgateway.airflow-3.svc.cluster.local:9091"

def push_metrics(job_name, metrics_dict):
    """Push metrics to Pushgateway"""
    metrics_lines = []
    
    for metric_name, metric_value in metrics_dict.items():
        # Format: metric_name value
        metrics_lines.append(f"{metric_name} {metric_value}")
    
    metrics_data = "\n".join(metrics_lines)
    url = f"{PUSHGATEWAY_URL}/metrics/job/{job_name}"
    
    try:
        response = requests.post(url, data=metrics_data)
        response.raise_for_status()
        print(f"✅ Successfully pushed metrics to {url}")
        print(f"📊 Metrics: {metrics_dict}")
    except Exception as e:
        print(f"❌ Failed to push metrics: {e}")
        raise

def data_processing_task(**context):
    """Simulate data processing and track metrics"""
    print("=" * 50)
    print("🔄 Starting Data Processing Task")
    print("=" * 50)
    
    start_time = time.time()
    
    # Simulate processing work
    records_processed = random.randint(1000, 5000)
    records_failed = random.randint(0, 50)
    
    print(f"Processing {records_processed} records...")
    time.sleep(random.uniform(2, 5))
    
    # Simulate occasional failures (10% chance)
    success = random.random() > 0.1
    
    duration = time.time() - start_time
    
    # Prepare metrics for Pushgateway
    metrics = {
        'airflow_data_processing_duration_seconds': round(duration, 2),
        'airflow_data_processing_records_total': records_processed,
        'airflow_data_processing_records_failed': records_failed,
        'airflow_data_processing_success': 1 if success else 0,
        'airflow_data_processing_last_run_timestamp': int(time.time()),
    }
    
    # Push to Pushgateway
    push_metrics(job_name='data_processing_dag', metrics_dict=metrics)
    
    print(f"✅ Processed {records_processed} records in {duration:.2f}s")
    print(f"📉 Failed: {records_failed} records")
    
    if not success:
        raise Exception("❌ Data processing failed!")
    
    return records_processed

def etl_pipeline_task(**context):
    """Simulate ETL pipeline and track metrics"""
    print("=" * 50)
    print("🔄 Starting ETL Pipeline")
    print("=" * 50)
    
    start_time = time.time()
    
    # Extract phase
    print("📥 Extract phase...")
    extract_records = random.randint(5000, 10000)
    time.sleep(1)
    
    # Transform phase
    print("⚙️  Transform phase...")
    transform_records = int(extract_records * random.uniform(0.92, 0.98))
    time.sleep(1.5)
    
    # Load phase
    print("📤 Load phase...")
    load_records = transform_records
    time.sleep(1)
    
    duration = time.time() - start_time
    data_loss_percent = ((extract_records - load_records) / extract_records) * 100
    
    # Prepare metrics
    metrics = {
        'airflow_etl_extract_records': extract_records,
        'airflow_etl_transform_records': transform_records,
        'airflow_etl_load_records': load_records,
        'airflow_etl_data_loss_percent': round(data_loss_percent, 2),
        'airflow_etl_duration_seconds': round(duration, 2),
        'airflow_etl_last_run_timestamp': int(time.time()),
    }
    
    # Push to Pushgateway
    push_metrics(job_name='etl_pipeline', metrics_dict=metrics)
    
    print(f"✅ ETL Complete:")
    print(f"   Extract: {extract_records}")
    print(f"   Transform: {transform_records}")
    print(f"   Load: {load_records}")
    print(f"   Data Loss: {data_loss_percent:.2f}%")
    print(f"   Duration: {duration:.2f}s")
    
    return load_records

def report_generation_task(**context):
    """Simulate report generation and track metrics"""
    print("=" * 50)
    print("📊 Starting Report Generation")
    print("=" * 50)
    
    start_time = time.time()
    
    # Generate reports
    reports_generated = random.randint(5, 20)
    report_size_mb = random.randint(10, 100)
    
    print(f"Generating {reports_generated} reports...")
    time.sleep(random.uniform(1, 3))
    
    duration = time.time() - start_time
    
    # Prepare metrics
    metrics = {
        'airflow_reports_generated': reports_generated,
        'airflow_reports_size_mb': report_size_mb,
        'airflow_reports_duration_seconds': round(duration, 2),
        'airflow_reports_last_run_timestamp': int(time.time()),
    }
    
    # Push to Pushgateway
    push_metrics(job_name='report_generation', metrics_dict=metrics)
    
    print(f"✅ Generated {reports_generated} reports ({report_size_mb}MB total)")
    print(f"   Duration: {duration:.2f}s")
    
    return reports_generated

# Define the DAG
with DAG(
    'prometheus_metrics_demo',
    default_args=default_args,
    description='Demo DAG pushing metrics to Prometheus Pushgateway',
    schedule_interval='*/5 * * * *',  # Every 5 minutes
    catchup=False,
    tags=['monitoring', 'prometheus', 'demo'],
) as dag:
    
    # Task 1: Data Processing
    task_data_processing = PythonOperator(
        task_id='data_processing',
        python_callable=data_processing_task,
        provide_context=True,
    )
    
    # Task 2: ETL Pipeline
    task_etl = PythonOperator(
        task_id='etl_pipeline',
        python_callable=etl_pipeline_task,
        provide_context=True,
    )
    
    # Task 3: Report Generation
    task_reports = PythonOperator(
        task_id='report_generation',
        python_callable=report_generation_task,
        provide_context=True,
    )
    
    # Define task dependencies
    task_data_processing >> task_etl >> task_reports