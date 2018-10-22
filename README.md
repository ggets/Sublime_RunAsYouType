# Run As You Type for SublimeText v3
Create a command (you can bind to a key) to evaluate the contents of the current view (tab) without saving it (even for new tabs)
(untested on Sublime text v2)

In the sublime-settings file you can set the program to be executed for the desired syntax. You get these by default:

PHP: php.exe

SQL: mysql.exe

JavaScript: node.exe

Plain text: calculate semi-colon-separated statements with a php script (provided in the scripts subdir)


If the binaries are not located in any dir from your PATH variable, you will have to include the full directory.
With MySQL for convinience you can set your default settings in the global "my.cnf" file, in your home in ".my.cnf", or alternatively in another file and then include it in the settings.
