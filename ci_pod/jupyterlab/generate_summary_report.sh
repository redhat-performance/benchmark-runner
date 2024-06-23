#!/bin/sh
/usr/local/bin/jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root &
# Sleep for a few seconds to allow JupyterLab to start
echo sleep 10
sleep 10
echo generate html summary report
/usr/local/bin/jupyter nbconvert --to html --execute /notebooks/templates/summary_report/summary_report.ipynb
echo update summary report version
echo sleep 10
sleep 10
/usr/local/bin/jupyter nbconvert --execute /notebooks/templates/summary_report/update_summary_report_versions.ipynb --to notebook --inplace
# Keep the container running
tail -f /dev/null
