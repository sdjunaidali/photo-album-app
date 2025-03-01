# minio_status_codes.py

class MinIOStatusCodes:
    # General status codes
    SUCCESS = 0
    FAILURE = 1

    # MinIO-specific status codes
    OBJECT_ALREADY_EXIST = 2
    NO_SUCH_BUCKET = 3
    NO_SUCH_KEY = 4
    ENTITY_TOO_LARGE = 5
    ACCESS_DENIED = 6
    INVALID_CREDENTIALS = 7
    PRECONDITION_FAILED = 8
    INTERNAL_ERROR = 9
    OBJECT_NOT_FOUND = 10

    @classmethod
    def get_status_description(cls, code):
        """Return a description for each status code."""
        descriptions = {
            cls.SUCCESS: "Operation succeeded",
            cls.FAILURE: "Operation failed",
            cls.OBJECT_ALREADY_EXIST: "Object already exists",
            cls.NO_SUCH_BUCKET: "Bucket does not exist",
            cls.NO_SUCH_KEY: "Object key does not exist",
            cls.ENTITY_TOO_LARGE: "Entity size too large",
            cls.ACCESS_DENIED: "Access denied",
            cls.INVALID_CREDENTIALS: "Invalid credentials",
            cls.PRECONDITION_FAILED: "Precondition failed",
            cls.INTERNAL_ERROR: "Internal server error",
            cls.OBJECT_NOT_FOUND: "Object Not Found",
        }
        return descriptions.get(code, "Unknown status code")
