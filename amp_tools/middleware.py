from amp_tools.settings import settings
from amp_tools import set_amp_detect


class AMPDetectionMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        if settings.AMP_TOOLS_GET_PARAMETER in request.GET:
            if (
                request.GET[settings.AMP_TOOLS_GET_PARAMETER]
                == settings.AMP_TOOLS_GET_VALUE
            ):
                set_amp_detect(is_amp_detect=True, request=request)
        else:
            set_amp_detect(is_amp_detect=False, request=request)

        return self.get_response(request)
