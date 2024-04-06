import sqlite3
conn = sqlite3.connect('tasks.db',check_same_thread=False)
# conn = sqlite3.connect('C:/Users/DELL/Intelligent System Final Project/Backend/Generating data for the first model/tasks.db',check_same_thread=False)
c = conn.cursor()

def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS "tasks" (
	"guid"	INTEGER,
	"title"	TEXT,
	"tag"	TEXT,
	"deadline"	DATETIME,
	"deadline_date"	DATE,
	"about"	TEXT,
	"task_status"	TEXT,
	"time_estimation"	TEXT,
	"start_time"	DATETIME,
	"end_time"	DATETIME,
	"is_late"	NUMERIC,
	"today_date"	DATE,
	"medication_taken"	NUMERIC,
	"avg_mood_int"	INTEGER,
	"avg_sleep_hours_int"	REAL,
	PRIMARY KEY("guid" AUTOINCREMENT)
);''')

def add_row(title, tag, deadline, deadline_date, about, task_status, time_estimation, start_time, end_time, is_late, today_date, avg_mood_int, avg_sleep_hours_int, medication_taken):
    c.execute('INSERT INTO "tasks"(title, tag, deadline, deadline_date, about, task_status, time_estimation, start_time, end_time, is_late, today_date, avg_mood_int, avg_sleep_hours_int, medication_taken) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(title, tag, deadline, deadline_date, about, task_status, time_estimation, start_time, end_time, is_late, today_date, avg_mood_int, avg_sleep_hours_int, medication_taken))
    conn.commit()
    
def view_all_data():
    c.execute('SELECT * FROM "tasks"')
    data = c.fetchall()
    return data

def view_all_task_names():
    c.execute('SELECT DISTINCT title FROM "tasks"')
    data = c.fetchall()
    return data
              
def get_task(task):
    c.execute('SELECT * FROM "tasks" WHERE title="{}"'.format(task))
    data = c.fetchall()
    return data

def get_today_tasks(deadline_date):
    c.execute('SELECT * FROM "tasks" WHERE deadline_date="{}"'(deadline_date.strftime('%m/%d/%Y')))
    data = c.fetchall()
    return data
              
def get_task_by_status(task_status):
    c.execute('SELECT * FROM "tasks" WHERE task_status="{}"'.format(task_status))
    data = c.fetchall()
              
# def edit_task_data(new_task,new_task_status,new_task_date,task,task_status,task_due_date):
#     c.execute("UPDATE taskstable SET task =?,task_status=?,task_due_date=? WHERE task=? and task_status=? and task_due_date=? ",(new_task,new_task_status,new_task_date,task,task_status,task_due_date))
#     conn.commit()
#     data = c.fetchall()
#     return data
              
def delete_data(task):
    c.execute('DELETE FROM "tasks" WHERE title="{}"'.format(task))
    conn.commit()



#  ****************************************************
#  ML Model Functions   
#  ****************************************************

def get_all_ml_data(filename):
    c.execute('SELECT * FROM '+ filename)
    data = c.fetchall()
    return data