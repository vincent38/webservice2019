git add .
git commit -m a
git push
gcloud app deploy --project chinajapanbbs --version 1
gcloud app deploy cron.yaml --project chinajapanbbs --version 1
gcloud app deploy index.yaml --project chinajapanbbs --version 1