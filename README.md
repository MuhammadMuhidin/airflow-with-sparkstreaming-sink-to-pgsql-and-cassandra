# Airflow + Spark Streaming → PostgreSQL & Cassandra Sink

Repositori ini menyediakan pipeline data real-time yang memanfaatkan Apache Airflow untuk orkestrasi, Apache Spark Streaming untuk pemrosesan streaming, serta dua _sink_ berbeda: PostgreSQL untuk data tabular dan Cassandra untuk skala tinggi.

## 🚀 Fitur Utama

- Orkestrasi DAG di Airflow untuk kontrol aliran data.
- Spark Streaming untuk konsumsi data (misalnya dari Kafka, API, atau file) secara real-time.
- Penyimpanan data hasil proses ke:
  - PostgreSQL (relational, ACID-safe)
  - Cassandra (NoSQL, skalabilitas horizontal)
- Konfigurasi Docker-Compose untuk menjalankan semua komponen secara lokal.

## 📦 Teknologi

- **Apache Airflow** – menjadwalkan dan mengatur workflow.
- **Apache Spark Streaming** – pemrosesan data real-time.
- **PostgreSQL** – data warehouse relasional.
- **Apache Cassandra** – penyimpanan data terdistribusi.
- **Docker & Docker Compose** – lingkungan containerized terpadu.
- (Opsional) **Kafka / REST API** – sumber data streaming.

## 🏗️ Struktur Projek

## ⚙️ Setup & Instalasi

1. **Clone repo**
   ```bash
   git clone https://github.com/MuhammadMuhidin/airflow-with-sparkstreaming-sink-to-pgsql-and-cassandra.git
   cd airflow-with-sparkstreaming-sink-to-pgsql-and-cassandra

2. Jalankan Docker Compose

docker-compose up --build -d

Layanan otomatis dijalankan:

Airflow (web, scheduler, worker)

Spark master & worker

PostgreSQL

Cassandra



3. Persiapkan skema database

PostgreSQL: jalankan skrip SQL (jika tersedia) untuk membuat tabel.

Cassandra: menggunakan cqlsh untuk mendefinisikan keyspace dan tabel.



4. Konfigurasi DAG Airflow

Buka web UI: http://localhost:8080 (default login airflow/airflow atau sesuaikan .env).

Modifikasi koneksi & variabel jika perlu (via Admin → Connections/Variables).



5. Pastikan konektivitas Spark ke DB

Tambahkan driver JDBC PostgreSQL di spark/jars/ jika belum ada.

Pastikan spark_stream.py memiliki URL/kredensial DB yang benar.




▶️ Cara Menjalankan

1. Trigger DAG
Dari UI Airflow, aktifkan dan jalankan DAG (misalnya spark_stream_dag).
Logger akan menampilkan status tugas.


2. Streaming Data
Jalankan Spark Streaming job:

spark-submit \
  --master spark://spark-master:7077 \
  --jars /path/to/postgresql.jar \
  spark/spark_stream.py


3. Verifikasi Output

PostgreSQL: cek tabel menggunakan psql atau GUI.

Cassandra: gunakan cqlsh, misalnya:

SELECT * FROM your_keyspace.your_table LIMIT 10;




🧩 Kustomisasi

Sumber data: tambahkan Kafka / API / file sebagai input Spark.

Sink lainnya: tambahkan Elasticsearch, Hive, dll dengan modifikasi script.

Skalabilitas: sesuaikan jumlah worker, memori, konfigurasi Cassandra untuk produksi.


🛠️ Troubleshooting

Cek log Airflow (docker logs <airflow-worker>).

Cek UI Spark (http://localhost:4040) untuk detail streaming.

Pastikan driver JDBC berada di spark/jars/.

Periksa koneksi Airflow-DB (Admin → Connections).


📄 License

MIT License – Bebas digunakan dan dimodifikasi.


---

🎯 Ringkasan

Komponen	Teknologi

Workflow	Airflow DAG + scheduler
Streaming engine	Apache Spark Streaming
Sumber Data	Kafka / HTTP API / File
Relational sink	PostgreSQL via JDBC
NoSQL sink	Cassandra via Spark connector
Lingkungan	Docker Compose


Pipeline ini ideal untuk demo end-to-end aliran data real-time dengan dual storage dan reproducible environment. Dokumentasi ini dapat dikembangkan sesuai kebutuhan proyek Anda: misalnya menambahkan validasi data, monitoring (Prometheus/Grafana), atau deployment ke Kubernetes/sistem klaster.
