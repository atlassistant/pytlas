Installing skills
=================

Install skills from a Git repository. If no host is given, it will take the value of `PYTLAS_DEFAULT_REPO_URL` which itsef defaults to `https://github.com/`.

From CLI
--------

.. code-block:: bash

  pytlas skills add atlassistant/pytlas-help https://git.yourownserver.com/myorga/my-skill
  
From code
---------

.. code-block:: python

  from pytlas.pam import install_skills
  
  # The first parameter is the skills directory
  # The second parameter is a function to print output messages
  skills = install_skills(os.getcwd(), print, 'atlassistant/pytlas-help', 'https://git.yourownserver.com/myorga/my-skill')
  
  # skills now have the list of successfuly installed or updated skills
