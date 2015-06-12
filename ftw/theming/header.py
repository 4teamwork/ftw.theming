from ftw.theming.interfaces import IThemingLayer


def set_ftw_theming_header(object, event):
    """Set an HTTP_X_FTW_THEMING header in the request when ftw.theming is enabled.

    For enabling ftw.theming, the ``ftw.theming:default`` profile must
    be installed, enabling the required request layer.
    """

    request = event.request
    if not IThemingLayer.providedBy(request):
        return
    request.environ['HTTP_X_FTW_THEMING'] = True
