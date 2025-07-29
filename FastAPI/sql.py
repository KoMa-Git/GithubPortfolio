import psycopg2
import os


DBNAME = os.environ['DATABASE']
USER = os.environ['USER']
PASSWORD = os.environ['PASSWORD']
HOST = os.environ['HOST']

def build_up():
    pass

def read_data():
    result = {}
    try:
        with psycopg2.connect(database=DBNAME,
                        user=USER,
                        password=PASSWORD,
                        host=HOST) as conn:
            print('Successfully connected to PostgreSQL on render.com')
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM employee")
                row = cur.fetchone()

                while row is not None:
                    result[row[0]] = { "name" : row[1], "age" : row[2], "position" : row[3]}
                    row = cur.fetchone()
                
                return result

    except (psycopg2.DatabaseError, Exception) as error:
            return {"Error": error}
    
def insert_data(name,age,position):
    
    sql = """INSERT INTO employee(full_name, age, position)
             VALUES(%s, %s, %s) RETURNING employee_id;"""

    employee_id = None

    try:
        with psycopg2.connect(database=DBNAME,
                        user=USER,
                        password=PASSWORD,
                        host=HOST) as conn:
            
            with conn.cursor() as cur:
                cur.execute(sql, (name,age,position,))
                
                rows = cur.fetchone()
                if rows:
                    employee_id = rows[0]
                
                conn.commit()
                
                return {"Info" : f"Data successfully inserted with following id: {employee_id}"}

    except (psycopg2.DatabaseError, Exception) as error:
            return {"Error": error}

def delete_data(id):
    
    check = 'SELECT employee_id FROM employee'
    sql = 'DELETE FROM employee WHERE employee_id = %s'
     
    try:
        with psycopg2.connect(database=DBNAME,
                        user=USER,
                        password=PASSWORD,
                        host=HOST) as conn:
            with conn.cursor() as cur:
                cur.execute(check)
                existing_ids = cur.fetchall()
                id = (id,)
                if id in existing_ids:
                    cur.execute(sql, (id,))
            
                    conn.commit()

                    return {"Info":f"Employee with id {id[0]} successfully deleted from database"}
                else:
                    return {"Error":f"Employee with id {id[0]} not existing in the database"}

    except (Exception, psycopg2.DatabaseError) as error:
        return{"Error": error}
        


