import psycopg2 as dbTool

def executeReadQuery(query, conn):
    cur = conn.cursor()
    cur.execute(query)
    response = cur.fetchall()
    cur.close()
    return response
   