C struct to Json auto-generator
===============================

An auto generator used to build a register description file for the 
[Avrora](http://compilers.cs.ucla.edu/avrora/) simulator using the 
[particle platform monitor implementation](https://github.com/ProgrammableMatter/avrora-particle-platform).

Usage
-----
    python CStructsToRegisterDescriptionJson.py
    
A windows appears showing the output which is also copied to clipboard.


Configuration
-------------
Output adjustments and overrides can be configured in 
    
    JsongConfig.py
    
The source file directory may be adjusted in 

    SourceConfig.py


    
