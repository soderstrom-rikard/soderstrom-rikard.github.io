Rewriting history with git filter-branch
========================================
Git has a great manual entry [#GIT_FILTER_BRANCH_MANUAL]_ for how to use ``filter-branch`` and since I'm bad at naming things,
this guide is actually about something more concrete than simply rewriting history with git ``filter-branch``.

Background
----------
At work, we had this repository that had aged badly and literally everything was bunched together with no thought of code separation.
Sure it's easy to be lazy and place everything in one place, even if they have nothing to do with each other, like for example two separate
applications. Well, alright they may be related, maybe there is an API that allows direct communication between the two, but that really
isn't a good enough reason to place them together. In this situation, what you do want is repository hierarchy, with a parent repository
that keeps track of all compatible versions of its children compatible.

Of course, the repository used at work was confidential so cannot reference it here. Instead I will use a "highly random" open source
project as reference, my personal favorite, the Linux kernel. Not that I am insinuating that the kernel needs to be broken down into
smaller pieces.


Clone a repo to break apart
---------------------------
Okay let us get started already.

.. code-block:: bash

    git clone git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git breakable-repository

Purge repository by pathspec
----------------------------
The problem at work, also have a problem with structure, trees that can potentially intersect with one another. So I needed a way to tell
``filter branch`` that I only want these directories and these files, therefor ``--subdirectory-filter`` will not work. We need to be able
to express us more precise that a simple directory.

Brace expansion for PATHSPECs
`````````````````````````````
First we need a way to handle brace expansion [#BASH_BRACE_EXPANSION]_ in a ``PATHSPEC``

So what is a branch expansion, let us take a look at it using echo

.. code-block:: bash

    # Simple
    echo a{,b}
    a ab

    # Nested
    echo a{,b{,c}}
    a ab abc

    # Multiple nested
    echo a{,b{,c}d{,e{,f}}}g
    ag abdg abdeg abdefg abcdg abcdeg abcdefg

So essentially we need away to replace the space between these expansions with the or of a regular expression, for ``grep`` without the 
``-e`` flag this is ``\|``. The stream editor ``sed`` [#SED]_ to the rescue with the expression ``s/ /\\\|/g``.

Putting it all together, we need

.. code-block:: bash

    PATHSPEC="$(echo a{,b{,c}d{,e{,f}}}g)"
    echo $PATHSPEC | sed 's/ /\/\|/g'
    ag/|abdg/|abdeg/|abdefg/|abcdg/|abcdeg/|abcdefg

Now we have a way to find the files to keep. At least as long as the PATHSPEC itself does not contain spaces (or repeats)


Listing files and folders to remove
```````````````````````````````````
This is probably the simplest section, this is a mere show, pipe and grep [#GREP]_ command. Where we will the ``-v`` flag to invert the
search pattern.

So place yourself in the ``breakable-repository``, then the files to keep could for example be

.. code-block:: bash

    PATHSPEC="$(echo drivers/{Makefile,net/can/{Makefile,spi}})"
    echo $PATHSPEC | sed 's/ /\/\|/g'
    git ls-files | grep $(echo $PATHSPEC | sed 's/ /\\\|/g')

As you may notice, the result may not be exactly what we wanted. Since the pattern ``drivers/makefile`` is repeated in some sub-directories.
Luckily, that is easily fixed by adding the start of string ``^`` (I noticed this when typing this, at work our paths did not contain
repeated patterns like these ones).

.. code-block:: bash

    PATHSPEC="$(echo ^drivers/{Makefile,net/can/{Makefile,spi}})"

And the those not to keep, also since we will be performing the same regular expression many times it is a good idea to remember it before
the looping over each commit.

.. code-block:: bash

    PATHSPEC="$(echo ^drivers/{Makefile,net/can/{Makefile,spi}})"
    KEEP="$(echo $PATHSPEC | sed 's/ /\\\|/g')"
    git ls-files | grep -v $KEEP
    # ... lots of files  (at time of writing, around 57k number of files) ...


Purging without checkout
````````````````````````
Up until now, we have only prepared us for the action. However, before we proceed, consider this; Checking out all these files, deleting
them, commit the changes and repeating the whole process for each commit will significant amount of time. Furthermore, isn't all the data
except the new git objects that are either treelike or commits already present?

Yes, they are and yes we can simply skip most of that by working with the index. This is done using the ``--index-filter`` argument for
``filter-branch`` command. But we also need to inform both the ``git ls-files`` and ``git rm`` commands to use the index, this is done by
adding the ``--cached`` argument.

So putting the first part of the puzzle together, we get.

.. code-block:: bash

    PATHSPEC="$(echo ^drivers/{Makefile,net/can/{Makefile,spi}})"
    KEEP="$(echo $PATHSPEC | sed 's/ /\\\|/g')"
    git filter-branch --index-filter \
        "git ls-files --cached | grep -v $KEEP | xargs git rm --cached -qr -- " HEAD

After a period of time, we now have a branch, purged from all unwanted files/commits, thou we did just destroy the branch we where standing
on. Therefore it is very important to remember to either make a new branch first or a complete copy of the repository before performing this
action.


For each commit perform a move operation
----------------------------------------
The second part is quite simple in comparison to the first, if we ignore the time to process factor.

.. code-block:: bash

    FROM=drivers
    TO=.
    git filter-branch --tree-filter "git mv -k $FROM $TO" HEAD

Final script
------------
Now that we have all the components, we can put together a nice little snippet that will perform the action we wish.
However, if you do try this on the Linux kernel repository, you may notice it will take quite some time, i.e. approximately 3-5 hours
depending on your machine for the purging alone, however, the last part will be significantly faster due to the fact that only the commits
touching those files will be revisited.

.. code-block:: bash

    #!/bin/env sh

    FROM="$1"
    TO="$2"
    KEEP="$(echo ${@:3} | sed 's/ /\\\|/g')"
    TMPBRANCH="$(mktemp -u -p new repo-XXXXX)"

    # Don't mess with original branch
    git branch --unset-upstream
    git branch -m $TMPBRANCH

    # Remove unwanted files
    echo "purging branch from any files not matching PATHSPEC -- ${@:3}"
    git filter-branch --index-filter \
    "git ls-files --cached | grep -v $KEEP | xargs git rm --cached -qr -- " HEAD

    # Move files
    echo "Rewriting history by moving files from $FROM to $TO"
    git filter-branch -f --tree-filter "git mv -k $FROM $TO" HEAD

Hope this will help someone (or myself again) in the future.

.. rubric:: References
.. [#GIT_FILTER_BRANCH_MANUAL] https://git-scm.com/docs/git-filter-branch
.. [#BASH_BRACE_EXPANSION]     https://www.gnu.org/software/bash/manual/bash.html#Brace-Expansion
.. [#SED]                      https://www.gnu.org/software/sed/manual/sed.html
.. [#GREP]                     https://www.gnu.org/software/grep/manual/grep.html
