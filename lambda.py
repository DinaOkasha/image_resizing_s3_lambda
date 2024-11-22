import boto3
from PIL import Image
from io import BytesIO

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Get bucket and object key from event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    
    destination_bucket = 'image-upload-resized-bucket1'
    resized_key = f"resized-{source_key}"
    
    try:
        # Fetch the image from the source bucket
        response = s3.get_object(Bucket=source_bucket, Key=source_key)
        image_data = response['Body'].read()
        
        # Open the image and resize it
        with Image.open(BytesIO(image_data)) as img:
            # Resize to half the original size
            width, height = img.size
            img_resized = img.resize((width // 2, height // 2))
            
            # Save resized image to a buffer
            buffer = BytesIO()
            img_resized.save(buffer, format=img.format)
            buffer.seek(0)
        
        # Upload the resized image to the destination bucket
        s3.put_object(Bucket=destination_bucket, Key=resized_key, Body=buffer, ContentType=response['ContentType'])
        
        print(f"Image resized and uploaded to {destination_bucket}/{resized_key}")
        return {"statusCode": 200, "body": "Image resized successfully."}
    
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": "Error processing image."}



#s3 bucket names: 'image-upload-sourse-bucket' ,'image-upload-resized-bucket1'
#iam policies fore the lambda role: 
#AmazonS3FullAccess (for simplicity in this scenario).
#AWSLambdaBasicExecutionRole.

#or

# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Action": [
#                 "s3:GetObject",
#                 "s3:PutObject"
#             ],
#             "Resource": [
#                 "arn:aws:s3:::image-upload-source-bucket/*",
#                 "arn:aws:s3:::image-upload-resized-bucket/*"
#             ]
#         },
#         {
#             "Effect": "Allow",
#             "Action": [
#                 "logs:CreateLogGroup",
#                 "logs:CreateLogStream",
#                 "logs:PutLogEvents"
#             ],
#             "Resource": "arn:aws:logs:*:*:*"
#         }
#     ]
# }
