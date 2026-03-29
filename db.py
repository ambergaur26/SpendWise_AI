import psycopg2

# Replace with your Neon/Postgres URL
DB_URL = "postgresql://neondb_owner:npg_fwju3J4CxFSz@ep-calm-sun-a1inmdjg-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

def get_connection():
    conn = psycopg2.connect(DB_URL)
    return conn