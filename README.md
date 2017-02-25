Elevator Design
===================

This is a interesting design problem that we might have thought when we are in an elevator. It's interesting because it's solution can be so simple or very difficult

We can spend 30 minutes or 30 hours on this simple and complicated problem :)

In this project, I am trying to investigate the basic requirement, extend these requirement to some more complete use cases, and then design the necessary interface, finally implement the code with Python 

### How to Run

* Python 2.7
* (Optional) modify the test scheduling task
* python Simulator.py

### Required Interface

* Querying the state of the elevators (what floor are they on and where they are going),
* Receiving an update about the status of an elevator,
* Receiving a pickup request,
* Time-stepping the simulation.

### Use Case Investigation

Required interface above is somewhat abstract. One fundamental question we might ask is, for the system to be efficient, what's the criteria for "efficient"?

In this system, I try to consider "efficient" as 1. User's waiting time (the time between requesting pick up and finally reach the destination) should be as low as possible; 2. The variance for user's waiting time should be as low as possible (because we don't want to see one customer waiting for a very long time, even if it might means shortest over all waiting time);
 
This performance criteria might bring in some conflicts: the solution for shortest waiting time might not means shortest expectation time for all users; The elevator might has to switch direction when they are heading towards a destination; 

Another necessary requirement is that each elevator should have a capacity constraint;

If we consider all possible requirement (for example, high utility for elevator or distribute travel distance to every elevator as even as possible). The problem would be a very hard problem.
 
Balance the requirement and the implementation feasibility, I specify the requirement as below:

* There is a same capacity constraint for every elevator
* If one elevator has set it's destination, it does not have to change the direction before it reaching the destination (this means the logic for deciding next destination is only executed when it reaches current destination) 
* User's overall waiting time should be as low as possible, but it should obey other existing requirements first
* User's waiting time variance should be as low as possible, but it should obey other existing requirements first as well


### Design Choice I

Given the requirement. We can first consider the most naive way of scheduling: **Scheduling destination according to the order of customers' coming.** 

The structure for storing customer info is also simple. Because it's like a queueing order, we can use a queue to store them. 

But this causes some obvious issue: User's overall waiting time is definitely not the shortest

Given the example below:

* The initial floor is 10;
* Sunil boards first and has destination 100;
* Christian boards second and has destination 3;

In the example above, the elevator would head to 100 floor first and then 3 floor, the over all distance is 90 + 90 + 7
. While a better solution is heading to 3 floor first, then we can get the distance: 7 + 7 + 90 



### Design Choice II 

In every logic moment, we can **seek for the nearest destination first.** After reaching that destination, we then decide the next destination also according to the nearest seeking destination.

But after some consideration, I find that it might violate the last requirement significantly.
 
For example
 * The initial floor is 40 
 * There are two customers, their destinations are: 50, 100.
 * So we have to head towards 50, but when the elevator reaches 50, another customer boards and has destination 40
 * Then we have to head towards 40, but if there is another customer boarding and he is heading towards 50 and it go on and on
 * The 100 floor customer would be delayed on and on
 
 
Given that, we should also consider the waiting time for every customer, and when deciding the next destination, we should consider both destinations and the waiting time for every customer 


More specifically, the logic for interface "pickup", when choosing the elevator to pickup the customer, there would be some comparison between different elevators
* Empty elevator vs Empty elevator: compare their current floor
* Fully occupied elevator does not participate in pickup (so it's possible to have all elevator fully occupied and the customer has to wait)
* Occupied elevator whose planned path does not contain customer's floor does not participate pickup: 
* Occupied elevator whose planned path contains current floor participate the pickup 
* Occupied participating elevator vs Empty elevator: compare floor 
* Occupied participating elevator vs Occupied participating elevator: compare floor


For deciding next destination:
* Consider destination of all passengers and the waiting time, these two attributes can generate a value according to the formula below
    >> val = distance_to_destination + ratio / waiting_time 
    
    the smaller the better
    
    

### Design Choice III (hasn't been implemented)

After implementing previous algorithm, I find that the system can be optimized in another aspect.

But since it's recommended to be finished within 4 hours, I just briefly write down the design choice

Given the example in previous design, it would cause the elevator to go up and down, this actually increase the overall path that the elevator travel

So if we prefer shorter overall distance, we can use a scan-like method: there are several customers on the elevator, their destinations are distributed above and below current floor, 
We can first heading towards the furthest point (for shorter side) and then goes back to the other furthest side. That would means shortest path thus shortest overall time 

Here is an example:
* Current floor: 30
* Customer destinations: [100, 70, 65, 40, 20, 10]

It's not difficult to find that the shortest path is first heading towards 10, then towards 100

Below is the specific state transaction and pickup rule

There are three kinds of states for one elevator:
* Vacant and has no destination
* Vacant and has destination
* Occupied and has destination


For these three state, there are different logics:

Vacant and has no destination
* Head towards the nearest waiting customer
* Once it choose a target customer, it's state changes to next state

Vacant and has destination
* Only pickup users that has same direction with the elevator (because it can extend the range of current customer) 
* Once it pickup a customer, it's state changes to next 

Occupied and has destination
* Only pickup customers with same destination, and after pickup, update the destination to the farest destination of customers on board



### Implementation

There are two files: ElevatorSystem.py and Simulator.py

* ElevatorSystem.py contains all classes for the system
* Simulator is used to run the test

#### Several Classes:

Customer (Actually it would better to be called "Passenger" :)
* containing both pickup floor, destination floor and the boarding time 

Elevator
* It stores customers in a map, to make it faster to get all passengers for a certain destination floor
* It calls the "update" function of the controller to update it's status
* Once deciding a destination, it heads towards that direction, only picking up passengers on the path


More detailed explanation is in the annotation of the code

Best wishes to you, my friend (content inside the image below :)

<img src="https://raw.github.com/suanmiao/ElevatorDesign/master/readme_imgs/my_friend.jpg" width="300">


Developed By
------------

* suanmiao (Hongkun Leng)


License
-------

    Copyright 2017 suanmiao

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


