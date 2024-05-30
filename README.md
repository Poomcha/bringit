# BringIt!
## Video Demo:  https://youtu.be/gOjZlnKX3NE
### Description:
BringIt! is a website to create colaborative lists.

It handles creation of an user and login, creation of an user profile, creation of lists and items.

Basically, a user create a list for a birthday for example, in this list he added all participants and created items he wants them to bring.  
On their view of the application, participants can choose which item they want to bring to the event.

### Important Files:
- **/app/\_\_init\_\_.py**  
Load the app, initialize the db and register all blueprints.  
I chose to use blueprints by reading Flask documentation because I have much more function than in classes projects, so it's better organized and maintainable.

- **/app/schema.sql**  
Contain the structure of the app database.  
    * **users:**  
    Each user have an id, an email and a password associate to him, separated from the user infos.  
    * **users__users:**  
    This table is used to track relationship between users.  
    sender_id and receiver_id are users id, and the relationship is the status, depending if users have accepted each other or rejected for example.
    * **infos:**  
    Contains all informations about the user, for example his lastname or profile picture url.  
    Related to each user by his unique user id.
    * **lists:**  
    All informations about a list excluding users and items related which will be added later.
    * **items:**  
    All informations about an item, same as list.
    * **lists_items:**  
    This table is used to store list / item association.  
    * **lists_users:**  
    Store lists / users association, and also the right of the user on the list associated to him, essentially if he's the creator of the list or not.
    * **items_users:**  
    Store items / users association, used to store who subscribe to any item. 

- **/app/db.py**  
This file contains useful functions to interact with the database that are used all over the app, get_db() connect to the database and return database object used to perform operation on it.  
close_db() just simply close the database connection once it's not needed anymore.
And init_db() is used to execute schema.sql in order to create the database. It's used by init_db_command() that allow the admin to create the database with a Flask command in terminal.

- **/app/models/*.py**  
Define all data models useful to the app with ***marshmallow*** module to simplify creation and validation of datas.  
Each file contain a class with the name of a table, and class "TableSchema" inheriting from marshmallow Schema classes, which implements the different data of each table, with a basic validation associated to it.  
Each models are imported and used in corresponding blueprints files to structure and validate incoming datas.


- **/app/helpers/handle_image.py**  
Functions to handles image files upload on an external service, imgbb.com.  
upload_image(image) convert image in paramater (FileStorage object) to a stream and then it is uploaded by a post request to imgbb which will store the image for us and give us back multiple URLs (3 for different image sizing, and one for deleting the image). These URLs are then returned by the function, and store on the database on each blueprint files.  
The 3 delete_image functions are very useful to quickly handle delete of an image when a list or item is modified or deleted for example.  


- **/app/auth.py**  
Blueprint of the authentification functionnality.  
Define the functions to signup, signin and logout users.  
Load user's infos in a special g object accessible on each requests.  
Also define useful decorators (login_required and login_prohibited) which will be used all over to restrict use of functions, if user is logged in or not.  

- **/app/profile.py**  
Blueprint to handle CRUD operations on user profile.  
Allow user to create and modify his profile, update his password and delete his account.

- **/app/lists.py**  
Blueprint to handle CRUD operations on lists AND items because they are submitted simulteanously from the same form on the same endpoint.  
Allow user to create, modify, read and delete lists. 

- **/app/item.py**  
Blueprint for user to subscribe/unsubscribe to items.

- **/app/bringers.py**  
Blueprint to handle relationship between users.  
By design users can only add others by their usernames, discord like. So you have to give someone your username in the first place to be added. I think it's better for privacy and against spamming.  


- **/app/templates/*.jinja**  
Contains multiple templates for each pages.
Trying to be the most reusable possible.






