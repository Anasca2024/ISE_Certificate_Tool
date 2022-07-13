# ISE_Certificate_Tool

This tool was tested with ISE 3.1. It may work with earlier versions but remains untested.

This tool can perform certificate importation and certificate viewing for any or all ISE nodes specified within a deployment.

This tool does some validation such as connection validation, credential validation, and conflicting certificates.

This tool prints the raw response of the ISE node when an error occurs. It will, in some cases, also print a suggested course of action to trouble shoot the issue based on the most common reasons for the issue.

# Installation
### Download 

git clone https://github.com/Anasca2024/ISE_Certificate_Tool

cd ISE_Certificate_Tool

### Install requirements
pip3 install -r requirements.txt

# Usage
### Option notes:

-l used to list all certificates on the designated nodes. This is one of two functionalities offered in this tool and can be used in combination with the install feature specified by -i. 

-i used to install certificates on the designated nodes and can be used in combination with -l.

-n this is used to specify the primary admin node. You must use a single IP address that is assigned to the node. 

-N used to specify specific nodes to run the process on. NOTE: you may only list nodes within the deployment. The primary admin node specified by -n will be omitted unless added to the list.

-P this option is used for a portal certificate tag. To use the default portal tag you would use -P \<any input>. To specify a portal tag, use a colon followed by the custom tag, ex: -P : example tag .

    All options:

      -h, --help            show this help message and exit
      -l                    List all certificates. Required: -n, -u, and -p. Other options are ignored.
      -i                    import certificate. Required: -n, -u, -p, -c, -f, and -k. Other options are ignored.
      -n <isenode>          ISE IP address
      -u <username>         GUI Admin username
      -p <password>         GUI Admin password
      -c <certfile>         Path to certificate file
      -f <keyfile>          Path to key file
      -k <keypassword>      Key encryption password
      -N <node> [<node> ...]
                            Node list (ipv4, FQDN, or hostname) to install certificate. Space separated.
      -A                    Certificate will be installed on all nodes
      -D                    Admin uses certificate
      -P <portal> [<portal> ...]
                            Portal uses certificate. A non-default tag is specified with P : <tag>
      -E                    Eap uses certificate
      -X                    Pxgrid uses certificate
      -R                    Radius uses certificate
      -S                    SAML uses certificate


### EXAMPLE 1: Listing all system certificates on one node
    $ ./python cert_tool.py   -l   -n 192.168.1.1 -u admin -p Password
    Testing connection to 192.168.1.1...
    Connection to 192.168.1.1 Successful!!!

    Loading certificates...

    ISE-Pod1:
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |  Certificate  |   Protocol    |   Issued To   |  Issued By   |  Valid From  |   Valid To   |  Days Until  | Expired? |
    |      ID       |               |               |              |              |              |  Expiration  |          |
    +===============+===============+===============+==============+==============+==============+==============+==========+
    |   2ba25388-   | ISE Messaging | ISE-Pod.lab   | Certificate  |  Wed Apr 27  |  Wed Apr 28  |  1764 days   |  VALID   |
    |  776d-4179-   |    Service    |    .com       |   Services   | 10:57:35 EST | 10:57:35 EST |              |          |
    |     9a7d-     |               |               | Endpoint Sub |     2022     |     2027     |              |          |
    | 99291375bd14  |               |               |  CA - ISE-   |              |              |              |          |
    |               |               |               |     Pod      |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |   9a0d9d67-   |    pxGrid     | ISE-Pod.lab   | Certificate  |  Wed Apr 27  |  Wed Apr 28  |  1764 days   |  VALID   |
    |  fdc8-4a54-   |               |    .com       |   Services   | 10:57:33 EST | 10:57:33 EST |              |          |
    |     9cb2-     |               |               | Endpoint Sub |     2022     |     2027     |              |          |
    | 9e8da806c6d1  |               |               |  CA - ISE-   |              |              |              |          |
    |               |               |               |     Pod      |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    | ebaac6ef-af74 |  Not in use   | ISE-Pod.lab   | ISE-Pod.lab  |  Wed Jun 29  |  Thu Jun 29  |   365 days   |  VALID   |
    |  -4f74-af3d-  |               |    .com       |   .com       | 07:24:34 EST | 07:24:34 EST |              |          |
    | d20d429c76f0  |               |               |              |     2022     |     2023     |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |   ebb5a742-   |    Admin,     | ISE-Pod.lab   | ISE-Pod.lab  |  Thu Apr 28  |  Sat Apr 27  |   668 days   |  VALID   |
    |  dba2-4212-   | Portal, EAP A |    .com       |   .com       | 10:56:40 EST | 10:56:40 EST |              |          |
    |     84e9-     | uthentication |               |              |     2022     |     2024     |              |          |
    | e68767e101d7  | , RADIUS DTLS |               |              |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |   60560a00-   |     SAML      | SAML_ISE-Pod. | SAML_ISE-Pod |  Thu Apr 28  |  Tue Apr 27  |  1763 days   |  VALID   |
    |  8e89-40be-   |               |    lab.com    | .lab.com     | 10:56:58 EST | 10:56:58 EST |              |          |
    |     8bdc-     |               |               |              |     2022     |     2027     |              |          |
    | 2aaf12aeff32  |               |               |              |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+

### EXAMPLE 2: Installing a certificate for EAP on two nodes

    $ ./python cert_tool.py   -l -i  -n 192.168.1.1 -u admin -p password -c CNrweheise31cssl.pem -f CNrweheise31cssl.pvk -k Password -N 192.168.1.1 rwehe-ise-2 -E
    Testing connection to 192.168.1.1...
    Connection to 192.168.1.1 Successful!!!

    Importing certificate...

    rwehe-ise:
    Certificate Successfully Imported.


    Loading certificates...

    rwehe-ise:
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |  Certificate  |   Protocol    |   Issued To   |  Issued By   |  Valid From  |   Valid To   |  Days Until  | Expired? |
    |      ID       |               |               |              |              |              |  Expiration  |          |
    +===============+===============+===============+==============+==============+==============+==============+==========+
    |   f3c0a2a7-   |     SAML      |  SAML_rwehe-i | SAML_rwehe-i |  Wed May 11  |  Mon May 10  |  1776 days   |  VALID   |
    |  d255-481e-   |               |  se.lab.local | se.lab.local | 23:12:07 UTC | 23:12:07 UTC |              |          |
    |     8785-     |               |               |              |     2022     |     2027     |              |          |
    | 0296ea0fc7a4  |               |               |              |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |   f7c265c0-   |    Admin,     |   rwehe-ise.  |  rwehe-ise.  |  Mon Jun 27  |  Wed Jun 26  |   728 days   |  VALID   |
    |  e40f-48f0-   |    Portal,    |    lab.com    |   lab.com    | 18:35:06 UTC | 18:35:06 UTC |              |          |
    |     8b8b-     |  RADIUS DTLS  |               |              |     2022     |     2024     |              |          |
    | b802d4f8b9f5  |               |               |              |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |   2b62a046-   |    pxGrid     |   rwehe-ise.  | Certificate  |  Sun Jun 26  |  Sun Jun 27  |  1824 days   |  VALID   |
    |  5c67-42a0-   |               |    lab.com    |   Services   | 19:08:42 UTC | 19:08:42 UTC |              |          |
    |     bb91-     |               |               | Endpoint Sub |     2022     |     2027     |              |          |
    | a191d120334a  |               |               | CA - rwehe-  |              |              |              |          |
    |               |               |               |    ise       |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |   cc8fb3f2-   | ISE Messaging |   rwehe-ise.  | Certificate  |  Sun Jun 26  |  Sun Jun 27  |  1824 days   |  VALID   |
    |  29a6-ec96-   |    Service    |    lab.com    |   Services   | 19:09:50 UTC | 19:09:50 UTC |              |          |
    |     be1b-     |               |               | Endpoint Sub |     2022     |     2027     |              |          |
    | 9ce46cce56f4  |               |               | CA - rwehe-  |              |              |              |          |
    |               |               |               |    ise       |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |   0d09689c-   | EAP Authentic |   rwehe-ise.  |  rwehe-ise.  |  Tue Jun 28  |  Wed Jun 28  |   364 days   |  VALID   |
    |  e8d1-4a8a-   |     ation     |    lab.com    |   lab.com    | 15:51:35 UTC | 15:51:35 UTC |              |          |
    |     8745-     |               |               |              |     2022     |     2023     |              |          |
    | 79e31b8168d1  |               |               |              |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+

    Importing certificate...

    rwehe-ise-2:
    Certificate Successfully Imported.


    Loading certificates...

    rwehe-ise-2:
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |  Certificate  |   Protocol    |   Issued To   |  Issued By   |  Valid From  |   Valid To   |  Days Until  | Expired? |
    |      ID       |               |               |              |              |              |  Expiration  |          |
    +===============+===============+===============+==============+==============+==============+==============+==========+
    |   18c212f1-   |    Admin,     |  rwehe-ise-2  |  rwehe-ise-2 |  Mon Jun 27  |  Wed Jun 26  |   728 days   |  VALID   |
    |  5773-4955-   |    Portal,    |   .lab.com    |   .lab.com   | 20:34:10 UTC | 20:34:10 UTC |              |          |
    |     8c17-     |  RADIUS DTLS  |               |              |     2022     |     2024     |              |          |
    | 525cf379c0e0  |               |               |              |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |   bc836a25-   |     SAML      | SAML_rwehe-is |  SAML_rwehe- |  Wed May 11  |  Mon May 10  |  1776 days   |  VALID   |
    |  ae4b-4b58-   |               |     e.lab.    |   ise.lab.   | 23:12:07 UTC | 23:12:07 UTC |              |          |
    |     b83e-     |               |     local     |    local     |     2022     |     2027     |              |          |
    | 2326b48f4b98  |               |               |              |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |   1bb142af-   | ISE Messaging |  rwehe-ise-2  | Certificate  |  Sun Jun 26  |  Sun Jun 27  |  1824 days   |  VALID   |
    |  34fd-4506-   |    Service    |   .lab.com    |   Services   | 23:53:20 UTC | 23:53:20 UTC |              |          |
    |     b69b-     |               |               | Endpoint Sub |     2022     |     2027     |              |          |
    | 9f5e3edb0116  |               |               | CA - rwehe-  |              |              |              |          |
    |               |               |               |   ise-2      |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |   e1a07dd8-   |    pxGrid     |  rwehe-ise-2  | Certificate  |  Sun Jun 26  |  Sun Jun 27  |  1824 days   |  VALID   |
    |  0ec5-41aa-   |               |   .lab.com    |   Services   | 23:53:20 UTC | 23:53:20 UTC |              |          |
    |     81cf-     |               |               | Endpoint Sub |     2022     |     2027     |              |          |
    | 44874afe81cd  |               |               | CA - rwehe-  |              |              |              |          |
    |               |               |               |   ise-2      |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    |   5fedcd85-   | EAP Authentic | rwehe-ise.lab | rwehe-ise.lab|  Tue Jun 28  |  Wed Jun 28  |   364 days   |  VALID   |
    |  1fb7-46c4-   |     ation     |     .com      |     .com     | 15:51:35 UTC | 15:51:35 UTC |              |          |
    |     ae77-     |               |               |              |     2022     |     2023     |              |          |
    | 9c2e9b506be8  |               |               |              |              |              |              |          |
    +---------------+---------------+---------------+--------------+--------------+--------------+--------------+----------+
    
# Copyright & License
### Copyright (c) 2022 Cisco Systems, Inc. and its affiliates
### All rights reserved.

### Licensed under the MIT License. You may obtain a copy of this license at the following link:

### https://spdx.org/licenses/MIT.html 

