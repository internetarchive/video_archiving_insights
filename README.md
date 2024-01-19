# Video Archiving Insights

A dashboard for video archiving insights based on accumulated metadata.

## To run

1. Install the pip3 package `internetarchive` onto the host machine and run `ia configure`. Either copy or hardlink the credential file (i.e. `ia.ini`) into the root of the project directory. This is required in order for the Dockerfile to build properly.
1. Run `docker compose up`

## TODO

1. Devise better warning strategy for viewmode > 1 day because they clutter the viewport when there are many (occurs in December of 2023).
1. Consider caching failed downloads as empty data when catching download errors in order to speed up the loading of viewmodes > 1 day.

## Bugs

1. When downloading metadata for days with the wrong name formatting, the loading of the metadata will fail, but the program fails to cleanup the remaining files after failure. See 2023-12-10 through 2023-12-13 for examples.
