# How connect to gcs:

1. Go to the Google Cloud sign-up page at https://console.cloud.google.com/.
2. Click on "Get Started for Free" in the top right corner.
3. If you already have a Google account, sign in. If not, follow the instructions to create a new account.
4. Once you have signed in, you will be taken to the Google Cloud Console. Click on the project dropdown menu in the top navigation bar and select "New Project."
5. In the "New Project" dialog box, enter "mla_dashboard_zoom" as the project name and click "Create."
6. Once the project is created, you will be taken to the project dashboard. Click on the navigation menu in the top left corner and select "Storage" under the "Storage" section.
7. Click on the "Create Bucket" button to create a new bucket.
8. In the "Create a bucket" dialog box, enter "mla_bucket" as the bucket name and click "Create."
9. Your bucket has now been created! You can use it to store files for the project.
10. Now go to the GCS console and navigate to the IAM & Admin section.
11. Click on "Service Accounts" and then click the "Create Service Account" button.
12. Enter a name for your service account, such as "mla-service-account", and click "Create".
13. On the next page, you'll be asked to add roles to your service account. For this example, we'll add the "BigQuery Admin" and "Storage Admin" roles. Select these roles from the list and click "Continue".
14. You'll now be presented with a summary of your service account details. Click "Done" to finish creating the account.
15. Select your newly created service account from the list, and then click on the "Keys" option.
16. Click on "Add Key" and select "JSON" as the key type. This will download a JSON file containing your service account's credentials.
17. Open the downloaded file and copy its contents.

# UI Prefect Config

1. In the Prefect UI, go to the "Bloks" page and create a new connection.
2. Select "GCS Bucket" as the connection type, and add+.
3. Block & Bucket Name: "mla-bucket".
4. On Gcp Credentials +add.
5. Now on Service Account Info paste the content of the file copied before with the user data.
6. Click "Create" and "Save" to save your connection.