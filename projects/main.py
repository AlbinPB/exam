from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import pyodbc
import datetime

import os
os.urandom(24)


app = Flask(__name__)
app.secret_key = os.urandom(24)


# Configure database connection
server = 'DESKTOP-PIKNNDF\SQLEXPRESS01'
database = 'todos'

driver = '{ODBC Driver 17 for SQL Server}'
connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
cnxn = pyodbc.connect(connection_string)
cursor = cnxn.cursor()

####user id maybe help in session
user_id = None
cursor.execute("SELECT * FROM Task WHERE User_id = ?", user_id)
tasks = cursor.fetchall()

cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ?", user_id)
subtasks = cursor.fetchall()
current_date = datetime.date.today()
username = None

@app.route('/')
def index():
    global username
    username = session.get('username')
    return render_template('index.html', user_id=user_id, username = username)




@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_id  # Use the global keyword to access the global variable

    if request.method == 'POST':
        username = request.form['username']
        # password = str(hash(request.form['password']))
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        # Check if username and password match a record in the login table
        cursor.execute("SELECT id FROM login WHERE username = ? AND password = ?", username, password)
        row = cursor.fetchone()
        if row:
            user_id = row[0]  # Store the user ID as a global variable
            session['username'] = username  # Set session variable for logged-in user
            
            return redirect(url_for('index'))  # Redirect to home page after login
        else:
            
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))  # Redirect back to login page if login fails
    else:
        return render_template('login.html',user_id=user_id)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        # password = str(hash(request.form['password']))
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        repassword = hashlib.sha256(request.form['repassword'].encode()).hexdigest()
        email = request.form['email']

        if password == repassword:
        # Insert user details into the signup table
            cursor.execute("INSERT INTO signup (username, password, email) VALUES (?, ?, ?)", username, password, email)
            cnxn.commit()
            cursor.execute("INSERT INTO login (username, password) VALUES (?, ?)", username, password)
            cnxn.commit()
            return redirect(url_for('login'))  # Redirect to home page after signup
        else:
            flash('Invalid Password Mismatch', 'error')
            return redirect(url_for('signup'))
    else:
        return render_template('signup.html',user_id=user_id)

@app.route('/logout')
def logout():
    global user_id
    user_id = None  # Clear the user ID
    session.pop('username', None)  # Remove the 'username' session variable
    
    return redirect(url_for('index'))  # Redirect to the home page after logout


# @app.route('/tasks')
# def tasks():
#     global user_id


#     if user_id is None:
        
#         return redirect_with_popup(url_for('login'))
#     else:
#         cursor.execute("SELECT * FROM Task WHERE User_id = ?", user_id)
#         tasks = cursor.fetchall()

#         cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ?", user_id)
#         subtasks = cursor.fetchall()

#         return render_template('task.html',user_id=user_id, tasks=tasks, subtasks=subtasks,username = username)



# def redirect_with_popup(location):
#     return f"""
#     <script>
#         alert("Please log in to access this feature.");
#         window.location.href = "{location}";
#     </script>
#     """
@app.route('/task_sub_add', methods=['GET', 'POST'])
def task_sub_add():


        # Handle GET request to render the initial page
        # cursor.execute("SELECT * FROM Task WHERE User_id = ?", user_id)
        # tasks = cursor.fetchall()

        # cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ?", user_id)
        # subtasks = cursor.fetchall()

        # return render_template('manage_task.html', tasks=tasks, subtasks=subtasks)
        if request.method == 'POST':
            task_name = request.form.get('task_name')
            priority = request.form.get('priority')
            category = request.form.get('category')
            due_date = request.form.get('due_date')
            status = request.form.get('status')
            user_id = request.form.get('user_id')
            task_id = request.form.get('task_id')

        # Insert the form data into the database
            cursor.execute("INSERT INTO Sub_Task (TaskName, Priority, Category, DueDate, User_id,TaskID, Status) VALUES (?,?, ?, ?, ?, ?, ?)", 
                        (task_name, priority, category, due_date,  user_id,task_id,status))
            cnxn.commit()

            # Retrieve tasks and subtasks from the database
        cursor.execute("SELECT * FROM Task WHERE User_id = ?", (user_id,))
        tasks = cursor.fetchall()

        cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ?", (user_id,))
        subtasks = cursor.fetchall()

        return render_template('task.html', tasks=tasks, subtasks=subtasks, user_id=user_id,username = username)



@app.route('/manage_task', methods=['GET', 'POST'])
def manage_task():
    global user_id
    global tasks
    global subtasks
    if user_id is None:
        return redirect_with_popup(url_for('login'))
        
    else:
        
        cursor.execute("SELECT * FROM Task WHERE User_id = ?", (user_id,))
        tasks = cursor.fetchall()

        cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ? order by status desc", (user_id,)) 
        subtasks = cursor.fetchall()

        return render_template('manage_task.html', tasks=tasks, subtasks=subtasks, user_id=user_id, date =current_date,username = username)


def redirect_with_popup(location):
    return f"""
    <script>
        alert("Please log in to access this feature.");
        window.location.href = "{location}";
    </script>
    """

@app.route('/manage_task_sub_add', methods=['GET', 'POST'])
def manage_task_sub_add():


        # Handle GET request to render the initial page
        # cursor.execute("SELECT * FROM Task WHERE User_id = ?", user_id)
        # tasks = cursor.fetchall()

        # cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ?", user_id)
        # subtasks = cursor.fetchall()

        # return render_template('manage_task.html', tasks=tasks, subtasks=subtasks)
        if request.method == 'POST':
            task_name = request.form.get('task_name')
            priority = request.form.get('priority')
            category = request.form.get('category')
            due_date = request.form.get('due_date')
            status = request.form.get('status')
            user_id = request.form.get('user_id')
            task_id = request.form.get('task_id')

        # Insert the form data into the database
            cursor.execute("INSERT INTO Sub_Task (TaskName, Priority, Category, DueDate, User_id,TaskID, Status) VALUES (?,?, ?, ?, ?, ?, ?)", 
                        (task_name, priority, category, due_date,  user_id,task_id,status))
            cnxn.commit()

            # Retrieve tasks and subtasks from the database
        cursor.execute("SELECT * FROM Task WHERE User_id = ?", (user_id,))
        tasks = cursor.fetchall()

        cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ? order by status desc", (user_id,)) 
        subtasks = cursor.fetchall()

        return render_template('manage_task.html', tasks=tasks, subtasks=subtasks, user_id=user_id,date =current_date,username = username)


@app.route('/manage_task_add', methods=['GET', 'POST'])
def manage_task_add():


        # Handle GET request to render the initial page
        # cursor.execute("SELECT * FROM Task WHERE User_id = ?", user_id)
        # tasks = cursor.fetchall()

        # cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ?", user_id)
        # subtasks = cursor.fetchall()

        # return render_template('manage_task.html', tasks=tasks, subtasks=subtasks)
        if request.method == 'POST':
            task_name = request.form.get('task_name')
            priority = request.form.get('priority')
            category = request.form.get('category')
            due_date = request.form.get('due_date')
            status = request.form.get('status')
            user_id = request.form.get('user_id')
            

        # Insert the form data into the database
            cursor.execute("INSERT INTO Task (TaskName, Priority, Category, DueDate, User_id, status) VALUES (?,?, ?, ?, ?, ?)", 
                        (task_name, priority, category, due_date,  user_id,status))
            cnxn.commit()

            # Retrieve tasks and subtasks from the database
        cursor.execute("SELECT * FROM Task WHERE User_id = ?", (user_id,))
        tasks = cursor.fetchall()

        cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ? order by status desc", (user_id,)) 
        subtasks = cursor.fetchall()

        return render_template('manage_task.html', tasks=tasks, subtasks=subtasks, user_id=user_id,date =current_date,username = username)

@app.route('/check_box',methods=['GET', 'POST'])
def check_box():
    if request.method == 'POST':
            sub_task_id = request.form.get('sub_task_id')
            cursor.execute("Update Sub_Task set status = 'Done' where SubTaskId = ?", (sub_task_id))
            cnxn.commit()

    
    cursor.execute("SELECT * FROM Task WHERE User_id = ?", (user_id,))
    tasks = cursor.fetchall()

    cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ? order by status desc", (user_id,)) 
    subtasks = cursor.fetchall()

    return render_template('manage_task.html', tasks=tasks, subtasks=subtasks, user_id=user_id,date =current_date,username = username)


@app.route('/sub_del',methods=['GET', 'POST'])
def sub_del():
    if request.method == 'POST':
            sub_task_id = request.form.get('sub_task_id')
            cursor.execute("Delete From Sub_Task where SubTaskID = ?", (sub_task_id))
            cnxn.commit()

    
    cursor.execute("SELECT * FROM Task WHERE User_id = ?", (user_id,))
    tasks = cursor.fetchall()

    cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ? order by status desc", (user_id,)) 
    subtasks = cursor.fetchall()

    return render_template('manage_task.html', tasks=tasks, subtasks=subtasks, user_id=user_id,date =current_date,username = username)

@app.route('/del_main',methods=['GET', 'POST'])
def del_main():
    if request.method == 'POST':
            task_id = request.form.get('task_id')
            cursor.execute("Delete From Task where TaskID = ?", (task_id))
            cnxn.commit()

    
    cursor.execute("SELECT * FROM Task WHERE User_id = ?", (user_id,))
    tasks = cursor.fetchall()

    cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ? order by status desc", (user_id,)) 
    subtasks = cursor.fetchall()

    return render_template('manage_task.html', tasks=tasks, subtasks=subtasks, user_id=user_id,date =current_date,username = username)


@app.route('/sub_task_update/<int:task_id>', methods=['GET', 'POST'])
def sub_task_update(task_id):


    cursor.execute("SELECT * FROM Sub_Task WHERE SubTaskID = ?", (task_id)) 
    subtasks = cursor.fetchall()

    return render_template('sub_task_update.html', subtasks=subtasks, task_id = task_id,date =current_date,username = username)

@app.route('/sub_task_update_no_para', methods=['GET', 'POST'])
def sub_task_update_no_para():

    task_name = request.form.get('task_name')
    priority = request.form.get('priority')
    category = request.form.get('category')
    due_date = request.form.get('due_date')
    status = request.form.get('status')
    task_id = request.form.get('sub_task_d')

    cursor.execute("update Sub_Task set TaskName = ?,Priority = ?,Category = ?,DueDate = ?,status = ? where SubTaskID = ?", (task_name,priority,category,due_date,status,task_id)) 
    cnxn.commit()

    cursor.execute("SELECT * FROM Task WHERE User_id = ?", (user_id,))
    tasks = cursor.fetchall()

    cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ? order by status desc", (user_id,)) 
    subtasks = cursor.fetchall()
    
    return render_template('manage_task.html', tasks= tasks,subtasks=subtasks, task_id = task_id ,user_id= user_id,date =current_date,username = username)

@app.route('/task_update/<int:task_id>', methods=['GET', 'POST'])
def task_update(task_id):


    cursor.execute("SELECT * FROM Task WHERE TaskID = ?", (task_id)) 
    tasks = cursor.fetchall()

    return render_template('task_update.html', tasks=tasks, task_id = task_id,date =current_date,username = username)

@app.route('/task_update_no_para', methods=['GET', 'POST'])
def task_update_no_para():

    task_name = request.form.get('task_name')
    priority = request.form.get('priority')
    category = request.form.get('category')
    due_date = request.form.get('due_date')
    status = request.form.get('status')
    task_id = request.form.get('task_id') 

    cursor.execute("update Task set TaskName = ?,Priority = ?,Category = ?,DueDate = ?,status = ? where TaskID = ?", (task_name,priority,category,due_date,status,task_id)) 
    cnxn.commit()

    cursor.execute("SELECT * FROM Task WHERE User_id = ?", (user_id,))
    tasks = cursor.fetchall()

    cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ? order by status desc", (user_id,)) 
    subtasks = cursor.fetchall()
    
    return render_template('manage_task.html', tasks= tasks,subtasks=subtasks, task_id = task_id ,user_id= user_id,date =current_date,username = username)

@app.route('/filter_task', methods=['GET', 'POST'])
def filter_task():


    filter = request.form.get('filter')
    print(filter,"date")
    print(current_date,'cur')
    if str(current_date) == str(filter):
        print("equal")
        cursor.execute("SELECT * FROM Task WHERE  User_id = ? and DueDate < ? and status != ?", (user_id,current_date,"Done"))
        tasks = cursor.fetchall()

    else:
        cursor.execute("SELECT * FROM Task WHERE User_id = ? and status = ?", (user_id,filter))
        tasks = cursor.fetchall()

    cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ? order by status desc", (user_id,)) 
    subtasks = cursor.fetchall()

    return render_template('manage_task.html', tasks= tasks,subtasks=subtasks,user_id= user_id,date =current_date,username = username)


@app.route('/sort', methods=['GET', 'POST'])
def sort():
    filter = request.form.get('sort')
    tasks = request.form.get('task')
    print(tasks)
    
    if filter == 'low':
        cursor.execute("SELECT * FROM task where User_ID = ? ORDER BY CASE priority WHEN 'Low' THEN 1 WHEN 'Medium' THEN 2 WHEN 'High' THEN 3 ELSE 4 END;",(user_id))
        tasks = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM task  where User_ID = ? ORDER BY CASE priority WHEN 'Low' THEN 1 WHEN 'Medium' THEN 2 WHEN 'High' THEN 3 ELSE 4 END desc;",(user_id))
        tasks = cursor.fetchall()

    cursor.execute("SELECT * FROM Sub_Task WHERE User_id = ? order by status desc", (user_id,)) 
    subtasks = cursor.fetchall()

    return render_template('manage_task.html', tasks= tasks,subtasks=subtasks,user_id= user_id,date =current_date,username = username)


if __name__ == '__main__':
    app.run(debug=True)
