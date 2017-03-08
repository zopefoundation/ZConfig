===================================
 Using Components to Extend Schema
===================================

.. XXX This section needs a lot of work, but should get people started
   who really want to add new pieces to ZConfig-configured applications.

It is possible to use schema components and the ``%import``
construct to extend the set of section types available for a specific
configuration file, and allow the new components to be used in place
of standard components.

The key to making this work is the use of abstract section types.
Wherever the original schema accepts an abstract type, it is possible
to load new implementations of the abstract type and use those instead
of, or in addition to, the implementations loaded by the original
schema.

Abstract types are generally used to represent interfaces.  Sometimes
these are interfaces for factory objects, and sometimes not, but
there's an interface that the new component needs to implement.  What
interface is required should be documented in the
``description`` element in the ``abstracttype`` element;
this may be by reference to an interface specified in a Python module
or described in some other bit of documentation.

The following things need to be created to make the new component
usable from the configuration file:


#. An implementation of the required interface.

#. A schema component that defines a section type that contains
   the information needed to construct the component.

#. A ``datatype`` function that converts configuration data to an
   instance of the component.

For simplicity, let's assume that the implementation is defined by a
Python class.

The example component we build here will be in the :mod:`noise`
package, but any package will do.  Components loadable using
``%import`` must be contained in the ``component.xml`` file;
alternate filenames may not be selected by the ``%import``
construct.

.. highlight:: xml

Create a ZConfig component that provides a section type to support
your component.  The new section type must declare that it implements
the appropriate abstract type; it should probably look something like
this::


 <component prefix="noise.server">
  <import package="ZServer"/>

  <sectiontype name="noise-generator"
               implements="ZServer.server"
               datatype=".NoiseServerFactory">

    <!-- specific configuration data should be described here -->

    <key name="port"
         datatype="port-number"
         required="yes">
      <description>
        Port number to listen on.
      </description>
    </key>

    <key name="color"
         datatype=".noise_color"
         default="white">
      <description>
        Silly way to specify a noise generation algorithm.
      </description>
    </key>

  </sectiontype>
 </component>


This example uses one of the standard ZConfig datatypes,
**port-number**, and requires two additional types to be
provided by the :mod:`noise.server` module:
``NoiseServerFactory`` and ``noise_color()``.

The ``noise_color()`` function is a datatype conversion for a
key, so it accepts a string and returns the value that should be used:

.. code-block:: python

  _noise_colors = {
      # color -> r,g,b
      'white': (255, 255, 255),
      'pink':  (255, 182, 193),
      }

  def noise_color(string):
      if string in _noise_colors:
          return _noise_colors[string]
      else:
          raise ValueError('unknown noise color: %r' % string)


``NoiseServerFactory`` is a little different, as it's the datatype
function for a section rather than a key.  The parameter isn't a
string, but a section value object with two attributes, ``port``
and ``color``.

Since the **ZServer.server** abstract type requires that the
component returned is a factory object, the datatype function can be
implemented at the constructor for the class of the factory object.
(If the datatype function could select different implementation
classes based on the configuration values, it makes more sense to use
a simple function that returns the appropriate implementation.)

A class that implements this datatype might look like this:

.. code-block:: python


  from ZServer.datatypes import ServerFactory
  from noise.generator import WhiteNoiseGenerator, PinkNoiseGenerator

  class NoiseServerFactory(ServerFactory):

    def __init__(self, section):
        # host and ip will be initialized by ServerFactory.prepare()
        self.host = None
        self.ip = None
        self.port = section.port
        self.color = section.color

    def create(self):
        if self.color == 'white':
            generator = WhiteNoiseGenerator()
        else:
            generator = PinkNoiseGenerator()
        return NoiseServer(self.ip, self.port, generator)


You'll need to arrange for the package containing this component to be
available on Python's ``sys.path`` before the configuration file is
loaded; this is mostly easily done by manipulating the
``PYTHONPATH`` environment variable.

Your configuration file can now include the following to load and use
your new component::


  %import noise

  <noise-generator>
    port 1234
    color white
  </noise-generator>
