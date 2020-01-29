#!/usr/bin/env python
import os
import jinja2
import webapp2
import time
from models import Tasks


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        self.response.out.write(template.render(params))


class TaskHandler(BaseHandler):
    def get(self):
        tasks = Tasks.query(Tasks.archived == False).fetch()
        tasks.sort(key=lambda r: r.date, reverse=True)

        params = {"tasks": tasks}

        return self.render_template("tasks.html", params=params)

    def post(self):
        entry = self.request.get("entry")

        if '<script>' not in entry and not entry == '':
            task = Tasks(task=entry)
            task.put()
            time.sleep(0.1)

        else:
            pass

        return self.redirect_to("tasks")


class EditTaskHandler(BaseHandler):
    def get(self, task_id):
        task = Tasks.get_by_id(int(task_id))
        params = {"task": task}
        return self.render_template("edit_task.html", params=params)

    def post(self, task_id):
        edited = self.request.get("edit")
        task = Tasks.get_by_id(int(task_id))
        task.task = edited
        task.put()
        time.sleep(0.1)
        return self.redirect_to("tasks")


class ArchiveTaskHandler(BaseHandler):
    def get(self, task_id):
        task = Tasks.get_by_id(int(task_id))
        task.archived = True
        task.put()
        time.sleep(0.1)

        tasks = Tasks.query(Tasks.archived == False).fetch()
        tasks.sort(key=lambda r: r.date, reverse=True)

        params = {"tasks": tasks,
                  "task_id": task_id}

        return self.render_template("archive_task.html", params=params)

    def post(self, task_id):
        task = Tasks.get_by_id(int(task_id))
        task.archived = False
        task.put()
        time.sleep(0.1)

        return self.redirect_to("tasks")


class ViewArchivedHandler(BaseHandler):
    def get(self):

        tasks = Tasks.query(Tasks.archived == True).fetch()
        tasks.sort(key=lambda r: r.date, reverse=True)

        if tasks:
            params = {"tasks": tasks}
        else:
            params = {"message": "There are no completed tasks."}

        return self.render_template("archived.html", params=params)


class RestoreTaskHandler(BaseHandler):
    def post(self, task_id):
        task = Tasks.get_by_id(int(task_id))
        task.archived = False
        task.put()
        time.sleep(0.1)

        if Tasks.query(Tasks.archived == True).fetch():
            return self.redirect_to("archived")
        else:
            return self.redirect_to("tasks")


class DeleteTaskHandler(BaseHandler):
    def get(self, task_id):
        task = Tasks.get_by_id(int(task_id))
        params = {"task": task}
        return self.render_template("delete_task.html", params=params)

    def post(self, task_id):
        task = Tasks.get_by_id(int(task_id))
        task.key.delete()
        time.sleep(0.1)

        return self.redirect_to("tasks")


app = webapp2.WSGIApplication([
    webapp2.Route('/', TaskHandler, name="tasks"),
    webapp2.Route('/archived-tasks', ViewArchivedHandler, name="archived"),
    webapp2.Route('/task/<task_id:\d+>/edit', EditTaskHandler),
    webapp2.Route('/task/<task_id:\d+>/archive', ArchiveTaskHandler),
    webapp2.Route('/task/<task_id:\d+>/restore', RestoreTaskHandler),
    webapp2.Route('/task/<task_id:\d+>/delete', DeleteTaskHandler),
], debug=True)
