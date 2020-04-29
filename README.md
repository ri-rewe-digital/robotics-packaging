# robotics-packing
Packing logic for place/packing problem. 

This implementation is based on the paper 'A biased random key genetic algorithm for 2D and 3D bin packing problems' by J.Goncalves and M. Resende.
This module integrates into the ri-robotics ros architecture by supplying a packing-action-server.

Start-scripts are found in the 'bin' directory, for non-ros developers a main file exists.

#### NON-Ros Start in the console
Be sure your `PYTHONPATH` is set correctly
```
$ cd to_your_checkout
your_checkout$ PYTHONPATH=$(pwd)/src:${PYTHONPATH}
```
Then start the application from to root directory
```
your_checkout$ bin/main_no_ross.py
```
For *non-ros* development, requirements are found in the requirements.txt
```
your_checkout$ pip3 install -r requirements.txt
```
#### ROS
A launch file is supplied, you can use it to start the action server as a node.
For your convenience an action client is supplied as well, you can start it by setting the parameter `run_client`
```
your_checkout$ roslaunch ri_packing packing.launch run_client:=true
```
for *ros* development, all requirements are configured int the package.xml as well as the setup.py. 
*Do not alter your `PYTHONPATH`*

## Developers

Entrypoint into the packing algorithm is the solver.py file. More specifically: solver.solve_packing_problem

#### Short-Overview
* _Solver_: Responsible for population management. Starting at generation 'zero' it creates new generations according to the papers logic.
* _Placer_: Manages the containers and the products therein. It uses a placement strategy to pack the delivery bins. It also triggers available space calculations in side the containers.
* _PlacementStrategy_: Is defined in the configuration and instantiated in the PlacementFactory accordingly.
* _Decoder_: Uses the chromosome to determine the location of the product boxes (first n genomes) and it's rotation (n+1:len()).
* _Chromosome_: A simple array based class containing the boxplacement evaluation (a float) and it's rotation (also a float)
* _Space_: A representation of none used container space.
* _ContainerList_: Manages containers
* _Container_: Manages it's empty spaces

As stated above, the placement-strategy is configurable. To create a new strategy, you will: 
1. put some "key" in the configuration
1. extend the switch in the PlacementFactory (and a function to call)
1. Create an implementation inheriting from PlacementStrategy.