
import MySQLdb

def get_db():
    db = MySQLdb.connect("localhost", "luegendetektor", "fake123", "luegendetektor")
    db.set_character_set('utf8')
    cursor = db.cursor()
    cursor.execute("SELECT VERSION()")
    row = cursor.fetchone()
    print "server version:", row[0]

    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    return db