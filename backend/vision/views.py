from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class AnalyzeView(APIView):
    def post(self, request):
        # TODO: integrate YOLOv8 via ultralytics
        return Response(
            {
                "detail": "Vision analysis scaffold is ready for future implementation.",
                "plannedFeatures": ["title region", "color", "layout"],
            },
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
