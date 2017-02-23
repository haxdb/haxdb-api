Modules
========

Each haxdb module is an actual python module.  Each module should be importable and have at least two functions: init() and run()


init(config, db, api)
----------------------

Every module has it's init() function called before any module's run() function is called.  This allows you to set up any database tables that other modules might be reliant upon.

The init() function has 3 parameters:

**config** is a dictionary of sections in the application config file.  Each section is a dictionary of configuration values for that section.

**db** is an instance of the db class.

**api** is an instance of api which has a flask app reference (api.app), permission decorators, and data functions (api.output, api.get)



run()
------

After all init() functions are called then each module will have it's run() function called.  The run() function has no parameters.