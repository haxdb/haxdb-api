Modules
========

Each haxdb module is an actual python module.  Each module should be importable and have at least two functions: init() and run()


init(haxdb)
----------------------

Every module has it's init() function called before any module's run() function is called.  This allows you to set up any database tables that other modules might be reliant upon.

The init function should have one parameter: an instance of haxdb.


run()
------

After all init() functions are called then each module will have it's run() function called.  The run() function has no parameters.
