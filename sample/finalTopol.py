"""Custom topology for CS 164 Fall Final Project
    
    Two directly connected switches, a server and three clients:
                    client(C2)
                        |
                        |
    client(C1) --- switch(SW1) --- switch(SW2) --- server(S1)
                        |
                        |
                    client(C3)
    Adding the 'topos' dict with a key/value pair to generate our newly defined
    topology enables one to pass in '--topo=mytopo' from the command line.
    """

"""
	********TO RUN THIS FILE *************
sudo mn --custom finalTopol.py --topo finaltopol -x
The -x option opens an xterm window for each node. You can close
the windows for the switches and remain with windows for the clients
and server only.
Alternatively you can run the command above without the -x option
then use the command xterm hostname to open a terminal eg
    mininet> xterm C1 
"""

from mininet.topo import Topo


class FinalTopol( Topo ):
    "Project topology."
    
    def __init__( self ):
        "Create custom topo for project."
        
        # Initialize topology
        Topo.__init__( self )
        
        # Add hosts and switches
        leftHost = self.addHost( 'C1' )
        topHost = self.addHost( 'C2' )
        bottomHost = self.addHost( 'C3' )
        
        leftSwitch = self.addSwitch( 'SW1' )
        rightSwitch = self.addSwitch( 'SW2' )
        
	serverHost = self.addHost( 'H1' )
       
        
        # Add links
        self.addLink( leftHost, leftSwitch )
        self.addLink( topHost, leftSwitch )
        self.addLink( bottomHost, leftSwitch )
        self.addLink( leftSwitch, rightSwitch )
        self.addLink( rightSwitch, serverHost )



topos = { 'finaltopol': ( lambda: FinalTopol() ) }