from pyats import aetest
from genie.testbed import load


EXPECTED_VLANS = ["110", "120", "130"]
EXPECTED_SVIS = ["Vlan110", "Vlan120", "Vlan130"]
EXPECTED_VRFS = ["CORP", "GUEST", "IOT"]


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect_to_devices(self, testbed):
        testbed.connect()
        self.parent.parameters["testbed"] = testbed


class VerifyCampusSegmentation(aetest.Testcase):

    @aetest.test
    def verify_core_vlans(self, testbed):
        core = testbed.devices["core01"]
        output = core.execute("show vlan brief")
        for vlan in EXPECTED_VLANS:
            assert vlan in output, f"Missing VLAN {vlan} on core01"

    @aetest.test
    def verify_core_svis(self, testbed):
        core = testbed.devices["core01"]
        output = core.execute("show ip interface brief | include Vlan")
        for svi in EXPECTED_SVIS:
            assert svi in output, f"Missing SVI {svi} on core01"

    @aetest.test
    def verify_core_vrfs(self, testbed):
        core = testbed.devices["core01"]
        output = core.execute("show vrf")
        for vrf in EXPECTED_VRFS:
            assert vrf in output, f"Missing VRF {vrf} on core01"

    @aetest.test
    def verify_access_vlans(self, testbed):
        for device_name in ["access01", "access02"]:
            device = testbed.devices[device_name]
            output = device.execute("show vlan brief")
            for vlan in EXPECTED_VLANS:
                assert vlan in output, f"Missing VLAN {vlan} on {device_name}"


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, testbed):
        testbed.disconnect()
