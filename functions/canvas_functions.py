#Debug offset is used to offset the date by a certain amount of weeks. This is useful for testing purposes. Set to 0 for normal use.
debug_offset = 0
#Set to true to ovveride the "has submitted" check. This is useful for testing purposes. Set to false for normal use.
ovveride = False

from canvasapi import Canvas
from datetime import datetime, timedelta
from markdownify import markdownify

class CanvasFunctions:
        def __init__(self, api_key, api_url):
            self.api_key = api_key
            self.api_url = api_url
            self.canvas = Canvas(self.api_url, self.api_key)

        def get_courses(self):
            user = self.canvas.get_current_user()
            courses = user.get_favorite_courses()

            #put courses in array
            return_courses = []
            for course in courses:

                return_courses.append([course.name, course.id, course])
     
            return return_courses

        def get_assignments(self, course):
            assignments = course.get_assignments()
            
            #put assignments in array
            return_assignments = []
            for assignment in assignments:
                return_assignments.append(assignment)
            
            return return_assignments

        def format_assignments(self):
            #get courses
            courses = self.get_courses()
            due_today = []
            due_this_week = []
            due_later = []
            unspecified = []
            for course in courses:

                #get assignments for each course
                assignments = self.get_assignments(course[2])

                #group assignments by due today, due this week, due later
                
                for assignment in assignments:
                    if assignment.has_submitted_submissions !=False and ovveride == False:
                        pass
                    else:
                        if(assignment.due_at != None):
                            due_at = datetime.strptime(assignment.due_at, '%Y-%m-%dT%H:%M:%SZ')
                            if due_at > datetime.now()-timedelta(weeks=debug_offset)-timedelta(days=1):
                                if due_at.date() == datetime.now().date()-timedelta(weeks=debug_offset):
                                    due_today.append([self.format_text(assignment.name, assignment.html_url), course[2].name, datetime.strptime(assignment.due_at, '%Y-%m-%dT%H:%M:%SZ').strftime("%A, %B %d: %I:%M %p")])
                                elif due_at.date() <= datetime.now().date() + timedelta(days=7)-timedelta(weeks=debug_offset):
                                    due_this_week.append([self.format_text(assignment.name, assignment.html_url), course[2].name, datetime.strptime(assignment.due_at, '%Y-%m-%dT%H:%M:%SZ').strftime("%A, %B %d: %I:%M %p")])
                                else:
                                    due_later.append([self.format_text(assignment.name, assignment.html_url), course[2].name, datetime.strptime(assignment.due_at, '%Y-%m-%dT%H:%M:%SZ').strftime("%A, %B %d: %I:%M %p")])
                        else:
                            unspecified.append([self.format_text(assignment.name, assignment.html_url), course[2].name, "No Due Date Specified"])
                           
            print(unspecified)
            return due_today, due_this_week, due_later, unspecified


        
        def format_text(self, description, url):
            markdowned =  markdownify(description)
            return f"[{markdowned}]({url})"
