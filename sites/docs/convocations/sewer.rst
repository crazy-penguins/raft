sewer tasks
===========

The sewer convocation allows you to easily create / renew certs from letsencrypt
in an aws environment by using the route53 DNS provider.

iam permission needed
=====================

The sewer convocations need some pretty hefty perms since they will be making
dns entries in the route53 hosted zone for letsencrypt dns verification,
pushing the certificates into ssm for ease of delivery, and encrypting
the private key with a specified kms key.

Here are the perms / actions that we recommend:

.. code-block:: yaml

      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: "Allow"
            Principal:
              Service:
                - "ec2.amazonaws.com"
            Action:
              - "sts:AssumeRole"
      Policies:
        - PolicyName: ssm-parameter-writer
          PolicyDocument:
            Version: 2012-10-17
            Statement:
              - Effect: Allow
                Action:
                  - "ssm:putparam*"
                Resource:
                  - !Sub "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/path/to/prefix/*"
        - PolicyName: ssm-parameter-reader
          PolicyDocument:
            Version: 2012-10-17
            Statement:
              - Effect: Allow
                Action:
                  - "ssm:getparam*"
                Resource:
                  - !Sub "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/path/to/prefix/*"
        - PolicyName: ssm-parameter-describer
          PolicyDocument:
            Version: 2012-10-17
            Statement:
              - Effect: Allow
                Action:
                  - "ssm:describeparameters"
                Resource:
                  - '*'
        - PolicyName: prod-and-staging-encryptor
          PolicyDocument:
            Version: 2012-10-17
            Statement:
              - Effect: Allow
                Action:
                  - "kms:DescribeKey"
                  - "kms:Encrypt"
                  - "kms:GenerateDataKeyWithoutPlaintext"
                  - "kms:GenerateRandom"
                Resource:
                  - "key-1-arn"
                  - "key-2-arn"
        - PolicyName: route53-changer
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: "Allow"
                Resource: "*"
                Action:
                  - "route53:listhostedzones"
                  - "route53:gethostedzone"
                  - "route53:gethostedzonecount"
              - Effect: "Allow"
                Resource:
                  - "arn:aws:route53:::hostedzone/${hosted_zone}"
                Action:
                  - "route53:changeresourcerecordsets"
                  - "route53:listresourcerecordsets"
