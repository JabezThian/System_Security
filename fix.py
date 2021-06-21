import shelve
from Users import User,Doctor

db = shelve.open("storage.db", 'c')
users_db = db["Users"]

users_db["T0392511G"] = User("T0392511G", "Daniel", "Jack", "M", "1999-10-22", "danieljack@gmail.com", "password")
users_db["T0392511G"].set_role("Patient")
users_db["T5739128U"] = User("T5739128U", "Chloe", "Soh", "F", "1995-09-15", "chloesoh@gmail.com", "password")
users_db["T5739128U"].set_role("Admin")
users_db["T1111111F"] = Doctor("T1111111F", "Eric", "Lee", "M", "1994-10-30", "samwilson@gmail.com", "password","Cardiology","us04web.zoom.us/j/5890364204?pwd=dnB5NE5MMnZXbWZKbDJiRXNuT29vUT09")
users_db["T1111111F"].set_role("Doctor")
users_db["T2222222F"] = Doctor("T2222222F", "Same", "Wilson", "M", "1994-10-30", "samwilson@gmail.com", "password","Gastroenterology","us04web.zoom.us/j/5890364204?pwd=dnB5NE5MMnZXbWZKbDJiRXNuT29vUT09")
users_db["T2222222F"].set_role("Doctor")
users_db["T3333333F"] = Doctor("T3333333F", "Benjamin", "Tan", "M", "1994-10-30", "samwilson@gmail.com", "password","Haematology","us04web.zoom.us/j/5890364204?pwd=dnB5NE5MMnZXbWZKbDJiRXNuT29vUT09")
users_db["T3333333F"].set_role("Doctor")
db['Users'] = users_db

db.close()
