Building Arch Linux ARM distribution in Yocto
=============================================
...WIP...

Creating the Arch Linux ARM layer
---------------------------------
Place yourself in the directory where you which to place the *meta-archlinuxarm* layer.

::
    yocto-layer create archlinuxarm

Creating the distribution configuration file
--------------------------------------------
In distribution layer, named meta-archlinuxarm from above create the file ::
    conf/distro/archlinuxarm.conf

In this file put the following contents ::
    DISTRO_NAME    = "Arch Linux ARM"
    DISTRO_VERSION = "2015.09.01"
    # DISTRO_FEATURES
    # DISTRO_EXTRA_RDEPENDS
    # DISTRO_EXTRA_RRECOMMENDS
    # TCLIBC

Provide miscellaneous variables
-------------------------------
Be sure to define any other variables for which you want to create a default or enforce as part of the distribution configuration. You can include nearly any variable from the *local.conf* file. The variables you use are not limited to the list in the previous bullet item.

Point to Your distribution configuration file
---------------------------------------------
In your *local.conf* file in the Build Directory, set your *DISTRO* variable to point to your distribution's configuration file. For example, if your distribution's configuration file is named *archlinuxarm.conf*, then you point to it as follows::
    DISTRO = "archlinuxarm"

Add more to the layer if necessary
----------------------------------
Use your layer to hold other information needed for the distribution

* Add recipes for installing distro-specific configuration files that are not already installed by another recipe. If you have distro-specific configuration files that are included by an existing recipe, you should add an append file (.bbappend) for those. For general information and recommendations on how to add recipes to your layer, see the "Creating Your Own Layer" and "Best Practices to Follow When Creating Layers" sections in the official documentation.
* Add any image recipes that are specific to your distribution.
* Add a psplash append file for a branded splash screen. For information on append files, see the "Using .bbappend Files" section.
* Add any other append files to make custom changes that are specific to individual recipes.

