Why templates are important?
last video we return some raw html string, taht is okay for something simple
for Full html pages with headers, navigation, footers and styling in python strings would be a nightmare
that's why templates coming, they let us write proper html files and just pass proper dynamic data to it.

Template inheretance:
THis will save you a lot of code duplications, for more pages, we need to copy paste alot, also if we want to change a navigation
we need to do that on every single web page, inheretence let us create a parent template with the common structure and the child
templates just fill in the parts that are different.


navigation:
we are using href='#' which is a dead link, it is just a placeholder, we are gonna update these to use URLfor, 
which is the proper way to generate urls in templates.
so there are two different usecases for using URLFOR in templates, first for route links like navigations and
second for static files like css, javascript and images.
but the benefit of using URLFOR is if you ever change your routes or change the mount path from /static to something else, then all the links will update automatically. it's more flexible and follows best practices.
instead of href='#' we write href='{{ url_for('specific_page') }}'
specific_page -> is a function, like home()
or href='{{url_for('static', path='css/main.css')}}'