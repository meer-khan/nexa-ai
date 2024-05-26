# nexa-ai


#Instructions to run backend

##Navigate to directory "~/Desktop/nexa-ai$" and type command: 

`uvicorn src.app:app --reload`


if some error occurs on database side and get to your linux terminal and type 
`sudo systemctl start mongod`

after start mongodb server check its status 

`sudo systemctl status mongod`

NOTE: Ubuntu shuts down mongodb server automatically after machine shutdown


Hit first command again, backend will start working
