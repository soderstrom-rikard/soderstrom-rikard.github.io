Publishing sphinx generated documents on github
===============================================
Back when I started (2017-09-05) using sphinx for my github pages. I quickly googled and found a thread.
However, the solutions they offered was not really what I was looking for.

So instead I will present how I did it.

Setting up your repository
--------------------------

First create the repository and place yourself in its directory. Also create an empty repository on your github.

.. code-block:: bash

  git init github-user.github.io
  cd github-user.github.io

After that, add your remote for your github repo. Create an empty commit and push it [#GITHUB_PAGES]_.

.. code-block:: bash

  git remote add origin https://github.com/github-user/github-user.github.io
  git commit --allow-empty "Inital commit"
  git push --set-upstream origin master


Now move to another empty branch *gh-pages*. This branch will contain all the sphinx sources.
Also add the first branch as a submodule at *build/html* [#LUCAS_BARDELLA]_.

.. code-block:: bash

  git checkout --orphan gh-pages
  git remote add https://github.com/github-user/github-user.github.io build/html


Creating your initial sphinx
----------------------------

Use the defaults from *sphinx-quickstart* except for the options explicitly shown below

.. code-block:: bash

    sphinx-quickstart
    ...
    > Separate source and build directories (y/n) [n]: y
    ...
    > githubpages: create .nojekyll file to publish the document on GitHub pages (y/n) [n]: y
    ...

After that, simply run

.. code-block:: bash

    make html             # Or whatever the equivalance is on M$

Publishing method
-----------------
When you have something you are satisfied with and ready to publish commit everything in submodule build/html first,
then commit the remainders.

Committing
``````````
.. code-block:: bash

    (cd build/html; git add .; git commit -m "$(date)")
    git add .; git commit -m "First version of proj"

Publishing
``````````
.. code-block:: bash

    (cd build/html; git push)
    git push

Having a blast
``````````````
Done!

.. rubric:: References
.. [#GITHUB_PAGES] https://pages.github.com
.. [#LUCAS_BARDELLA] http://lucasbardella.com/blog/2010/02/hosting-your-sphinx-docs-in-github
