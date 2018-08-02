from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file as oauth_file, client, tools

from google.appengine.ext import ndb
import webapp2
import jinja2
import os
from webapp2_extras import sessions
from models import *
from google.appengine.api import mail
<<<<<<< HEAD
from models import*
import getpass
=======
>>>>>>> 20e8d9ed38be5a24c51355dcd2e34ef51ff7d42e

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

SCOPES = 'https://www.googleapis.com/auth/calendar'

store = oauth_file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)

service = build('calendar', 'v3', http=creds.authorize(Http()))


def verification(email,password):
    #verify email and password
    #return true if exists
    #return false if account doesnt exist with given input
    return True


def calendar_event(summary,location,description,time_zone,start_time,end_time,):
    event = {
      'summary': 'Come to the Party',
      'location': '800 Howard St., San Francisco, CA 94103',
      'description': 'Its gonna be L1T.',
      'start': {
        'dateTime': '2018-09-01T09:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
      },
      'end': {
        'dateTime': '2018-09-01T17:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
      },
      'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=0'
      ],
      'attendees': [
        {'email': 'abdinajka@gmail.com'},
        {'email': 'teddymk@google.com'},
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 60},
        ],
      },
    }
    event = service.events().insert(calendarId='college.connect.cssi@gmail.com', body=event).execute()
    event_link = event.get('htmlLink')
    return event_link

def email(connect_title,time,location,user_email,user_name,mail_subject):
    sender_address = "college.connect.cssi@gmail.com"
    mail_to = user_name+" "+"<"+user_email+">"
    mail_body = user_name+""":
        Your Connect Event, """+connect_title+""", is scheduled for
        """+time+""" at """+location+"""!

        Thank you for choosing College Connect!!
        The College Connect Team
        """
    mail_html = """
        <html><head></head><body>"""+user_name+""":<br><br>
        Your Connect Event, <b>"""+connect_title+"""</b>, is scheduled for
        """+time+""" at """+location+"""!<br><br>

        Thank you for choosing College Connect!!<br>
        The College Connect Team
        </body></html>"""

    # mail_html = """
    #     <html><head></head><body>%(name)s :
    #     Your Connect Event,<b> %(title)s </b>, is scheduled for
    #     %(time)s at %(loc)s!
    #
    #     Thank you for choosing College Connect!!
    #     The College Connect Team
    #     </body></html>""" %
    #     {'name':user_name,'title':connect_title,'time':time,'loc':location}

    message = mail.EmailMessage(sender=sender_address,
                                subject = mail_subject,
                                to = mail_to,
                                body = mail_body,
                                html = mail_html)
    message.send()

class BaseHandler(webapp2.RequestHandler):              # taken from the webapp2 extrta session example
    def dispatch(self):                                 # override dispatch
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)       # dispatch the main handler
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class WelcomeHandler(BaseHandler):
    def get(self):
        welcome_template = JINJA_ENVIRONMENT.get_template('templates/welcome.html')
        self.response.write(welcome_template.render())

    def post(self):
        email = self.request.get('email')
        password = self.request.get('password')

        if ((verification(email,password))):
            user = User.query().filter(User.email == email).fetch()[0]
            self.session['user']= email
            user_dict = {'user':user}
            self.redirect('/dashboard')
        else:
            pass
            #display error message in welcome

class SignUpHandler(BaseHandler):
    def get (self):
        signup_template=JINJA_ENVIRONMENT.get_template('templates/signup.html')
        self.response.write(signup_template.render())
    def post(self):
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        email = self.request.get('email')
        password = self.request.get('password')
        college = self.request.get('college')
        courses = self.request.get('courses') # list
        profile_pic = self.request.get('profile_pic')
        name = [first_name,last_name]

        new_user = User(name = name, email = email,
                        password = password, college = college,
                        profile_pic = profile_pic,
                        friends=[])

        # if not mail.is_email_valid(email):
        #     self.get()  # Show the form again.
        # else:
        #     confirmation_url = create_new_user_confirmation(email)
        #     sender_address = "college.connect.cssi@gmail.com"
        #     subject = 'Confirm your registration'
        #     body = """Thank you for creating an account!
        #     Please confirm your email address by clicking on the link below:
        #     {}""".format(confirmation_url)
        #     mail.send_mail(sender_address, email, subject, body)

        new_user = User(name = name, email = email,
                        password = password, college = college,
                        profile_pic = profile_pic, college_pic = "",
                        friends=[],)

        new_user.put()
        self.session['user'] = email
        self.redirect('/dashboard')

class DashboardHandler(BaseHandler):

    def get(self): #get rid of eventually or check to see if signed in
        all_posts_query = FeedMessage.query().order(-FeedMessage.date)
        all_posts = all_posts_query.fetch()
        post_values = {'post': all_posts}
        dashboard_template = JINJA_ENVIRONMENT.get_template('templates/dashboard.html')
        self.response.write(dashboard_template.render(post_values))

        # # user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        # # email("Party","7/31/18 4:00pm","The moon","abdinajka@gmail.com","Najib","Here is your email")

    def post(self):
        post_content = self.request.get('status')

        if len(post_content)>0:
            new_post = FeedMessage(post=post_content)
            new_post.put()

        self.redirect('/dashboard')

class FeedHandler(BaseHandler):
    def get(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        user_dict={'user':user}
        feed_template = JINJA_ENVIRONMENT.get_template('templates/partials/feed.html')
        self.response.write(feed_template.render(user_dict))

    def post(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]

class UserProfileHandler(BaseHandler):
    def get (self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        user_dict={'user':user}
        userprofile_template = JINJA_ENVIRONMENT.get_template('templates/userprofile.html')
        self.response.write(userprofile_template.render(user_dict))

    def post(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        user_dict={'user':user}
        newsfeed_template = JINJA_ENVIRONMENT.get_template('templates/userprofile.html')

class MessagesHandler(BaseHandler):
    def get (self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        user_dict={'user':user}
        messages_template = JINJA_ENVIRONMENT.get_template('templates/messages.html')
        self.response.write(messages_template.render(user_dict))

    def post(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        user_dict={'user':user}

class HostConnectHandler(BaseHandler):
    def get(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        user_dict={'user':user}
        hostconnect_template = JINJA_ENVIRONMENT.get_template('templates/hostconnect.html')
        self.response.write(hostconnect_template.render(user_dict))

    def post(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        time = self.request.get('time')
        date = self.request.get('date')

        durration = self.request.get('durration')
        location = self.request.get('location')
        connect_title = self.request.get('title')
        course = self.request.get('course')
        new_ConnectEvent = ConnectEvent(connect_time = time_date, connect_location = location,
                                durration = durration, connect_title = connect_title, course = course)
        new_ConnectEvent_key = new_ConnectEvent.put()
        users_keys = [user.key]
        new_UserConnectEvent = UserConnectEvent(users=users_keys,
                                                connect_event=new_ConnectEvent_key)
        new_UserConnectEvent.put()

        email(connect_title,time,location,user.email,user.name,"College Connect: Your Connect Event is Scheduled!")

class JoinConnectHandler(BaseHandler):
    def get(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        user_dict={'user':user}
        joinconnect_template = JINJA_ENVIRONMENT.get_template('templates/joinconnect.html')
        self.response.write(joinconnect_template.render(user_dict))

    def post(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]

class FriendsHandler(BaseHandler):
    def get(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        user_dict={'user':user}
        friends_template = JINJA_ENVIRONMENT.get_template('templates/friends.html')
        self.response.write(freinds_template.render(user_dict))

    def post(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        # friend_added = self.request.get('friends_added') #if just one friend
        friends_added = self.request.get('friends_added')
        user.friends.extend(friend_added)

class CoursesHandler(BaseHandler):
    def get(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        user_dict={'user':user}
        courses_template = JINJA_ENVIRONMENT.get_template('templates/courses.html')
        self.response.write(courses_template.render(user_dict))

    def post(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]

class ViewConnectsHandler(BaseHandler):
    def get(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        user_dict={'user':user}
        viewconnects_template = JINJA_ENVIRONMENT.get_template('templates/partials/viewconnects.html')
        self.response.write(viewconnects_template.render(user_dict))

    def post(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]

<<<<<<< HEAD
class AboutUsHandler(BaseHandler):
    def get(self):
        creators_template = JINJA_ENVIRONMENT.get_template('templates/aboutus.html')
        self.response.write(creators_template.render())
=======
class SettingsHandler(BaseHandler):
    def get(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
        user_dict={'user':user}
        settings_template = JINJA_ENVIRONMENT.get_template('templates/partials/settings.html')
        self.response.write(settings_template.render(user_dict))

    def post(self):
        user = User.query().filter(User.email == self.session.get('user')).fetch()[0]
>>>>>>> 20e8d9ed38be5a24c51355dcd2e34ef51ff7d42e

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'some-secret-key',
}

app = webapp2.WSGIApplication([
    ('/', WelcomeHandler),
    ('/signup', SignUpHandler),
    ('/dashboard', DashboardHandler),
    ('/feed', FeedHandler),
    ('/userprofile', UserProfileHandler),
<<<<<<< HEAD
    ('/hostconnect', HostConnectHandler),
    ('/joinconnect', JoinConnectHandler),
    ('/friends', FriendsHandler),
    ('/courses', CoursesHandler),
    ('/upcomingconnects', UpcomingConnectsHandler),
    ('/aboutus', AboutUsHandler)
=======
    ('/hostconnect',HostConnectHandler),
    ('/joinconnect',JoinConnectHandler),
    ('/friends',FriendsHandler),
    ('/courses',CoursesHandler),
    ('/messages',MessagesHandler),
    ('/settings',SettingsHandler),
    ('/viewconnects',ViewConnectsHandler)
>>>>>>> 20e8d9ed38be5a24c51355dcd2e34ef51ff7d42e
], debug=True, config=config)
