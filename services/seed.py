import sqlite3
# login with email#######
# conn = sqlite3.connect("database/cms.db")
# cur = conn.cursor()
#
# users = [
#     ("Admin", "admin", "admin@cms.com"),
#     ("Supervisor One", "supervisor", "sup@cms.com"),
#     ("Engineer One", "engineer", "eng@cms.com"),
# ]
#
# cur.executemany(
#     "INSERT INTO users (name, role, email) VALUES (?, ?, ?)",
#     users
# )
#
# conn.commit()
# conn.close()
# print("Default users added")


#login with user name password
conn = sqlite3.connect("database/cms.db")
cur = conn.cursor()

users = [
    ("admin", "Admin", "admin", "admin123"),
    ("supervisor", "Supervisor One", "supervisor", "sup123"),
    ("engineer", "Engineer One", "engineer", "eng123"),
]

cur.executemany(
    "INSERT INTO users (name, role, email, password) VALUES (?, ?, ?, ?)",
    users
)

conn.commit()
conn.close()
print("Users with username & password added")
