====================  =================================================================================
Tests                 |travis| |coveralls|
--------------------  ---------------------------------------------------------------------------------
Downloads             |pip dm| |pip dw| |pip dd|
--------------------  ---------------------------------------------------------------------------------
About                 |pip license| |pip wheel| |pip pyversions| |pip implem|
--------------------  ---------------------------------------------------------------------------------
Status                |version| |status|
====================  =================================================================================

About
=====

Inspired by Concordion_, and a little bit by Fitnesse_ and RobotFramework_, LiveDoc_ is a way to maintain documentation live.

The idea is to use documentation as test, so documentation is tested as well. This way you will be sure it is always updated and you can show beautiful reports to the Product Owners.

Principles
----------

- Should be simple, so `eval` will be used to process the embedded code.
- Should be easy to be used, by supporting Markdown_ to avoid hard HTML.
- Should be extensible, by allowing custom fixtures, like Concordion_ does.
- Should be powerful, by providing tools to simplify the work, just like RobotFramework_ libraries do.

Comparative
-----------

====================================  ==========  ========  ==============  =======
Feature                               Concordion  Fitnesse  RobotFramework  LiveDoc
====================================  ==========  ========  ==============  =======
Markdown support                      Yes         No        No              Yes
Customizable output                   No          No        No              Yes
Xunit integration                     Yes         Yes       Yes             Planed
REST test facilities                  No          No        Yes             Planed
Tables to write examples              Yes         Yes       Yes             Yes
Fixtures language                     Java        Many      Python or Java  Python
HTML generators integration           No          No        No              Yes
Different kind of tables              No          Yes       No              Planed
====================================  ==========  ========  ==============  =======

How does it work?
=================

LiveDoc_ parses the generated HTML, searching some special code. You can generate that code anyway you want.

In order to write Markdown_ easily, I've chosen the Concordion_ way: by adding links to ``-`` with code in the ``title`` attribute. Example:

    <a href="-" title="a = TEXT">5</a>

This will show the value, ``5`` as usual HTML text, but will assign the text to the variable ``a``. Now you can operate with it:

    <a href="-" title="a += TEXT">5</a>

And check the result:

    <a href="-" title="a == TEXT">10</a>

Or just show it (LiveDoc_ will show anything assigned to ``OUT`` variable):

    <a href="-" title="OUT = a"></a>

And you can add text in between:

    By setting the value of <a href="-" title="a = TEXT">5</a> and adding <a href="-" title="a += TEXT">5</a> more, it will return <a href="-" title="a == TEXT">10</a>.

But this is hard to be written and read, so it can be simplified by using Markdown_:

    By setting the value of [5](- "a = TEXT") and adding [5](- "a += TEXT") more, it will return [10](- "a == TEXT)".



Roadmap
=======

- **0.2.0**: fixture load
- **0.3.0**: advanced fixtures
- **0.4.0**: junit reports

FAQ
===

Does LiveDoc support python 2?
------------------------------

No. Python 2 is deprecated and will be retired on 2020, so please, move on to Python 3.


.. |travis| image:: https://img.shields.io/travis/magmax/livedoc.svg
  :target: `Travis`_
  :alt: Travis results

.. |coveralls| image:: https://img.shields.io/coveralls/magmax/livedoc.svg
  :target: `Coveralls`_
  :alt: Coveralls results_

.. |pip version| image:: https://img.shields.io/pypi/v/livedoc.svg
    :target: https://pypi.python.org/pypi/livedoc
    :alt: Latest PyPI version

.. |pip dm| image:: https://img.shields.io/pypi/dm/livedoc.svg
    :target: https://pypi.python.org/pypi/livedoc
    :alt: Last month downloads from pypi

.. |pip dw| image:: https://img.shields.io/pypi/dw/livedoc.svg
    :target: https://pypi.python.org/pypi/livedoc
    :alt: Last week downloads from pypi

.. |pip dd| image:: https://img.shields.io/pypi/dd/livedoc.svg
    :target: https://pypi.python.org/pypi/livedoc
    :alt: Yesterday downloads from pypi

.. |pip license| image:: https://img.shields.io/pypi/l/livedoc.svg
    :target: https://pypi.python.org/pypi/livedoc
    :alt: License

.. |pip wheel| image:: https://img.shields.io/pypi/wheel/livedoc.svg
    :target: https://pypi.python.org/pypi/livedoc
    :alt: Wheel

.. |pip pyversions| image::  	https://img.shields.io/pypi/pyversions/livedoc.svg
    :target: https://pypi.python.org/pypi/livedoc
    :alt: Python versions

.. |pip implem| image::  	https://img.shields.io/pypi/implementation/livedoc.svg
    :target: https://pypi.python.org/pypi/livedoc
    :alt: Python interpreters

.. |status| image::	https://img.shields.io/pypi/status/livedoc.svg
    :target: https://pypi.python.org/pypi/livedoc
    :alt: Status

.. |version| image:: https://img.shields.io/pypi/v/livedoc.svg
    :target: https://pypi.python.org/pypi/livedoc
    :alt: Status



.. _Travis: https://travis-ci.org/magmax/livedoc
.. _Coveralls: https://coveralls.io/r/magmax/livedoc

.. _@magmax9: https://twitter.com/magmax9
.. _Concordion: http://concordion.org
.. _LiveDoc: https://github.com/magmax/livedoc
.. _Fitnesse: http://fitnesse.org/
.. _RobotFramework: http://robotframework.org/
.. _Markdown: https://daringfireball.net/projects/markdown/
