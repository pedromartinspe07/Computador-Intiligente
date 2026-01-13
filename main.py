# main.py

from armor.mark_5 import MarkV
from energy.arc_reactor_sim import ArcReactorSim
from navigation.auto_follow_sim import AutoFollowSim

armor = MarkV()
reactor = ArcReactorSim()
nav = AutoFollowSim()

print(armor.activate())
reactor.accelerate_particles()
nav.update_target(5, 5)

print(armor.status())
print(reactor.status())
print(nav.follow())
