from routeTracker.logReader import logReader


def test_resetValues():
    # given
    reader = logReader()
    reader.firstCheck = False
    reader.checked = "filename"
    reader.activeFile = "activeFileName"
    reader.currentSystem = "Sol"
    reader.carrierFuel = 1000

    reader.carrierInventory = 2000
    reader.shipInventory = 500
    reader.carrierName = "Sunk Cost Fallacy"
    reader.oldSystem = "LHS 20"
    reader.lastJumpRequest = 10
    # when
    reader.resetValues()
    # then
    assert reader.firstCheck is True
    assert reader.checked is None
    assert reader.activeFile is None
    assert reader.currentSystem is 'unknown'
    assert reader.carrierFuel == 0

    assert reader.carrierInventory == 0
    assert reader.shipInventory == 0
    assert reader.carrierName == 'unknown'
    assert reader.oldSystem == 'unknown'
    assert reader.lastJumpRequest == 0
