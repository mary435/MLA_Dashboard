# How to connect dbt:

1. Sign up for a new account on the dbt website (https://cloud.getdbt.com/signup).
2. Once you have created an account, log in and create a new project.
3. If you already used dbt in another project in the upper right corner, select "Create new account". Enter a name and click create.
4. Choose a connection: select bigquery and click next. Then click on the green button "Upload a Service Account JSON file". And we upload the same file that we downloaded before. Finally click on "test connection".
5. Setup a Repository: Select "git clone" and paste the url of your repository that we just cloned. Finally click on "next".
6. The project is created and now you can see the project in develop.


# How configure dbt to update the data automatically every day:
1. At the top left look for the deploy option: Click on Environments.
2. Create Environment.
3. Chose a name: "Production", Environment Type: Deployment and dbt Version latest.
4. On Deployment Credentials: Dataset: production. And save it.
5. At the top left look for the deploy option: Click on Jobs.
6. Create a new Job.
7. Chose a name, Environment: "Production", check on Generate docs on run.
8. Add a schedule so that it runs every day at 2:00 p.m. (1 hour later than prefect)
9. And save.
10. Run now to try it.




