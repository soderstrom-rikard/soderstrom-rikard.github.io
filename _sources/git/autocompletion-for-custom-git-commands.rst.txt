Autocompletion for custom git commands
======================================

Custom git commands, or git extensions, can be used to make highly specialized commands for the project
you are currently working in. This is great and all, but they do not have autocompletion as normal git commands.

So let us fix that.

complete & compgen utilities
----------------------------
``compgen`` is responsible for generating a list of matches given some options,
while ``complete`` specifies how any argument to a given match should be completed.

Essentially ``compgen`` says, hey dude, I got this list of matches for you, and then ``complete`` say, oh really?
Well for that match I have the following arguments for you to begin matching against.

``complete`` and ``compgen`` share the following options ``abcdefgjksuv]``.

* ``-a`` Names of Alias
* ``-b`` Names of Builtins (shell)
* ``-c`` Names of Commands (all available commands in your path)
* ``-d`` Names of Directory
* ``-e`` Names of Exported shell variables
* ``-f`` Names of Files and Functions
* ``-g`` Names of Groups
* ``-j`` Names of Job
* ``-k`` Names of Keywords reserved by the shell
* ``-s`` Names of Services
* ``-u`` Names of Users
* ``-v`` Names of Variables (none exported shell variables)

compgen
```````
From the little intro we have learned that ``compgen`` somehow creates some list of matches.
With the options staring us in or face it becomes rather easy. For example, ``compgen -b`` will return the complete
list of all builtin shell commands, one item per line. That's it. It is yours, to do what every you wish to do with.

For example filter it.

complete
````````
Let us start simple and with an example.

.. code-block:: bash

    complete -W '-a -b ..' compgen

From the manual [#BASH_MANUAL]_ we see that ``-W`` causes any word in the following string to be used as completions.
So in the above example when we type *compgen <TAB><TAB>* the following line get printed in the console.

::

    .. -a -b

If we type *-* then *..* is removed from the line. Perfect, we have autocompletion.
But that isn't very interesting. Instead we are going to register a function that will return the matches for us.

Before that, there are some things we should know. In the environment the function is run, there are some environmental
variables available for us. These are:

========================== ===================================================================
Variable                   Description
========================== ===================================================================
``COMP_WORDS``             A bash array containing each individual word of the current line
``COMP_CWORD``             The index in ``COMP_WORDS`` that contains the word under the cursor
``COMP_WORDS[COMP_CWORD]`` Word under the cursor
``COMP_REPLY``             Returns the possible completions back to ``complete``
========================== ===================================================================

Now we have our building blocks. So let us do something silly. Everytime compgen is the command.
Return the previously written word when pressing tab.

.. code-block:: bash

    _previous()
    {
        COMPREPLY=(${COMP_WORDS[COMP_CWORD-1]})
    }

    complete -F _previous compgen

But how do we signal that its time to stop?
One way is to return a non zero exit status. This will however inform bash that something is wrong, ie probably not
what we want to do. Instead we need to return an empty ``COMPREPLY``. So a simple if something, else something would
suffice.

Clearing completions for a certain command
''''''''''''''''''''''''''''''''''''''''''''''
In order to clear the completions for a command, it needs to be registered with the ``-r`` option.
So to clear completions for ``compgen``, do 

.. code-block:: bash

    complete -r compgen

Listing all registered completions
''''''''''''''''''''''''''''''''''
What if we forgot or are interested in knowing how a certain command performs autocompletion.
Well that is also simple, just run the ``complete`` command without any arguments, like so

.. code-block:: bash

    complete

This is the same as supplying the ``-p`` option, p for print.

git comlete wrappers
--------------------
Git is extensible and modular, so it already have a way to map your "*git custom command*". Git essentially searches
for any command in PATH (or current directory) starting with *git-* and registers the function
``_git_YOUR_CUSTOM_COMMAND``  with ``complete`` if you have created that function. This is done
on the fly (in one or more subshells), so we never actually see these registration.
But this is really nice, since all we need to do is ensure that git finds your script and your bash function.
And voila! autocompletions in git is here.

To show this, let's create an empty executable in a temporary folder, add it to our path and re-read the git
completion file. Then simply define a ridicolous function with any dashes replaced with an underscore.
Voila! git autocompletion for a custom command

.. code-block:: bash
   :emphasize-lines: 6,7

    TMP=`mktemp -d`                                     # Create tmp dir
    touch $TMP/git-custom-command                       # In tmp dir add file git-custom-command
    chmod u+x $TMP/git-custom-command                   # Make it executable
    export PATH=$TMP:$PATH                              # Place it in your path
    source /usr/share/bash-completion/completions/git   # Re-read completions (or start a subshell)
    _git_custom_command() { COMPREPLY=("c1 c2"); }      # Create your autocompletion function
    git custom-command<TAB><TAB>                        # Autocomplete !
    rm -rf $TMP                                         # Clean up your mess


git compgen wrappers
````````````````````
If you type *__git<TAB><TAB>* and you will find a list of a number of internal git functions. Generated by git 
completions script. There are a lot of them here. So let us focus on a few of them.

================================= ===============================================================================
git bash function                 Description
================================= ===============================================================================
``__gitcomp``                     Generates a ``COMPREPLY`` from space,tab or newline seperated list
``__gitcomp_nl``                  Creates an empty ``COMPREPLY`` and fills it from newline seperated words
``__git_complete``                Creates custom command completions, as shown in previous example
``__gitdir``                      Gives the path to current repository *.git* folder
``__git_find_on_cmdline``         Returns subcommand if it is present on the command line
``__git_heads``                   List all available branches
``__git_list_all_commands``       Ask git to tell us which commands exists
``__git_list_porcelain_commands`` Filter out plumbing commands and return the user friendly ones
``__git_main``                    Bind everything together to generate proper autocompletions for git
``__git_refs``                    List all references (heads, remotes, tags etc)
``__git_remotes``                 List all remotes
``__git_tags``                    List all tags
``__git_wrap__git_main``          This is the function that gets mapped to ``complete``
================================= ===============================================================================



Final notes
-----------
Finally I would like to thank the authors of the bash manual. It helps a lot in understanding everything.
We all have our own way to learn, and I do not believe this guide could have been written in 4 hours without the help
of the others behind the references [#BASH_MANUAL]_,[#GIT_BASH_COMPLETION]_,[#COMPGEN_STACKOVERFLOW]_,
[#COMPGEN_SERVER_TUTORIALS]_,[#CUSTOM_COMPLETIONS]_

::

    _git_YOUR_CUSTOM_GIT_COMMAND ()
    {
      COMPREPLY("Hello world")
    }

Let your imagination take you away to that magic place. 

.. rubric:: References
.. [#BASH_MANUAL]              https://www.gnu.org/software/bash/manual/bash.html#Programmable-Completion-Builtins
.. [#GIT_BASH_COMPLETION]      https://github.com/git/git/blob/master/contrib/completion/git-completion.bash
.. [#COMPGEN_STACKOVERFLOW]    https://unix.stackexchange.com/questions/151118/understand-compgen-builtin-command
.. [#COMPGEN_SERVER_TUTORIALS] http://www.serverwatch.com/server-tutorials/a-look-at-the-compgen-bash-builtin.html
.. [#CUSTOM_COMPLETIONS]       http://eli.thegreenplace.net/2013/12/26/adding-bash-completion-for-your-own-tools-an-example-for-pss
