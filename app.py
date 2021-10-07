import dbcreds
import mariadb

class LoginError (Exception):
    def __init__(self):
        super().__init__("Failed to log in with the provided credentials")


# I have to connect in different contexts, should make this a function
def connectDB():
    conn = None
    cursor = None

    try:
        conn=mariadb.connect(
                            user=dbcreds.user,
                            password=dbcreds.password,
                            host=dbcreds.host,
                            port=dbcreds.port,
                            database=dbcreds.database
                            )
        cursor = conn.cursor()
    # Only one thing can go wrong, which is the connection to the DB failing
    except:
        if (cursor != None):
            cursor.close()
        if (conn != None):
            conn.close()
        raise ConnectionError("Failed to connect to the database")
    
    return (conn, cursor)


def login(username, password):
    try:
        (conn, cursor) = connectDB()
        cursor.execute("SELECT * FROM hackers WHERE alias=?",[username,])
        result = cursor.fetchall()

        # If true, user exists
        if cursor.rowcount == 1:
            # If true, the password is correct for the given username
            if password == result[0][2]:
                # I use the user ID from the login for my exploit interactions (it's a FK)
                run_blog(result[0][0])
        raise LoginError()
    # I know that my own function can raise a ConnectionError, should handle it
    except ConnectionError:
        print("Error while attempting to connect to the database")
    # I can give my exception a name and raise it again for somebody else to catch
    except LoginError as error:
        raise error
    except ValueError as error:
        # I can even grab the error message directly and integrate it into my print
        print("There was an error: "+ str(error))
        exit()
    except mariadb.DataError:
        print("Something wrong with your data")
    except mariadb.OperationalError:
        print("Operational error on the connection")
    except mariadb.ProgrammingError:
        print("Your query was wrong")
    except mariadb.IntegrityError:
        print("Your query would have broken the database and we stopped it")
    except:
        print("Something went wrong")
    finally:
        if (cursor != None):
            cursor.close()

        if (conn != None):
            conn.rollback()
            conn.close()



def run_blog(user_id):
    while (True):
        print("\n\nPlease select one of the following options:\n"+
            "1: Enter a new exploit\n"+
            "2: See all my exploits\n"+
            "3: See everyone else's exploits\n"+
            "4: Exit")

        choice = input("Choice: ")

        # Define the valid choices and raise an exception if choice is invalid
        if (choice not in ["1","2","3","4"]):
            raise ValueError("Error! Invalid choice, exiting")

        if (choice == "1"):

            print("Please enter your exploit:")
            content = input()

            if (content == ""):
                raise ValueError("Error! Exploit cannot be empty, exiting")

            createExploit(user_id, content)

        elif(choice == "2"):
            print("Fetching all posts...\n\n")
            getExploits(user_id, True)

        elif(choice == "3"):
            getExploits(user_id, False)

        elif(choice == "4"):
            exit()


def createExploit(user_id, content):
    # Create the variables so they are visible in the finally scope
    conn = None
    cursor = None
        
    try:
        (conn, cursor) = connectDB()
        cursor.execute("INSERT INTO exploits(user_id, content) VALUES(?,?)", [user_id,content])
        conn.commit()
        print("Exploit successfully created!\n\n")
    # I know that my own function can raise a ConnectionError, should handle it
    except ConnectionError:
        print("Error while attempting to connect to the database")
    except mariadb.DataError:
        print("Something wrong with your data")
    except mariadb.OperationalError:
        print("Operational error on the connection")
    except mariadb.ProgrammingError:
        print("Your query was wrong")
    except mariadb.IntegrityError:
        print("Your query would have broken the database and we stopped it")
    except:
        print("Something went wrong")
    finally:
        if (cursor != None):
            cursor.close()

        if (conn != None):
            conn.rollback()
            conn.close()


# The only difference between getting own posts and others' is in the equality of the query
# We can kill 2 queries with one function by adding a boolean
def getExploits(user_id, own_posts=True):
    # Create the variables so they are visible in the finally scope
    conn = None
    cursor = None
        
    try:
        (conn, cursor) = connectDB()

        if own_posts:
            cursor.execute("SELECT alias,content FROM hackers JOIN exploits ON hackers.id=exploits.user_id WHERE hackers.id=?",[user_id,])
        elif not own_posts:
            cursor.execute("SELECT alias,content FROM hackers JOIN exploits ON hackers.id=exploits.user_id WHERE hackers.id!=?",[user_id,])

        posts = cursor.fetchall()
        prettyPrintExploits(posts)
    # I know that my own function can raise a ConnectionError, should handle it
    except ConnectionError:
        print("Error while attempting to connect to the database")
    except mariadb.DataError:
        print("Something wrong with your data")
    except mariadb.OperationalError:
        print("Operational error on the connection")
    except mariadb.ProgrammingError:
        print("Your query was wrong")
    except mariadb.IntegrityError:
        print("Your query would have broken the database and we stopped it")
    except:
        print("Something went wrong")
    finally:
        if (cursor != None):
            cursor.close()

        if (conn != None):
            conn.rollback()
            conn.close()


def prettyPrintExploits(posts):
    # I assume these maximum lengths for the columns of the table, otherwise the padding breaks
    USER_LENGTH=20
    POST_LENGTH=100

    header = "Username".ljust(USER_LENGTH), "Content".ljust(POST_LENGTH)
    print(  "|"+
            "|".join(header)+
            "|")
    # Plus 3 for the vertical separation bars
    print("-"*(USER_LENGTH+POST_LENGTH+3))

    # I know that fetchall returns an array of tuples, so I know how to get each individual value (this also assumes I know the order of columns in my DB)
    for post in posts:
        # Pad each part with spaces for consistent display, regardless of data length
        padded_post = (post[0].ljust(USER_LENGTH), post[1].ljust(POST_LENGTH))
        print(  "|"+
                "|".join(padded_post)+
                "|")
        print("-"*(USER_LENGTH+POST_LENGTH+3))



print("Hello and welcome to the blog!")

login_attempts = 0

while (login_attempts < 3):
    print("\n\nPlease enter login information")

    username = input("Username:")

    password = input("Password:")

    try:
        login(username, password)

        
    except LoginError:
        print("Invalid credentials.")
        # Python doesn't have ++ :(
        login_attempts += 1
    
    

# Exit after 3 failed attempts to log in
print("Too many failed attempts, exiting")

    