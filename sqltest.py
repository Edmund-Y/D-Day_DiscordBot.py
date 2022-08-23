import mariadb, json, os
import matplotlib.pyplot as plt

with open(os.path.join(os.path.dirname(__file__), 'apikey.json')) as f:
    secrets = json.loads(f.read())

try:
    conn = mariadb.connect(
        user=secrets.get('sql_usr'),
        password=secrets.get('sql_pw'),
        host=secrets.get('sql_addr'),
        port=secrets.get('sql_port'),
        database=secrets.get('sql_usr')
    )
    cur = conn.cursor()
    cur.execute("""SELECT playdate, dstats, COUNT(*) FROM test_attendances GROUP BY playdate, dstats;""")
    rsu = cur.fetchall()
    xdayone = []
    xdaytwo = []
    xdaythr = []
    yvalueone = []
    yvaluetwo = []
    yvaluethr = []
    yname = []
    for a, b in enumerate(rsu):
        if a%3 == 0:
            xdayone.append(b[0])
            yvalueone.append(b[2])
        elif a%3 == 1:
            xdaytwo.append(b[0])
            yvaluetwo.append(b[2])
        elif a%3 == 2:
            xdaythr.append(b[0])
            yvaluethr.append(b[2])
        yname.append(b[1])
    print(dict.fromkeys(yname))
    print(f'{xdayone} / {yvalueone}')
    print(f'{xdaytwo} / {yvaluetwo}')
    print(f'{xdaythr} / {yvaluethr}')

    plt.plot(xdayone, yvalueone, 'r')
    plt.plot(xdaytwo, yvaluetwo, 'g')
    plt.plot(xdaythr, yvaluethr, 'b')
    plt.xlabel('day')
    plt.ylabel('player')
    plt.show()

except mariadb.Error as e:
    print(f'Error connecting to MariaDB Platform: {e}')
finally:
    cur.close()
    conn.close()