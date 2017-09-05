Embedded Linux Development on C.H.I.P
=====================================
The intention with this guide is to give a brief introduction to compiling your sources. It is by no means complete.
The guide aims to be as generic as possible. So no editor/ide specific details will be added (hopefully).

General Hardware Information
----------------------------

* ARM CortexTM-A8 Core
* ARMv7 Instruction set plus Thumb-2 Instruction Set
* 32KB Instruction Cache and 32KB Data Cache
* 256KB L2 Cache
* 3D Graphic Engine
* Support Open GL ES 1.1/2.0 and open VG 1.1
* Support multi-format video decoding, including VP6/8, AVS, H.264, H.263 , MPEG-1/2/4, etc
* Up to 1080p@30fps resolution in all formats

You can find the datasheet in the git repo `CHIP-Hardware <https://github.com/NextThingCo/CHIP-Hardware/tree/master>`_.

Toolchain
---------
In this section a list of many available toolchains will be added over time.

Buildroot
`````````
Essentially ::
    $ git clone --branch chip/stable https://github.com/NextThingCo/CHIP-buildroot.git ~/chip-buildroot
    $ cd chip-buildroot
    $ make chip_defconfig
    $ make menuconfig
    Add/remove packages
    $ make linux-menuconfig
    Add/remove kernel features/drivers
    $ make

The resulting images will be found under ``output/images``

Yocto
`````

There are nightly toolchain installer builds available from *autobuilder.yoctoproject.org*. So you could simply download the arm toolchain from there.
You can download the latest build from `[here] <http://autobuilder.yoctoproject.org/pub/releases/CURRENT/toolchain/x86_64/poky-glibc-x86_64-core-image-sato-armv7a-vfp-neon-toolchain-1.8+snapshot.sh>`_.

In order to build the default configuration make sure you have the following packages installed: *git, diffstat, unzip, texinfo, python2, chrpath, wget, xterm, sdl, socat, cpio and lzop*

Compile your own toolchain
''''''''''''''''''''''''''
In order to compile it yourself, we need to do a little more.
To compile a toolchain using yocto, we need first to download the sources and setup the build environment.

::
    $ git clone --branch fido git://git.yoctoproject.org/poky.git ~/poky
    $ cd poky && source oe-init-build-env build-chip-toolchain

Any armv7 toolchain should suffice. As basis for the toolchain we are going to use a MACHINE with the same instruction set (armv7). As an example, the *olinuxino-a13* machine from meta-sunxi bitbake layer have the armv7 instruction set.

::
    $ git clone https://github.com/linux-sunxi/meta-sunxi

Add the path to the layer in BBLAYERS variable by editing *~/poky/build-chip-toolchain/conf/bblayers.conf*

::
    BBLAYERS ?= " \
      /home/user/poky/meta \
      /home/user/poky/meta-yocto \
      /home/user/poky/meta-yocto-bsp \
      /home/user/meta-sunxi \
      "

Now edit the *~/poky/build-chip-toolchain/conf/local.conf* and change the machine to an Allwinner A13 machine.

::
    MACHINE ?= olinuxino-a13

Time to build the toolchain, simply type

::
    $ bitbake -k meta-toolchain

You can now find the toolchain installer under *~/poky/build-chip-toolchain/tmp/deploy/sdk*

Install the toolchain
'''''''''''''''''''''
The install script have a few options you may or may not wish to tweak. ::
    Usage: poky-glibc-x86_64-meta-toolchain-armv7a-vfp-neon-toolchain-1.8.sh [-y] [-d <dir>]"
      -y         Automatic yes to all prompts"
      -d <dir>   Install the SDK to <dir>"
    ======== Advanced DEBUGGING ONLY OPTIONS ========"
      -S         Save relocation scripts"
      -R         Do not relocate executables"
      -D         use set -x to see what is going on"

To install the toolchain simply run the following as superuser (sudo, su etc), it requires superuser because default installation dir is */opt*. ::
    # cd /home/user/poky/build-chip-toolchain/tmp/deploy/sdk
    # ./poky-glibc-x86_64-meta-toolchain-armv7a-vfp-neon-toolchain-1.8.sh -y

If you downloaded the pre-built toolchain then it would have been named *poky-glibc-x86_64-core-image-sato-armv7a-vfp-neon-toolchain-1.8+snapshot.sh*.

U-boot
------
The universal bootloader.

Compile U-boot
``````````````

In order to build the bootloader, first make sure your toolchain is ready to use. ::
    $ source /opt/poky/1.8/environment-setup-armv7a-vfp-neon-poky-linux-gnueabi
    $ echo "[$ARCH]$CROSS_COMPILE"
    [arm]arm-poky-linux-gnueabi-

When the toolchain is ready to use, get the u-boot sources and compile them. ::
    $ git clone --branch nextthing/CHIP https://github.com/NextThingCo/CHIP-u-boot.git chip-u-boot
    $ cd chip-u-boot
    $ make CHIP_defconfig
    $ make

U-boot Commands
```````````````
The following section describes the most important commands available in U-Boot. Please note that U-Boot is highly configurable, so not all of these commands may be available in the configuration of U-Boot installed on your hardware, or additional commands may exist. You can use the help command to print a list of all available commands for your configuration.

Here is a list of some common commands that may exist in your u-boot configuration::
     Information Commands
     bdinfo     - Print Board Info structure
     coninfo    - Print console devices and informations
     flinfo     - Print FLASH memory information
     iminfo     - Print header information for application image
     help       - Print online help

     Memory Commands
     base       - Print or set address offset
     crc32      - Checksum calculation
     cmp        - Memory compare
     cp         - Memory copy
     md         - Memory display
     mm         - Memory modify (auto-incrementing)
     mtest      - Simple RAM test
     mw         - Memory write (fill)
     nm         - Memory modify (constant address)
     loop       - Infinite loop on address range

     Flash Memory Commands
     cp         - Memory copy
     flinfo     - Print FLASH memory information
     erase      - Erase FLASH memory
     protect    - Enable or disable FLASH write protection
     mtdparts   - Define a Linux compatible MTD partition scheme

     Execution Control Commands
     source     - Run script from memory
     bootm      - Boot application image from memory
     go         - Start application at address 'addr'

     Download Commands
     bootp      - Boot image via network using BOOTP/TFTP protocol
     dhcp       - Invoke DHCP client to obtain IP/boot params
     loadb      - Load binary file over serial line (kermit mode)
     loads      - Load S-Record file over serial line
     rarpboot   - Boot image via network using RARP/TFTP protocol
     tftpboot   - Boot image via network using TFTP protocol

     Environment Variables Commands
     printenv   - Print environment variables
     saveenv    - Save environment variables to persistent storage
     setenv     - Set environment variables
     run        - Run commands in an environment variable
     bootd      - Boot default, i.e., run 'bootcmd'

     Flattened Device Tree support
     fdt addr   - Select FDT to work on
     fdt list   - Print one level
     fdt print  - Recursive print
     fdt mknode - Create new nodes
     fdt set    - Set node properties
     fdt rm     - Remove nodes or properties
     fdt move   - Move FDT blob to new address
     fdt chosen - Fixup dynamic info

     Special Commands
     i2c        - I2C sub-system

     Miscellaneous Commands
     echo       - Echo args to console
     reset      - Perform RESET of the CPU
     sleep      - Delay execution for some time
     version    - Print monitor version
     ?          - Alias for 'help'

You can find details about the `commands from www.denx.de <http://www.denx.de/wiki/view/DULG/UBootCommandLineInterface>`_

Linux Kernel
------------

Install build dependencies
``````````````````````````
gcc, etc..

Compile Linux Kernel
````````````````````
In order to build the kernel, first make sure your toolchain is ready to use. ::
    $ source /opt/poky/1.8/environment-setup-armv7a-vfp-neon-poky-linux-gnueabi
    $ echo "[$ARCH]$CROSS_COMPILE"
    [arm]arm-poky-linux-gnueabi-

When the toolchain is ready to use, get the linux sources for C.H.I.P and compile them. ::
    $ git clone https://github.com/NextThingCo/CHIP-linux.git chip-linux
    $ cd chip-linux
    $ make sunxi_defconfig
    $ make

Device Tree Compilation
-----------------------
The DTS file needs to be compiled into a DTB file that the kernel can understand. The device tree compiler (DTC), located under *scripts/dtc* in the linux kernel source, will compile the DTS file into a DTB file with the command::
    $ ./scripts/dtc/dtc -I dts -O dtb -o devicetree.dtb CHIP.dts

The DTC compiler can also de-compile a DTB file back to the DTS file with the command::
    $ ./scripts/dtc/dtc -I dtb -O dts -o CHIP.dts devicetree.dtb

You can view other options for the DTC compiler with the `-h` option::
    $ ./scripts/dtc/dtc -h

