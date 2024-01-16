# Video Archiving Insights

A dashboard for video archiving insights based on accumulated metadata.

## To run

1. Install the pip3 package `internetarchive` onto the host machine and run `ia configure`. Either copy or hardlink the credential file (i.e. `ia.ini`) into the root of the project directory. This is required in order for the Dockerfile to build properly.
1. Run `docker compose up`
