import csv
import os
import sqlite3

# Resolve the resources folder relative to this file, so paths work
# no matter what directory the script is run from.
_RESOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'resources')

# Connect to the SQLite in-memory database
conn = sqlite3.connect(':memory:')

# A cursor object to execute SQL commands
cursor = conn.cursor()


def main():

    # users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        userId INTEGER PRIMARY KEY,
                        firstName TEXT,
                        lastName TEXT
                      )'''
                   )

    # callLogs table (with FK to users table)
    cursor.execute('''CREATE TABLE IF NOT EXISTS callLogs (
        callId INTEGER PRIMARY KEY,
        phoneNumber TEXT,
        startTime INTEGER,
        endTime INTEGER,
        direction TEXT,
        userId INTEGER,
        FOREIGN KEY (userId) REFERENCES users(userId)
    )''')

    # You will implement these methods below. They just print TO-DO messages for now.
    load_and_clean_users(os.path.join(_RESOURCES_DIR, 'users.csv'))
    load_and_clean_call_logs(os.path.join(_RESOURCES_DIR, 'callLogs.csv'))
    write_user_analytics(os.path.join(_RESOURCES_DIR, 'userAnalytics.csv'))
    write_ordered_calls(os.path.join(_RESOURCES_DIR, 'orderedCalls.csv'))

    # Helper method that prints the contents of the users and callLogs tables. Uncomment to see data.
    # select_from_users_and_call_logs()

    # Close the cursor and connection. main function ends here.
    cursor.close()
    conn.close()


# TODO: Implement the following 4 functions. The functions must pass the unit tests to complete the project.

def _clean_row(row, num_fields):
    fields = [field.strip() for field in row]
    if len(fields) != num_fields or not all(fields):
        return None
    return fields

# This function will load the users.csv file into the users table, discarding any records with incomplete data
def load_and_clean_users(file_path):
    with open(file_path, 'r' , newline='') as file:
        reader = csv.reader(file)

        next(reader, None)

        for row in reader:
            fields = _clean_row(row, 2)
            if fields is None:
                continue

            cursor.execute('INSERT INTO users (firstName, lastName) VALUES (?, ?)', fields)
    conn.commit()

# This function will load the callLogs.csv file into the callLogs table, discarding any records with incomplete data
def load_and_clean_call_logs(file_path):
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file)

        next(reader, None)

        for row in reader:
            fields = _clean_row(row, 5)
            if fields is None:
                continue

            phone_number, start_time, end_time, direction, user_id = fields

            try:
                start_time, end_time, user_id = int(start_time), int(end_time), int(user_id)
            except ValueError:
                continue
            
            cursor.execute('''INSERT INTO callLogs (phoneNumber, startTime, endTime, direction, userId)
                              VALUES (?, ?, ?, ?, ?)''',
                           (phone_number, start_time, end_time, direction, user_id))
    conn.commit()


# This function will write analytics data to testUserAnalytics.csv - average call time, and number of calls per user.
# You must save records consisting of each userId, avgDuration, and numCalls
# example: 1,105.0,4 - where 1 is the userId, 105.0 is the avgDuration, and 4 is the numCalls.
def write_user_analytics(csv_file_path):
    cursor.execute('''SELECT userId, AVG(endTime - startTime), COUNT(*)
                      FROM callLogs
                      GROUP BY userId
                      ORDER BY userId''')
    rows = cursor.fetchall()

    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['userId', 'avgDuration', 'numCalls'])
        for user_id, avg_duration, num_calls in rows:
            writer.writerow([user_id, float(avg_duration), num_calls])


# This function will write the callLogs ordered by userId, then start time.
# Then, write the ordered callLogs to orderedCalls.csv
def write_ordered_calls(csv_file_path):
    cursor.execute('''SELECT callId, phoneNumber, startTime, endTime, direction, userId
                      FROM callLogs
                      ORDER BY userId, startTime''')
    rows = cursor.fetchall()

    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['callId', 'phoneNumber', 'startTime', 'endTime', 'direction', 'userId'])
        writer.writerows(rows)



# No need to touch the functions below!------------------------------------------

# This function is for debugs/validation - uncomment the function invocation in main() to see the data in the database.
def select_from_users_and_call_logs():

    print()
    print("PRINTING DATA FROM USERS")
    print("-------------------------")

    # Select and print users data
    cursor.execute('''SELECT * FROM users''')
    for row in cursor:
        print(row)

    # new line
    print()
    print("PRINTING DATA FROM CALLLOGS")
    print("-------------------------")

    # Select and print callLogs data
    cursor.execute('''SELECT * FROM callLogs''')
    for row in cursor:
        print(row)


def return_cursor():
    return cursor


if __name__ == '__main__':
    main()