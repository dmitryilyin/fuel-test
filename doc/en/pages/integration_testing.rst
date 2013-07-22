====================
 Integration testing
====================

Integration testing provides functional testing for a single Puppet module or for a group of modules. To run these
tests you have to prepare specific testing manifests in the *tests* directory of your module.

These manifests usually can also be an good example of how the module can be used. Usually each of these tests check
specific parts of a module, functions or common use cases.

Fuel-test contains some scripts to make use of these testing manifests. They can run all of a module's tests and
collect their results into Jenkins using **xUnit** XML format.

Integration tests provide much wider coverage than modular ones. They can check functionality of one or more modules
in required environments. This enables both code consistency and functionality to be tested.

Test manifests are relatively easy to write, although integration testing tends to be much more useful for developers. Therefore,
it would be better to focus on integration tests rather than on unit testing.

Testing algorithm
-----------------

In order to implement integration testing you should create a special testing environment fist.
Next, you can start to apply the Puppet module inside this environment and check the results.

The process of testing can be described by the following steps:

.. image:: images/integration_tests_scheme.png
   :alt: integration tests scheme
   :align: center

1. Create a virtual system from the prepared image with a supported operating system.
2. Take a snapshot of the clean state of operating system in order to be able to revert back later.
3. Run the first test in the testing environment and save the results.
4. Revert to the snapshot of the clean state.
5. Run the next test, save the result, and revert once again.
6. Collect all the test results in xUnit XML format and put it into Jenkins.

Implementing a test
-----------------

To implement integration testing with Jenkins you need to create a set of test scripts for each Puppet module.
Each test script should create a testing environment and run all the tests for its module.
In order to simplify creating a set of test scripts it is a good idea to utilize the power of the templating engine.

This is the scheme of this process:

.. image:: images/make_tests_templates.png
   :alt: Scheme of the integration testing
   :align: center

- First you should prepare a script implementing the testing algorithm above and make it like the template.
- Use the MakeTests script to scan the directory containing Puppet modules to find all the test manifests.
- MakeTests will take each script's template and expands paths and filenames for each module and creates methods to run each test manifest.
- All of these scripts will be saved into a special directory.
- A Jenkins job is created. It should run all test methods of each test script and collect their results as XML file.

Using the MakeTests script
----------------------

The MakeTests script contains 5 classes:

- **MakeTests** - main class of the script. It provides the program startup and reading and writing of files.
- **PuppetModule** - represents each Puppet module.  MakeTests object creates a list of objects for each Puppet module.
- **PuppetTest** -  represents a single test. PuppetModule object creates a list of these objects for each test manifest.
- **Interface** - helper class.  Provides features for error and debug message output.
- **Color** - helper class. For color text output on terminal.

MakeTests accepts the following arguments:

mandatory:
- Path to directory where scripts built from templates are stored.
- Path to directory with Puppet modules to be tested.
optional:
- (-m) path to directory with puppet modules on the testing environment. It is useful when you create tests not on the
system you intend to run them.
- (-t) path to the directory with templates.
- (-f) file with default template
- (-k) keep all the  previous tests

Using templates
---------------

MakeTests uses the **jinja2** template engine. It uses by default template from **templates** directory.
You can specify another template using the -f option.

You can use this set of variables inside your template:

**General variables**

- *modules_path* - Path to puppet modules on testing host system.
- *local_modules_path* - Path to modules on the system where tests were created. Usually equals to modules_path.
- *internal_modules_path* - Path to modules inside a guest virtual system.
- *internal_manifests_path* - Path to manifests inside a guest virtual system.
- *tests_directory_path* - Path to the directory containing test files.

**PuppetModule**

- *module.name* - Name of this Puppet module.
- *module.path* - Path to the Puppet module on the system where tests were built.
- *module.tests* - A list of PuppetTest objects representing every test file of this module.
- *module.dependencies* - List of direct dependencies this module depends on.

**PuppetTest**

- *test.name* - Name of this test.
- *test.path* - Path to this test. Relative to module and excluding file name.
- *test.file* - NAme of the file which this test represents.

Template files can include other template files giving you an ability to make a complex script from many pieces. Some
of these pieces can be shared by several scripts. Templates can also extend other templates by replacing some of
its blocks.

Inside your template you can use loops, control logic and different filters. You can learn more about **jinja2**
template engine here http://jinja.pocoo.org and learn all its syntax from this
file http://jinja.pocoo.org/docs/jinja-docs.pdf

Jenkins
-------

This task is made to support integration testing

http://jenkins-product.srt.mirantis.net:8080/view/puppet_integration/
