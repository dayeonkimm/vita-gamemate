from rest_framework.pagination import PageNumberPagination


class ReviewPagination(PageNumberPagination):
    page_size = 10


class UserGameReviewPagination(PageNumberPagination):
    page_size = 5
