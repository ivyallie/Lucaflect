# Lucaflect

An online comics magazine framework built on Flask. 
Features: 
- Display comics as "infinite canvas" or show pages individually. 
- Create "collections" of comics to make anthologies, issues, etc.
- Supports multiple users.
- Custom layout of content on index page.

## Version
The current version is 0.1 (Beta). This has been tested locally but so far I have not deployed it to an actual server. Use at your own risk.

## First time run
To set up the database:

    $ flask initialize_db

then, once flask server is running, go to /register to set up an account. The first account registered will have admin privileges by default but they can be revoked later by another user if desired.

## Notes
I primarily built this to improve my programming skills and learn my way around Flask. This is my first full-featured web app and likely has some problems. I know the code isn't as elegant as it ought to be. As with any code written by some random person on the internet, use this at your own risk. Trust no one.