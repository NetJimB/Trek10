

To deploy:
```
aws cloudformation package --template-file template.yaml --output-template-file template.package.yaml --s3-bucket <BUCKET_NAME>
aws cloudformation deploy --template-file template.package.yaml --stack-name ms-isac-waf --capabilities CAPABILITY_IAM
```

Get the rules bucket using this command:
```
aws cloudformation describe-stacks --stack-name ms-isac-waf --query "Stacks[0].Outputs[?OutputKey=='RulesBucket'].OutputValue" --output text
```

Create a file and put the MS-ISAC information here. It has to be in CIDR format

Example file waf.txt:
```
145.239.23.7/32
```

When that is uploaded, it will rewrite the rules to exclude any IP ranges entered. If the file is deleted, it will remove the IP ranges from the WAF
