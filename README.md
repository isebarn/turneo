# How to run it
You need pipenv installed and then you do

	pipenv install
	pipenv shell
	flask run

You must have the `.env` file configured

# .env

	FLASK_APP=main
	FLASK_ENV=development

	DB_USER=<user>
	DB_PWD=<password>
	DB_HOST=<mongo server URL>
	DB_NAME=<database name>

# How to create a collection

If you need a collection called *User* with the fields

	User
		id
		name
		birthday
		float
		alive
		facts

Add to the file `schema.txt`

	table user {
		id int [pk, increment]
		name varchar
		birthday datetime
		age float
		alive boolean
		facts dict
	}

and run

	cd templates
	python generate.py

This will generate the following endpoints

	GET http://127.0.0.1:5000/api/user
	POST http://127.0.0.1:5000/api/user
	PATCH http://127.0.0.1:5000/api/user

As well as `MongoEngine` model

	class User(Extended):
		name = StringField()
		birthday = DateTimeField()
		age = FloatField()
		alive = BooleanField()
		facts = DictField()


# Example usage of endpoints

## GET
*Use to retrieve all users, optionally matching attributes*

	GET http://127.0.0.1:5000/api/user
	GET http://127.0.0.1:5000/api/user?name='John'
	GET http://127.0.0.1:5000/api/user?age=12
	GET http://127.0.0.1:5000/api/user?name='John'&age=12

## POST

*Use to create a new user*

	POST http://127.0.0.1:5000/api/user
	json = {
		name: "John",
		birthday: "2021-01-01",
		age: 12
		alive: true
		facts: {
			"fears": ["bees", "honey"],
			"likes": ["beers", "honeys"],
			"salary": 30000
		}
	}

	# Response
	{
	  "_cls": "User",
	  "_id": {
	    "$oid": "61a9ffc1d0ad33f23b30dba6"
	  },
	  "age": 12.0,
	  "alive": true,
	  "birthday": "2021-01-01T00:00:00",
	  "facts": {
	    "fears": [
	      "bees",
	      "honey"
	    ],
	    "likes": [
	      "beers",
	      "honeys"
	    ],
	    "salary": 30000
	  },
	  "name": "John"
	}


Note the `$oid` value, it's important for `PATCH`

## PATCH

*Use to update a user*

Given user

	{
	  "_cls": "User",
	  "_id": {
	    "$oid": "61a9ffc1d0ad33f23b30dba6"
	  },
	  "age": 12.0,
	  "alive": true,
	  "birthday": "2021-01-01T00:00:00",
	  "facts": {
	    "fears": [
	      "bees",
	      "honey"
	    ],
	    "likes": [
	      "beers",
	      "honeys"
	    ],
	    "salary": 30000
	  },
	  "name": "John"
	}

To update his age to 10, call

	PATCH 
	POST http://127.0.0.1:5000/api/user
	json = {
	  "_cls": "User",
	  "_id": {
	    "$oid": "61a9ffc1d0ad33f23b30dba6"
	  },
	  "age": 41.0,
	}

	# Response
	{
	  "_cls": "User",
	  "_id": {
	    "$oid": "61a9ffc1d0ad33f23b30dba6"
	  },
	  "age": 10.0,
	  "alive": true,
	  "birthday": "2021-01-01T00:00:00",
	  "facts": {
	    "fears": [
	      "bees",
	      "honey"
	    ],
	    "likes": [
	      "beers",
	      "honeys"
	    ],
	    "salary": 30000
	  },
	  "name": "John"
	}	