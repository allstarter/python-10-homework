#!/usr/bin/env python3
from aws_cdk import App
from cdk_stack.cdk_s3_image_resizing_stack import CdkS3ImageResizingStack


app = App()
CdkS3ImageResizingStack(app, "cdk-s3-image-resizing")

app.synth()
