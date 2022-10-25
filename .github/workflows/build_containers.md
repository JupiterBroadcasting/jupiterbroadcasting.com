# Containers Docs

This is the documentation for how the build_container-*.yml files works, and the needed permissions/setup around it.

## Registry

We're using quay.io for the container registry, reasons why are outlined in [this comment](https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/issues/244#issuecomment-1213146790)

## Authentication to registry

1. Naviage to: <https://quay.io/signin/>
2. Create a Red Hat account if you don't have one, or sign in
3. Navigate to the following (be sure to replace `<username>` with your quay.io username): `https://quay.io/user/<username>?tab=repos`
4. Click "Create New Repository" (near the top right)
5. Give the repo a name (this will be the name of you container) i.e. jb_web_container
6. Make sure you've selected the Repository Visibility as Public and you're going to be choosing "(Empty repository)" for the Initialize repository section
7. Navigate to the following (be sure to replace `<username>` with your quay.io username): `https://quay.io/user/<username>?tab=robots`
8. Click "Create Robot Account"
9. Give the robot a name (i.e. `jb_web_container`), and a description
10. find the repo you just created, and select the dropdown that says "None"
11. Choose the "Write" permission
12. Click "Add permissions"
13. Click on the gear on the far right side of the screen for your new robot account
14. Click "View Credentials"
15. Create an environment variables based on [this guide](https://blog.elreydetoda.site/github-action-security/), and have the environment name called production_containers.
16. Click "Add Secret" under Environment secrets, and add the following secrets
    * `REGISTRY_PASSWORD` = your robot account token (long string of random characters)
17. Then go to this link (replace `GH_user_name` with your GitHub username): `https://github.com/jupiterbroadcasting/jupiterbroadcasting.com/settings/secrets/actions/new`, to create a repo secret
    * `REGISTRY_USER` = your robot account username
      * This isn't necessarily that sensative, so creating a repo secret instead of an environment secret is ok
