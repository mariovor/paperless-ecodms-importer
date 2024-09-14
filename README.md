# Importer from EcoDMS to Paperless-ngx


## What can it do?

First, take into account that **THIS IS IN DEVELOPMENT AND WORK IN PROGRESS**. 

Secondly, reading the EcoDMS backup might not work for you because of configuration differences between EcoDMS instances.

**Supported**

* Read your EcoDMS backup and upload files to paperless.

**Not Supported**

At the moment, no metadata is used from EcoDMS

## Prerequisites

* Running instance of Paperless.
* An export of EcoDMS already unzipped on your hard disk.
* An authentication token for your account in paperless.

##
Set the environment variables

* *ECODMS_PATH_EXPORT_FILE*: The path to the export file, e.g., */home/user/export/offline_export/archive/export.xml*.
* *PAPERLESS_API_URL*: The url to your paperless instance without trailing slash. For a local instance, e.g., http://localhost:9000/api.
* *PAPERLESS_TOKEN*: Your token for your account.

Run *import_from_ecdms_to_paperless.py*. 


