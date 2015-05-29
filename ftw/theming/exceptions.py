

class CyclicResourceOrder(Exception):
    """This exception is raised when the resource order is cyclic because of
    ``before`` and ``after`` statements on resources.
    The order is not reliable any more and therefore the exception is raised.
    """

    def __init__(self, cyclic_order, resources=None, graph=None):
        self.cyclic_order = cyclic_order
        self.resources = resources
        self.graph = graph
        message = 'Cyclic resource order: {0}'.format(self.cyclic_order)
        super(CyclicResourceOrder, self).__init__(message)
