from storages.backends.s3boto3 import S3Boto3Storage
from storages.backends.s3boto3 import S3StaticStorage

# 장고 MEDIA 파일을 다루는 각종 설정을 커스텀할 수 있습니다.
#  - "media" 폴더에 저장되도록 location 설정을 해줍니다.
#  - "public-read" 권한으로 업로드되도록 default_acl 설정을 해줍니다.
class AwsMediaStorage(S3Boto3Storage):
    location = "media"
    default_acl = "public-read"

# 장고 STATIC 파일을 다루는 각종 설정을 커스텀할 수 있습니다.
#  - "static" 폴더에 저장되도록 location 설정을 해줍니다.
#  - "public-read" 권한으로 업로드되도록 default_acl 설정을 해줍니다.
class AwsStaticStorage(S3StaticStorage):
    location = "static"
    default_acl = "public-read"
