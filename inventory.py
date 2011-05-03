import cgi
import os
import datetime
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Item(db.Model):
    code = db.IntegerProperty()
    name = db.StringProperty()
    value = db.FloatProperty()
    owner = db.StringProperty()
    owned = db.StringProperty()
    usage = db.StringProperty()
    broken = db.StringProperty()
    unwanted = db.StringProperty()
    username = db.UserProperty()
    timestamp = db.DateTimeProperty()
    
class UserTest(webapp.RequestHandler):
    def get(self):
        pass
        

class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {}
        self.response.out.write(template.render('templates/index.html', template_values))
        
class CreateEntry(webapp.RequestHandler):
    def get(self):
        self.user_name = users.get_current_user()
        if not self.user_name:
            self.redirect(users.create_login_url(self.request.uri))

        #add item code here
        items = Item.all().order('-code')

        self.item_code=1
        if items.count() > 0:
            self.item_code = items[0].code+1
        
        template_values = {'item_code': self.item_code,
                           'user_name': self.user_name,
                           }
        self.response.out.write(template.render('templates/createitem.html', template_values))

    def post(self):
        self.user_name = users.get_current_user()
        if not self.user_name:
            self.redirect(users.create_login_url(self.request.uri))
        #retrieves the information from the form
        #creates and adds the item to the database system
        newitem = Item()
        newitem.code        = int(self.request.get("code"))
        newitem.name        = self.request.get("name")
        newitem.value       = float(self.request.get("value"))
        newitem.owner       = self.request.get("owner")
        newitem.owned       = self.request.get("owned")
        newitem.usage       = self.request.get("usage")
        newitem.broken      = self.request.get("broken")
        newitem.unwanted    = self.request.get("unwanted")
        newitem.username    = self.user_name
        newitem.timestamp   = datetime.datetime.now()
        newitem.put()
        
        template_values = {'item_code': str(newitem.code),
                           'item_name': newitem.name,
                           'item_value': str(newitem.value),
                           'item_owner': newitem.owner,
                           'item_owned': newitem.owned,
                           'item_usage': newitem.usage,
                           'item_broken': newitem.broken,
                           'item_unwanted': newitem.unwanted,
                           'item_username': newitem.username,
                           'item_timestamp': newitem.timestamp,
                           }
        
        self.response.out.write(template.render('templates/newitem.html', template_values))
        

class EditEntry(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('I still need to be written...')   

class DeleteEntry(webapp.RequestHandler):
    def get(self):
        self.user_name = users.get_current_user()
        if not self.user_name:
            self.redirect(users.create_login_url(self.request.uri))

        items = db.GqlQuery("SELECT * FROM Item ORDER BY code")
        num_items = items.count()
        has_items = bool(num_items)

        template_values = {'items': items,
                           'has_items': has_items,
                           'num_items': num_items,
                           }
            
        self.response.out.write(template.render('templates/deleteitem.html', template_values))
        
    def post(self):
        self.user_name = users.get_current_user()
        if not self.user_name:
            self.redirect(users.create_login_url(self.request.uri))
        for response in Item.all().filter("code =",int(self.request.get("code"))):
            response.delete()
    
        self.response.out.write('''
        <html>
            <body>
                <h1>Item(s) Deleted!</h1>
                <h2><a href="/">Back to Home</a></h2>
            </body>
        </html>
        ''')
        
class ListEntries(webapp.RequestHandler):
    def get(self):
        
        items = db.GqlQuery("SELECT * FROM Item ORDER BY code")
        num_items = items.count()
        has_items = bool(num_items)
        
        template_values = {'items': items,
                           'has_items': has_items,
                           'num_items': num_items,
                           }
        self.response.out.write(template.render('templates/listitems.html', template_values))
        
class ItemPage(webapp.RequestHandler):
    def get(self, item_code):
        for response in Item.all().filter("code =",int(item_code)):
            template_values = {'item_code': str(response.code),
                               'item_name': response.name,
                               'item_value': str(response.value),
                               'item_owner': response.owner,
                               'item_owned': response.owned,
                               'item_usage': response.usage,
                               'item_broken': response.broken,
                               'item_unwanted': response.unwanted,
                               }
        
        self.response.out.write(template.render('templates/itempage.html', template_values))
        

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/createitem', CreateEntry),
                                      ('/edititem', EditEntry),
                                      ('/deleteitem', DeleteEntry),
                                      ('/listitems', ListEntries),
                                      ('/usertest', UserTest),
                                      (r'/(\d+)', ItemPage)
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
