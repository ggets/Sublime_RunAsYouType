# Run As You Type

  A Sublime Text plugin to allow creating a command (you can bind to a key) to evaluate the contents of the current view (tab) without saving it (even for new, unsaved tabs). It's just like an interactive console.

## Requirements:

* Sublime Text v3+

## Features:

*	Hit **`F10`** and evaluate the code in the current view/buffer


* In the sublime-settings file you can set the program to be executed for the desired syntax.
You get these by default:

**PHP**: php.exe

**SQL**: mysql.exe

**JavaScript**: node.exe

**Python**: python3.exe

**JSON**: jq.exe

**Plain text**: calculate semi-colon-separated statements with a php script (provided in the scripts subdir)



If the binaries are not located in any dir from your PATH variable, you will have to include the full directory path.
With MySQL for convinience you can set your default settings in the global "my.cnf" file, in your home in ".my.cnf", or alternatively in another file and then include it in the settings.


## Installation

### Sublime Text [Package Control][] package manager

1. Open "Package Control: Install Package" from the Command Palette (**`Ctrl/Super`** + **`Shift`** + **`P`**).
2. Select the "Run As You Type" option to install.

[Package Control]: http://wbond.net/sublime_packages/package_control

### Manual installation via Git

```bash
git clone https://github.com/ggets/Sublime_RunAsYouType.git "Run As You Type"
```


**Ideas and pull requests are welcome**

To-do:
  Add menu to pick from different scripts (i.e. PHP Calculus, cURL, etc...)
