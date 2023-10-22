import aws_cdk as core
import aws_cdk.assertions as assertions

from mirage.mirage_stack import mirageStack

# example tests. To run these tests, uncomment this file along with the example
# resource in mirage/mirage_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = mirageStack(app, "mirage")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
