import boto
import gcs_oauth2_boto_plugin
import os
import shutil
import StringIO
import tempfile
import time
from google.cloud import storage


GOOGLE_STORAGE = 'gs'
# URI scheme for accessing local files.
LOCAL_FILE = 'file'
DOGS_BUCKET ='others-1543514007'

source = "/home/emeka/codes/environment/www/actsciArchive-unilag/static/files/10.pdf"
fff = "1.pdf"


def download_blob(bucket_name, source_blob_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(source_blob_name)

    print('downloaded ' +source_blob_name)


download_blob(DOGS_BUCKET, fff)




# def upload_blob(DOGS_BUCKET, source_file_name, destination_blob_name="a blob has no name"):
#     """Uploads a file to the bucket."""
#     storage_client = storage.Client()
#     bucket = storage_client.get_bucket(DOGS_BUCKET)
#     blob = bucket.blob(destination_blob_name)

#     blob.upload_from_filename(source_file_name)

#     print('File {} uploaded to {}.'.format(
#         source_file_name,
#         destination_blob_name))

# upload_blob(DOGS_BUCKET, source)


# dest_dir = os.getenv('HOME')
# for filename in ('collie.txt', 'labrador.txt'):
#   src_uri = boto.storage_uri(
#       DOGS_BUCKET + '/' + filename, GOOGLE_STORAGE)

#   # Create a file-like object for holding the object contents.
#   object_contents = StringIO.StringIO()

#   # The unintuitively-named get_file() doesn't return the object
#   # contents; instead, it actually writes the contents to
#   # object_contents.
#   src_uri.get_key().get_file(object_contents)

#   local_dst_uri = boto.storage_uri(
#       os.path.join(dest_dir, filename), LOCAL_FILE)

#   bucket_dst_uri = boto.storage_uri(
#       DOGS_BUCKET + '/' + filename, GOOGLE_STORAGE)

#   for dst_uri in (local_dst_uri, bucket_dst_uri):
#     object_contents.seek(0)
#     dst_uri.new_key().set_contents_from_file(object_contents)

#   object_contents.close()





# # Your project ID can be found at https://console.cloud.google.com/
# # If there is no domain for your project, then project_id = 'YOUR_PROJECT'
# project_id = 'project-actsci'

# # Make some temporary files.
# temp_dir = "/home/emeka/codes/environment/www/actsciArchive-unilag/static/files"
# filename = "1.pdf"
# # Upload these files to DOGS_BUCKET.

# with open(os.path.join(temp_dir, filename), 'r') as localfile:


#     dst_uri = boto.storage_uri(DOGS_BUCKET + '/' + filename, GOOGLE_STORAGE)
# # The key-related functions are a consequence of boto's
# # interoperability with Amazon S3 (which employs the
# # concept of a key mapping to localfile).
#     dst_uri.new_key().set_contents_from_file(localfile)
#     print 'Successfully created "%s/%s"' % (dst_uri.bucket_name, dst_uri.object_name)

# shutil.rmtree(temp_dir)  # Don't forget to clean up!
