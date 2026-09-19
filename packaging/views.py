from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from packaging.serializers import RecommendBoxRequestSerializer
from packaging.services import recommend_box


class APIRootView(APIView):
    """
    Root API Information View.
    GET /
    """
    def get(self, request, *args, **kwargs):
        return Response({
            "system": "AI-Assisted Box Selection System",
            "version": "1.0.0",
            "status": "online",
            "endpoints": {
                "recommend_box": "/api/orders/recommend-box/",
                "admin": "/admin/"
            },
            "documentation": "Send POST request to /api/orders/recommend-box/ with items payload."
        }, status=status.HTTP_200_OK)


class RecommendBoxAPIView(APIView):
    """
    API View to recommend the optimal shipping box for an ecommerce order.
    POST /api/orders/recommend-box/
    """

    def get(self, request, *args, **kwargs):
        """Friendly GET response with instructions and example payload for browser exploration."""
        return Response({
            "message": "Send a POST request to this endpoint to evaluate an order and recommend the optimal box.",
            "method": "POST",
            "example_request": {
                "items": [
                    {"product_id": 1, "quantity": 1},
                    {"product_id": 2, "quantity": 2}
                ]
            }
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = RecommendBoxRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "error": "Invalid request payload",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        items = serializer.validated_data['items']
        result = recommend_box(items)

        # If no recommendation could be found, return 422 Unprocessable Entity with reason & rejections
        if result.get("recommendation") is None:
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(result, status=status.HTTP_200_OK)


