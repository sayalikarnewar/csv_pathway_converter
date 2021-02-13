from views import Handle

def setupRoutes(app):
    app.router.add_get('/', Handle, name="get_handle")
    app.router.add_post('/', Handle)
