import mysql.connector


class ConnectorKaffeDB:
    def __init__(self, ip="", user="", pw="", db=""):
        # Connector aufbauen
        self.ip = ip
        self.dbUser = user
        self.passwd = pw
        self.dbName = db
        self.connection = mysql.connector.connect(host=self.ip, user=self.dbUser, passwd=self.passwd, db=self.dbName)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    """
        General
    """

    def execute(self, querry=""):
        self.cursor.execute("BEGIN")
        self.cursor.execute(querry)
        self.cursor.execute("COMMIT")

    def get(self, key="", data=""):
        self.cursor.execute("BEGIN")
        self.cursor.execute("SELECT User FROM {0} WHERE x = {1};".format(key, data))
        ergebnis = self.cursor.fetchall()
        self.cursor.execute("COMMIT")
        return ergebnis

    def quarry(self, quarry=""):
        self.cursor.execute("BEGIN")
        self.cursor.execute(quarry)
        ergebnis = self.cursor.fetchall()
        self.cursor.execute("COMMIT")
        return ergebnis
    """
        User management
    """
    def addUser(self, guthaben, name, gesicht, status, muedigkeit):
        self.execute("INSERT INTO User(Guthaben, Name, Gesicht, Status, Muedigkeit) VALUES('" + guthaben + "', '$" + name + "', '" + gesicht + "', '" + status + "', '$" + muedigkeit + "')")

    def getUserFace(self, name):
        return self.get("Gesicht", name)

    def getUserGuthaben(self, name):
        return self.get("Guthaben", name)

    def getUserName(self, name):
        return self.get("Name", name)

    def getUserStatus(self, name):
        return self.get("Status", name)

    def getUserMuedigkeit(self, name):
        return self.get("Muedigkeit", name)

    'Kaffe'
    def addKaffe(self, kosten,  name ):
        self.execute("INSERT INTO kaffeart(Kosten, Name) VALUES('{0}', '{1}')".format(kosten, name))

    def getKaffe(self, name):
        return self.get("kaffeart", name)


    'Abrechnung'
    def addAbrechnungPunkt( self, produkt, kosten, user, guthaben):
        self.execute("INSERT INTO Abrechnung(Produkt, Kosten, Guthaben, USER) VALUES('{0}', '{1}', '{2}', '{3}')".format(produkt, kosten, guthaben, user))

    def generateExcel(self):
        self.cursor.execute("BEGIN")
        self.cursor.execute("SELECT * FROM Abrechnung ORDER BY Name")
        ergebnis = self.cursor.fetchall()
        self.cursor.execute("COMMIT")
        return ergebnis


# Not needed because only used as library
# if __name__=="__main__":
#     db = ConnectorKaffeDB();
#     db.addUser(0.21, "Christian","jölkajsdökj", "20302", "90" );
#     print (getUserName("Christian"));
