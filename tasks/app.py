from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session
import sqlite3
import datetime

# configure application
app = Flask(__name__)

# connect to database
connection=sqlite3.connect('tasks.db', check_same_thread=False)

# test connection
print(connection.total_changes)

# create cursor object
db = connection.cursor()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        #retrieve input from user
        name = request.form.get("name")
        if not name:
            tasks = db.execute("SELECT * FROM tasks ORDER BY CASE WHEN time='' THEN NULL ELSE time END NULLS LAST")
            return render_template("index.html", nameError = "Must enter name of task", tasks=tasks)
        description = request.form.get("description")
        date = request.form.get("date")

        db.execute("INSERT INTO tasks (name, description, time) VALUES (?, ?, ?)", (name, description, date))
        connection.commit()
        tasks = db.execute("SELECT * FROM tasks ORDER BY CASE WHEN time='' THEN NULL ELSE time END NULLS LAST")

        return redirect ("/")

    else:
        tasks = db.execute("SELECT * FROM tasks ORDER BY CASE WHEN time='' THEN NULL ELSE time END NULLS LAST")
        return render_template("index.html", tasks=tasks)
    
@app.route("/sort", methods=["POST"])
def sort():
    if request.method == "POST":
        sortSelection = int(request.form['sort'])
        if sortSelection == 1:
            tasks = db.execute("SELECT * FROM tasks ORDER BY name COLLATE NOCASE ASC")
            return render_template("index.html", tasks=tasks)
        elif sortSelection == 2:
           tasks = db.execute("SELECT * FROM tasks ORDER BY name COLLATE NOCASE DESC")
           return render_template("index.html", tasks=tasks)
        elif sortSelection == 3:
            tasks = db.execute("SELECT * FROM tasks ORDER BY CASE WHEN time='' THEN NULL ELSE time END ASC NULLS LAST")
            return render_template("index.html", tasks=tasks)
        else: 
            tasks = db.execute("SELECT * FROM tasks ORDER BY CASE WHEN time='' THEN NULL ELSE time END DESC NULLS LAST")

            return render_template("index.html", tasks=tasks)

@app.route("/history")
def history():
    history = db.execute("SELECT * FROM history ORDER BY time DESC")
    return render_template("history.html", history=history)

@app.route("/done", methods=["GET", "POST"])
def done():
    if request.method == "POST":
        id = request.form['done']
        task = db.execute("SELECT * FROM tasks WHERE id=?", [id])
        task = task.fetchall()
        name = task[0][1]
        description = task[0][2]
        time = datetime.date.today()
        db.execute("INSERT INTO history (name, description, time) VALUES (?, ?, ?)", (name, description, time))
        connection.commit()
        db.execute("DELETE FROM tasks WHERE id = ?", [id])

        return redirect("/")
    
@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        id = request.form['delete']
        db.execute("DELETE FROM tasks WHERE id = ?", [id])

        return redirect("/")

@app.route("/deleteHistory", methods=["GET", "POST"])
def deleteHistory():
    if request.method == "POST":
        id = request.form['del']
        db.execute("DELETE FROM history WHERE id = ?", [id])

        return redirect("/history")
    
@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        id = request.form['edit']
        task = db.execute("SELECT * FROM tasks WHERE id = ?", [id])
        return render_template("edit.html", task=task)
    

@app.route("/updated", methods=["POST"])
def updated():
    if request.method == "POST":
        id = request.form['update']
        task = db.execute("SELECT * FROM tasks WHERE id = ?", [id])
        name = request.form.get("name")
        if not name:
            task = db.execute("SELECT * FROM tasks WHERE id = ?", [id])
            return render_template("edit.html", nameError = "Must enter name of task", task=task)
        description = request.form.get("description")
        date = request.form.get("date")
        #update sql entry with newly input info
        db.execute("UPDATE tasks SET name = ?, description = ?, time = ? WHERE id = ?", [name, description, date, id])
        connection.commit()

        return redirect("/")
    
