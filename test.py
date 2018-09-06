import pandas as pd
from datetime import datetime, timedelta
import time

#Get museum database
basedf = pd.read_excel('BaseMuséesVTest.xlsx')

#Get common transports database
basetpc = pd.read_excel('MuseumTPC.xlsx')


#Column name
MUSEUM_ID = "ID"
CLOSED = "FERME"
CLOSED_DATE = "FERMETURE ANNUELLE"
PERMANENT = "EXPOSITION PERMANENTE"
BEGIN = "DATE DEBUT"
END = "DATE FIN"
ACCESS = "ACCESSIBILITE"
WEEK_DAY = ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI", "DIMANCHE"]
TOPIC = "THEMATIQUE"
WAITING = "DUREE MOYENNE ATTENTE"
VISIT = "DUREE MOYENNE VISITE"
FULL_PRICE = "PLEIN TARIF"
LOW_PRICE = "TARIF REDUIT"
FREE = "GRATUIT"
QUICK_ACCESS = "BILLETS COUPE FILE"
NAME = "NOM EXPOSITION"
REMAINING_TIME_TO_OPEN = "TEMPS RESTANT AVANT OUVERTURE"
REMAINING_TIME_TO_CLOSE = "TEMPS RESTANT AVANT FERMETURE"
AVAILABLE = "MUSEUM ACCESSIBLE"

#Topics
PAINT = "Peinture"


#Get user inputs
#userdf = pd.read_excel('CurrentUser.xlsx')
#for dev use hard coded values
dte = '2018-10-23 11:35'
tme_struct = time.strptime(dte, '%Y-%m-%d %H:%M')
userDate = datetime(*tme_struct[0:6])
favoriteTopics = [PAINT]


#extract museums that are not closed for specific date
def removeClosedDate(data):
   #remove closed museum
   data = data.loc[data[CLOSED]==0]

   #get user current date (dd/mm)
   userdaymonth = f"{userDate.day:02d}/{userDate.month:02d}"

   #extract annual closed dates
   #we keep nan values which means always opened and also rows which nor match with user date
   data = data.loc[(data[CLOSED_DATE].isnull()) | (data[CLOSED_DATE].str.contains(userdaymonth)==False)]


#extract museums that are opened for user date. This should be apply after removeClosedDate function.
def getDayOpenedMuseum(data):
   #get user day index
   uday = userDate.weekday()	
   #keep museum opened for such day
   data = data.loc[~data[WEEK_DAY[uday]].isnull()]


#function for dataframe apply method to compute remaining time to open
def computeRemainingTimeToOpen(x):
   startTime,endTime = x.split("-")
   startT = datetime.strptime(startTime,"%H:%M")
   startT = userDate.replace(hour = int(startT.hour), minute = int(startT.minute))
   if startT > userDate:
      return ((startT-userDate)/timedelta(minutes=1))
   else:
      return 0


#function for dataframe apply method to compute remaining time to close
def computeRemainingTimeToClose(x):
   startTime,endTime = x.split("-")
   endT = datetime.strptime(endTime,"%H:%M")
   endT = userDate.replace(hour = int(endT.hour), minute = int(endT.minute))
   if endT > userDate:
      return ((endT-userDate)/timedelta(minutes=1))
   else:
      return 0 	

	
#For each museums add a column displaying remaining time until opened time (0 if already opened) and remaining time until closed time (0 if already closed).
def getHourRemaining(data):
   #get user day index
   uday = userdate.weekday()
	
   data[REMAINING_TIME_TO_OPEN] = data[WEEK_DAY[uday]].apply(computeRemainingTimeToOpen).astype(int)
   data[REMAINING_TIME_TO_CLOSE] = data[WEEK_DAY[uday]].apply(computeRemainingTimeToClose).astype(int)

#For each museum add a column displaying if the museum could be vistited (taking account waiting time and time to visit)
def checkAvailableMuseumForVisit(data):
   #fill nan with 0 for waiting time, and 60 minutes for time to visit
   data[WAITING].fillna(0,inplace=True)
   data[VISIT].fillna(60,inplace=True)
   data[AVAILABLE] = data.map(lambda x : 0 if x[REMAINING_TIME_TO_CLOSE] < x[WAITING]+x[VISIT] else 1, axis=1)


#sort museums according user favorite topics
def getFavoriteMuseums(data):


