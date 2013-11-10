mv puppet/manifests/gybatch.pp puppet/manifests/gybatch.pp.bu
mv puppet/modules/python/manifests/venv/isolate.pp puppet/modules/python/manifests/venv/isolate.pp.bu
mv puppet/manifests/files/celeryflower.conf puppet/manifests/files/celeryflower.conf.bu
cp aws_files/gybatch.pp puppet/manifests/gybatch.pp
cp aws_files/isolate.pp puppet/modules/python/manifests/venv/isolate.pp
cp aws_files/celeryflower.conf puppet/manifests/files/celeryflower.conf

echo
echo "Applied AWS changes to puppet files (old files in .bu)"
echo "Diff:"
echo 

diff aws_files/gybatch.pp puppet/manifests/gybatch.pp
diff aws_files/isolate.pp puppet/modules/python/manifests/venv/isolate.pp
diff aws_files/celeryflower.conf puppet/manifests/files/celeryflower.conf
