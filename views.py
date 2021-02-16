from aiohttp import web
import json
import aiohttp_jinja2
import asyncio

from pathway_reader import parse_pathway
import csv

@aiohttp_jinja2.template("layout.html")
class Handle(web.View):
    async def get(self):        #get the html page
        return {}

    async def post(self):
        form = await self.request.post()        #request the data from the form
        try:
            file_name = form['filename'].filename   #get the filename of the csv file uploaded
        except:
            return {"response": "no such file found"}
        try:    
            with open(file_name) as content:    #open the file
                reader = csv.reader(content)    #read the file
                parse_pathway(csv_data=reader)  #pass the file i
        except:
            return {"response": "file didn't open or function call failure"}

        return {"response" : "thank you :D"}
            
