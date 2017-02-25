from ElevatorSystem import ElevatorController
import time

controller = ElevatorController(2, 3)

# an array of tasks, each element means customers that come at that time index
# schedule = [[(1, 5)], [(1, 10)], [], [], [], [], [], [], [(10, 3)]]
schedule = [[(1, 5), (1, 6), (1, 4), (1, 7), (50, 1)], [(1, 10)], [], [], [], [], [], [], [(10, 3)]]

x = 0
while x < len(
        schedule) or controller.active_elevator > 0 or controller.waiting_count > 0:
    if x < len(schedule):
        task = schedule[x]
        for customer in task:
            controller.pickup(customer[0], customer[1])
    controller.step()
    time.sleep(0.1)
    print "step %d  status %s, active elevator %d, waiting count %d" % (
        x, str(controller.query_status()), controller.active_elevator, controller.waiting_count)
    x += 1
