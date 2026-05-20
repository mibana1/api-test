from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class RecommendView(APIView):
    def post(self, request):
        # TODO: add embedding model
        # TODO: add vector store
        # TODO: add similarity search
        # TODO: wire to search APIs for final result enrichment
        return Response(
            {
                "detail": "Recommendation pipeline scaffold is ready for future implementation.",
                "plannedInput": {
                    "isbn": request.data.get("isbn"),
                    "description": request.data.get("description"),
                },
            },
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
