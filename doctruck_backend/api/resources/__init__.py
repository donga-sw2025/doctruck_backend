from doctruck_backend.api.resources.user import UserResource, UserList
from doctruck_backend.api.resources.food_truck import FoodTruckResource, FoodTruckList
from doctruck_backend.api.resources.location import LocationResource, LocationList
from doctruck_backend.api.resources.document import DocumentResource, DocumentList
from doctruck_backend.api.resources.admin_document import (
    AdminDocumentPending,
    AdminDocumentVerify,
    AdminDocumentList,
    AdminDocumentResource,
)
from doctruck_backend.api.resources.admin_location import (
    AdminLocationList,
    AdminLocationResource,
)
from doctruck_backend.api.resources.admin_user import AdminUserList, AdminUserResource
from doctruck_backend.api.resources.admin_document_location import (
    AdminDocumentLocationConnect,
    AdminDocumentLocationList,
)
from doctruck_backend.api.resources.food_truck_location import (
    LocationInterest,
    MyLocationInterests,
)
from doctruck_backend.api.resources.recommendation import (
    RecommendedLocations,
    RecommendedDocuments,
)


__all__ = [
    "UserResource",
    "UserList",
    "FoodTruckResource",
    "FoodTruckList",
    "LocationResource",
    "LocationList",
    "DocumentResource",
    "DocumentList",
    "AdminDocumentPending",
    "AdminDocumentVerify",
    "AdminDocumentList",
    "AdminDocumentResource",
    "AdminLocationList",
    "AdminLocationResource",
    "AdminUserList",
    "AdminUserResource",
    "AdminDocumentLocationConnect",
    "AdminDocumentLocationList",
    "LocationInterest",
    "MyLocationInterests",
    "RecommendedLocations",
    "RecommendedDocuments",
]
