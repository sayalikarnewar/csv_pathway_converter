import jinja2
import aiohttp_jinja2
from aiohttp import web

from routes import setupRoutes


app = web.Application()

#setting up the jinja template
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

#adding the routes
setupRoutes(app)

#run the web app
web.run_app(app)