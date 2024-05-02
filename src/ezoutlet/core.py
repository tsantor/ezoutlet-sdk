import logging

import requests

from .constants import ControlConstants
from .constants import TargetConstants
from .responses import ControlResponse
from .responses import StatusResponse
from .utils import xml_to_dict

logger = logging.getLogger("ezoutlet-sdk")


class EzOutletAPI:
    """
    EzOutlet API client. Works with models:
    - EZ-73a (2 outlet).  https://www.proxicast.com/shopping/pwr-ez-73a.html
    - EZ-72b (1 outlet).  https://www.proxicast.com/shopping/ezoutlet5.html
    - EZ-62b (1 outlet).
    """

    def __init__(self, ip: str, user: str, password: str):
        self.ip = ip
        self.user = user
        self.password = password
        self.base_url = f"http://{ip}" if not ip.startswith("http://") else ip

        self.client = requests.Session()
        self.client.timeout = (3.0, 10.0)  # (connect, read)

    def _build_control_url(self, target: int, control: int) -> str:
        """Build control URL."""
        return (
            f"{self.base_url}/cgi-bin/control2.cgi?"
            f"user={self.user}&"
            f"passwd={self.password}&"
            f"target={target}&"
            f"control={control}"
        )

    def target_control(self, target: int, control: int) -> ControlResponse:
        """Make request."""
        url = self._build_control_url(target, control)
        response = self.client.get(url)
        response.raise_for_status()
        return ControlResponse(**xml_to_dict(response.text))

    def turn_on_outlet(self, outlet_num: int = 1) -> str:
        """Turn on outlet."""
        return self.target_control(outlet_num, ControlConstants.ON)

    def turn_off_outlet(self, outlet_num: int = 1) -> str:
        """Turn off outlet."""
        return self.target_control(outlet_num, ControlConstants.OFF)

    def reset_outlet(self, outlet_num: int = 1) -> str:
        """Reset outlet."""
        return self.target_control(outlet_num, ControlConstants.RESET)

    def enable_auto_reset(self) -> str:
        """Enable auto reset."""
        return self.target_control(TargetConstants.OUTLET, ControlConstants.ON)

    def disable_auto_reset(self) -> str:
        """Disable auto reset."""
        return self.target_control(TargetConstants.OUTLET, ControlConstants.OFF)

    def _build_status_url(self) -> str:
        """Build status URL."""
        return f"http://{self.user}:{self.password}@{self.ip}/xml/outlet_status.xml"

    def get_status(self) -> StatusResponse:
        """Get outlet status."""
        url = self._build_status_url()
        response = self.client.get(url)
        response.raise_for_status()
        return StatusResponse(**xml_to_dict(response.text))
