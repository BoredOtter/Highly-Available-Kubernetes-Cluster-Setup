import psycopg2
import time
import random
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Database connection parameters
DB_PARAMS = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'app'),
    'user': os.environ.get('DB_USER', 'app'),
    'password': os.environ.get('DB_PASSWORD', 'app'),
    'connect_timeout': 5
}

def create_table():
    """Create a table if it doesn't exist."""
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS test_table (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        age INT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    '''
    success = False
    while not success:
        success = execute_query(create_table_query, operation='Create Table')
        if not success:
            logging.warning("Create Table failed. Retrying in 1 second.")
            time.sleep(1)

def execute_query(query, params=None, operation=''):
    """Execute a database query."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        with conn.cursor() as cur:
            cur.execute(query, params)
            if operation.lower() == 'write':
                new_id = cur.fetchone()[0]
                conn.commit()
                logging.info(f"Inserted data with id {new_id}")
                return True  # Success
            elif operation.lower() == 'read':
                result = cur.fetchone()[0]
                conn.commit()
                logging.info(f"Total records in test_table: {result}")
                return result
            elif operation.lower() == 'create table':
                conn.commit()
                logging.info("Table created successfully.")
                return True
            else:
                conn.commit()
                return True
    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        logging.warning(f"{operation} failed: {e}.")
        return False  # Failure
    except Exception as e:
        logging.error(f"Unexpected error during {operation}: {e}")
        return False  # Failure
    finally:
        if conn:
            conn.close()

def write_data(name, age):
    """Write data to the database, retrying every 0.5 seconds on failure."""
    insert_query = '''
    INSERT INTO test_table (name, age)
    VALUES (%s, %s)
    RETURNING id;
    '''
    success = False
    start_time = time.time()
    retries = 0 
    while not success:
        success = execute_query(insert_query, params=(name, age), operation='Write')
        if not success:
            retries += 1
            logging.warning(f"Data insert failed for ({name}, {age}). Will retry in 0.5 seconds.")
            time.sleep(0.5)
        else:
            total_time = time.time() - start_time
            logging.info(f"Data insert succeeded after {retries} retries, total time: {total_time:.2f} seconds.")
    return success

def read_data():
    """Read data from the database, retrying every 1 second on failure."""
    select_query = 'SELECT COUNT(*) FROM test_table;'
    while True:
        result = execute_query(select_query, operation='Read')
        if result is not False:
            return result
        else:
            logging.warning("Read operation failed. Retrying in 1 second.")
            time.sleep(1)

def main():
    try:
        create_table()

        # Get the current number of records in the table
        initial_records = read_data()
        if initial_records is None:
            initial_records = 0

        total_attempted_inserts = initial_records  # Initialize with existing records

        logging.info(f"Starting with {initial_records} existing records.")

        while True:
            # Generate data
            name = f"User_{random.randint(1, 1000)}"
            age = random.randint(18, 70)
            total_attempted_inserts += 1

            # Write data
            write_data(name, age)

            # Read data
            total_records = read_data()
            if total_records is not None:
                logging.info(f"Total attempted inserts: {total_attempted_inserts}, Total records in database: {total_records}")

                # Check for discrepancies
                if total_records < total_attempted_inserts:
                    missing = total_attempted_inserts - total_records
                    logging.warning(f"{missing} records missing in the database.")
                elif total_records > total_attempted_inserts:
                    logging.error("Total records exceed total attempted inserts, which should not happen.")

            time.sleep(1)  # Delay between operations
    except KeyboardInterrupt:
        logging.info("Application interrupted by user.")
    except Exception as e:
        logging.error(f"Application error: {e}")

if __name__ == "__main__":
    main()
