# Photo Album App

This is a web app that allows users to save photos on their device and have the ability to search through their 
gallery for photos that meet certain criteria by using natural language through speech or text. There is use 
of Amazon's Rekogniton to index each photo with the elements in it like 'dog running' or 'a man eating'. In addition
to Rekogniton, the user can also add custom indexes to a photo during upload like "me and my dad". As this web 
application is microservice-driven web application, it uses AWS's clouformation to deploy the full product whenever 
a change is made. 