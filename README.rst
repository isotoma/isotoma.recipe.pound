Pound buildout recipe
=====================

This package provides buildout_recipes for the configuration of pound_.  This
is a more fully featured recipe than others we've found on PyPI, and supports
things like 500 error pages, emergency servers and configurable affinity.

We use the system pound, so this recipe will not install pound for you.  If you
wish to install pound, use `zc.recipe.cmmi`_ perhaps.

.. _buildout: http://pypi.python.org/pypi/zc.buildout
.. _pound: http://www.apsis.ch/pound/
.. _`zc.recipe.cmmi`: http://pypi.python.org/pypi/zc.recipe.cmmi

An example of a standard setup::

    [pound]
    recipe = isotoma.recipe.pound
    address = 127.0.0.1
    port = 8080
    session = COOKIE:_ZopeID:3600
    err500 = /var/www/emergency/index.html
    emergency = 127.0.0.1:8090
    backends = 
        127.0.0.1:8081
        127.0.0.1:8082
        127.0.0.1:8083

If you use pound or another loadbalancer, you might find `isotoma.recipe.portmap`_ useful too.

.. _`isotoma.recipe.portmap`: http://pypi.python.org/pypi/isotoma.recipe.portmap


Mandatory parameters
--------------------

address
    The address on which to listen for connections
port
    The port on which to listen for connections
backends
    A list of backends, supplied as ``address:port`` pairs, separated by whitespace

Optional parameters
-------------------

executable
    The path to the pound binary.  Defaults to ``/usr/sbin/pound``.
poundctl
    The path to the poundctl binary.  Defaults to ``/usr/sbin/poundctl``.
user
    The user to run pound as.  Defaults to ``www-data``.
group
    The group to run pound as.  Defaults to ``www-data``.
logfacility
    The syslog facility to which to send log output.  Defaults to ``local0``.
loglevel
    The logging level.  Defaults to '2'.
alive
    The number of seconds between checks for aliveness of previously dead backends.  Defaults to '30'.
timeout
    The timeout for HTTP requests to a backend.  Defaults to '60'.
xHTTP
    Which verbs are accepted.  See the pound manual for more details.  Defaults to '0' (accept only standard verbs).
template
    The full path to the configuration file template, if you want to customise further.  Defaults to pound.cfg template in this package.
session
    If you wish to have session affinity, provide the configuration here as ``type:id:TTL``.
emergency
    If you use an emergency server, provide the configuration here as ``address:port``.
err500
    If you wish to provide an error 500 page, provide the full path here.

Emergency Servers
-----------------

Recipes are also included to help construct emergency pages.  Pound's support
for emergency serving is pretty rudimentary, so it needs some help to provide a
decent service.  The emergency recipe:

 * provides an apache configuration suitable for use in this situation
 * processes the index page of the emergency content with a simple string substitution, so the image and css resources can be located

The index page of the emergency server is suitable for using in the err500
directive as well.

To use this, you should first create a directory containing an index.html page,
and whatever resources are needed to serve this page from apache.  In the
template, refer to all resouces using ``$baseurl``. For example, if we have::

    htdocs/index.html
    htdocs/images/logo.png

then in `index.html` put::

    <html>
        <body>
            <img src="$baseurl/images/logo.png" />
        </body>
    </html>

Then provide a recipe like::

    [emergency]
    recipe = isotoma.recipe.pound:emergency
    path = /path/to/htdocs
    interfaces = 
        127.0.0.1:8090
        32.32.32.32:emerg.example.com:80
    listen = yes
    public = http://www.emerg.example.com
    access_log = /var/log/apache2/help.help.access.log
    error_log = /var/log/apache2/help.help.error.log
    substitute = index.html

``$baseurl`` will be replaced with the value of public.

This might seem like an overly convoluted way of setting up something
relatively simple, but if you want valid and testable configurations in
continuous integration, staging and production environments this is worth
the effort.

