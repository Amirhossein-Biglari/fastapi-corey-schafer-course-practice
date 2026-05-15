We build out backend authentication infrastrucutre (password hashing, json web token utilities, login endpoints)
then we create registration and login forms frontend and wire everything together.

This video covers authentication, in next video we use authentication to protect routes and make sure users are authorized
to do certain things.

authentication -> answers the question of who are you?
authorization -> what are you allowed to do?

Need to install three new packages for authentication
1- pwlib[argon2] -> password hashing, more resistent to gpu cracking attacks than bcrypt?
2- pyjwt -> creating and veryfing jwt tokens, json web token authorization,
3- pydantic-settings -> managing our configurations (instead of python .env, why? 1- pydantic centeralize all of our configurations into one settings module, 2- it validates types automatically, 3- it fails fast, 4- it uses secrets string from pydantic to avoid accidentally exposing secrests in logs or print statements) -> it still loads things from .env file so there is no change
in your workflow, it is cleaner more modern fastapi approach


We are gonna create a config.py file that loads our application configuration from environment variables like secret key for
sign in token, it is like python .env but with validation built-in
config.py file defines what settings our application needs, which comes from env variables or .env file

To generate a secret key you can use this code in terminal:
python -c "import secrets; print(secrets.token_hex(32))"

