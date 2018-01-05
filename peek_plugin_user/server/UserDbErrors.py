

# class UserIsNotLoggedInError(Exception):
#     def __init__(self, userName):
#         self.userName = userName
#
#     def __str__(self):
#         return "User %s is not logged in on any device" % self.userName


class UserIsNotLoggedInToThisDeviceError(Exception):
    def __init__(self, userName):
        self.userName = userName

    def __str__(self):
        return "User %s is not logged in this device" % self.userName


class UserNotFoundException(Exception):
    def __init__(self, userName):
        self.userName = userName

    def __str__(self):
        return "User %s is foind in database" % self.userName
