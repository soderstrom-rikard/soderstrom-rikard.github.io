Understanding Secure Shell Tunneling
====================================
.. graphviz::

   digraph foo {
      "gotaland" -> "goteborg";
      "malmo" -> "gotaland" [dir = "both"];

      "gotaland" -> "svealand";
      "stockholm" -> "uppsala";
      "stockholm" -> "svealand" [dir = "both"];

      "norrland" -> "uppsala";
      "norrland" -> "umea";
      "kiruna" -> "norrland";
   }

Let us use the hypothetical network map above, this means some city servers in Sweden between
would have some issues communicating.

The goal for today is to let a user that can reach umea connect to goteborg.
You are however limited in such a way that you can only login to kiruna and gotaland directly.
So how do we solve this?

But first let us explore a couple of concepts related to ssh tunneling general.

Concept 1 - Local Forwarding
............................
The term "local forwarding" simply means open an ssh tunnel from my local computer to a host
reachable by server x [#SSH_MANUAL]_. In common tongue this is normally just called an ssh tunnel.

::

     -L [bind_address:]port:host:hostport
     -L [bind_address:]port:remote_socket
     -L local_socket:host:hostport
     -L local_socket:remote_socket
             Specifies that connections to the given TCP port or Unix socket on the local (client) host are to be
             forwarded to the given host and port, or Unix socket, on the remote side.  This works by allocating a
             socket to listen to either a TCP port on the local side, optionally bound to the specified bind_address,
             or to a Unix socket.  Whenever a connection is made to the local port or socket, the connection is for‐
             warded over the secure channel, and a connection is made to either host port hostport, or the Unix
             socket remote_socket, from the remote machine.

             Port forwardings can also be specified in the configuration file.  Only the superuser can forward privi‐
             leged ports.  IPv6 addresses can be specified by enclosing the address in square brackets.

             By default, the local port is bound in accordance with the GatewayPorts setting.  However, an explicit
             bind_address may be used to bind the connection to a specific address.  The bind_address of “localhost”
             indicates that the listening port be bound for local use only, while an empty address or ‘*’ indicates
             that the port should be available from all interfaces.

Connections made to the `bind_address` and `port` on the local machine will be forwarded to the `host` and `hostport` reachable by the remote machine.

Let us have a look at an example

.. code-block:: bash

    # From kiruna
    kiruna$ ssh norrland
    norrland$ ssh -L umea:80022:uppsala:20022 -p 70022 umea
    umea$

    # From umea
    umea$ ssh -p 80022 umea
    uppsala$

This has now made umea able to reach uppsala on port 20022.
So we have started the navigation towards goteborg

Concept 2 - Remote Forwarding
.............................
The term "remote forwarding" is the opposite of "local forwarding" in the regard that it forwards
the connection made on the server back to a host reachable from our local machine [#SSH_MANUAL]_.
In common tongue this is called a reverse ssh tunnel.

::

     -R [bind_address:]port:host:hostport
     -R [bind_address:]port:local_socket
     -R remote_socket:host:hostport
     -R remote_socket:local_socket
     -R [bind_address:]port
             Specifies that connections to the given TCP port or Unix socket on the remote (server) host are to be
             forwarded to the local side.

             This works by allocating a socket to listen to either a TCP port or to a Unix socket on the remote side.
             Whenever a connection is made to this port or Unix socket, the connection is forwarded over the secure
             channel, and a connection is made from the local machine to either an explicit destination specified by
             host port hostport, or local_socket, or, if no explicit destination was specified, ssh will act as a
             SOCKS 4/5 proxy and forward connections to the destinations requested by the remote SOCKS client.

             Port forwardings can also be specified in the configuration file.  Privileged ports can be forwarded
             only when logging in as root on the remote machine.  IPv6 addresses can be specified by enclosing the
             address in square brackets.

             By default, TCP listening sockets on the server will be bound to the loopback interface only.  This may
             be overridden by specifying a bind_address.  An empty bind_address, or the address ‘*’, indicates that
             the remote socket should listen on all interfaces.  Specifying a remote bind_address will only succeed
             if the server's GatewayPorts option is enabled (see sshd_config(5)).

             If the port argument is ‘0’, the listen port will be dynamically allocated on the server and reported to
             the client at run time.  When used together with -O forward, the allocated port will be printed to the
             standard output.


Connections made to the `bind_address` and `port` on the remote server will be forwarded to the `host` and `hostport` reachable by the local machine.

.. code-block:: bash

    # From gotaland
    gotaland$ ssh -R svealand:10022:gotaland:20022 -p 30022 svealand
    svealand$

    # From svealand
    svealand$ ssh -p 10022 svealand
    gotaland$


Concept 3 - Jump Servers
.............................
The term "remote forwarding" is the opposite of "local forwarding" in the regard that it forwards
the connection made on the server back to a host reachable from our local machine [#SSH_MANUAL]_.
In common tongue this is called a reverse ssh tunnel.

::

     ssh connects and logs into the specified destination, which may be specified as either [user@]hostname or a URI
     of the form ssh://[user@]hostname[:port].  The user must prove their identity to the remote machine using one of
     several methods (see below).

     ...

     -J destination
             Connect to the target host by first making a ssh connection to the jump host described by destination
             and then establishing a TCP forwarding to the ultimate destination from there.  Multiple jump hops may
             be specified separated by comma characters.  This is a shortcut to specify a ProxyJump configuration di‐
             rective.  Note that configuration directives supplied on the command-line generally apply to the desti‐
             nation host and not any specified jump hosts.  Use ~/.ssh/config to specify configuration for jump
             hosts.

So why am I talking about jump servers? Weren't we talking about ssh tunnels?

Well, the real power of ssh tunnels only become clear when used in combination with jump servers.
In the "Remote Forwarding" concept we could only reach svealand.

But let us extend that example with jump server syntax

.. code-block:: bash

    # From malmo
    malmo$ ssh -J gotaland:10022,svealand:20022,stockholm:30022 \
               -R localhost:50022:gotaland:10022 -p 40022 uppsala
    uppsala$

    # From uppsala
    svealand$ ssh -J localhost:50022 -p 60022 goteborg
    gotaborg$

This has now made uppsala able to reach goteborg.

Putting it all together
.............................

With a small tweak of the first example we can now do

.. code-block:: bash

    # User 1 from malmo
    malmo$ ssh -J gotaland:10022,svealand:20022,stockholm:30022 \
               -R localhost:50022:gotaland:10022 -p 40022 uppsala
    uppsala$

    # User 2 from kiruna
    kiruna$ ssh norrland
    norrland$ ssh -L umea:80022:uppsala:50022 -p 70022 umea
    umea$

    # User 3 from umea
    umea$ ssh -J umea:80022,uppsala:50022 -p 60022 goteborg
    goteborg$

User from umea is now able to reach goteborg. User 1,2 and 3 can all be separate users or the same.
But in accordance with the rules of this exercise, User 1 and User 2 are the same while User 3 is different.

.. rubric:: References
.. [#SSH_MANUAL]  https://www.man7.org/linux/man-pages/man1/ssh.1.html
