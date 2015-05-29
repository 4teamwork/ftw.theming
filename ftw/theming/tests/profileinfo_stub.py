from functools import partial
import re


class ProfileInfoStub(object):

    def __init__(self, *installed):
        self.installed = map(partial(re.sub, r'^profile\-', ''), installed)

    def is_profile_installed(self, profileid):
        profileid = re.sub(r'^profile\-', '', profileid)
        return profileid in self.installed
