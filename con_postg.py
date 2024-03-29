 

import psycopg2
import os

class DB():
    """class manage postgresql database"""


    def __init__(self):
        #self.user_db = {'host':os.environ['HOST'],
        #    'database':os.environ['DATABASE'],
        #    'user': os.environ['USER'],
        #    'password':os.environ['PASSWORD']}

        self.herokuDB = os.environ['DATABASE_URL']




    def start(self):
        xconnect = psycopg2.connect(self.herokuDB)
        cur = xconnect.cursor()


        try:
            cur.execute("""create table Match (
                id_match serial primary key,
                status_code integer,
                acuracy varchar(10),
                private varchar(50),
                public varchar(50),
                amount float8,
                assets integer
                );""")
            xconnect.commit()
            cur.execute("""create table Error (
                id_err serial  primary key,
                status_code integer,
                private varchar(50),
                public varchar(50),
                message text
                );""")
            xconnect.commit()
            cur.execute("""create table Statistics (
                id_session  serial primary key ,
                match integer ,
                not_found integer,
                error integer,
                criticalerror integer
                );""")

            xconnect.commit()
            xconnect.close()

            return True

        except psycopg2.errors.DuplicateTable:
            return True
        except Exception as err:
            xconnect.close()
            return (False, err)


    def added_match(self, status_code, acuracy, private, public, amount = 0, assets = 0):
        """method for insert data into the tables"""

        xconnect = psycopg2.connect(self.herokuDB)




        cur = xconnect.cursor()


        match = """INSERT INTO match(status_code, acuracy, private, public, amount, assets) VALUES (%s,%s,%s,%s,%s,%s);"""
        insert = (status_code, acuracy, private, public, amount, assets)
        clio = cur.execute(match, insert)
        xconnect.commit()
        xconnect.close()
        return clio

    def added_error(self, status_code, message , private = 'not have', public = 'not have' ):
        """method for save a logs of errors"""
        xconnect = psycopg2.connect(self.herokuDB)
        cur = xconnect.cursor()
        try:
            match = """insert into Error (status_code,  private, public, message) values (%s,%s,%s,%s);"""
            insert =  (status_code,  private, public, message)
            cur.execute(match, insert)
            xconnect.commit()
            xconnect.close()
            return True
        except Exception as err:
            xconnect.close()
            return False





    def added_std(self, upgrade, match = 0, not_found = 0,error = 0, critical_error = 0 ):
        """method for save sttistics info and make reports"""

        xconnect = psycopg2.connect(self.herokuDB )




        cur = xconnect.cursor()

        try:
            if upgrade == False:
                cur.execute("""insert into Statistics (match, not_found, error, criticalerror) values (%s,%s,%s,%s); """, (match, not_found,error,critical_error))

                xconnect.commit()
                xconnect.close()
            elif upgrade == True:
                cur.execute("""select id_session from Statistics ORDER BY id_session DESC LIMIT 1;""")
                col = cur.fetchone()
                print(col)
                cur.execute("""update Statistics SET match = %s, not_found = %s,error = %s, criticalerror = %s  WHERE id_session = %s;""", (match,not_found,error, critical_error, col))


                xconnect.commit()
                xconnect.close()
            return True
        except Exception as err:
            xconnect.close()
            return (False, err)

    def getter_report(self):
        xconnect = psycopg2.connect(self.herokuDB )
        cur = xconnect.cursor()
        list_report = []
        try:
            cur.execute("""select  SUM (match) AS total_match from Statistics """)

            list_report.append(cur.fetchone()[0])


            cur.execute("""select SUM (not_found) as nt from Statistics""")
            list_report.append(cur.fetchone()[0])


            cur.execute("""select SUM (error) as error from Statistics""")
            list_report.append(cur.fetchone()[0])

            cur.execute("""select SUM (criticalerror) as cerror from Statistics""")
            list_report.append(cur.fetchone()[0])

            xconnect.close()
            return (True, list_report)

        except Exception as err:
            xconnect.close()
            return(False , err)

    def getter_match(self):
        xconnect = psycopg2.connect(self.herokuDB )
        cur = xconnect.cursor()

        try:
            cur.execute("""select * from match""")

            total = cur.fetchall()

            xconnect.close()
            return (True, total)
        except Exception as err:
            xconnect.close()
            return(False , err)



    def getter_error(self):
        xconnect = psycopg2.connect(self.herokuDB )
        cur = xconnect.cursor()

        try:
            cur.execute("""select * from error""")

            total = cur.fetchall()

            xconnect.close()
            return (True, total)
        except Exception as err:
            xconnect.close()
            return(False , err)


if __name__ == '__main__':
    db = DB()
    db.start()
    db.added_match(202, 'good', 'sdasdasdsdad', 'asdadasdasd', 2213123, 123)
    db.added_std(False,100,3,1,1)
    print(db.getter_report())
    print(db.getter_match())
    print(db.getter_error())
