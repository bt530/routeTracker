from dataclasses import dataclass


@dataclass(frozen=False)
class RouteData:
    firstCheck = True
    checked = None
    activeFile = None
    currentSystem = 'unknown'
    carrierFuel = 0
    carrierInventory = 0
    shipInventory = 0
    carrierName = 'unknown'
    oldSystem = 'unknown'
    lastJumpRequest = 0
