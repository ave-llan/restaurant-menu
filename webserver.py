from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

## import CRUD Operations ##
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()



class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                for restaurant in session.query(Restaurant).all():
                    output += "<p>"
                    output += "%s<br>" % restaurant.name
                    output += "<a href='restaurants/%s/edit'>Edit</a><br>" % restaurant.id
                    output += "<a href='restaurants/%s/delete'>Delete</a><br>" % restaurant.id
                    output += "</p>"
                output += "<p><a href='/restaurants/new'>"
                output += "Make a new restaurant here</a></p>"
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += ("<form method='Post' enctype='multipart/form-data' "
                           "action='/restaurants/new'>"
                           "<input name='restaurantName' type='text' "
                           "placeholder = 'New Restaurant Name' >"
                           "<input type='submit' value='Create'> </form>")
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # grab the restaurant id from the path
                restaurant_id = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id = restaurant_id)[0]

                output = ""
                output += "<html><body>"
                output += "<h1>%s</h1>" % restaurant.name
                output += ("<form method='Post' enctype='multipart/form-data' "
                           "action='/restaurants/%s/edit'>") % restaurant_id
                output += ("<input name='restaurantName' type='text' "
                           "placeholder= '%s' >") % restaurant.name
                output += "<input type='submit' value='Rename'> </form>"
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # grab the restaurant id from the path
                restaurant_id = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id = restaurant_id)[0]

                output = ""
                output += "<html><body>"
                output += "<h1>Are you sure you want to delete %s?</h1>" % restaurant.name
                output += ("<form method='Post' enctype='multipart/form-data' "
                           "action='/restaurants/%s/delete'>") % restaurant_id
                output += "<input type='submit' value='Delete'> </form>"
                output += "</body></html>"
                self.wfile.write(output)
                return



        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_name = fields.get('restaurantName')[0]

                # Create new Restaurant class
                new_restaurant = Restaurant(name = restaurant_name)
                session.add(new_restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

                return

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_name = fields.get('restaurantName')[0]

                # get id from path    
                restaurant_id = self.path.split("/")[2]

                # Find and rename the Restaurant
                restaurant = session.query(Restaurant).filter_by(id = restaurant_id)[0]
                restaurant.name = restaurant_name
                session.add(restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()


            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                # get id from path    
                restaurant_id = self.path.split("/")[2]

                # Find and delete the Restaurant
                restaurant = session.query(Restaurant).filter_by(id = restaurant_id)[0]
                session.delete(restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()


        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()