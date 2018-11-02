# "Professor Oak" Laboratory Management Server

[![Build Status](https://travis-ci.com/canismarko/professor_oak.svg?branch=master)](https://travis-ci.com/canismarko/professor_oak)

Install all python dependcies with `pip install -r requirements.txt`
from the project root. Run `python manage.py runserver` to start the
development server. This should NOT be used for deployment. Now visit
`http://localhost:8000` in a web browser to see the site.

## Project Architecture

Much of this information is redundant with the Django
documentation. Refer to
[https://docs.djangoproject.com/en/1.8/](Django's documentation)
for more information.

The project is organized into apps (folders) for different
functionality. Components common to all apps are stored in the
`professor_oak` directory.

## Webpage Request Roadmap

After you enter the site's url in your browser, the web server
generates an HttpRequest and passes it off to Django. Django looks at
the url of the request and compares it against the expressions listed
in `professor_oak/urls.py`. In some cases, if the expression is
followed by `include(<app_name>)`, Django will look in that app's
directory for a file named `urls.py` and continue checking there.

Assuming Django finds a matching expression, it finds and calls the
corresponding view function in `views.py`. A view function must return
an `HttpResponse` object which then gets sent back to the browser. In
our case, most views will not generate HTML themselves but will look
up a template file. The view may generate some data to put in to the
template before returning it; this is known as a *context*. Global
templates live in the `professor_oak/templates` directory and
app-spefic templates live in the corresponding `app_name/templates`
directories.

## Model Descriptions

In Django, a *Model* class is equivalent to a database table. An
instance of that class corresponds to a database row. Professor oak
defines many models, here are some of the main ones.

### Chemical Inventory Models

**Chemical** - This is the general idea of a chemical (eg Lithium
  hydroxide). It is *not* a bottle of lithium hydroxide, just the
  general concept of lithium hydroxide. An instance of `Chemical`
  describes safety information among other things.

**Container** - This is a specific container of a chemical. This could
  be a specific bottle of lithium hydroxide in your lab. Attributes
  associated with a container include things like its location, amount
  and owner.
