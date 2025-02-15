# Importer from EcoDMS to Paperless-ngx


## What can it do?

First, take into account that this script was a one-shot and used for my migration from EcoDMS to paperless.
The migration has been completed. 

Secondly, reading the EcoDMS backup might not work for you because of configuration differences between EcoDMS instances.

**Supported**

* Read your EcoDMS backup and upload files to paperless.
* Metadata:
  * Title
  * Create date
  * Folder (as tag)
  * Document Type
  * Archive number
  * Tax relevance (as tag)

**Not Supported**

At the moment, no other metadata is used from EcoDMS.

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


