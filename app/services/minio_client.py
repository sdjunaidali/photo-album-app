import logging
from minio import Minio, S3Error
import os
import io
from .minio_status_codes import MinIOStatusCodes
from minio.commonconfig import CopySource
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MinIO client
minio_client = Minio(
    settings.minio_endpoint.replace("http://", "").replace("https://", ""),
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=False,
)

# Ensure the bucket exists
def setup_minio_bucket():
    try:
        if not minio_client.bucket_exists(settings.minio_bucket_name):
            minio_client.make_bucket(settings.minio_bucket_name)
            logger.info(f"Bucket '{settings.minio_bucket_name}' created.")
        else:
            logger.info(f"Bucket '{settings.minio_bucket_name}' already exists.")
    except S3Error as e:
        error_code = MinIOStatusCodes.NO_SUCH_BUCKET if e.code == "NoSuchBucket" else MinIOStatusCodes.FAILURE
        logger.error(f"Error checking/creating bucket: {str(e)}")
        raise Exception(f"Setup error: {MinIOStatusCodes.get_status_description(error_code)}")

# Upload a file to MinIO with reference count handling
def upload_to_minio(file_data: bytes, bucket_name: str, object_name: str):
    try:
        # Check if object already exists
        try:
            stat = minio_client.stat_object(bucket_name, object_name)
            # Increment the reference count if object exists
            ref_count = int(stat.metadata.get("x-amz-meta-ref-count", 0)) + 1

            # Update the metadata with the new reference count
            copy_source = CopySource(bucket_name, object_name)
            minio_client.copy_object(
                bucket_name,
                object_name,
                copy_source,
                metadata={"x-amz-meta-ref-count": str(ref_count)},
                metadata_directive="REPLACE"
            )
            logger.info(f"Reference count updated to {ref_count} for object {object_name}")
            return MinIOStatusCodes.OBJECT_ALREADY_EXIST
        except S3Error as e:
            if e.code != "NoSuchKey":
                logger.error(f"Error checking object existence: {str(e)}")
                return MinIOStatusCodes.FAILURE

        # Upload file with initial reference count
        metadata = {"x-amz-meta-ref-count": "1"}
        file_like_object = io.BytesIO(file_data)
        minio_client.put_object(bucket_name, object_name, file_like_object, length=len(file_data), metadata=metadata)
        logger.info(f"File uploaded successfully to {bucket_name}/{object_name} with ref-count 1")
        return MinIOStatusCodes.SUCCESS
    except S3Error as e:
        logger.error(f"Upload failed: {str(e)}")
        return MinIOStatusCodes.FAILURE

# Generate MinIO object URL
def get_minio_object_url(bucket_name: str, object_name: str) -> str:
    return f"{settings.minio_endpoint}/{bucket_name}/{object_name}"

# Delete an object reference from MinIO
def delete_from_minio(bucket_name: str, object_name: str) -> int:
    """
    Decrements the reference count of an object and deletes it if the count reaches zero.
     :param bucket_name: The name of the bucket
     :param object_name: The name of the object to delete
     :return: MinIOStatusCodes.SUCCESS if successful, otherwise an error code
    """
    try:
        # Check the current reference count
        stat = minio_client.stat_object(bucket_name, object_name)
        ref_count = int(stat.metadata.get("x-amz-meta-ref-count", 0))

        if ref_count > 1:
            # Decrement the reference count
            ref_count -= 1

            logger.info(f"Deleting object {object_name} from bucket {bucket_name}")
            # Update the metadata with the decremented reference count
            copy_source = CopySource(bucket_name, object_name)
            minio_client.copy_object(
                bucket_name,
                object_name,
                copy_source,
                metadata={"x-amz-meta-ref-count": str(ref_count)},
                metadata_directive="REPLACE"
            )
            logger.info(f"Reference count decremented to {ref_count} for object {object_name}")
            return MinIOStatusCodes.SUCCESS
        else:
            # Delete the object if reference count reaches zero
            minio_client.remove_object(bucket_name, object_name)
            logger.info(f"Object '{object_name}' deleted from bucket '{bucket_name}' as reference count reached 0")
            return MinIOStatusCodes.SUCCESS
    except S3Error as e:
        if e.code == "NoSuchKey":
            logger.warning(f"Object '{object_name}' not found in bucket '{bucket_name}'")
            return MinIOStatusCodes.OBJECT_NOT_FOUND
        else:
            logger.error(f"Failed to delete object '{object_name}' from bucket '{bucket_name}': {str(e)}")
            return MinIOStatusCodes.FAILURE